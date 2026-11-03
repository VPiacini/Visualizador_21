"""Motor de partida ao vivo: valida a jogada pedida e calcula o próximo estado."""
from .games.game import Game
from .move import Move, apply_move
from .piece import Piece


def _state(game: Game, pieces: list[Piece], player: int, n: int, status: str, over: bool, actions: list) -> dict:
    plays = [] if over else game.rules.plays(pieces, player, n)
    return {
        "pieces": [p.to_dict() for p in pieces],
        "player": player,
        "n": n,
        "status": status,
        "over": over,
        "actions": actions,
        "plays": [{"from": f, "to": t} for f, t, _ in plays],
    }


def start(game: Game) -> dict:
    return _state(game, game.initial_pieces, 1, 0, "", False, [])


def play(game: Game, pieces: list[Piece], player: int, n: int, frm: str | None, to: str) -> dict | None:
    """Próximo estado após a jogada, ou None se ela é ilegal."""
    rules = game.rules
    match = next((p for p in rules.plays(pieces, player, n) if p[0] == frm and p[1] == to), None)
    if match is None:
        return None
    actions = match[2]
    pieces = apply_move(pieces, Move(player, actions))
    n += 1
    status, over = rules.status(pieces, player, n)
    nxt = 3 - player
    if not over and not rules.plays(pieces, nxt, n):
        if rules.plays(pieces, player, n):
            status += f" · Jogador {nxt} passa a vez"
            nxt = player
        else:
            status, over = status + " · Empate", True
    return _state(game, pieces, nxt, n, status, over, actions)
