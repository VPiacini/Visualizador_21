"""
Jogo = configuração inicial + sequência de jogadas + comentários.
"""
from dataclasses import dataclass

from ..move import Move
from ..piece import Piece


@dataclass
class Game:
    id: str
    name: str
    subtitle: str
    objective: str
    player_goal: dict[int, str] | None
    initial_pieces: list[Piece]
    moves: list[Move]
