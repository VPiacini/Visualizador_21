// View (camada de apresentação): não conhece regras de jogo, apenas
// desenha o que o Controller/Model já calculou (history + comentários).

import { forwardSteps, backwardSteps } from "./timeline.js";
import { createAnimator } from "./animator.js";

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
const btnEnd = document.getElementById("btn-end");
const btnPlay = document.getElementById("btn-play");
const speedEl = document.getElementById("play-speed");
const notationEl = document.getElementById("notation-box");
const selectorEl = document.getElementById("game-selector");

let currentGame = null; // dados serializados vindos de /api/games/<id>
let currentIndex = 0;
let epoch = 0; // invalida respostas que chegam depois de reiniciar ou trocar de jogo

// Notação das ações de uma jogada: "d4→e5", "+e5" (colocar), "×e5" (remover), "⟳e5" (virar).
function notation(actions, prevPieces) {
  return (
    actions
      .map((a) => {
        if (a.type === "move") {
          const before = prevPieces.find((p) => p.id === a.pieceId);
          return `${before ? before.position : "?"}→${a.to}`;
        }
        if (a.type === "place") return `+${a.position}`;
        if (a.type === "remove") return `×${a.position}`;
        return `⟳${a.position}`;
      })
      .join(" ") || "passa a vez"
  );
}

const animator = createAnimator(boardEl);

// reprodução automática
let timer = null;
let autoplay = 0; // diferente de 0 enquanto toca; muda a cada parada

function stopAutoplay() {
  clearTimeout(timer);
  timer = null;
  autoplay = 0;
  btnPlay.innerHTML = "&#9654;";
}

async function tick() {
  const run = autoplay;
  if (currentIndex >= currentGame.moves.length) return stopAutoplay();
  const interval = 1000 / Number(speedEl.value);
  const t0 = performance.now();
  await renderState(currentIndex + 1, "forward", interval);
  if (run !== autoplay) return;
  timer = setTimeout(tick, Math.max(0, interval - (performance.now() - t0)));
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
      return `<div class="legend-item p${p}"><span class="legend-dot p${p}"></span><span><b>Jogador ${p}</b>${goal}</span></div>`;
    })
    .join("");
}

// destaca no quadro de jogadores quem fez a jogada em exibição
function markActivePlayer(player) {
  legendEl.querySelectorAll(".legend-item").forEach((el) => {
    el.classList.toggle("active", el.classList.contains(`p${player}`));
  });
}

function clearHighlights() {
  document.querySelectorAll(".square.from, .square.dest, .square.put, .square.gone").forEach((el) => {
    el.classList.remove("from", "dest", "put", "gone");
  });
}

function markSquares(prevPieces, actions) {
  clearHighlights();

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
}

// mode: "forward" e "backward" animam só quando o índice anda exatamente 1; o resto é instantâneo
function renderState(index, mode = "instant", budget) {
  const from = currentIndex;
  currentIndex = index;
  const { history, moves } = currentGame;
  const lastMove = index > 0 ? moves[index - 1] : null;
  const player = lastMove ? lastMove.player : null;
  markSquares(index > 0 ? history[index - 1] : [], lastMove ? lastMove.actions : []);

  let done;
  if (mode === "forward" && index === from + 1) {
    done = animator.play(forwardSteps(history[from], lastMove), history[from], history[index], { player, budget });
  } else if (mode === "backward" && index === from - 1) {
    done = animator.play(backwardSteps(history[from], history[index]), history[from], history[index], { player, scale: 0.6 });
  } else {
    animator.reset(history[index], player);
    done = Promise.resolve();
  }

  counterEl.textContent = `${index}/${currentGame.moves.length}`;
  markActivePlayer(lastMove ? lastMove.player : 0);
  statusEl.textContent = lastMove ? lastMove.status : "";
  notationEl.textContent = lastMove ? notation(lastMove.actions, currentGame.history[index - 1]) : "";
  commentEl.textContent = lastMove ? lastMove.comment : currentGame.objective;
  btnPrev.disabled = index <= 0;
  btnNext.disabled = btnEnd.disabled = index >= currentGame.moves.length;
  return done;
}

