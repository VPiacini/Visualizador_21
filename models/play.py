"""Valida uma jogada pelas regras do jogo e calcula o próximo estado."""
from .games.game import Game, History
from .move import Move, apply_move
from .piece import Piece


def _state(game: Game, pieces: list[Piece], player: int, history: History, status: str, over: bool, actions: list) -> dict:
    plays = [] if over else game.rules.plays(pieces, player, history)
    return {
        "pieces": [p.to_dict() for p in pieces],
        "player": player,
        "history": history.to_json(),
        "status": status,
        "over": over,
        "actions": actions,
        "plays": [{"path": list(path)} for path, _ in plays],
    }


def start(game: Game) -> dict:
    """Estado inicial do modo Jogar (GET /api/games/<id>/start)."""
    return _state(game, game.initial_pieces, 1, History.compact([]), "", False, [])


def play(game: Game, pieces: list[Piece], player: int, history: History, path: tuple[str, ...]) -> dict | None:
    """Próximo estado após a jogada, ou None se ela é ilegal.

    Se o próximo jogador não tiver lance, ele passa a vez; se nenhum dos dois tiver, é empate.
    """
    rules = game.rules
    match = next((p for p in rules.plays(pieces, player, history) if p[0] == path), None)
    if match is None:
        return None
    actions = match[1]
    after = apply_move(pieces, Move(player, actions))
    history = history.push(pieces)
    status, over = rules.status(after, player, history)
    nxt = 3 - player
    if not over and not rules.plays(after, nxt, history):
        if rules.plays(after, player, history):
            status += f" · Jogador {nxt} passa a vez"
            nxt = player
        else:
            status, over = status + " · Empate", True
    return _state(game, after, nxt, history, status, over, actions)
