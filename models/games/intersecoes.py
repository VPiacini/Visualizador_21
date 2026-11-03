from ..piece import Piece
from .game import Game, History, Rules
from .helpers import Builder, best_run, flip, move, place, sq

TARGET = 4


def guide_pos(b: Builder, player: int) -> str:
    return next(p.position for p in b.pieces if p.id == f"guide-{player}")


def line_moves_from_start(player: int) -> list[str]:
    return [sq(0, r) for r in range(7)] if player == 1 else [sq(c, 7) for c in range(1, 8)]


def line_moves(b: Builder, player: int) -> list[str]:
    cur = guide_pos(b, player)
    return [s for s in line_moves_from_start(player) if s != cur]


def intersection(b: Builder, guide1: str, guide2: str) -> str:
    return f"{guide2[0]}{guide1[1:]}"  # coluna da guia 2 × linha da guia 1


def inter_after(b: Builder, player: int, to: str) -> str:
    g1, g2 = (to, guide_pos(b, 2)) if player == 1 else (guide_pos(b, 1), to)
    return intersection(b, g1, g2)


def check_win(b: Builder, pos: str, mover: int) -> int | None:
    for pl in (mover, 3 - mover):
        for c in range(8):
            for r in range(8):
                s = sq(c, r)
                if b.owner(s) == pl and best_run(b, s, pl, ("disc",)) >= TARGET:
                    return pl
    return None


def plays(pieces: list[Piece], player: int, history: History) -> list:
    b = Builder(pieces)
    if history.n == 0:
        return [((s,), [place(s, "guide", 1, "guide-1")]) for s in line_moves_from_start(1)]
    if history.n == 1:
        g1 = guide_pos(b, 1)
        return [
            ((s,), [place(s, "guide", 2, "guide-2"), place(intersection(b, g1, s), "disc", 2)])
            for s in line_moves_from_start(2)
        ]
    cur = guide_pos(b, player)
    targets = line_moves(b, player)
    crosses = {t: inter_after(b, player, t) for t in targets}
    all_taken = all(b.at(c) is not None for c in crosses.values())
    out = []
    for t, cross in crosses.items():
        if b.at(cross) is None:
            out.append(((cur, t), [move(f"guide-{player}", t), place(cross, "disc", player)]))
        elif all_taken:
            out.append(((cur, t), [move(f"guide-{player}", t), flip(cross, 3 - b.owner(cross))]))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    winner = check_win(Builder(pieces), "", mover)
    return (f"Vitória do jogador {winner}", True) if winner else ("", False)


INTERSECOES = Game(
    id="intersecoes",
    name="Interseções",
    subtitle="O jogo nos cruzamentos",
    objective=(
        "Cada jogador move a sua guia (coluna a / linha 8) e coloca uma peça na "
        f"interseção das duas guias. Vence quem alinhar {TARGET} peças."
    ),
    player_goal=None,
    initial_pieces=[],
    rules=Rules(plays, status),
)
