from ..piece import Piece
from .game import Game
from .helpers import Builder, move, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="pawn", position=sq(c, r), player=pl)
    for pl, r in ((1, 1), (2, 6))
    for c in range(8)
]
# Lances (origem, destino), alternando jogador 1 e 2.
SCRIPT: list = [
    ("f2", "f4"), ("a7", "a6"), ("h2", "h3"), ("g7", "g6"),
    ("f4", "f5"), ("g6", "f5"), ("d2", "d3"), ("b7", "b6"),
    ("a2", "a3"), ("a6", "a5"), ("d3", "d4"), ("f5", "f4"),
    ("a3", "a4"), ("f4", "f3"), ("e2", "f3"), ("b6", "b5"),
    ("d4", "d5"), ("b5", "a4"), ("f3", "f4"), ("d7", "d6"),
    ("c2", "c4"), ("h7", "h6"), ("c4", "c5"), ("d6", "c5"),
    ("f4", "f5"), ("h6", "h5"), ("h3", "h4"), ("e7", "e5"),
    ("f5", "e6"), ("c5", "c4"), ("e6", "f7"), ("c7", "c6"),
    ("f7", "f8"),
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


def build() -> list:
    b = Builder(INITIAL)
    ep = None
    for i, (frm, to) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        assert grid.get(frm) == player
        match = [m for m in pawn_moves(grid, frm, player, ep) if m[0] == to]
        assert match, f"lance ilegal {frm}->{to}"
        victim = match[0][1]
        pid = b.at(frm).id
        actions = ([remove(victim)] if victim else []) + [move(pid, to)]
        text = f"Jogador {player} avança de {frm} a {to}."
        if victim and victim != to:
            text = f"Jogador {player} captura en passant: de {frm} a {to}, retirando o peão de {victim}."
        elif victim:
            text = f"Jogador {player} captura em {to}, saindo de {frm}."
        elif abs(xy(to)[1] - xy(frm)[1]) == 2:
            text = f"Jogador {player} avança duas casas, de {frm} a {to} (primeiro movimento do peão)."
        ep = ep_square(player, frm, to)
        goal = 7 if player == 1 else 0
        status = ""
        if xy(to)[1] == goal:
            text += " Chegou ao outro lado do tabuleiro e vence."
            status = f"Vitória do jogador {player}"
        b.add(player, actions, text, status)
    return b.moves


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
    moves=build(),
)
