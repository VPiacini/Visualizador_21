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
    rules=Rules(plays, status),
)
