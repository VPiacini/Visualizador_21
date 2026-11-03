from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS8, flip, place, sq, step

INITIAL = [
    Piece(id="d5", type="stone", position="d5", player=1),
    Piece(id="e4", type="stone", position="e4", player=1),
    Piece(id="d4", type="stone", position="d4", player=2),
    Piece(id="e5", type="stone", position="e5", player=2),
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


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    out = []
    for c in range(8):
        for r in range(8):
            pos = sq(c, r)
            if taken := flips(grid, pos, player):
                out.append(((pos,), [place(pos, "stone", player)] + [flip(t, player) for t in taken]))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    grid = {p.position: p.player for p in pieces}
    n1 = sum(p.player == 1 for p in pieces)
    n2 = sum(p.player == 2 for p in pieces)
    text = f"Peças — J1: {n1} · J2: {n2}"
    if valid_moves(grid, 1) or valid_moves(grid, 2):
        return text, False
    return f"{text} · " + ("Empate" if n1 == n2 else f"Vitória do jogador {1 if n1 > n2 else 2}"), True


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
    rules=Rules(plays, status),
)
