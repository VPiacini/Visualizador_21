from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS8, move, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
]

def run_from(grid: dict[str, int], pos: str, d: tuple[int, int], player: int) -> list[str]:
    """Casas consecutivas de `player` a partir de pos (inclusive) na direção d."""
    out, s = [], pos
    while s and grid.get(s) == player:
        out.append(s)
        s = step(s, d)
    return out


def all_moves(grid: dict[str, int], player: int):
    """(traseira, d, tamanho, j) -> casas inimigas capturadas (lista vazia se só desloca)."""
    out = {}
    for rear, pl in grid.items():
        if pl != player:
            continue
        for d in DIRS8:
            ahead = run_from(grid, rear, d, player)
            for ell in range(1, len(ahead) + 1):
                if ell > 1 and False:
                    continue
                front = ahead[ell - 1]
                for j in range(1, ell + 1):
                    s = step(front, d, j)
                    if not s or grid.get(s) == player:
                        break
                    if s not in grid:
                        out[(rear, d, ell, j)] = []
                        continue
                    enemy = run_from(grid, s, d, 3 - player)
                    if len(enemy) < ell:
                        out[(rear, d, ell, j)] = enemy
                    break
    return out


def far_row_count(grid: dict[str, int], player: int) -> int:
    row = 7 if player == 1 else 0
    return sum(1 for s, p in grid.items() if p == player and xy(s)[1] == row)


def has_won(grid: dict[str, int], player: int) -> bool:
    """No início da vez: mais peças na última linha do outro lado que o adversário."""
    return far_row_count(grid, player) > far_row_count(grid, 3 - player)


def plays(pieces: list[Piece], player: int, history: History) -> list:
    """Caminho = (traseira, destino) para uma peça só; (traseira, frente, destino) para falanges."""
    grid = {p.position: p.player for p in pieces}
    ids = {p.position: p.id for p in pieces}
    out = []
    for (rear, d, ell, j), taken in all_moves(grid, player).items():
        squares = run_from(grid, rear, d, player)[:ell]
        dest = step(squares[-1], d, j)
        path = (rear, dest) if ell == 1 else (rear, squares[-1], dest)
        actions = [remove(t) for t in taken] + [
            move(ids[s], step(s, d, j)) for s in reversed(squares)
        ]
        out.append((path, actions))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    grid = {p.position: p.player for p in pieces}
    text = f"Última linha adversária — J1: {far_row_count(grid, 1)} · J2: {far_row_count(grid, 2)}"
    if has_won(grid, 3 - mover):
        return f"{text} · Vitória do jogador {3 - mover}", True
    return text, False


EPAMINONDAS = Game(
    id="epaminondas",
    name="Epaminondas",
    subtitle="A força das falanges",
    objective=(
        "Falanges (linhas de peças vizinhas) andam até tantas casas quanto o seu "
        "tamanho, na direção do alinhamento, e capturam falanges menores. Vence "
        "quem, no início da sua vez, tiver mais peças na última linha do outro lado."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    rules=Rules(plays, status),
)
