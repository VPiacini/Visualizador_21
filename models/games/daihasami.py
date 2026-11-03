from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS4, move, sq, step, xy

TARGET = 4
INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
]


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


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    return [
        ((p.position, to), [move(p.id, to)])
        for p in pieces
        if p.player == player
        for to in moves_from(grid, p.position)
    ]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    if aligned({p.position: p.player for p in pieces}, mover):
        return f"Vitória do jogador {mover}", True
    return "", False


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
    rules=Rules(plays, status),
)
