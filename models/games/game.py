"""
Jogo = configuração inicial + sequência de jogadas + comentários.
Jogos jogáveis também trazem `rules`.
"""
from dataclasses import dataclass
from typing import Callable

from ..move import Move
from ..piece import Piece

# (origem ou None, destino, ações). Origem None = jogada por clique direto no destino.
Play = tuple[str | None, str, list[dict]]


@dataclass
class Rules:
    # (peças, jogador, jogadas já feitas) -> jogadas legais
    plays: Callable[[list[Piece], int, int], list[Play]]
    # (peças, quem jogou, jogadas feitas incluindo esta) -> (texto de status, partida acabou)
    status: Callable[[list[Piece], int, int], tuple[str, bool]]


@dataclass
class Game:
    id: str
    name: str
    subtitle: str
    objective: str
    player_goal: dict[int, str] | None
    initial_pieces: list[Piece]
    moves: list[Move]
    rules: Rules | None = None
