from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS8, move, sq, step

CAMP1 = [sq(c, r) for c in range(8) for r in range(8) if c + r <= 3]    # canto a1
CAMP2 = [sq(c, r) for c in range(8) for r in range(8) if c + r >= 11]   # canto h8
INITIAL = [Piece(id=f"p1-{s}", type="stone", position=s, player=1) for s in CAMP1] + [
    Piece(id=f"p2-{s}", type="stone", position=s, player=2) for s in CAMP2
]
GOAL = {1: CAMP2, 2: CAMP1}


def paths_from(grid: dict[str, int], pos: str) -> list[tuple[str, ...]]:
    """Passo para uma vizinha livre, ou sequência de saltos por cima de qualquer peça."""
    out = [(pos, s) for d in DIRS8 if (s := step(pos, d)) and s not in grid]
    g = {s: p for s, p in grid.items() if s != pos}

    def jumps(cur: str, path: tuple[str, ...]):
        for d in DIRS8:
            over, land = step(cur, d), step(cur, d, 2)
            if over in g and land and land not in g and land not in path:
                out.append(path + (land,))
                jumps(land, path + (land,))

    jumps(pos, (pos,))
    return out


def goal_filled(grid: dict[str, int], player: int) -> bool:
    return all(s in grid for s in GOAL[player]) and any(grid[s] == player for s in GOAL[player])


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    return [
        (path, [move(p.id, path[-1])])
        for p in pieces
        if p.player == player
        for path in paths_from(grid, p.position)
    ]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    if history.n >= 2 and goal_filled({p.position: p.player for p in pieces}, mover):
        return f"Vitória do jogador {mover}", True
    return "", False


HALMA = Game(
    id="halma",
    name="Halma",
    subtitle="Deslocando-se rapidamente por saltos",
    objective=(
        "Levar as peças ao canto oposto. Anda-se 1 casa em qualquer direção ou "
        "salta-se uma peça (sua ou do adversário), em sequência. Vence quem "
        "ocupar totalmente o campo inicial do adversário."
    ),
    player_goal={1: "ocupar o canto h8", 2: "ocupar o canto a1"},
    initial_pieces=INITIAL,
    rules=Rules(plays, status),
)
