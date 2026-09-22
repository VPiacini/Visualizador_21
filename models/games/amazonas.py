from ..move import Move
from ..piece import Piece
from .game import Game

AMAZONAS = Game(
    id="amazonas",
    name="Amazonas",
    subtitle="Criando bloqueios no tabuleiro",
    objective=(
        "Deixar o adversário sem nenhuma jogada válida: cada lance move uma "
        "peça em linha reta e depois lança, a partir dela, uma flecha "
        "(bloqueio) também em linha reta."
    ),
    player_goal=None,
    initial_pieces=[
        Piece(id="p1-a3", type="amazon", position="a3", player=1),
        Piece(id="p1-c1", type="amazon", position="c1", player=1),
        Piece(id="p1-f1", type="amazon", position="f1", player=1),
        Piece(id="p1-h3", type="amazon", position="h3", player=1),
        Piece(id="p2-a6", type="amazon", position="a6", player=2),
        Piece(id="p2-c8", type="amazon", position="c8", player=2),
        Piece(id="p2-f8", type="amazon", position="f8", player=2),
        Piece(id="p2-h6", type="amazon", position="h6", player=2),
    ],
    moves=[
        Move(
            player=1,
            actions=[
                {"type": "move", "pieceId": "p1-c1", "to": "c4"},
                {"type": "place", "position": "h4", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 1 move a amazona de c1 para c4 e, a partir dela, "
                "lança uma flecha até h4."
            ),
        ),
        Move(
            player=2,
            actions=[
                {"type": "move", "pieceId": "p2-h6", "to": "h5"},
                {"type": "place", "position": "d5", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 2 desce a amazona de h6 para h5 e atira até d5, "
                "disputando o centro do tabuleiro."
            ),
        ),
        Move(
            player=1,
            actions=[
                {"type": "move", "pieceId": "p1-f1", "to": "f4"},
                {"type": "place", "position": "f6", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 1 avança f1 até f4 e lança uma flecha até f6, "
                "próxima das peças adversárias."
            ),
        ),
        Move(
            player=2,
            actions=[
                {"type": "move", "pieceId": "p2-c8", "to": "c6"},
                {"type": "place", "position": "e6", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 2 desce c8 até c6 e bloqueia e6, ampliando o cerco "
                "perto do canto direito."
            ),
        ),
    ],
)
