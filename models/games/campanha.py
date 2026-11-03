from ..piece import Piece
from .game import Game, History, Rules
from .helpers import LINES4, Builder, move, place, sq, step, xy

KNIGHT_JUMPS = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
TARGET = 4  # o livro aceita 5 (mais lento) ou 4 (mais dinâmico)
INITIAL = [
    Piece(id="n1", type="knight", position="d4", player=1),
    Piece(id="n2", type="knight", position="e5", player=2),
]


def knight_pos(b: Builder, player: int) -> str:
    return next(p.position for p in b.pieces if p.id == f"n{player}")


def knight_moves(b: Builder, player: int) -> list[str]:
    c, r = xy(knight_pos(b, player))
    return [s for dc, dr in KNIGHT_JUMPS if b.empty(s := sq(c + dc, r + dr))]


def marks_run(b: Builder, pos: str, player: int) -> int:
    """Maior alinhamento de peças marcadas (não conta o Cavalo) passando por pos."""
    def mine(s):
        p = b.at(s) if s else None
        return bool(p and p.type == "disc" and p.player == player)

    best = 1
    for d in LINES4:
        n = 1
        for sign in (1, -1):
            k = 1
            while mine(step(pos, (d[0] * sign, d[1] * sign), k)):
                n += 1
                k += 1
        best = max(best, n)
    return best


def plays(pieces: list[Piece], player: int, history: History) -> list:
    b = Builder(pieces)
    frm = knight_pos(b, player)
    return [((to,), [move(f"n{player}", to), place(frm, "disc", player)]) for to in knight_moves(b, player)]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    b = Builder(pieces)
    if any(marks_run(b, p.position, mover) >= TARGET for p in pieces if p.type == "disc" and p.player == mover):
        return f"Vitória do jogador {mover}", True
    if not knight_moves(b, 3 - mover):
        return f"Vitória do jogador {mover}", True
    return "", False


CAMPANHA = Game(
    id="campanha",
    name="Campanha",
    subtitle="No trote do cavalo",
    objective=(
        "Cada jogador move o seu Cavalo (salto do xadrez) e deixa uma peça na "
        f"casa de partida. Vence quem alinhar {TARGET} peças ou bloquear o "
        "Cavalo adversário."
    ),
    player_goal={1: "alinhar 4 (Cavalo claro)", 2: "alinhar 4 (Cavalo escuro)"},
    initial_pieces=INITIAL,
    rules=Rules(plays, status),
)
