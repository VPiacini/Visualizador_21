from ..piece import Piece
from .game import Game
from .helpers import DIRS8, Builder, move, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
]
# Lance = [casa traseira, [dx, dy], tamanho da falange, casas percorridas pela frente].
SCRIPT: list = [
    ["f1", [-1, 1], 2, 2], ["b8", [0, -1], 2, 2], ["b1", [1, 1], 3, 3],
    ["f8", [0, -1], 2, 2], ["e1", [1, 1], 2, 2], ["e7", [1, -1], 2, 2],
    ["g1", [0, 1], 3, 2], ["h8", [0, -1], 2, 2], ["g3", [0, 1], 4, 1],
    ["h6", [0, -1], 3, 2], ["g7", [-1, 1], 1, 1], ["h4", [0, -1], 3, 1],
    ["g5", [0, 1], 2, 2], ["c8", [1, 0], 3, 1], ["g7", [0, 1], 1, 1],
    ["d8", [1, 0], 3, 1], ["c1", [1, 1], 2, 2],
]

NOMES = {(0, 1): "para cima", (0, -1): "para baixo", (1, 0): "para a direita", (-1, 0): "para a esquerda",
         (1, 1): "na diagonal ↗", (-1, 1): "na diagonal ↖", (1, -1): "na diagonal ↘", (-1, -1): "na diagonal ↙"}


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


def build() -> list:
    b = Builder(INITIAL)
    for i, (rear, d, ell, j) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        assert not has_won(grid, player), "a partida já tinha terminado"
        d = tuple(d)
        taken = all_moves(grid, player).get((rear, d, ell, j))
        assert taken is not None, f"lance ilegal {rear} {d} {ell} {j}"
        squares = run_from(grid, rear, d, player)[:ell]
        ids = [b.at(s).id for s in squares]
        actions = [remove(t) for t in taken] + [
            move(pid, step(s, d, j)) for pid, s in reversed(list(zip(ids, squares)))
        ]
        what = "uma peça" if ell == 1 else f"uma falange de {ell} peças"
        text = f"Jogador {player} move {what} ({squares[0]}…{squares[-1]}) {j} casa(s) {NOMES[d]}."
        if taken:
            text += f" Ao chegar à falange adversária de {len(taken)} peça(s), captura {', '.join(taken)}."
        b.add(player, actions, text)
        g2 = {p.position: p.player for p in b.pieces}
        b.moves[-1].status = f"Última linha adversária — J1: {far_row_count(g2, 1)} · J2: {far_row_count(g2, 2)}"
    if SCRIPT:
        nxt = 3 - (1 if (len(SCRIPT) - 1) % 2 == 0 else 2)
        g2 = {p.position: p.player for p in b.pieces}
        if has_won(g2, nxt):
            b.moves[-1].comment += f" Na sua vez, o jogador {nxt} tem mais peças na última linha adversária e vence."
            b.moves[-1].status += f" · Vitória do jogador {nxt}"
    return b.moves


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
    moves=build(),
)