const STORE = "partida:"; // localStorage: texto do JSON enviado, por jogo
const srcLivro = document.getElementById("src-livro");
const srcMine = document.getElementById("src-mine");
const srcRemove = document.getElementById("src-remove");
let source = "livro";

function stored(gameId) {
  try {
    return localStorage.getItem(STORE + gameId);
  } catch {
    return null;
  }
}

function store(gameId, text) {
  try {
    if (text === null) localStorage.removeItem(STORE + gameId);
    else localStorage.setItem(STORE + gameId, text);
  } catch {
    /* sem armazenamento: a partida vale só até trocar de jogo */
  }
}

async function loadGame(gameId) {
  const mine = ++epoch;
  const res = await fetch(`/api/games/${gameId}`);
  const game = await res.json();
  if (mine !== epoch) return;
  showGame(game, "livro");
}

async function postReplay(text) {
  const res = await fetch("/api/replay", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: text,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "partida inválida");
  return data;
}

async function loadMine(gameId, text) {
  const mine = ++epoch;
  const game = await postReplay(text);
  if (mine === epoch) showGame(game, "mine");
}

function showGame(game, from) {
  const gameId = game.id;
  currentGame = game;
  source = from;
  srcLivro.classList.toggle("active", from === "livro");
  srcMine.classList.toggle("active", from === "mine");
  srcMine.hidden = srcRemove.hidden = stored(gameId) === null;
  document.getElementById("source-switch").classList.toggle("empty", srcMine.hidden);
  stopAutoplay();

  nameEl.textContent = currentGame.name;
  subtitleEl.textContent = currentGame.subtitle;
  renderLegend(currentGame);
  buildStaticBoard();
  renderState(0);

  document.querySelectorAll(".game-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.gameId === gameId);
  });
}

srcLivro.addEventListener("click", () => loadGame(currentGame.id));
srcMine.addEventListener("click", () =>
  loadMine(currentGame.id, stored(currentGame.id)).catch((err) => {
    alert(`Não foi possível abrir a partida guardada: ${err.message}`);
    store(currentGame.id, null);
    loadGame(currentGame.id);
  })
);
srcRemove.addEventListener("click", () => {
  if (!confirm("Remover a partida guardada deste jogo?")) return;
  store(currentGame.id, null);
  if (source === "mine") loadGame(currentGame.id);
  else {
    srcMine.hidden = srcRemove.hidden = true;
    document.getElementById("source-switch").classList.add("empty");
  }
});

btnPrev.addEventListener("click", () => {
  stopAutoplay();
  if (currentIndex > 0) renderState(currentIndex - 1, "backward");
});
btnNext.addEventListener("click", () => {
  stopAutoplay();
  if (currentIndex < currentGame.moves.length) renderState(currentIndex + 1, "forward");
});
btnReset.addEventListener("click", () => {
  stopAutoplay();
  renderState(0);
});
btnEnd.addEventListener("click", () => {
  stopAutoplay();
  renderState(currentGame.moves.length);
});
btnPlay.addEventListener("click", () => {
  if (autoplay) return stopAutoplay();
  if (currentIndex >= currentGame.moves.length) renderState(0);
  btnPlay.innerHTML = "&#10074;&#10074;";
  autoplay = performance.now();
  timer = setTimeout(tick, 1000 / Number(speedEl.value));
});

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft") btnPrev.click();
  else if (e.key === "ArrowRight") btnNext.click();
});

selectorEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".game-btn");
  if (btn) loadGame(btn.dataset.gameId);
});

const fileLoadEl = document.getElementById("file-load");
document.getElementById("btn-load").addEventListener("click", () => fileLoadEl.click());
fileLoadEl.addEventListener("change", async () => {
  const file = fileLoadEl.files[0];
  fileLoadEl.value = "";
  if (!file) return;
  try {
    const text = await file.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error("o arquivo não é um JSON válido");
    }
    const target = data && data.game;
    if (target && target !== currentGame.id && !confirm(`Este arquivo é da partida de "${target}", não do jogo aberto. Abrir esse jogo?`)) return;
    const game = await postReplay(text);
    ++epoch;
    store(game.id, text);
    showGame(game, "mine");
  } catch (err) {
    alert(`Não foi possível carregar a partida: ${err.message}`);
  }
});

loadGame(window.DEFAULT_GAME_ID);
