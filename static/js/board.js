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
const modeSwitchEl = document.getElementById("mode-switch");
const modeToggle = document.getElementById("mode-toggle");

let currentGame = null; // dados serializados vindos de /api/games/<id>
let currentIndex = 0;
let epoch = 0; // invalida respostas que chegam depois de reiniciar ou trocar de jogo
let live = null; // modo Jogar: estado vindo de /start ou /play + path (casas já clicadas do lance)
let sending = false;

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

function clearHighlights(classes = ["from", "dest", "put", "gone", "hint", "selected"]) {
  boardEl.querySelectorAll(classes.map((c) => `.square.${c}`).join(", ")).forEach((el) => {
    el.classList.remove(...classes);
  });
}

function mark(square, cls) {
  const el = boardEl.querySelector(`[data-square="${square}"]`);
  if (el) el.classList.add(cls);
}

function markSquares(prevPieces, actions) {
  clearHighlights();
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

// ---- modo Jogar: dois jogadores se alternam; o servidor valida cada lance ----

const startsWith = (path, prefix) => prefix.every((sq, i) => path[i] === sq);
const sameAs = (a, b) => a.length === b.length && startsWith(a, b);
const candidates = (path) => live.plays.filter((p) => startsWith(p.path, path));

// casas do lance em curso e para onde ele pode seguir
function markPlays() {
  clearHighlights(["hint", "selected"]);
  if (live.over) return;
  candidates(live.path).forEach((p) => {
    mark(p.path.length > live.path.length ? p.path[live.path.length] : live.path[live.path.length - 1], "hint");
  });
  live.path.forEach((sq) => mark(sq, "selected"));
}

function renderLive() {
  markSquares(live.prev, live.actions);
  markPlays();
  counterEl.textContent = live.over ? "Fim de jogo" : `Vez do Jogador ${live.player}`;
  markActivePlayer(live.over ? live.mover : live.player);
  statusEl.textContent = live.status;
  notationEl.textContent = live.mover ? notation(live.actions, live.prev) : "";
  commentEl.textContent = currentGame.objective;
  btnPrev.disabled = live.undo.length === 0;
  btnPrev.setAttribute("aria-label", "Desfazer jogada");
  btnPrev.title = "Desfazer jogada";
}

async function startLive() {
  const mine = ++epoch;
  stopAutoplay();
  const res = await fetch(`/api/games/${currentGame.id}/start`);
  const state = await res.json();
  if (mine !== epoch) return;
  live = { ...state, path: [], prev: [], mover: null, undo: [] };
  boardEl.classList.add("playing");
  animator.reset(live.pieces);
  renderLive();
}

function stopLive() {
  epoch++;
  live = null;
  boardEl.classList.remove("playing");
  btnPrev.setAttribute("aria-label", "Jogada anterior");
  btnPrev.title = "Jogada anterior";
  renderState(currentIndex);
}

function setMode(jogar) {
  modeToggle.checked = jogar;
  document.body.classList.toggle("jogando", jogar);
  if (jogar) startLive();
  else stopLive();
}

async function sendPlay(path) {
  if (sending) return;
  sending = true;
  const mine = epoch;
  const before = live;
  try {
    const res = await fetch(`/api/games/${currentGame.id}/play`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pieces: before.pieces, player: before.player, history: before.history, path }),
    });
    if (mine !== epoch) return;
    if (!res.ok) {
      live.path = [];
      return renderLive();
    }
    const state = await res.json();
    if (mine !== epoch) return;
    const { path: _, undo, ...saved } = before;
    live = { ...state, path: [], prev: before.pieces, mover: before.player, undo: [...undo, saved] };
    renderLive();
    animator.play(forwardSteps(before.pieces, { actions: state.actions, path }), before.pieces, live.pieces, { player: before.player });
  } finally {
    sending = false;
  }
}

function undoLive() {
  if (!live.undo.length || sending) return;
  const from = live.pieces;
  const undo = live.undo.slice(0, -1);
  live = { ...live.undo[live.undo.length - 1], path: [], undo };
  renderLive();
  animator.play(backwardSteps(from, live.pieces), from, live.pieces, { player: live.mover, scale: 0.6 });
}

// Acumula o caminho de cliques; envia quando só resta uma jogada possível
// (ou, havendo jogadas mais longas, quando se clica de novo na última casa).
function pickSquare(square) {
  const last = live.path[live.path.length - 1];
  if (square === last && live.plays.some((p) => sameAs(p.path, live.path))) return sendPlay(live.path);
  for (const path of [[...live.path, square], [square]]) {
    const cands = candidates(path);
    if (!cands.length) continue;
    live.path = path;
    if (cands.every((p) => sameAs(p.path, path))) return sendPlay(path);
    return markPlays();
  }
  live.path = [];
  markPlays();
}

boardEl.addEventListener("click", (e) => {
  const sq = e.target.closest(".square");
  if (live && !live.over && !sending && sq) pickSquare(sq.dataset.square);
});

modeToggle.addEventListener("change", () => setMode(modeToggle.checked));

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
  live = null;
  boardEl.classList.remove("playing");
  modeSwitchEl.hidden = !game.playable;

  nameEl.textContent = currentGame.name;
  subtitleEl.textContent = currentGame.subtitle;
  renderLegend(currentGame);
  buildStaticBoard();
  renderState(0);
  setMode(modeToggle.checked && game.playable);

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
  if (live) return undoLive();
  stopAutoplay();
  if (currentIndex > 0) renderState(currentIndex - 1, "backward");
});
btnNext.addEventListener("click", () => {
  if (live) return;
  stopAutoplay();
  if (currentIndex < currentGame.moves.length) renderState(currentIndex + 1, "forward");
});
btnReset.addEventListener("click", () => {
  if (modeToggle.checked) return startLive();
  stopAutoplay();
  renderState(0);
});
btnEnd.addEventListener("click", () => {
  if (live) return;
  stopAutoplay();
  renderState(currentGame.moves.length);
});
btnPlay.addEventListener("click", () => {
  if (live) return;
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
