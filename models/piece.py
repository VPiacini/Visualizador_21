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
