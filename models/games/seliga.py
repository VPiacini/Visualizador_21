from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS4, DIRS8, move, place, remove, sq, step

CENTER = ["d4", "e4", "d5", "e5"]
PIECES = 12


def components(grid: dict[str, int]) -> list[set[str]]:
    """Grupos de peças vizinhas (8 direções), sem distinguir cor."""
    left, out = set(grid), []
    while left:
        stack, comp = [left.pop()], set()
        while stack:
            s = stack.pop()
            comp.add(s)
            for d in DIRS8:
                n = step(s, d)
                if n in left:
                    left.discard(n)
                    stack.append(n)
        out.append(comp)
    return out


def settle(grid: dict[str, int], dest: str):
    """Aplica a regra dos grupos. Devolve (grid final, peças eliminadas) ou None se
    o grupo da peça movida não é o maior (derrota de quem moveu)."""
    comps = components(grid)
    mine = next(c for c in comps if dest in c)
    if any(len(c) > len(mine) for c in comps):
        return None
    dropped = [s for c in comps if c is not mine for s in c]
    return {s: p for s, p in grid.items() if s not in dropped}, dropped


def chains(grid, pos, player, taken=()):
    out = []
    for d in DIRS4:
        over, land = step(pos, d), step(pos, d, 2)
        if over in grid and grid[over] == 3 - player and over not in taken and land and land not in grid:
            path = [((land,), (over,))]
            g = {s: p for s, p in grid.items() if s != over}
            path += [((land,) + p, (over,) + t) for p, t in chains(g, land, player, taken + (over,))]
            out += path
    return out


def captures(grid: dict[str, int], player: int):
    """Todos os lances de captura: caminho completo -> casas capturadas (inclui prefixos)."""
    out = {}
    for pos, pl in grid.items():
        if pl != player:
            continue
        g = {s: p for s, p in grid.items() if s != pos}
        for path, taken in chains(g, pos, player):
            out[(pos,) + path] = taken
    return out


def result_of(grid: dict[str, int], path: tuple, taken: tuple, player: int):
    g = dict(grid)
    g.pop(path[0])
    for t in taken:
        g.pop(t)
    g[path[-1]] = player
    return settle(g, path[-1])


def safe_moves(grid: dict[str, int], player: int) -> dict:
    return {p: t for p, t in captures(grid, player).items() if result_of(grid, p, t, player)}


def can_place(grid: dict[str, int], pos: str, player: int) -> bool:
    if pos in grid:
        return False
    mine = [s for s, p in grid.items() if p == player]
    if not mine:
        return pos in CENTER
    return any(step(pos, d) in mine for d in DIRS8)


def plays(pieces: list[Piece], player: int, history: History) -> list:
    grid = {p.position: p.player for p in pieces}
    if history.n < 2 * PIECES:
        pid = f"p{player}-{sum(1 for v in grid.values() if v == player) + 1}"
        return [
            ((pos,), [place(pos, "stone", player, pid)])
            for r in range(8)
            for c in range(8)
            if can_place(grid, pos := sq(c, r), player)
        ]
    ids = {p.position: p.id for p in pieces}
    out = []
    for path, taken in safe_moves(grid, player).items():
        _, dropped = result_of(grid, path, taken, player)
        out.append((path, [move(ids[path[0]], path[-1])] + [remove(t) for t in taken] + [remove(x) for x in dropped]))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    if history.n < 2 * PIECES:
        return "", False
    n1 = sum(p.player == 1 for p in pieces)
    text = f"Peças — J1: {n1} · J2: {len(pieces) - n1}"
    if not safe_moves({p.position: p.player for p in pieces}, 3 - mover):
        return f"{text} · Vitória do jogador {mover}", True
    return text, False


SELIGA = Game(
    id="seliga",
    name="Se Liga",
    subtitle="Mantendo-se conectado",
    objective=(
        "Cada jogador posiciona 12 peças (sempre vizinhas de uma sua). Depois só "
        "se joga capturando por salto ortogonal; ao final o grupo da peça movida "
        "deve ser o maior, e os grupos menores desconectados saem. Perde quem não puder jogar."
    ),
    player_goal=None,
    initial_pieces=[],
    rules=Rules(plays, status),
)
