"""
Peça genérica do tabuleiro.

O mesmo formato serve para qualquer um dos 21 jogos: uma peça neutra
(como o marcador do Rastros), peças com dono (como as amazonas), ou
peças de bloqueio criadas durante a partida.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Piece:
    id: str
    type: str
    position: str
    player: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "position": self.position,
            "player": self.player,
        }
