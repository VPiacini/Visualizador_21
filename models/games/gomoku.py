from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS8, Builder, best_run, place, remove, sq, step

def captures(b: Builder, pos: str, player: int) -> list[str]:
    taken = []
    for d in DIRS8:
        p1, p2, p3 = (step(pos, d, k) for k in (1, 2, 3))
        if None in (p1, p2, p3):
            continue
        if b.owner(p1) == b.owner(p2) == 3 - player and b.owner(p3) == player:
            taken += [p1, p2]
    return taken


def plays(pieces: list[Piece], player: int, history: History) -> list:
    b = Builder(pieces)
    out = []
    for c in range(8):
        for r in range(8):
            pos = sq(c, r)
            if b.empty(pos):
                taken = captures(b, pos, player)
                out.append(((pos,), [place(pos, "disc", player)] + [remove(t) for t in taken]))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    # J1 joga nas jogadas ímpares: pares capturados = peças postas e já fora do tabuleiro / 2.
    n = history.n
    placed = {1: (n + 1) // 2, 2: n // 2}
    pairs = {q: (placed[3 - q] - sum(p.player == 3 - q for p in pieces)) // 2 for q in (1, 2)}
    text = f"Pares capturados — J1: {pairs[1]} · J2: {pairs[2]}"
    b = Builder(pieces)
    if any(best_run(b, p.position, mover) >= 5 for p in pieces if p.player == mover) or pairs[mover] >= 5:
        return f"{text} · Vitória do jogador {mover}", True
    return text, False


GOMOKU = Game(
    id="gomoku",
    name="Gomoku e Quina",
    subtitle="5-em-linha com captura",
    objective=(
        "Alinhar cinco peças (horizontal, vertical ou diagonal) ou capturar "
        "cinco pares de peças adversárias, flanqueando-os."
    ),
    player_goal=None,
    initial_pieces=[],
    rules=Rules(plays, status),
)
