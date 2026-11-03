from ..piece import Piece
from .game import Game, Rules
from .helpers import DIRS8, Builder, best_run, place, remove, sq, step

# Casas jogadas, alternando jogador 1 e 2. Regras: Quina (Pente) — 5 em linha
# ou 5 pares capturados. Um par é capturado ao ser flanqueado por quem joga.
SCRIPT: list[str] = [
    "d5", "c5", "d6", "d4", "c4", "d7", "b4", "a4", "e5",
    "b6", "e3", "a7", "e4", "e6", "e2", "e1", "f5", "d3",
    "c8", "e6", "d5", "g6", "d2", "e4", "d4", "f5",
]


def captures(b: Builder, pos: str, player: int) -> list[str]:
    taken = []
    for d in DIRS8:
        p1, p2, p3 = (step(pos, d, k) for k in (1, 2, 3))
        if None in (p1, p2, p3):
            continue
        if b.owner(p1) == b.owner(p2) == 3 - player and b.owner(p3) == player:
            taken += [p1, p2]
    return taken


def build() -> list:
    b = Builder([])
    pairs = {1: 0, 2: 0}
    for i, pos in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        assert b.empty(pos), f"{pos} ocupada"
        taken = captures(b, pos, player)
        b.add(player, [place(pos, "disc", player)] + [remove(t) for t in taken], "")
        pairs[player] += len(taken) // 2
        won_line = best_run(b, pos, player) >= 5
        won_pairs = pairs[player] >= 5
        assert not (won_line or won_pairs) or i == len(SCRIPT) - 1
        text = f"Jogador {player} coloca em {pos}."
        if taken:
            text += f" Captura o par {taken[0]}-{taken[1]}" + (
                f" e o par {taken[2]}-{taken[3]}." if len(taken) > 2 else "."
            )
        elif best_run(b, pos, player) == 4:
            text += " Forma 4 em linha: ameaça de 5."
        elif best_run(b, pos, player) == 3:
            text += " Forma 3 em linha."
        if won_line:
            text += " Fecha 5 em linha e vence."
        if won_pairs:
            text += " Chega a 5 pares capturados e vence."
        b.moves[-1].comment = text
        b.moves[-1].status = f"Pares capturados — J1: {pairs[1]} · J2: {pairs[2]}" + (
            f" · Vitória do jogador {player}" if (won_line or won_pairs) else ""
        )
    return b.moves


def plays(pieces: list[Piece], player: int, n: int) -> list:
    b = Builder(pieces)
    out = []
    for c in range(8):
        for r in range(8):
            pos = sq(c, r)
            if b.empty(pos):
                taken = captures(b, pos, player)
                out.append((None, pos, [place(pos, "disc", player)] + [remove(t) for t in taken]))
    return out


def status(pieces: list[Piece], mover: int, n: int) -> tuple[str, bool]:
    # J1 joga nas jogadas ímpares: pares capturados = peças postas e já fora do tabuleiro / 2.
    placed = {1: (n + 1) // 2, 2: n // 2}
    pairs = {q: (placed[3 - q] - sum(p.player == 3 - q for p in pieces)) // 2 for q in (1, 2)}
    text = f"Pares capturados — J1: {pairs[1]} · J2: {pairs[2]}"
    b = Builder(pieces)
    if any(best_run(b, p.position, mover) >= 5 for p in pieces if p.player == mover) or pairs[mover] >= 5:
        return f"{text} · Vitória do jogador {mover}", True
    return text, False


GOMOKU = Game(
    id="gomoku",
    name="Gomoku e Quina",
    subtitle="5-em-linha com captura",
    objective=(
        "Alinhar cinco peças (horizontal, vertical ou diagonal) ou capturar "
        "cinco pares de peças adversárias, flanqueando-os."
    ),
    player_goal=None,
    initial_pieces=[],
    moves=build(),
    rules=Rules(plays, status),
)
