from ..piece import Piece
from .game import Game, History, Rules
from .helpers import move, remove, sq, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="pawn", position=sq(c, r), player=pl)
    for pl, r in ((1, 1), (2, 6))
    for c in range(8)
]


def pawn_moves(grid: dict[str, int], pos: str, player: int, ep: str | None):
    """Lances do peão: (destino, casa capturada ou None). `ep` = casa de en passant."""
    fwd = 1 if player == 1 else -1
    c, r = xy(pos)
    start = 1 if player == 1 else 6
    out = []
    one = sq(c, r + fwd)
    if one and one not in grid:
        out.append((one, None))
        two = sq(c, r + 2 * fwd)
        if r == start and two and two not in grid:
            out.append((two, None))
    for dc in (-1, 1):
        diag = sq(c + dc, r + fwd)
        if not diag:
            continue
        if grid.get(diag) == 3 - player:
            out.append((diag, diag))
        elif diag == ep:
            out.append((diag, sq(c + dc, r)))  # peão capturado fica ao lado
    return out


def ep_square(player: int, frm: str, to: str) -> str | None:
    """Casa 'pulada' por um avanço duplo (alvo do en passant), senão None."""
    if abs(xy(to)[1] - xy(frm)[1]) == 2:
        return sq(xy(frm)[0], (xy(frm)[1] + xy(to)[1]) // 2)
    return None


def last_ep(pieces: list[Piece], player: int, history: History) -> str | None:
    """Casa pulada pelo avanço duplo que o adversário de `player` acabou de fazer, se houve."""
    before = {q.id: q.position for q in history.last or []}
    for q in pieces:
        old = before.get(q.id)
        if old and old != q.position and q.player != player and (target := ep_square(q.player, old, q.position)):
            return target
    return None


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {q.position: q.player for q in pieces}
    ep = last_ep(pieces, player, history)
    return [
        ((q.position, to), ([remove(victim)] if victim else []) + [move(q.id, to)])
        for q in pieces
        if q.player == player
        for to, victim in pawn_moves(grid, q.position, player, ep)
    ]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    goal = 7 if mover == 1 else 0
    if any(q.player == mover and xy(q.position)[1] == goal for q in pieces):
        return f"Vitória do jogador {mover}", True
    return "", False


PEOES = Game(
    id="peoes",
    name="Batalha dos Peões",
    subtitle="Um jogo pré-enxadrístico",
    objective=(
        "Só peões de xadrez, com os mesmos movimentos (avanço de 1 ou 2 casas "
        "no primeiro lance, captura na diagonal, en passant). Vence quem levar "
        "um peão ao outro lado primeiro."
    ),
    player_goal={1: "chegar à linha 8", 2: "chegar à linha 1"},
    initial_pieces=INITIAL,
    rules=Rules(plays, status),
)
