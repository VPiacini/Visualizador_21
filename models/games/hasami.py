from ..piece import Piece
from .game import Game
from .helpers import DIRS4, Builder, move, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, r in ((1, 0), (2, 7))
    for c in range(8)
]
# Lances (origem, destino): uma casa na ortogonal; alternando jogador 1 e 2.
SCRIPT: list = [
    ("e1", "e2"), ("c8", "c7"), ("c1", "c2"), ("e8", "e7"),
    ("c2", "c3"), ("c7", "c8"), ("e2", "e3"), ("c8", "c7"),
    ("e3", "e4"), ("d8", "d7"), ("c3", "c4"), ("d7", "d6"),
    ("c4", "c5"), ("e7", "e6"), ("c5", "d5"), ("e6", "e5"),
    ("d5", "c5"), ("d6", "e6"), ("e4", "f4"), ("e6", "f6"),
    ("f4", "f5"), ("e5", "d5"), ("f5", "e5"), ("f6", "e6"),
    ("e5", "f5"), ("e6", "e5"), ("c5", "d5"), ("c7", "c6"),
    ("d5", "d6"), ("c6", "b6"), ("d6", "c6"), ("b8", "c8"),
    ("c6", "c7"), ("b6", "c6"),
]


def is_corner(square: str) -> bool:
    c, r = xy(square)
    return c in (0, 7) and r in (0, 7)


def custody(
    grid: dict[str, int], to: str, player: int, multi: bool = True, corners: bool = True
) -> list[str]:
    """Peças adversárias cercadas em linha entre `to` e outra peça do jogador (+ cantos)."""
    taken = []
    for d in DIRS4:
        run, k = [], 1
        while (s := step(to, d, k)) and grid.get(s) == 3 - player:
            run.append(s)
            k += 1
        end = step(to, d, k)
        if run and end and grid.get(end) == player and (multi or len(run) == 1):
            taken += run
        # canto: a peça no canto só tem dois lados para fechar
        adj = step(to, d)
        if corners and adj and is_corner(adj) and grid.get(adj) == 3 - player:
            others = [n for dd in DIRS4 if (n := step(adj, dd)) and n != to]
            if others and all(grid.get(n) == player for n in others):
                taken.append(adj)
    return list(dict.fromkeys(taken))


def step_moves(grid: dict[str, int], pos: str) -> list[str]:
    return [s for d in DIRS4 if (s := step(pos, d)) and s not in grid]


def build() -> list:
    b = Builder(INITIAL)
    for i, (frm, to) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        assert grid.get(frm) == player and to in step_moves(grid, frm), f"lance ilegal {frm}->{to}"
        pid = b.at(frm).id
        g2 = dict(grid)
        g2[to] = g2.pop(frm)
        taken = custody(g2, to, player)
        text = f"Jogador {player} move de {frm} a {to}."
        if taken:
            text = f"Jogador {player} move de {frm} a {to} e captura por custódia: {', '.join(taken)}."
        b.add(player, [move(pid, to)] + [remove(t) for t in taken], text)
        left = sum(1 for p in b.pieces if p.player == 3 - player)
        if left <= 1:
            b.moves[-1].comment += f" O jogador {3 - player} fica com apenas uma peça e perde."
            b.moves[-1].status = f"Vitória do jogador {player}"
    return b.moves


HASAMI = Game(
    id="hasami",
    name="Hasami Shogi",
    subtitle="Captura por custódia (Petteia e Latrunculi são variantes)",
    objective=(
        "As peças andam uma casa na ortogonal. Cercar uma ou mais peças "
        "adversárias em linha, entre a peça movida e outra sua, captura-as. "
        "Vence quem deixar o adversário com apenas uma peça (a partida mostrada é um trecho)."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    moves=build(),
)
