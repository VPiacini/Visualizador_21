"""
Move = {player, actions: [...], comment}. Cada action:
  {"type": "move",   "pieceId": ..., "to": ...}
  {"type": "place",  "position": ..., "piece": {"type": ..., "player": ...}}
  {"type": "remove", "position": ...}
"""
from dataclasses import dataclass
from typing import Any

from .piece import Piece


@dataclass
class Move:
    player: int
    actions: list[dict[str, Any]]
    comment: str = ""

    def move_action(self) -> dict[str, Any] | None:
        return next((a for a in self.actions if a["type"] == "move"), None)


def apply_action(pieces: list[Piece], action: dict[str, Any]) -> list[Piece]:
    kind = action["type"]

    if kind == "move":
        return [
            Piece(p.id, p.type, action["to"], p.player)
            if p.id == action["pieceId"]
            else p
            for p in pieces
        ]

    if kind == "place":
        info = action["piece"]
        new_id = action.get("id") or f'{info["type"]}-{action["position"]}'
        new_piece = Piece(
            id=new_id,
            type=info["type"],
            position=action["position"],
            player=info.get("player"),
        )
        return pieces + [new_piece]

    if kind == "remove":
        return [p for p in pieces if p.position != action["position"]]

    return pieces


def apply_move(pieces: list[Piece], move: Move) -> list[Piece]:
    for action in move.actions:
        pieces = apply_action(pieces, action)
    return pieces


def build_history(
    initial_pieces: list[Piece], moves: list[Move]
) -> list[list[Piece]]:
    history = [initial_pieces]
    current = initial_pieces
    for move in moves:
        current = apply_move(current, move)
        history.append(current)
    return history
