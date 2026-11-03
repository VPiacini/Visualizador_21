from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS4, move, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, r in ((1, 0), (2, 7))
    for c in range(8)
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


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    out = []
    for p in pieces:
        if p.player != player:
            continue
        for to in step_moves(grid, p.position):
            g2 = {s: pl for s, pl in grid.items() if s != p.position} | {to: player}
            taken = custody(g2, to, player)
            out.append(((p.position, to), [move(p.id, to)] + [remove(t) for t in taken]))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    if sum(p.player == 3 - mover for p in pieces) <= 1:
        return f"Vitória do jogador {mover}", True
    return "", False


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
    rules=Rules(plays, status),
)
