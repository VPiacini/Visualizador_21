"""
Controller — única camada que conhece o Flask. Traduz requisições HTTP
em chamadas ao Model e decide o que devolver (página renderizada ou JSON).
"""
from flask import Blueprint, abort, jsonify, render_template

from models.games.game import Game
from models.games.registry import get_game, list_games
from models.move import build_history

bp = Blueprint("game", __name__)


def serialize_game(game: Game) -> dict:
    """Monta o pacote de dados que a View (JS no navegador) precisa para
    reproduzir a partida inteira sem novas requisições por jogada."""
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
