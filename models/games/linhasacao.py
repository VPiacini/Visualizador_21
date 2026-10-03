from ..piece import Piece
from .game import Game
from .helpers import DIRS8, Builder, move, remove, sq, step, xy

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
# Lances (origem, destino), alternando jogador 1 e 2.
SCRIPT: list = [
    ("b1", "h1"), ("a2", "a8"), ("g8", "f7"), ("h2", "g2"),
    ("b8", "b7"), ("h7", "g6"), ("b7", "e7"), ("g2", "g5"),
    ("c8", "e6"), ("g6", "g3"), ("d8", "d6"), ("h4", "f4"),
    ("f7", "d5"), ("h3", "e3"), ("h1", "e4"), ("h6", "h4"),
    ("f8", "f5"), ("g3", "d3"), ("d6", "f4"), ("e3", "b6"),
    ("f4", "e5"), ("d3", "b3"), ("e8", "e2"), ("h5", "g6"),
    ("c1", "e3"),
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


def build() -> list:
    b = Builder(INITIAL)
    for i, (frm, to) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        assert grid.get(frm) == player and to in moves_from(grid, frm), f"lance ilegal {frm}->{to}"
        pid = b.at(frm).id
        capture = grid.get(to) == 3 - player
        actions = ([remove(to)] if capture else []) + [move(pid, to)]
        text = f"Jogador {player} move de {frm} a {to}" + (" e captura a peça adversária." if capture else ".")
        b.add(player, actions, text)
        g2 = {p.position: p.player for p in b.pieces}
        winner = player if connected(g2, player) else (3 - player if connected(g2, 3 - player) else None)
        if winner:
            b.moves[-1].comment += f" Todas as peças do jogador {winner} ficam conectadas."
            b.moves[-1].status = f"Vitória do jogador {winner}"
    return b.moves


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
    moves=build(),
)
