// Um elemento por peça (chave: id), reaproveitado entre jogadas para poder animar.

const FILES = "abcdefgh";
const DUR = { hop: 220, place: 180, remove: 180, flip: 260, promote: 260 };
const EASE = "ease-in-out";

const xy = (sq) => [FILES.indexOf(sq[0]), Number(sq.slice(1)) - 1];
const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function color(player) {
  return player === 1 ? "var(--player1)" : player === 2 ? "var(--player2)" : "#b9af9a";
}

function stepDuration(s) {
  return s.kind === "move" ? DUR.hop * (s.path.length - 1) : DUR[s.kind];
}

export function totalDuration(groups) {
  return groups.reduce((t, g) => t + Math.max(...g.map(stepDuration)), 0);
}

export function createAnimator(boardEl) {
  const els = new Map();
  let target = [];
  let lastPlayer = null;
  let token = 0;

  function inner(piece) {
    if (piece.type === "block") {
      const block = document.createElement("div");
      block.className = "block";
      return block;
    }
    const disc = document.createElement("div");
    disc.className = "disc";
    disc.dataset.type = piece.type;
    disc.style.background = color(piece.player ?? lastPlayer);
    return disc;
  }

  function put(piece) {
    let el = els.get(piece.id);
    if (!el) {
      el = document.createElement("div");
      el.className = "piece";
      els.set(piece.id, el);
      boardEl.appendChild(el);
    }
    const [col, row] = xy(piece.position);
    el.style.left = `${(col / 8) * 100}%`;
    el.style.top = `${((7 - row) / 8) * 100}%`;
    el.replaceChildren(inner(piece));
    return el;
  }

  function drop(id) {
    els.get(id)?.remove();
    els.delete(id);
  }

  function sync(pieces) {
    const keep = new Set(pieces.map((p) => p.id));
    [...els.keys()].filter((id) => !keep.has(id)).forEach(drop);
    pieces.forEach(put);
  }

  function animate(el, keyframes, duration) {
    const a = el.animate(keyframes, { duration, easing: EASE });
    return a.finished.then(
      () => true,
      () => false // cancelada por finish()
    );
  }

  function run(step, scale, pieceOf) {
    const el = els.get(step.id);
    if (step.kind === "place") {
      const node = put(step.piece);
      return animate(node.firstChild, [{ transform: "scale(0)", opacity: 0 }, { transform: "scale(1)", opacity: 1 }], DUR.place * scale);
    }
    if (!el) return Promise.resolve();
    if (step.kind === "move") {
      const [fc, fr] = xy(step.path[step.path.length - 1]);
      const frames = step.path.map((sq) => {
        const [c, r] = xy(sq);
        return { transform: `translate(${(c - fc) * 100}%, ${(fr - r) * 100}%)` };
      });
      const piece = pieceOf(step.id);
      if (piece) put({ ...piece, position: step.path[step.path.length - 1] });
      el.style.zIndex = 2;
      return animate(el, frames, stepDuration(step) * scale).then(() => (el.style.zIndex = ""));
    }
    if (step.kind === "remove") {
      return animate(el, [{ transform: "scale(1)", opacity: 1 }, { transform: "scale(0.6)", opacity: 0 }], DUR.remove * scale).then(
        (done) => done && els.get(step.id) === el && drop(step.id)
      );
    }
    if (step.kind === "flip") {
      const from = el.firstChild.style.background;
      const to = color(step.player);
      el.firstChild.style.background = to;
      Object.assign(pieceOf(step.id) ?? {}, { player: step.player });
      return animate(el.firstChild, [
        { transform: "rotateY(0)", background: from },
        { transform: "rotateY(90deg)", background: from, offset: 0.5 },
        { transform: "rotateY(90deg)", background: to, offset: 0.5 },
        { transform: "rotateY(0)", background: to },
      ], DUR.flip * scale);
    }
    if (step.kind === "promote") {
      const node = put(step.piece);
      Object.assign(pieceOf(step.id) ?? {}, { type: step.piece.type });
      return animate(node.firstChild, [
        { transform: "scale(0.6)", opacity: 0.4 },
        { transform: "scale(1.25)", opacity: 1, offset: 0.6 },
        { transform: "scale(1)" },
      ], DUR.promote * scale);
    }
    return Promise.resolve();
  }

  // termina na hora o que estiver tocando e deixa o tabuleiro no estado final
  function finish() {
    token++;
    boardEl.getAnimations({ subtree: true }).forEach((a) => a.cancel());
    els.forEach((el) => (el.style.zIndex = ""));
    sync(target);
  }

  function reset(pieces, player = null) {
    token++;
    boardEl.getAnimations({ subtree: true }).forEach((a) => a.cancel());
    els.forEach((el) => el.remove());
    els.clear();
    target = pieces;
    lastPlayer = player;
    sync(pieces);
  }

  // `start`: posição antes da jogada; `budget`: tempo máximo em ms (reprodução automática)
  async function play(groups, start, finalPieces, { player = null, scale = 1, budget } = {}) {
    finish();
    const mine = token;
    target = finalPieces;
    lastPlayer = player;
    if (reducedMotion() || !groups.length) return sync(finalPieces);

    const total = totalDuration(groups) * scale;
    if (budget) scale *= Math.min(1, (0.7 * budget) / total);
    const current = new Map(start.map((p) => [p.id, { ...p }]));
    const pieceOf = (id) => current.get(id);

    for (const group of groups) {
      group.filter((s) => s.kind === "place").forEach((s) => current.set(s.id, { ...s.piece }));
      await Promise.all(group.map((s) => run(s, scale, pieceOf)));
      if (mine !== token) return;
      group.forEach((s) => {
        if (s.kind === "remove") current.delete(s.id);
        if (s.kind === "move") current.get(s.id).position = s.path[s.path.length - 1];
      });
    }
    sync(finalPieces);
  }

  return { reset, play, finish };
}
