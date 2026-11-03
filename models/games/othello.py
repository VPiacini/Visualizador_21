from ..piece import Piece
from .game import Game
from .helpers import DIRS8, Builder, flip, place, sq, step

INITIAL = [
    Piece(id="d5", type="stone", position="d5", player=1),
    Piece(id="e4", type="stone", position="e4", player=1),
    Piece(id="d4", type="stone", position="d4", player=2),
    Piece(id="e5", type="stone", position="e5", player=2),
]
# Casas jogadas, alternando 1 e 2; "-" = passa a vez (sem jogada válida).
SCRIPT: list[str] = [
    "c4", "e3", "f5", "g6", "e2", "c5", "f6", "c3", "h6", "f3",
    "g4", "e6", "d6", "f7", "b4", "h5", "h4", "c6", "e7", "a5",
    "a4", "b3", "e8", "f8", "c7", "a3", "b5", "a6", "c2", "d1",
    "d7", "d8", "c1", "f4", "g5", "d2", "d3", "e1", "f1", "f2",
    "g3", "c8", "b6", "h3", "g8", "h8", "b8", "a8", "a2", "a1",
    "h2", "a7", "b7", "g1", "h1", "h7", "g2", "b1", "b2", "g7",
]


def flips(grid: dict[str, int], pos: str, player: int) -> list[str]:
    """Peças adversárias convertidas ao colocar em pos (vazio se a jogada é inválida)."""
    if pos in grid:
        return []
    out = []
    for d in DIRS8:
        run, k = [], 1
        while (s := step(pos, d, k)) and grid.get(s) == 3 - player:
            run.append(s)
            k += 1
        if run and grid.get(step(pos, d, k)) == player:
            out += run
    return out


def valid_moves(grid: dict[str, int], player: int) -> list[str]:
    return [s for c in range(8) for r in range(8) if flips(grid, s := sq(c, r), player)]


def build() -> list:
    b = Builder(INITIAL)
    player = 1
    for pos in SCRIPT:
        grid = {p.position: p.player for p in b.pieces}
        if pos == "-":
            assert not valid_moves(grid, player), "passou tendo jogada"
            b.add(player, [], f"Jogador {player} não tem jogada válida e passa a vez.")
        else:
            taken = flips(grid, pos, player)
            assert taken, f"jogada inválida {pos}"
            b.add(
                player,
                [place(pos, "stone", player)] + [flip(t, player) for t in taken],
                f"Jogador {player} coloca em {pos} e conquista {len(taken)} peça(s): {', '.join(taken)}.",
            )
        n1 = sum(p.player == 1 for p in b.pieces)
        n2 = sum(p.player == 2 for p in b.pieces)
        b.moves[-1].status = f"Peças — J1: {n1} · J2: {n2}"
        player = 3 - player
    last_grid = {p.position: p.player for p in b.pieces}
    if SCRIPT and not valid_moves(last_grid, 1) and not valid_moves(last_grid, 2):
        n1 = sum(p.player == 1 for p in b.pieces)
        n2 = sum(p.player == 2 for p in b.pieces)
        end = "empate" if n1 == n2 else f"vitória do jogador {1 if n1 > n2 else 2}"
        b.moves[-1].comment += f" Ninguém mais pode jogar: {n1} x {n2} — {end}."
        b.moves[-1].status += f" · {end.capitalize()}"
    return b.moves


OTHELLO = Game(
    id="othello",
    name="Othello (Reversi)",
    subtitle="Disputa das casas do tabuleiro",
    objective=(
        "Colocar uma peça cercando em linha peças adversárias, que viram suas. "
        "Se não houver jogada válida, passa-se a vez. Vence quem tiver mais "
        "peças quando ninguém puder jogar."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    moves=build(),
)
