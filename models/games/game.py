"""
Jogo = configuração inicial + sequência de jogadas + comentários.
Jogos jogáveis também trazem `rules`.
"""
from dataclasses import dataclass
from typing import Callable

from ..move import Move
from ..piece import Piece, position_key

# (caminho de cliques, ações): 1 casa = colocar, 2 = mover, mais = flecha ou salto em cadeia.
Play = tuple[tuple[str, ...], list[dict]]


@dataclass
class History:
    """Posições anteriores à atual. `full` guarda todas; `compact` só n, last e seen."""

    n: int  # jogadas feitas
    last: list[Piece] | None  # posição imediatamente anterior
    seen: frozenset[str]  # position_key de todas as posições anteriores
    positions: list[list[Piece]] | None = None  # só no modo full

    @classmethod
    def compact(cls, positions: list[list[Piece]]) -> "History":
        return cls(
            len(positions),
            positions[-1] if positions else None,
            frozenset(position_key(p) for p in positions),
        )

    @classmethod
    def full(cls, positions: list[list[Piece]]) -> "History":
        h = cls.compact(positions)
        h.positions = list(positions)
        return h

    def push(self, pieces: list[Piece]) -> "History":
        seen = self.seen | {position_key(pieces)}
        positions = None if self.positions is None else self.positions + [pieces]
        return History(self.n + 1, pieces, seen, positions)

    def to_json(self) -> dict:
        if self.positions is not None:
            return {"positions": [[p.to_dict() for p in pos] for pos in self.positions]}
        return {
            "n": self.n,
            "last": None if self.last is None else [p.to_dict() for p in self.last],
            "seen": sorted(self.seen),
        }

    @classmethod
    def from_json(cls, d: dict) -> "History":
        try:
            if "positions" in d:
                return cls.full([[Piece(**p) for p in pos] for pos in d["positions"]])
            last = None if d["last"] is None else [Piece(**p) for p in d["last"]]
            seen = frozenset(str(k) for k in d["seen"])
            n = int(d["n"])
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            raise ValueError("histórico inválido") from e
        if n < 0:
            raise ValueError("histórico inválido")
        return cls(n, last, seen)


@dataclass
class Rules:
    # (peças, jogador, histórico anterior às peças) -> jogadas legais
    plays: Callable[[list[Piece], int, History], list[Play]]
    # (peças após a jogada, quem jogou, histórico anterior às peças) -> (texto de status, partida acabou)
    status: Callable[[list[Piece], int, History], tuple[str, bool]]


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
