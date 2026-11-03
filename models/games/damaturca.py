from ..piece import Piece
from .game import Game, History, Rules
from .helpers import move, place, remove, sq, step, xy

INITIAL = [
    Piece(id=f"p{pl}-{sq(c, r)}", type="stone", position=sq(c, r), player=pl)
    for pl, ranks in ((1, (1, 2)), (2, (5, 6)))
    for r in ranks
    for c in range(8)
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


def plays(pieces: list[Piece], player: int, history: History) -> list:
    by_pos = {p.position: p for p in pieces}
    far = 7 if player == 1 else 0
    out = []
    for path, taken in legal_moves({p.position: (p.player, p.type == "dama") for p in pieces}, player).items():
        piece, dest = by_pos[path[0]], path[-1]
        actions = [move(piece.id, dest)] + [remove(t) for t in taken]
        if piece.type != "dama" and xy(dest)[1] == far:
            actions += [remove(dest), place(dest, "dama", player, piece.id)]
        out.append((path, actions))
    return out


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    grid = {p.position: (p.player, p.type == "dama") for p in pieces}
    if not legal_moves(grid, 3 - mover):
        return f"Vitória do jogador {mover}", True
    return "", False


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
    rules=Rules(plays, status),
)
