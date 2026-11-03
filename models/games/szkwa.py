from .game import Game
from .helpers import DIRS4, Builder, place, remove, step

MAX_PIECES = 50
# Casas jogadas, alternando jogador 1 e 2 (sempre se joga: não há passe).
SCRIPT: list[str] = [
    "e7", "d6", "b4", "g6", "h7", "g1", "h6", "b6", "d8", "c6",
    "h3", "e5", "a6", "a7", "e6", "a5", "a2", "b8", "c1", "g3",
    "h1", "h2", "c7", "h4", "b1", "h1", "a1", "f7", "g5", "f1",
    "c5", "f5", "e1", "d3", "h3", "c8", "c3", "f8", "d4", "g7",
    "c2", "c4", "d1", "g4", "e3", "h5", "d2", "h8", "e8", "e4",
    "d3", "a3", "g5", "g2", "e2", "d7", "a4", "f6", "b3", "b7",
    "f3", "a8", "f2", "d8", "f4", "e6", "h6", "g8", "g1", "a6",
    "e8", "e7", "g4", "b2", "a3", "h4", "h5", "h1", "h2", "f1",
    "c7", "h1", "g2", "e8", "h7", "h4", "d5", "b5", "g3",
]


def group_of(grid: dict[str, int], pos: str) -> tuple[set[str], int]:
    """Grupo ortogonal de pos e o número de liberdades (casas vazias vizinhas)."""
    player, group, libs, stack = grid[pos], set(), set(), [pos]
    while stack:
        s = stack.pop()
        if s in group:
            continue
        group.add(s)
        for d in DIRS4:
            n = step(s, d)
            if n is None:
                continue
            if n not in grid:
                libs.add(n)
            elif grid[n] == player:
                stack.append(n)
    return group, len(libs)


def captured_by(grid: dict[str, int], pos: str, player: int) -> list[str]:
    """Peças adversárias que ficam sem liberdade depois de jogar em pos (grid já inclui pos)."""
    taken, seen = [], set()
    for d in DIRS4:
        n = step(pos, d)
        if n and grid.get(n) == 3 - player and n not in seen:
            group, libs = group_of(grid, n)
            seen |= group
            if libs == 0:
                taken += sorted(group)
    return taken


def build() -> list:
    b = Builder([])
    caps = {1: 0, 2: 0}
    placed = {1: 0, 2: 0}
    for i, pos in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        assert pos not in grid and placed[player] < MAX_PIECES, f"jogada inválida {pos}"
        placed[player] += 1
        grid[pos] = player
        taken = captured_by(grid, pos, player)
        caps[player] += len(taken)
        text = f"Jogador {player} coloca em {pos}."
        if taken:
            text += f" Cerca e captura {len(taken)} peça(s): {', '.join(taken)}."
        b.add(player, [place(pos, "stone", player)] + [remove(t) for t in taken], text,
              f"Capturas — J1: {caps[1]} · J2: {caps[2]}")
    full = SCRIPT and len(b.pieces) == 64
    if full:
        end = "empate" if caps[1] == caps[2] else f"vitória do jogador {1 if caps[1] > caps[2] else 2}"
        b.moves[-1].comment += f" Tabuleiro cheio: {end}."
        b.moves[-1].status += f" · {end.capitalize()}"
    return b.moves


SZKWA = Game(
    id="szkwa",
    name="Sz'kwa (Go e Envio)",
    subtitle="Grupos sem liberdade são eliminados",
    objective=(
        "Colocar uma peça por vez; um grupo adversário (vizinhança ortogonal) sem "
        "nenhuma casa vazia ao redor é capturado. Vence quem capturar mais peças. "
        "O Go e o Envio seguem a mesma ideia de cercamento."
    ),
    player_goal=None,
    initial_pieces=[],
    moves=build(),
)
