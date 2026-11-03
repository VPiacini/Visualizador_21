from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS8, Builder, move, place, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, r in ((1, 0), (2, 7))
    for c in range(8)
]


def moves_from(grid: dict, pos: str) -> list[tuple[str, str | None]]:
    """(destino, casa capturada). Soldado anda 1; Rei desliza; ambos capturam saltando 1 peça."""
    player, is_king = grid[pos]
    out = []
    for d in DIRS8:
        k = 1
        while (s := step(pos, d, k)) and s not in grid:
            out.append((s, None))
            if not is_king:
                break
            k += 1
        over, land = step(pos, d), step(pos, d, 2)
        if over in grid and grid[over][0] != player and land and land not in grid:
            out.append((land, over))
    return out


def plays(pieces: list[Piece], player: int, history: History) -> list:
    if history.n < 2:
        b = Builder(pieces)
        return [
            ((s,), [place(s, "king", player, f"k{player}")])
            for r in range(2, 6)
            for c in range(8)
            if b.empty(s := sq(c, r))
        ]
    grid = {p.position: (p.player, p.type == "king") for p in pieces}
    return [
        ((p.position, to), ([remove(victim)] if victim else []) + [move(p.id, to)])
        for p in pieces
        if p.player == player
        for to, victim in moves_from(grid, p.position)
    ]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    if history.n < 2:
        return "", False
    kings = {p.player: p for p in pieces if p.type == "king"}
    reached = 3 - mover in kings and mover in kings and xy(kings[mover].position)[1] == (7 if mover == 1 else 0)
    if 3 - mover not in kings or reached:
        return f"Vitória do jogador {mover}", True
    return "", False


GOGOL = Game(
    id="gogol",
    name="Gogol",
    subtitle="Salve seu Rei ou pegue do adversário",
    objective=(
        "Capturar o Rei adversário (saltando sobre ele) ou levar o seu Rei ao "
        "outro lado do tabuleiro. Soldados andam 1 casa, o Rei desliza; ambos "
        "capturam saltando uma peça vizinha."
    ),
    player_goal={1: "Rei até a linha 8", 2: "Rei até a linha 1"},
    initial_pieces=INITIAL,
    rules=Rules(plays, status),
)
