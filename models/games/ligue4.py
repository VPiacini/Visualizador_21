from ..piece import Piece
from .game import Game, History, Rules
from .helpers import Builder, best_run, place, sq

def target(b: Builder, rank: int, side: str) -> str | None:
    cols = range(8) if side == "E" else range(7, -1, -1)
    return next((s for c in cols if b.empty(s := sq(c, rank - 1))), None)


def plays(pieces: list[Piece], player: int, history: History) -> list:
    b = Builder(pieces)
    spots = {t for rank in range(1, 9) for side in "ED" if (t := target(b, rank, side))}
    return [((s,), [place(s, "disc", player)]) for s in sorted(spots)]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    b = Builder(pieces)
    if any(best_run(b, p.position, mover) >= 4 for p in pieces if p.player == mover):
        return f"Vitória do jogador {mover}", True
    return "", False


LIGUE4 = Game(
    id="ligue4",
    name="Ligue 4",
    subtitle="Sob o efeito da gravidade",
    objective=(
        "Alinhar quatro peças em qualquer direção. Aqui há duas gravidades: "
        "as peças se empilham a partir das colunas a e h."
    ),
    player_goal=None,
    initial_pieces=[],
    rules=Rules(plays, status),
)
