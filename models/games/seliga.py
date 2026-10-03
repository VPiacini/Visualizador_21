from .game import Game
from .helpers import DIRS4, DIRS8, Builder, move, place, remove, step

CENTER = ["d4", "e4", "d5", "e5"]
PIECES = 12
# Primeiro as 24 colocações (casas), depois capturas como caminhos (origem, salto1, ...).
SCRIPT: list = [
    "e4", "d4", "d3", "d5", "c4", "c3",
    "e5", "c5", "b4", "b3", "e6", "a4",
    "c2", "a3", "b5", "c6", "d6", "b2",
    "b6", "a5", "d2", "c1", "e3", "d7",
    ("c2", "a2"), ("d5", "f5"), ("b5", "d5"), ("c6", "a6"), ("c4", "c2"), ("c1", "c3"),
    ("e4", "c4"), ("b3", "b5"), ("d3", "b3"), ("a3", "c3", "c5"),
]


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


def build() -> list:
    b = Builder([])
    count = {1: 0, 2: 0}
    for i, item in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        grid = {p.position: p.player for p in b.pieces}
        if i < 2 * PIECES:
            assert can_place(grid, item, player), f"colocação inválida {item}"
            count[player] += 1
            first = count[player] == 1
            b.add(player, [place(item, "stone", player, f"p{player}-{count[player]}")],
                  f"Jogador {player} coloca a peça {count[player]} em {item}"
                  + (" (no centro)." if first else ", vizinha a uma peça sua."))
            continue
        path = tuple(item)
        taken = safe_moves(grid, player).get(path)
        assert taken is not None, f"lance ilegal ou perdedor {path}"
        pid = next(p.id for p in b.pieces if p.position == path[0])
        final, dropped = result_of(grid, path, taken, player)
        actions = [move(pid, path[-1])] + [remove(t) for t in taken] + [remove(s) for s in dropped]
        text = f"Jogador {player} salta {' → '.join(path)} e captura {', '.join(taken)}."
        if dropped:
            text += f" Grupos desconectados eliminados: {', '.join(sorted(dropped))}."
        b.add(player, actions, text)
        n1 = sum(1 for p in b.pieces if p.player == 1)
        n2 = sum(1 for p in b.pieces if p.player == 2)
        b.moves[-1].status = f"Peças — J1: {n1} · J2: {n2}"
        nxt = {p.position: p.player for p in b.pieces}
        if not safe_moves(nxt, 3 - player):
            b.moves[-1].comment += f" O jogador {3 - player} não tem lance válido e perde."
            b.moves[-1].status += f" · Vitória do jogador {player}"
    return b.moves


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
    moves=build(),
)
