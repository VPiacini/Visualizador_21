"""Peça genérica do tabuleiro: id estável (usado pelas animações), tipo, casa e dono."""
import hashlib
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


def position_key(pieces: list[Piece]) -> str:
    """Identificador curto de uma posição, independente da ordem das peças."""
    flat = sorted((p.position, p.type, p.player or 0) for p in pieces)
    return hashlib.blake2b(repr(flat).encode(), digest_size=8).hexdigest()
