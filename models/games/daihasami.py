from ..piece import Piece
from .game import Game
from .helpers import DIRS4, Builder, move, sq, step, xy

TARGET = 4
INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
]
# Lances (origem, destino), alternando jogador 1 e 2.
SCRIPT: list = [
    ("e2", "e5"), ("f7", "f5"), ("d2", "d6"), ("e7", "e6"),
    ("f2", "f4"), ("g7", "g3"), ("g2", "g4"), ("e6", "e4"),
    ("d1", "d3"), ("d7", "d5"), ("c2", "c6"), ("e8", "e6"),
    ("b2", "b6"), ("a8", "a6"), ("c1", "c3"), ("e4", "c4"),
    ("b1", "b3"), ("d5", "d4"), ("e1", "e3"),
]


def grid_of(b: Builder) -> dict[str, int]:
    return {p.position: p.player for p in b.pieces}


def moves_from(grid: dict[str, int], pos: str) -> list[str]:
    """Desliza na ortogonal quantas casas livres quiser, ou salta uma peça vizinha."""
    out = []
    for d in DIRS4:
        k = 1
        while (s := step(pos, d, k)) and s not in grid:
            out.append(s)
            k += 1
        if (over := step(pos, d)) and over in grid and (land := step(pos, d, 2)) and land not in grid:
            out.append(land)
    return out


def central(square: str) -> bool:
    return 2 <= xy(square)[1] <= 5  # fora das duas linhas iniciais de cada lado


def aligned(grid: dict[str, int], player: int) -> bool:
    mine = {s for s, pl in grid.items() if pl == player and central(s)}
    for s in mine:
        for d in ((1, 0), (0, 1), (1, 1), (1, -1)):
            if all(step(s, d, k) in mine for k in range(1, TARGET)):
                return True
    return False


def build() -> list:
    b = Builder(INITIAL)
    for i, (frm, to) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = grid_of(b)
        assert grid.get(frm) == player and to in moves_from(grid, frm), f"lance ilegal {frm}->{to}"
        jumped = abs(xy(frm)[0] - xy(to)[0]) + abs(xy(frm)[1] - xy(to)[1]) == 2 and \
            step(frm, ((xy(to)[0] - xy(frm)[0]) // 2, (xy(to)[1] - xy(frm)[1]) // 2)) in grid
        pid = b.at(frm).id
        b.add(player, [move(pid, to)],
              f"Jogador {player} {'salta' if jumped else 'desliza'} de {frm} a {to}.")
        if aligned(grid_of(b), player):
            b.moves[-1].comment += f" Forma {TARGET} em linha na região central e vence."
            b.moves[-1].status = f"Vitória do jogador {player}"
    return b.moves


DAIHASAMI = Game(
    id="daihasami",
    name="Dai Hasami Shogi",
    subtitle="Uma dinâmica diferente de alinhamento",
    objective=(
        f"Alinhar {TARGET} peças (inclusive na diagonal) na região central, "
        "fora das duas linhas iniciais de cada lado. As peças deslizam na "
        "ortogonal ou saltam uma peça vizinha; não há capturas."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    moves=build(),
)
