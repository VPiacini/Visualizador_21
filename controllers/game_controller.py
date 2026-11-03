import os
import time

from flask import Blueprint, abort, jsonify, render_template, request

from models.games.game import Game
from models.games.registry import get_game, list_games
from models.games.game import History
from models.move import build_history
from models.piece import Piece
from models.play import play, start

bp = Blueprint("game", __name__)


def serialize_game(game: Game) -> dict:
    # manda o histórico inteiro de uma vez, sem 1 request por jogada
    history = build_history(game.initial_pieces, game.moves)
    return {
        "id": game.id,
        "name": game.name,
        "subtitle": game.subtitle,
        "objective": game.objective,
        "playerGoal": game.player_goal,
        "playable": game.rules is not None,
        "history": [[p.to_dict() for p in state] for state in history],
        "moves": [
            {
                "player": m.player,
                "comment": m.comment,
                "move": m.move_action(),
                "actions": m.actions,
                "status": m.status,
            }
            for m in game.moves
        ],
    }


@bp.route("/")
def index():
    games = list_games()
    return render_template(
        "index.html",
        games=[{"id": g.id, "name": g.name} for g in games],
        default_game=games[0].id,
    )


@bp.route("/api/games")
def api_games():
    return jsonify(
        [{"id": g.id, "name": g.name, "subtitle": g.subtitle} for g in list_games()]
    )


@bp.route("/api/games/<game_id>")
def api_game(game_id: str):
    game = get_game(game_id)
    if game is None:
        abort(404)
    return jsonify(serialize_game(game))


def playable_game(game_id: str) -> Game:
    game = get_game(game_id)
    if game is None or game.rules is None:
        abort(404)
    return game


@bp.route("/api/games/<game_id>/start")
def api_start(game_id: str):
    mode = os.environ.get("HISTORY_MODE", "compact")
    return jsonify(start(playable_game(game_id), mode))


def log_metrics(game_id: str, started: float, resp_bytes: int) -> None:
    try:
        import resource

        peak = f" maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f}MB"
    except ImportError:
        peak = ""
    mode = os.environ.get("HISTORY_MODE", "compact")
    print(
        f"[metrics] {game_id} {mode} req={request.content_length or 0}B "
        f"resp={resp_bytes}B ms={(time.perf_counter() - started) * 1000:.1f}{peak}",
        flush=True,
    )


@bp.route("/api/games/<game_id>/play", methods=["POST"])
def api_play(game_id: str):
    started = time.perf_counter()
    game = playable_game(game_id)
    body = request.get_json(silent=True) or {}
    try:
        pieces = [Piece(**p) for p in body["pieces"]]
        path = tuple(body["path"])
        player = int(body["player"])
        history = History.from_json(body["history"])
        if player not in (1, 2) or not path or not all(isinstance(q, str) for q in path):
            abort(400)
        state = play(game, pieces, player, history, path)
    except (KeyError, TypeError, ValueError, AttributeError, IndexError, StopIteration):
        abort(400)
    if state is None:
        abort(400)
    response = jsonify(state)
    if os.environ.get("METRICS") == "1":
        log_metrics(game_id, started, response.content_length or 0)
    return response
