from ..piece import Piece
from .game import Game
from .helpers import Builder, place, sq

BLOCKS = ["b2", "g2", "d4", "e4", "d5", "e5", "b7", "g7"]
VALUES = {3: 3, 4: 10, 5: 25, 6: 56, 7: 119}
# Ordem em que as casas livres foram jogadas (jogador 1 começa).
SCRIPT = [
    "h7", "g6", "a3", "a5", "f1", "h1", "f8", "e6",
    "c1", "f6", "h6", "d6", "c6", "h5", "h3", "c8",
    "h8", "g8", "d3", "f5", "g5", "f7", "f4", "c7",
    "c3", "b3", "c2", "e3", "c4", "c5", "a4", "a2",
    "b4", "d1", "g1", "b5", "a7", "e2", "e1", "h2",
    "e7", "g3", "f3", "f2", "a1", "d2", "b1", "h4",
    "a6", "b8", "a8", "d8", "e8", "d7", "b6", "g4",
]


def score(b: Builder, player: int) -> int:
    """Soma dos alinhamentos ortogonais (sequências máximas de 3 ou mais)."""
    total = 0
    for fixed in range(8):
        for horizontal in (True, False):
            run = 0
            for k in range(9):
                cell = None if k == 8 else (
                    sq(k, fixed) if horizontal else sq(fixed, k)
                )
                if cell and b.owner(cell) == player:
                    run += 1
                else:
                    total += VALUES.get(run, 0)
                    run = 0
    return total


def build() -> list:
    initial = [Piece(id=f"block-{s}", type="block", position=s) for s in BLOCKS]
    b = Builder(initial)
    last = {1: 0, 2: 0}
    for i, pos in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        assert b.empty(pos), f"{pos} ocupada"
        b.add(player, [place(pos, "disc", player)], "")
        now = score(b, player)
        gained = now - last[player]
        last[player] = now
        text = f"Jogador {player} coloca em {pos}."
        if gained:
            text += f" Forma alinhamento(s) que valem +{gained} pontos."
        b.moves[-1].comment = text
        b.moves[-1].status = f"Pontos — J1: {score(b, 1)} · J2: {score(b, 2)}"
    if not b.moves:
        return b.moves
    s1, s2 = score(b, 1), score(b, 2)
    final = "empate" if s1 == s2 else f"vitória do jogador {1 if s1 > s2 else 2}"
    b.moves[-1].comment += f" Tabuleiro cheio: {s1} x {s2} — {final}."
    b.moves[-1].status += f" · {final.capitalize()}"
    return b.moves


PAHTUM = Game(
    id="pahtum",
    name="Pah Tum",
    subtitle="Alinhamentos de diferentes valores",
    objective=(
        "Preencher o tabuleiro alternando peças. No fim, pontuam os "
        "alinhamentos ortogonais: 3 peças = 3, 4 = 10, 5 = 25, 6 = 56, 7 = 119."
    ),
    player_goal=None,
    initial_pieces=[Piece(id=f"block-{s}", type="block", position=s) for s in BLOCKS],
    moves=build(),
)
