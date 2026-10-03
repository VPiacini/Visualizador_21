from ..piece import Piece
from .game import Game
from .helpers import Builder, best_run, place, sq

# (linha, gravidade): "E" empilha a partir da coluna a, "D" a partir da coluna h.
SCRIPT: list[tuple[int, str]] = [
    (3, "D"), (2, "D"), (8, "E"), (6, "E"), (4, "D"), (4, "E"), (8, "D"), (8, "D"),
    (3, "D"), (8, "D"), (5, "D"), (6, "D"), (8, "E"), (5, "E"), (3, "E"), (7, "E"),
]

LADO = {"E": "esquerda", "D": "direita"}


def target(b: Builder, rank: int, side: str) -> str | None:
    cols = range(8) if side == "E" else range(7, -1, -1)
    return next((s for c in cols if b.empty(s := sq(c, rank - 1))), None)


def build() -> list:
    b = Builder([])
    for i, (rank, side) in enumerate(SCRIPT):
        player = 1 if i % 2 == 0 else 2
        pos = target(b, rank, side)
        assert pos, f"linha {rank} cheia"
        b.add(player, [place(pos, "disc", player)], "")
        run = best_run(b, pos, player)
        win = run >= 4
        assert not win or i == len(SCRIPT) - 1, "partida deveria ter acabado"
        comment = (
            f"Jogador {player} coloca na linha {rank} pela gravidade da "
            f"{LADO[side]}; a peça para em {pos}."
        )
        if win:
            comment += " Forma 4 em linha e vence a partida."
        elif run == 3:
            comment += " Cria uma sequência de 3: o adversário precisa reagir."
        b.moves[-1].comment = comment
        if win:
            b.moves[-1].status = f"Vitória do jogador {player}"
    return b.moves


LIGUE4 = Game(
    id="ligue4",
    name="Ligue 4",
    subtitle="Sob o efeito da gravidade",
    objective=(
        "Alinhar quatro peças em qualquer direção. Aqui há duas gravidades: "
        "as peças se empilham a partir das colunas a e h."
    ),
    player_goal=None,
    initial_pieces=[],
    moves=build(),
)
