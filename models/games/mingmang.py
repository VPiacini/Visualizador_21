from ..move import Move, apply_move
from ..piece import Piece, position_key
from .game import Game, History, Rules
from .hasami import custody
from .helpers import flip, move, sq
from .makyek import slides

# ponytail: posição inicial adaptada (linhas 1-2 e 7-8); a figura 17.1 do livro não
# está no texto — ajustar INITIAL se a posição original for outra.
INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (0, 1)), (2, (6, 7)))
    for r in ranks
    for c in range(8)
]


def captured(grid: dict[str, int], to: str, player: int) -> list[str]:
    """Custódia em linha de uma ou mais peças; cantos nunca são capturados."""
    return custody(grid, to, player, multi=True, corners=False)


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    out = []
    for p in pieces:
        if p.player != player:
            continue
        for to in slides(grid, p.position):
            g2 = {s: pl for s, pl in grid.items() if s != p.position} | {to: player}
            taken = captured(g2, to, player)
            actions = [move(p.id, to)] + [flip(t, player) for t in taken]
            if position_key(apply_move(pieces, Move(player, actions))) not in history.seen:
                out.append(((p.position, to), actions))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    n1 = sum(p.player == 1 for p in pieces)
    text = f"Peças — J1: {n1} · J2: {len(pieces) - n1}"
    other = 3 - mover
    if not any(p.player == other for p in pieces) or not plays(pieces, other, history):
        return f"{text} · Vitória do jogador {mover}", True
    return text, False


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
    rules=Rules(plays, status),
)
