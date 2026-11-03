"""Utilidades comuns aos jogos: coordenadas, construtores de ação e o Builder.

Cada jogo calcula as consequências das jogadas (capturas, viradas...) com as
suas próprias regras e usa o Builder para montar a partida validando cada lance.
"""
from ..board import FILES
from ..move import Move, apply_move
from ..piece import Piece

DIRS4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIRS8 = DIRS4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]
LINES4 = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 4 eixos (sem repetir sentido)


def sq(col: int, row: int) -> str | None:
    return f"{FILES[col]}{row + 1}" if 0 <= col < 8 and 0 <= row < 8 else None


def xy(square: str) -> tuple[int, int]:
    return FILES.index(square[0]), int(square[1:]) - 1


def step(square: str, d: tuple[int, int], n: int = 1) -> str | None:
    c, r = xy(square)
    return sq(c + d[0] * n, r + d[1] * n)


def move(piece_id: str, to: str) -> dict:
    return {"type": "move", "pieceId": piece_id, "to": to}


def place(pos: str, ptype: str, player: int | None = None, pid: str | None = None) -> dict:
    a = {"type": "place", "position": pos, "piece": {"type": ptype}}
    if player is not None:
        a["piece"]["player"] = player
    if pid:
        a["id"] = pid
    return a


def remove(pos: str) -> dict:
    return {"type": "remove", "position": pos}


def flip(pos: str, player: int) -> dict:
    return {"type": "flip", "position": pos, "player": player}


class Builder:
    """Acumula as jogadas aplicando-as ao tabuleiro, para consultar o estado atual."""

    def __init__(self, initial: list[Piece]):
        self.initial = list(initial)
        self.pieces = list(initial)
        self.moves: list[Move] = []

    def at(self, pos: str) -> Piece | None:
        return next((p for p in self.pieces if p.position == pos), None)

    def owner(self, pos: str) -> int | None:
        p = self.at(pos)
        return p.player if p else None

    def empty(self, pos: str | None) -> bool:
        return pos is not None and self.at(pos) is None

    def add(self, player: int, actions: list[dict], comment: str, status: str = "") -> None:
        m = Move(player=player, actions=actions, comment=comment, status=status)
        self.pieces = apply_move(self.pieces, m)
        self.moves.append(m)


def run_length(
    b: Builder, pos: str, player: int, d: tuple[int, int], types: tuple[str, ...] | None = None
) -> int:
    """Quantas peças de `player` (e `types`, se dado) estão alinhadas em `pos` no eixo d."""
    def mine(s):
        p = b.at(s) if s else None
        return bool(p and p.player == player and (types is None or p.type in types))

    n = 1
    for sign in (1, -1):
        k = 1
        while True:
            nxt = step(pos, (d[0] * sign, d[1] * sign), k)
            if not mine(nxt):
                break
            n += 1
            k += 1
    return n


def best_run(b: Builder, pos: str, player: int, types: tuple[str, ...] | None = None) -> int:
    return max(run_length(b, pos, player, d, types) for d in LINES4)
