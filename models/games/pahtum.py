from ..piece import Piece
from .game import Game, History, Rules
from .helpers import Builder, place, sq

BLOCKS = ["b2", "g2", "d4", "e4", "d5", "e5", "b7", "g7"]
VALUES = {3: 3, 4: 10, 5: 25, 6: 56, 7: 119}


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


def plays(pieces: list[Piece], player: int, history: History) -> list:
    b = Builder(pieces)
    return [((s,), [place(s, "disc", player)]) for r in range(8) for c in range(8) if b.empty(s := sq(c, r))]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    b = Builder(pieces)
    s1, s2 = score(b, 1), score(b, 2)
    text = f"Pontos — J1: {s1} · J2: {s2}"
    if len(pieces) < 64:
        return text, False
    return f"{text} · " + ("Empate" if s1 == s2 else f"Vitória do jogador {1 if s1 > s2 else 2}"), True


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
    rules=Rules(plays, status),
)
