from ..piece import Piece
from .game import Game
from .hasami import custody
from .helpers import Builder, flip, move, sq
from .makyek import slides

# ponytail: posição inicial adaptada (linhas 1-2 e 7-8); a figura 17.1 do livro não
# está no texto — ajustar INITIAL se a posição original for outra.
INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
]
# Lances (origem, destino): deslizam na ortogonal; não pode repetir posição já ocorrida.
SCRIPT: list = [
    ("h2", "h5"), ("e7", "e3"), ("a2", "a6"), ("c7", "c3"),
    ("a6", "g6"), ("d7", "d3"), ("f2", "f4"), ("a7", "a2"),
    ("f4", "c4"), ("f7", "f2"), ("c4", "d4"), ("b2", "b3"),
    ("d4", "e4"), ("f8", "f3"), ("e4", "f4"), ("e8", "e4"),
    ("h5", "e5"), ("h7", "h2"), ("e4", "c4"), ("g2", "g3"),
    ("g1", "g2"), ("b3", "b2"), ("f4", "d4"), ("c8", "c5"),
    ("g6", "c6"), ("b7", "b3"), ("e5", "e4"), ("g7", "c7"),
    ("e4", "f4"), ("d8", "d5"),
]


def state_key(grid: dict[str, int]) -> frozenset:
    return frozenset(grid.items())


def captured(grid: dict[str, int], to: str, player: int) -> list[str]:
    """Custódia em linha de uma ou mais peças; cantos nunca são capturados."""
    return custody(grid, to, player, multi=True, corners=False)


def build() -> list:
    b = Builder(INITIAL)
    seen = {state_key({p.position: p.player for p in b.pieces})}
    for i, (frm, to) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        assert grid.get(frm) == player and to in slides(grid, frm), f"lance ilegal {frm}->{to}"
        pid = b.at(frm).id
        g2 = dict(grid)
        g2[to] = g2.pop(frm)
        taken = captured(g2, to, player)
        for t in taken:
            g2[t] = player
        key = state_key(g2)
        assert key not in seen, "posição repetida"
        seen.add(key)
        text = f"Jogador {player} move de {frm} a {to}."
        if taken:
            text += f" Cerca {', '.join(taken)}: essas peças passam a ser do jogador {player}."
        b.add(player, [move(pid, to)] + [flip(t, player) for t in taken], text)
        mine = sum(1 for p in b.pieces if p.player == player)
        theirs = len(b.pieces) - mine
        b.moves[-1].status = f"Peças — J1: {sum(p.player == 1 for p in b.pieces)} · J2: {sum(p.player == 2 for p in b.pieces)}"
        if theirs == 0:
            b.moves[-1].comment += f" O jogador {3 - player} ficou sem peças."
            b.moves[-1].status += f" · Vitória do jogador {player}"
    return b.moves


MINGMANG = Game(
    id="mingmang",
    name="Ming Mang",
    subtitle="Conquistando os espaços do tabuleiro",
    objective=(
        "As peças deslizam na ortogonal. Cercar peças adversárias em linha as "
        "converte para o seu lado (os cantos não podem ser capturados). Perde "
        "quem ficar sem peças ou sem jogada. Partida de exemplo: um trecho."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    moves=build(),
)
