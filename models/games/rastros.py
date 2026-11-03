from ..move import Move
from ..piece import Piece
from .game import Game, History, Rules
from .helpers import DIRS8, move, place, step

def plays(pieces: list[Piece], player: int, history: History) -> list:
    marker = next(p for p in pieces if p.id == "marker")
    blocked = {p.position for p in pieces if p.type == "block"}
    return [
        ((s,), [move("marker", s), place(marker.position, "block")])
        for d in DIRS8
        if (s := step(marker.position, d)) and s not in blocked
    ]


def status(pieces: list[Piece], mover: int, history: History) -> tuple[str, bool]:
    at = next(p.position for p in pieces if p.id == "marker")
    goal = {"h8": 1, "a1": 2}.get(at)
    if goal:
        return f"Vitória do jogador {goal}", True
    if not plays(pieces, 3 - mover, history):
        return f"Vitória do jogador {mover}", True
    return "", False


RASTROS = Game(
    id="rastros",
    name="Rastros",
    subtitle="Uma única vez em cada lugar",
    objective="Levar a peça até o seu destino, ou bloquear o adversário sem movimentos.",
    player_goal={1: "destino h8", 2: "destino a1"},
    initial_pieces=[Piece(id="marker", type="marker", position="d4", player=None)],
    moves=[
        Move(
            player=1,
            actions=[
                {"type": "move", "pieceId": "marker", "to": "e5"},
                {"type": "place", "position": "d4", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 1 avança na diagonal para e5. A casa d4, de onde "
                "a peça saiu, vira um bloqueio permanente."
            ),
        ),
        Move(
            player=2,
            actions=[
                {"type": "move", "pieceId": "marker", "to": "d6"},
                {"type": "place", "position": "e5", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 2 desloca a peça para d6, deixando e5 bloqueada. "
                "Ele busca aproximar-se de a1, seu destino."
            ),
        ),
        Move(
            player=1,
            actions=[
                {"type": "move", "pieceId": "marker", "to": "e7"},
                {"type": "place", "position": "d6", "piece": {"type": "block"}},
            ],
            comment="Jogador 1 responde subindo para e7, bloqueando d6 atrás de si.",
        ),
        Move(
            player=2,
            actions=[
                {"type": "move", "pieceId": "marker", "to": "f8"},
                {"type": "place", "position": "e7", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 2 move para f8. Note que isso aproxima a peça do "
                "destino do adversário — cada jogada precisa ser pensada "
                "com cuidado."
            ),
        ),
        Move(
            player=1,
            actions=[
                {"type": "move", "pieceId": "marker", "to": "g8"},
                {"type": "place", "position": "f8", "piece": {"type": "block"}},
            ],
            comment="Jogador 1 desliza lateralmente até g8, mantendo-se na linha 8.",
        ),
        Move(
            player=2,
            actions=[
                {"type": "move", "pieceId": "marker", "to": "g7"},
                {"type": "place", "position": "g8", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 2 desce para g7 — não há outra casa vizinha livre "
                "a explorar."
            ),
        ),
        Move(
            player=1,
            actions=[
                {"type": "move", "pieceId": "marker", "to": "h8"},
                {"type": "place", "position": "g7", "piece": {"type": "block"}},
            ],
            comment=(
                "Jogador 1 sobe até h8, seu destino. A partida termina com "
                "a vitória do Jogador 1."
            ),
        ),
    ],
    rules=Rules(plays, status),
)
