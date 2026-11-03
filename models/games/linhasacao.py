from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS8, move, remove, sq, step

# P1 nas linhas 1 e 8 (b..g); P2 nas colunas a e h (linhas 2..7): 12 peças cada.
INITIAL = [
    Piece(id=f"p1-{sq(c, r)}", type="stone", position=sq(c, r), player=1)
    for r in (0, 7)
    for c in range(1, 7)
] + [
    Piece(id=f"p2-{sq(c, r)}", type="stone", position=sq(c, r), player=2)
    for c in (0, 7)
    for r in range(1, 7)
]


def line_count(grid: dict[str, int], pos: str, d: tuple[int, int]) -> int:
    """Peças (de qualquer cor) na linha inteira (coluna, linha ou diagonal) de pos em d."""
    n = 1
    for sign in (1, -1):
        k = 1
        while (s := step(pos, (d[0] * sign, d[1] * sign), k)):
            n += s in grid
            k += 1
    return n


def moves_from(grid: dict[str, int], pos: str) -> list[str]:
    player, out = grid[pos], []
    for d in DIRS8:
        n = line_count(grid, pos, d)
        to = step(pos, d, n)
        if not to or grid.get(to) == player:
            continue
        if any(grid.get(step(pos, d, k)) == 3 - player for k in range(1, n)):
            continue  # pode saltar as suas peças, nunca as do adversário
        out.append(to)
    return out


def connected(grid: dict[str, int], player: int) -> bool:
    mine = {s for s, p in grid.items() if p == player}
    if not mine:
        return False
    seen, stack = set(), [next(iter(mine))]
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        stack += [n for d in DIRS8 if (n := step(s, d)) in mine and n not in seen]
    return seen == mine


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    return [
        ((p.position, to), ([remove(to)] if grid.get(to) == 3 - player else []) + [move(p.id, to)])
        for p in pieces
        if p.player == player
        for to in moves_from(grid, p.position)
    ]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    grid = {p.position: p.player for p in pieces}
    winner = mover if connected(grid, mover) else (3 - mover if connected(grid, 3 - mover) else None)
    return (f"Vitória do jogador {winner}", True) if winner else ("", False)


LINHASACAO = Game(
    id="linhasacao",
    name="Linhas de Ação",
    subtitle="Tentando se conectar",
    objective=(
        "Conectar todas as suas peças (vizinhas em qualquer direção). Cada peça "
        "anda em linha reta tantas casas quantas peças houver naquela linha; "
        "salta as suas, nunca as do adversário, e captura ao pousar sobre ele."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    rules=Rules(plays, status),
)
