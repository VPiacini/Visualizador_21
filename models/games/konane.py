from ..piece import Piece
from .game import Game
from .helpers import DIRS4, Builder, move, remove, sq, step

# P1 ocupa as casas com (coluna + linha) par (a1 é do jogador 1); P2 as ímpares.
INITIAL = [
    Piece(id=f"p{1 if (c + r) % 2 == 0 else 2}-{sq(c, r)}", type="stone",
          position=sq(c, r), player=1 if (c + r) % 2 == 0 else 2)
    for c in range(8)
    for r in range(8)
]
# Duas casas retiradas na abertura (J1 e J2), depois capturas (origem, destino).
SCRIPT: list = [
    "e5", "d5", ("g5", "e5"), ("f3", "f5"),
    ("d4", "f4"), ("g4", "e4"), ("d2", "d4"), ("h3", "f3"),
    ("f2", "f4"), ("e4", "g4"), ("h2", "d2"), ("c2", "e2"),
    ("f6", "f4"), ("d7", "d3"), ("b4", "d4"), ("b5", "f5"),
    ("f8", "f6"), ("h5", "h3"), ("b2", "b4"), ("b7", "b3"),
    ("g7", "g5"), ("f5", "f3"), ("d4", "d2"), ("e2", "e4"),
    ("f6", "b6"), ("c8", "c6"), ("d8", "f8"), ("g4", "g6"),
    ("b6", "d6"), ("h7", "h5"),
]


def piece_at(b: Builder, pos: str) -> Piece:
    p = b.at(pos)
    assert p, f"sem peça em {pos}"
    return p


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


def build() -> list:
    b = Builder(INITIAL)
    for i, item in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        if i < 2:
            pos = item
            assert piece_at(b, pos).player == player
            b.add(player, [remove(pos)], f"Jogador {player} retira a sua peça de {pos}, abrindo a primeira casa livre.")
            continue
        frm, to = item
        match = [m for m in jumps(b, player) if m[0] == frm and m[1] == to]
        assert match, f"captura ilegal {frm}->{to}"
        taken = match[0][2]
        pid = piece_at(b, frm).id
        b.add(player, [move(pid, to)] + [remove(t) for t in taken],
              f"Jogador {player} salta de {frm} a {to} e captura {', '.join(taken)}"
              + (" (captura múltipla em linha reta)." if len(taken) > 1 else "."))
        if not jumps(b, 3 - player):
            b.moves[-1].comment += f" O jogador {3 - player} não tem mais capturas e perde."
            b.moves[-1].status = f"Vitória do jogador {player}"
    return b.moves


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
    moves=build(),
)
