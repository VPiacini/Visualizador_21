from .game import Game
from .helpers import Builder, best_run, flip, move, place, sq, xy
from ..board import FILES

TARGET = 4
SCRIPT = [
    "a7", "h8", "a3", "c8", "a2", "h8", "a4", "d8",
    "a1", "g8", "a5", "e8", "a1", "f8", "a6", "e8",
    "a7",
]  # destino da peça guia de quem joga (a1..a7 / b8..h8)


def guide_pos(b: Builder, player: int) -> str:
    return next(p.position for p in b.pieces if p.id == f"guide-{player}")


def line_moves(b: Builder, player: int) -> list[str]:
    cur = guide_pos(b, player)
    cells = [sq(0, r) for r in range(7)] if player == 1 else [sq(c, 7) for c in range(1, 8)]
    return [s for s in cells if s != cur]


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


def build() -> list:
    b = Builder([])
    for i, to in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        if i == 0:
            b.add(1, [place(to, "guide", 1, "guide-1")], f"Jogador 1 coloca a sua peça guia em {to}, na coluna a.")
            continue
        if i == 1:
            g1 = guide_pos(b, 1)
            cross = intersection(b, g1, to)
            b.add(
                2,
                [place(to, "guide", 2, "guide-2"), place(cross, "disc", 2)],
                f"Jogador 2 coloca a guia em {to} (linha 8) e uma peça na interseção {cross}: "
                f"coluna da guia dele, linha da guia do adversário.",
            )
            continue
        cur = guide_pos(b, player)
        assert to in line_moves(b, player), f"guia de {player} não vai a {to}"
        cross = inter_after(b, player, to)
        occupied = lambda t: b.at(inter_after(b, player, t)) is not None
        acts = [move(f"guide-{player}", to)]
        if b.at(cross) is None:
            acts.append(place(cross, "disc", player))
            text = f"Jogador {player} move a guia de {cur} a {to}; a interseção é {cross} e ali fica uma peça sua."
        else:
            assert all(occupied(t) for t in line_moves(b, player)), "havia interseção livre"
            acts.append(flip(cross, 3 - b.owner(cross)))
            text = (
                f"Jogador {player} move a guia de {cur} a {to}. Todas as interseções possíveis estão "
                f"ocupadas, então a peça em {cross} troca de dono."
            )
        b.add(player, acts, text)
        winner = check_win(b, cross, player)
        if winner:
            assert i == len(SCRIPT) - 1
            b.moves[-1].comment += f" Forma {TARGET} em linha para o jogador {winner}."
            b.moves[-1].status = f"Vitória do jogador {winner}"
    return b.moves


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
    moves=build(),
)
