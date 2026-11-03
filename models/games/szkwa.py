from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS4, place, remove, sq, step

MAX_PIECES = 50


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


def plays(pieces: list[Piece], player: int, history: History) -> list:
    placed = (history.n + 1) // 2 if player == 1 else history.n // 2
    if placed >= MAX_PIECES:
        return []
    grid = {p.position: p.player for p in pieces}
    out = []
    for r in range(8):
        for c in range(8):
            pos = sq(c, r)
            if pos in grid:
                continue
            taken = captured_by({**grid, pos: player}, pos, player)
            out.append(((pos,), [place(pos, "stone", player)] + [remove(t) for t in taken]))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    # J1 joga nas jogadas ímpares: capturas de um jogador = peças do outro postas e já fora do tabuleiro.
    placed = {1: (history.n + 1) // 2, 2: history.n // 2}
    caps = {q: placed[3 - q] - sum(p.player == 3 - q for p in pieces) for q in (1, 2)}
    text = f"Capturas — J1: {caps[1]} · J2: {caps[2]}"
    if len(pieces) < 64 and history.n < 2 * MAX_PIECES:
        return text, False
    return f"{text} · " + ("Empate" if caps[1] == caps[2] else f"Vitória do jogador {1 if caps[1] > caps[2] else 2}"), True


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
    rules=Rules(plays, status),
)
