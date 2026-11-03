from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS4, move, remove, sq, step
from .hasami import custody

# ponytail: posição inicial adaptada (linhas 1-2 e 7-8); a figura 16.1 do livro não
# está no texto — ajustar INITIAL se a posição original for outra.
INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
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


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    out = []
    for p in pieces:
        if p.player != player:
            continue
        for to in slides(grid, p.position):
            g2 = {s: pl for s, pl in grid.items() if s != p.position} | {to: player}
            cust, inter = captures(g2, to, player)
            out.append(((p.position, to), [move(p.id, to)] + [remove(t) for t in cust + inter]))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    if not any(p.player == 3 - mover for p in pieces):
        return f"Vitória do jogador {mover}", True
    return "", False


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
    rules=Rules(plays, status),
)
