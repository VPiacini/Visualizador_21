from ..piece import Piece
from .game import Game
from .helpers import DIRS8, Builder, move, place, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, r in ((1, 0), (2, 7))
    for c in range(8)
]
# Duas casas dos Reis (J1, J2) e depois lances (origem, destino).
SCRIPT: list = [
    "f4", "d4", ("f4", "f6"), ("d4", "d3"),
    ("c1", "c2"), ("d3", "f3"), ("c2", "c3"), ("a8", "a7"),
    ("e1", "f2"), ("f3", "g4"), ("h1", "h2"), ("c8", "c7"),
    ("b1", "a2"), ("g8", "h7"), ("f2", "g3"), ("g4", "e4"),
    ("f1", "e2"), ("e4", "h1"),
]


def grid_of(b: Builder) -> dict[str, tuple[int, bool]]:
    return {p.position: (p.player, p.type == "king") for p in b.pieces}


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


def build() -> list:
    b = Builder(INITIAL)
    for i, item in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        if i < 2:
            assert b.empty(item) and 2 <= xy(item)[1] <= 5, "Rei só nas quatro linhas centrais"
            b.add(player, [place(item, "king", player, f"k{player}")],
                  f"Jogador {player} coloca o seu Rei em {item}, numa das quatro linhas centrais.")
            continue
        frm, to = item
        grid = grid_of(b)
        assert grid.get(frm, (0,))[0] == player, f"{frm} não é do jogador {player}"
        match = [m for m in moves_from(grid, frm) if m[0] == to]
        assert match, f"lance ilegal {frm}->{to}"
        victim = match[0][1]
        pid, is_king = b.at(frm).id, b.at(frm).type == "king"
        who = "o Rei" if is_king else "um Soldado"
        actions = ([remove(victim)] if victim else []) + [move(pid, to)]
        text = f"Jogador {player} move {who} de {frm} a {to}."
        status = ""
        if victim:
            text = f"Jogador {player} captura em {victim}: {who} salta de {frm} a {to}."
            if grid[victim][1]:
                text += " Era o Rei adversário: vitória."
                status = f"Vitória do jogador {player}"
        if is_king and xy(to)[1] == (7 if player == 1 else 0) and not status:
            text += " O Rei chegou ao outro lado do tabuleiro: vitória."
            status = f"Vitória do jogador {player}"
        b.add(player, actions, text, status)
    return b.moves


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
    moves=build(),
)
