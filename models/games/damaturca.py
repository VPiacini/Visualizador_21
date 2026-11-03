from ..piece import Piece
from .game import Game
from .helpers import Builder, move, place, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (1, 2)), (2, (5, 6)))
    for r in ranks
    for c in range(8)
]
# Cada lance é a lista de casas percorridas: (origem, destino) ou (origem, salto1, salto2...).
SCRIPT: list = [
    ("b3", "b4"), ("b6", "b5"), ("b4", "b6", "b8"),
    ("c6", "c5"), ("e3", "e4"), ("h6", "h5"),
    ("f3", "f4"), ("f6", "f5"), ("f4", "f6", "h6", "h8"),
    ("h5", "h4"), ("h3", "h5"), ("f7", "f6"),
    ("h5", "h6"), ("e6", "e5"), ("e4", "e6", "c6", "c8"),
    ("d7", "d6"), ("c8", "c4"), ("g7", "g6"),
    ("c4", "c7"), ("g6", "g5"), ("c7", "f7", "f5", "h5"),
    ("a6", "a5"), ("c3", "c4"), ("d6", "d5"),
    ("h5", "c5"), ("a7", "a6"), ("c5", "c8"),
    ("a6", "b6"), ("b8", "b5"), ("a5", "c5", "c3", "e3", "e1"),
    ("d2", "d3"), ("e1", "e2"), ("f2", "d2"),
]


def forward(player: int) -> int:
    return 1 if player == 1 else -1


def directions(player: int, is_dama: bool) -> list[tuple[int, int]]:
    f = forward(player)
    return [(1, 0), (-1, 0), (0, 1), (0, -1)] if is_dama else [(0, f), (1, 0), (-1, 0)]


def chains(grid, pos, player, is_dama, taken=(), last_dir=None):
    """Todas as sequências de captura a partir de pos: lista de (caminho, capturadas)."""
    out = []
    for d in directions(player, is_dama):
        if last_dir and d == (-last_dir[0], -last_dir[1]):
            continue  # não pode voltar sobre a mesma linha
        k = 1
        if is_dama:
            while (s := step(pos, d, k)) and s not in grid:
                k += 1
        over = step(pos, d, k)
        if not over or over not in grid or grid[over][0] == player or over in taken:
            continue
        land = step(pos, d, k + 1)
        if not land or land in grid:
            continue
        lands = [land]
        if is_dama:
            n = k + 2
            while (s := step(pos, d, n)) and s not in grid:
                lands.append(s)
                n += 1
        for L in lands:
            nxt = chains(grid, L, player, is_dama, taken + (over,), d)
            if nxt:
                out += [((L,) + p, (over,) + c) for p, c in nxt]
            else:
                out.append(((L,), (over,)))
    return out


def legal_moves(grid: dict, player: int) -> dict[tuple, tuple]:
    """caminho completo -> casas capturadas. Captura é obrigatória (e vai até o fim)."""
    caps, plain = {}, {}
    for pos, (pl, dama) in grid.items():
        if pl != player:
            continue
        g = {s: v for s, v in grid.items() if s != pos}  # a peça sai da casa ao saltar
        for path, taken in chains(g, pos, player, dama):
            caps[(pos,) + path] = taken
        for d in directions(player, dama):
            k = 1
            while (s := step(pos, d, k)) and s not in grid:
                plain[(pos, s)] = ()
                if not dama:
                    break
                k += 1
    return caps or plain


def grid_of(b: Builder) -> dict:
    return {p.position: (p.player, p.type == "dama") for p in b.pieces}


def build() -> list:
    b = Builder(INITIAL)
    for i, path in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        path = tuple(path)
        legal = legal_moves(grid_of(b), player)
        assert path in legal, f"lance ilegal {path}"
        taken = legal[path]
        pid, was_dama = b.at(path[0]).id, b.at(path[0]).type == "dama"
        dest = path[-1]
        actions = [move(pid, dest)] + [remove(t) for t in taken]
        promoted = not was_dama and xy(dest)[1] == (7 if player == 1 else 0)
        if promoted:
            actions += [remove(dest), place(dest, "dama", player, pid)]
        trail = " → ".join(path)
        text = f"Jogador {player} joga {trail}."
        if taken:
            text = f"Jogador {player} captura {len(taken)} peça(s) ({', '.join(taken)}): {trail}."
        if promoted:
            text += " A peça chega ao fim do tabuleiro e vira Dama (anda várias casas)."
        b.add(player, actions, text)
        if not legal_moves(grid_of(b), 3 - player):
            b.moves[-1].comment += f" O jogador {3 - player} fica sem jogadas."
            b.moves[-1].status = f"Vitória do jogador {player}"
    return b.moves


DAMATURCA = Game(
    id="damaturca",
    name="Dama Turca (Tama)",
    subtitle="Uma dama diferente",
    objective=(
        "Peças andam 1 casa para frente ou para os lados (nunca na diagonal) e "
        "capturam saltando; capturar é obrigatório. Ao chegar ao fim viram Dama, "
        "que anda e captura de longe. Vence quem tirar todas as peças do adversário."
    ),
    player_goal=None,
    initial_pieces=INITIAL,
    moves=build(),
)
