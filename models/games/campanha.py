from ..piece import Piece
from .game import Game
from .helpers import LINES4, Builder, move, place, sq, step, xy

KNIGHT_JUMPS = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
TARGET = 4  # o livro aceita 5 (mais lento) ou 4 (mais dinâmico)
INITIAL = [
    Piece(id="n1", type="knight", position="d4", player=1),
    Piece(id="n2", type="knight", position="e5", player=2),
]
# Casas de destino do Cavalo, alternando jogador 1 e 2.
SCRIPT = [
    "e6", "c4", "f8", "a5", "d7", "b7", "b6", "c5",
    "c8", "a4", "e7", "c3", "g6", "a2", "h4", "c1",
    "f5", "b3", "e3",
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


def build() -> list:
    b = Builder(INITIAL)
    for i, to in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        frm = knight_pos(b, player)
        assert to in knight_moves(b, player), f"lance ilegal {frm}->{to}"
        b.add(player, [move(f"n{player}", to), place(frm, "disc", player)], "")
        run = marks_run(b, frm, player)
        text = f"Jogador {player} leva o Cavalo de {frm} a {to} e deixa uma peça em {frm}."
        status = ""
        if run >= TARGET:
            text += f" Forma {run} em linha e vence."
            status = f"Vitória do jogador {player}"
        elif not knight_moves(b, 3 - player):
            text += f" O Cavalo do jogador {3 - player} fica sem movimentos: vitória."
            status = f"Vitória do jogador {player}"
        elif run == TARGET - 1:
            text += f" Já são {run} peças alinhadas: ameaça de vitória."
        b.moves[-1].comment, b.moves[-1].status = text, status
    return b.moves


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
    moves=build(),
)
