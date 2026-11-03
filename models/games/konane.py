from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS4, Builder, move, remove, sq, step

# P1 ocupa as casas com (coluna + linha) par (a1 é do jogador 1); P2 as ímpares.
INITIAL = [
    Piece(id=f"p{1 if (c + r) % 2 == 0 else 2}-{sq(c, r)}", type="stone",
          position=sq(c, r), player=1 if (c + r) % 2 == 0 else 2)
    for c in range(8)
    for r in range(8)
]


def jumps(b: Builder, player: int) -> list[tuple[str, str, list[str]]]:
    """Todas as capturas possíveis: (origem, destino, casas capturadas) em linha reta."""
    out = []
    for p in b.pieces:
        if p.player != player:
            continue
        for d in DIRS4:
            taken, k = [], 1
            while True:
                over, land = step(p.position, d, k), step(p.position, d, k + 1)
                if over and b.owner(over) == 3 - player and b.empty(land):
                    taken.append(over)
                    out.append((p.position, land, list(taken)))
                    k += 2
                else:
                    break
    return out


def plays(pieces: list[Piece], player: int, history: History) -> list:
    b = Builder(pieces)
    if history.n < 2:
        # abertura: cada jogador retira uma peça sua; o 2º, vizinha da casa aberta
        gap = next((s for c in range(8) for r in range(8) if b.empty(s := sq(c, r))), None)
        near = {step(gap, d) for d in DIRS4} if gap else None
        return [((p.position,), [remove(p.position)]) for p in pieces
                if p.player == player and (near is None or p.position in near)]
    return [((frm, to), [move(b.at(frm).id, to)] + [remove(t) for t in taken])
            for frm, to, taken in jumps(b, player)]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    if history.n >= 2 and not jumps(Builder(pieces), 3 - mover):
        return f"Vitória do jogador {mover}", True
    return "", False


KONANE = Game(
    id="konane",
    name="Konane",
    subtitle="Se não conseguir capturar perde",
    objective=(
        "Capturar saltando sobre uma peça adversária vizinha (na ortogonal) "
        "para a casa vazia logo depois. Quem não conseguir capturar perde."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    rules=Rules(plays, status),
)
