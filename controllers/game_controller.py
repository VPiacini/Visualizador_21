from dataclasses import replace

from werkzeug.exceptions import RequestEntityTooLarge
from flask import Blueprint, abort, jsonify, render_template, request

from models.games.game import Game
from models.games.registry import get_game, list_games
from models.move import build_history
from models.replay import replay

bp = Blueprint("game", __name__)
MAX_UPLOAD = 1_000_000  # bytes


def serialize_game(game: Game) -> dict:
    # manda o histórico inteiro de uma vez, sem 1 request por jogada
    history = build_history(game.initial_pieces, game.moves)
    return {
        "id": game.id,
        "name": game.name,
        "subtitle": game.subtitle,
        "objective": game.objective,
        "playerGoal": game.player_goal,
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


@bp.route("/api/replay", methods=["POST"])
def api_replay():
    request.max_content_length = MAX_UPLOAD
    try:
        body = request.get_json(silent=True)
    except RequestEntityTooLarge:
        return jsonify(error="arquivo maior que 1 MB"), 413
    if not isinstance(body, dict):
        return jsonify(error="o arquivo precisa ser um JSON com game e moves"), 400
    game = get_game(body.get("game"))
    if game is None:
        return jsonify(error=f"jogo desconhecido: {body.get('game')!r}"), 404
    try:
        return jsonify(serialize_game(replace(replay(game, body.get("moves")), subtitle="Partida carregada")))
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        return jsonify(error=str(e) or "partida inválida"), 400
