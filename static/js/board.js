// View (camada de apresentação): não conhece regras de jogo, apenas
// desenha o que o Controller/Model já calculou (history + comentários).

const FILES = ["a", "b", "c", "d", "e", "f", "g", "h"];
const RANKS = [1, 2, 3, 4, 5, 6, 7, 8];

const boardEl = document.getElementById("board");
const rankLabelsEl = document.getElementById("rank-labels");
const fileLabelsEl = document.getElementById("file-labels");
const legendEl = document.getElementById("player-legend");
const nameEl = document.getElementById("game-name");
const subtitleEl = document.getElementById("game-subtitle");
const commentEl = document.getElementById("comment-box");
const counterEl = document.getElementById("move-counter");
const statusEl = document.getElementById("status-box");
const btnPrev = document.getElementById("btn-prev");
const btnNext = document.getElementById("btn-next");
const btnReset = document.getElementById("btn-reset");
const btnMode = document.getElementById("btn-mode");
const selectorEl = document.getElementById("game-selector");

let currentGame = null; // dados serializados vindos de /api/games/<id>
let currentIndex = 0;
let live = null; // estado do modo Jogar: resposta de /start ou /play + selected

function squareToCoord(square) {
  const col = FILES.indexOf(square[0]);
  const row = parseInt(square.slice(1), 10) - 1;
  return { col, row };
}

function buildStaticBoard() {
  boardEl.innerHTML = "";
  RANKS.slice()
    .reverse()
    .forEach((rank) => {
      FILES.forEach((file) => {
        const isLight = (FILES.indexOf(file) + rank) % 2 === 0;
        const sq = document.createElement("div");
        sq.className = `square ${isLight ? "light" : "dark"}`;
        sq.dataset.square = `${file}${rank}`;
        boardEl.appendChild(sq);
      });
    });

  rankLabelsEl.innerHTML = RANKS.map((r) => `<span>${r}</span>`).join("");
  fileLabelsEl.innerHTML = FILES.map((f) => `<span>${f}</span>`).join("");
}

function renderLegend(game) {
  legendEl.innerHTML = [1, 2]
    .map((p) => {
      const goal = game.playerGoal ? ` — ${game.playerGoal[p]}` : "";
      return `<div class="legend-item"><span class="legend-dot p${p}"></span>Jogador ${p}${goal}</div>`;
    })
    .join("");
}

function clearHighlights() {
  document.querySelectorAll(".square.from, .square.dest, .square.put, .square.gone").forEach((el) => {
    el.classList.remove("from", "dest", "put", "gone");
  });
}

function draw(pieces, prevPieces, actions, lastPlayer) {
  clearHighlights();
  boardEl.querySelectorAll(".piece").forEach((el) => el.remove());

  const mark = (square, cls) => {
    const el = boardEl.querySelector(`[data-square="${square}"]`);
    if (el) el.classList.add(cls);
  };
  actions.forEach((a) => {
    if (a.type === "move") {
      const before = prevPieces.find((p) => p.id === a.pieceId);
      if (before) mark(before.position, "from");
      mark(a.to, "dest");
    } else if (a.type === "place" || a.type === "flip") {
      mark(a.position, "put");
    } else if (a.type === "remove") {
      mark(a.position, "gone");
    }
  });

  pieces.forEach((piece) => {
    const { col, row } = squareToCoord(piece.position);
    const wrapper = document.createElement("div");
    wrapper.className = "piece";
    wrapper.style.left = `${(col / 8) * 100}%`;
    wrapper.style.top = `${((7 - row) / 8) * 100}%`;

    if (piece.type === "block") {
      const block = document.createElement("div");
      block.className = "block";
      wrapper.appendChild(block);
    } else {
      const disc = document.createElement("div");
      disc.className = "disc";
      disc.dataset.type = piece.type;
      const player = piece.player ?? lastPlayer;
      disc.style.background =
        player === 1 ? "var(--player1)" : player === 2 ? "var(--player2)" : "#b9af9a";
      wrapper.appendChild(disc);
    }
    boardEl.appendChild(wrapper);
  });
}

