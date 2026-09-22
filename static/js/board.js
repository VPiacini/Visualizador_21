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
const btnPrev = document.getElementById("btn-prev");
const btnNext = document.getElementById("btn-next");
const btnReset = document.getElementById("btn-reset");
const selectorEl = document.getElementById("game-selector");

let currentGame = null; // dados serializados vindos de /api/games/<id>
let currentIndex = 0;

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
  document.querySelectorAll(".square.from, .square.dest").forEach((el) => {
    el.classList.remove("from", "dest");
  });
}

function renderState(index) {
  currentIndex = index;
  const pieces = currentGame.history[index];
  const lastMove = index > 0 ? currentGame.moves[index - 1] : null;

  clearHighlights();
  boardEl.querySelectorAll(".piece").forEach((el) => el.remove());

  if (lastMove && lastMove.move) {
    const prevPieces = currentGame.history[index - 1];
    const before = prevPieces.find((p) => p.id === lastMove.move.pieceId);
    if (before) {
      const fromEl = boardEl.querySelector(`[data-square="${before.position}"]`);
      if (fromEl) fromEl.classList.add("from");
    }
    const destEl = boardEl.querySelector(`[data-square="${lastMove.move.to}"]`);
    if (destEl) destEl.classList.add("dest");
  }

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
      const player = piece.player ?? (lastMove ? lastMove.player : null);
      disc.style.background =
        player === 1 ? "var(--player1)" : player === 2 ? "var(--player2)" : "#b9af9a";
      wrapper.appendChild(disc);
    }
    boardEl.appendChild(wrapper);
  });

  counterEl.textContent = `Jogada ${index} / ${currentGame.moves.length}`;
  commentEl.textContent = lastMove ? lastMove.comment : currentGame.objective;
  btnPrev.disabled = index <= 0;
  btnNext.disabled = index >= currentGame.moves.length;
}

async function loadGame(gameId) {
  const res = await fetch(`/api/games/${gameId}`);
  currentGame = await res.json();

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
btnReset.addEventListener("click", () => renderState(0));

selectorEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".game-btn");
  if (btn) loadGame(btn.dataset.gameId);
});

loadGame(window.DEFAULT_GAME_ID);
