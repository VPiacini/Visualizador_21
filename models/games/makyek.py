from ..piece import Piece
from .game import Game
from .helpers import DIRS4, Builder, move, remove, sq, step
from .hasami import custody

# ponytail: posição inicial adaptada (linhas 1-2 e 7-8); a figura 16.1 do livro não
# está no texto — ajustar INITIAL se a posição original for outra.
INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
]
# Lances (origem, destino): deslizam na ortogonal sem saltar.
SCRIPT: list = [
    ("c2", "c5"), ("b7", "b5"), ("a2", "a5"), ("b8", "b5"),
    ("e2", "e6"), ("c7", "c2"), ("e6", "g6"), ("b5", "g5"),
    ("b1", "b8"), ("c2", "e2"), ("d1", "d2"), ("e7", "e2"),
    ("h2", "h6"), ("d7", "d1"), ("h6", "g6"), ("e2", "f2"),
    ("g6", "g7"), ("h8", "h2"), ("g7", "g2"), ("a7", "a2"),
    ("g2", "b2"), ("d1", "b1"), ("b8", "c8"), ("g8", "g2"),
    ("b2", "f2"), ("e8", "e2"), ("f1", "f2"), ("b1", "b8"),
    ("f2", "f6"), ("a2", "h2"),
]


def slides(grid: dict[str, int], pos: str) -> list[str]:
    out = []
    for d in DIRS4:
        k = 1
        while (s := step(pos, d, k)) and s not in grid:
            out.append(s)
            k += 1
    return out


def intervention(grid: dict[str, int], to: str, player: int) -> list[str]:
    """Peça movida entre duas adversárias vizinhas (mesma linha ou coluna): ambas caem."""
    taken = []
    for a, b in (((1, 0), (-1, 0)), ((0, 1), (0, -1))):
        p, q = step(to, a), step(to, b)
        if p and q and grid.get(p) == 3 - player and grid.get(q) == 3 - player:
            taken += [p, q]
    return taken


def captures(grid, to, player):
    cust = custody(grid, to, player, multi=False)
    inter = [t for t in intervention(grid, to, player) if t not in cust]
    return cust, inter


def build() -> list:
    b = Builder(INITIAL)
    for i, (frm, to) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        assert grid.get(frm) == player and to in slides(grid, frm), f"lance ilegal {frm}->{to}"
        pid = b.at(frm).id
        g2 = dict(grid)
        g2[to] = g2.pop(frm)
        cust, inter = captures(g2, to, player)
        text = f"Jogador {player} move de {frm} a {to}."
        parts = []
        if cust:
            parts.append(f"custódia ({', '.join(cust)})")
        if inter:
            parts.append(f"intervenção ({', '.join(inter)})")
        if parts:
            text += " Captura por " + " e por ".join(parts) + "."
        b.add(player, [move(pid, to)] + [remove(t) for t in cust + inter], text)
        if not any(p.player == 3 - player for p in b.pieces):
            b.moves[-1].comment += f" O jogador {3 - player} perdeu todas as peças."
            b.moves[-1].status = f"Vitória do jogador {player}"
    return b.moves


MAKYEK = Game(
    id="makyek",
    name="Mak-Yek",
    subtitle="Captura por intervenção",
    objective=(
        "As peças deslizam na ortogonal, sem saltar. Capturam por custódia "
        "(cercar uma peça entre duas suas) e por intervenção (entrar entre duas "
        "adversárias, que caem juntas). Partida de exemplo: um trecho do jogo."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    moves=build(),
)