function renderState(index) {
  currentIndex = index;
  const lastMove = index > 0 ? currentGame.moves[index - 1] : null;
  draw(
    currentGame.history[index],
    index > 0 ? currentGame.history[index - 1] : [],
    lastMove ? lastMove.actions : [],
    lastMove ? lastMove.player : null
  );

  counterEl.textContent = `Jogada ${index} / ${currentGame.moves.length}`;
  statusEl.textContent = lastMove ? lastMove.status : "";
  commentEl.textContent = lastMove ? lastMove.comment : currentGame.objective;
  btnPrev.disabled = index <= 0;
  btnNext.disabled = index >= currentGame.moves.length;
}

function setControlsDisabled(off) {
  btnPrev.disabled = btnNext.disabled = off;
}

function renderLive() {
  draw(live.pieces, live.prev, live.actions, live.mover);
  const dests = live.plays.filter((p) => (live.selected ? p.from === live.selected : p.from === null));
  const starts = live.selected ? [] : live.plays.filter((p) => p.from !== null);
  dests.forEach((p) => markSquare(p.to, "hint"));
  starts.forEach((p) => markSquare(p.from, "hint"));
  if (live.selected) markSquare(live.selected, "selected");

  setControlsDisabled(true);
  counterEl.textContent = live.over ? "Fim de jogo" : `Vez do Jogador ${live.player}`;
  statusEl.textContent = live.status;
  commentEl.textContent = currentGame.objective;
}

function markSquare(square, cls) {
  const el = boardEl.querySelector(`[data-square="${square}"]`);
  if (el) el.classList.add(cls);
}

async function startLive() {
  const res = await fetch(`/api/games/${currentGame.id}/start`);
  live = { ...(await res.json()), selected: null, prev: [], mover: null };
  boardEl.classList.add("playing");
  btnMode.textContent = "Assistir";
  renderLive();
}

function stopLive() {
  live = null;
  boardEl.classList.remove("playing");
  btnMode.textContent = "Jogar";
  renderState(0);
}

async function sendPlay(from, to) {
  const res = await fetch(`/api/games/${currentGame.id}/play`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pieces: live.pieces, player: live.player, n: live.n, from, to }),
  });
  if (!res.ok) return;
  const prev = live.pieces;
  const mover = live.player;
  live = { ...(await res.json()), selected: null, prev, mover };
  renderLive();
}

boardEl.addEventListener("click", (e) => {
  if (!live || live.over) return;
  const rect = boardEl.getBoundingClientRect();
  const col = Math.floor(((e.clientX - rect.left) / rect.width) * 8);
  const row = 7 - Math.floor(((e.clientY - rect.top) / rect.height) * 8);
  if (col < 0 || col > 7 || row < 0 || row > 7) return;
  const square = `${FILES[col]}${row + 1}`;

  const direct = live.plays.find(
    (p) => p.to === square && p.from === (live.selected ?? null)
  );
  if (direct) return sendPlay(direct.from, direct.to);
  live.selected = live.plays.some((p) => p.from === square) ? square : null;
  renderLive();
});

btnMode.addEventListener("click", () => {
  if (live) stopLive();
  else startLive();
});

async function loadGame(gameId) {
  const res = await fetch(`/api/games/${gameId}`);
  currentGame = await res.json();
  live = null;
  boardEl.classList.remove("playing");
  btnMode.disabled = !currentGame.playable;
  btnMode.textContent = "Jogar";

  nameEl.textContent = currentGame.name;
  subtitleEl.textContent = currentGame.subtitle;
  renderLegend(currentGame);
  buildStaticBoard();
  renderState(0);

  document.querySelectorAll(".game-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.gameId === gameId);
  });
}

btnPrev.addEventListener("click", () => {
  if (currentIndex > 0) renderState(currentIndex - 1);
});
btnNext.addEventListener("click", () => {
  if (currentIndex < currentGame.moves.length) renderState(currentIndex + 1);
});
btnReset.addEventListener("click", () => (live ? startLive() : renderState(0)));

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft") btnPrev.click();
  else if (e.key === "ArrowRight") btnNext.click();
});

selectorEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".game-btn");
  if (btn) loadGame(btn.dataset.gameId);
});

loadGame(window.DEFAULT_GAME_ID);
