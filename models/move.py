"""
Estrutura de jogada + motor genérico de interpretação.

Uma jogada é sempre: { player, actions: [...], comment }
Cada action pode ser:
  {"type": "move",   "pieceId": ..., "to": ...}
  {"type": "place",  "position": ..., "piece": {"type": ..., "player": ...}}
  {"type": "remove", "position": ...}

Isso cobre tanto uma jogada simples (um único "move") quanto uma jogada
complexa com múltiplas alterações no tabuleiro (ex.: mover peça + lançar
bloqueio, como no Rastros e no Amazonas).

Nenhuma regra de jogo é validada aqui — apenas a interpretação mecânica
da jogada sobre a lista de peças.
"""
from dataclasses import dataclass, field
from typing import Any

from .piece import Piece


@dataclass
class Move:
    player: int
    actions: list[dict[str, Any]]
    comment: str = ""

    def move_action(self) -> dict[str, Any] | None:
        """Primeira ação do tipo 'move' desta jogada (útil para destacar
        origem/destino na interface)."""
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
    """Estado do tabuleiro em cada índice, derivado reduzindo a posição
    inicial com moves[0..index-1]. history[0] é a posição inicial."""
    history = [initial_pieces]
    current = initial_pieces
    for move in moves:
        current = apply_move(current, move)
        history.append(current)
    return history
