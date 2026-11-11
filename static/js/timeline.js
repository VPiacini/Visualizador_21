// Transforma uma jogada em passos de animação, sem tocar no DOM.
// Passos de um mesmo grupo tocam juntos; os grupos tocam em sequência.

const placedId = (a) => a.id ?? `${a.piece.type}-${a.position}`;

// trecho do path entre origem e destino; sem os dois em ordem, linha reta
function route(path, from, to) {
  const i = path.indexOf(from);
  const j = path.indexOf(to, i + 1);
  return i >= 0 && j > i ? path.slice(i, j + 1) : [from, to];
}

export function forwardSteps(prevPieces, move) {
  let pieces = prevPieces.map((p) => ({ ...p }));
  const path = move.path ?? [];
  const steps = [];

  move.actions.forEach((a, i) => {
    if (a.type === "move") {
      const p = pieces.find((x) => x.id === a.pieceId);
      if (!p) return;
      steps.push({ kind: "move", id: p.id, path: route(path, p.position, a.to) });
      p.position = a.to;
    } else if (a.type === "place") {
      const piece = { id: placedId(a), type: a.piece.type, position: a.position, player: a.piece.player ?? null };
      const prev = steps[steps.length - 1];
      if (prev && prev.kind === "remove" && prev.id === piece.id && move.actions[i - 1]?.position === a.position) {
        steps[steps.length - 1] = { kind: "promote", id: piece.id, piece };
      } else {
        steps.push({ kind: "place", id: piece.id, piece });
      }
      pieces.push(piece);
    } else if (a.type === "remove") {
      pieces.filter((x) => x.position === a.position).forEach((p) => steps.push({ kind: "remove", id: p.id }));
      pieces = pieces.filter((x) => x.position !== a.position);
    } else if (a.type === "flip") {
      pieces.filter((x) => x.position === a.position).forEach((p) => {
        steps.push({ kind: "flip", id: p.id, player: a.player });
        p.player = a.player;
      });
    }
  });

  const groups = [];
  steps.forEach((s) => {
    const last = groups[groups.length - 1];
    if (last && s.kind !== "move" && last[0].kind === s.kind) last.push(s);
    else groups.push([s]);
  });
  return groups;
}

export function backwardSteps(fromPieces, toPieces) {
  const before = new Map(fromPieces.map((p) => [p.id, p]));
  const after = new Map(toPieces.map((p) => [p.id, p]));
  const steps = [];

  fromPieces.forEach((p) => {
    if (!after.has(p.id)) steps.push({ kind: "remove", id: p.id });
  });
  toPieces.forEach((q) => {
    const p = before.get(q.id);
    if (!p) return steps.push({ kind: "place", id: q.id, piece: q });
    if (p.position !== q.position) steps.push({ kind: "move", id: q.id, path: [p.position, q.position] });
    if (p.type !== q.type) steps.push({ kind: "promote", id: q.id, piece: q });
    else if (p.player !== q.player) steps.push({ kind: "flip", id: q.id, player: q.player });
  });
  return steps.length ? [steps] : [];
}
