from ..piece import Piece
from .game import Game
from .helpers import DIRS8, Builder, move, sq, step, xy

CAMP1 = [sq(c, r) for c in range(8) for r in range(8) if c + r <= 3]    # canto a1
CAMP2 = [sq(c, r) for c in range(8) for r in range(8) if c + r >= 11]   # canto h8
INITIAL = [Piece(id=f"p1-{s}", type="stone", position=s, player=1) for s in CAMP1] + [
    Piece(id=f"p2-{s}", type="stone", position=s, player=2) for s in CAMP2
]
GOAL = {1: CAMP2, 2: CAMP1}
# Lances = caminho (origem, destino) ou (origem, salto1, salto2, ...).
SCRIPT: list = [
    ("a1", "c3"), ("g8", "e6"), ("a2", "c4"),
    ("h8", "f6", "d6"), ("b3", "d5", "d7", "f5"), ("f7", "d5", "b3"),
    ("c3", "c5", "e7"), ("h7", "f7", "d7", "d5"), ("c1", "c3", "c5", "e5", "g5"),
    ("h6", "f4"), ("a3", "c3", "c5", "e5", "c7"), ("f8", "d8", "b6"),
    ("b1", "d3", "b5", "b7", "d7", "f7", "h7"), ("h5", "f7", "d7", "b7", "b5", "d3", "b1"), ("b2", "b4", "d4"),
    ("g6", "g4", "e4", "c6", "a6"), ("c4", "e4", "g4", "g6", "g8"), ("e6", "c6", "e4", "c4", "a2"),
    ("c7", "d8"), ("e8", "e6", "g4", "e4", "c4"), ("d4", "e5"),
    ("d6", "d4", "b4", "b2"), ("d8", "f6", "d4", "d6", "f8", "h6", "h8"), ("f4", "f6", "d4", "b4"),
    ("c2", "d3"), ("g7", "f6"), ("a4", "c2", "e4", "g6"),
    ("f6", "f4", "d6", "d4", "d2"), ("d3", "e4"), ("b4", "a3"),
    ("e4", "e6", "e8"), ("b6", "a5"), ("d1", "d3", "b5"),
    ("a5", "c5", "c3", "a1"), ("f5", "h5", "f7"), ("d2", "c1"),
    ("g5", "h6"), ("c4", "e6", "e4", "c6", "a4", "c2"), ("e7", "f8"),
    ("d5", "c4"), ("b5", "c6"), ("c4", "c3"),
    ("g6", "g7"), ("c2", "a4"), ("e5", "f6"),
    ("c3", "c2"), ("c6", "c7"), ("a6", "b5"),
    ("c7", "c8"), ("c2", "d1"), ("f6", "g6"),
    ("b5", "b4"), ("c8", "d8"), ("b4", "c3"),
    ("g6", "h5"), ("c3", "c2"),
]


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
    return all(s in grid for s in GOAL[player])


def build() -> list:
    b = Builder(INITIAL)
    for i, path in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        path = tuple(path)
        grid = {p.position: p.player for p in b.pieces}
        assert grid.get(path[0]) == player and path in paths_from(grid, path[0]), f"lance ilegal {path}"
        pid = b.at(path[0]).id
        jumps = len(path) - 1 if abs(xy(path[1])[0] - xy(path[0])[0]) == 2 or abs(xy(path[1])[1] - xy(path[0])[1]) == 2 else 0
        text = (f"Jogador {player} avança de {path[0]} a {path[1]}." if not jumps
                else f"Jogador {player} salta {' → '.join(path)} ({jumps} salto(s) em sequência).")
        b.add(player, [move(pid, path[-1])], text)
        if i >= 2 and goal_filled({p.position: p.player for p in b.pieces}, player):
            b.moves[-1].comment += " O campo inicial adversário está completamente ocupado: vitória."
            b.moves[-1].status = f"Vitória do jogador {player}"
    return b.moves


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
    moves=build(),
)
