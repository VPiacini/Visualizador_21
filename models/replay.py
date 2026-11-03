"""Reproduz uma partida real (lista de cliques por lance) com as regras do jogo."""
from dataclasses import replace

from .games.game import Game, History
from .move import Move
from .piece import Piece
from .play import play

MAX_LANCES = 500
MAX_COMENTARIO = 2000


def replay(game: Game, entries: list[dict]) -> Game:
    """`entries`: [{"path": ["d4"], "comment": "opcional"}, ...]. ValueError se algum lance for ilegal."""
    if game.rules is None:
        raise ValueError("este jogo não aceita partidas carregadas")
    if not isinstance(entries, list) or len(entries) > MAX_LANCES:
        raise ValueError(f"a partida precisa ser uma lista de até {MAX_LANCES} lances")
    for i, e in enumerate(entries, 1):
        path, comment = e.get("path") if isinstance(e, dict) else None, e.get("comment", "") if isinstance(e, dict) else None
        if not (isinstance(path, list) and path and all(isinstance(q, str) for q in path)):
            raise ValueError(f'lance {i}: "path" deve ser uma lista de casas, como ["d4"]')
        if not isinstance(comment, str) or len(comment) > MAX_COMENTARIO:
            raise ValueError(f'lance {i}: "comment" deve ser texto de até {MAX_COMENTARIO} caracteres')
    pieces, player, history, moves = game.initial_pieces, 1, History.compact([]), []
    for i, e in enumerate(entries, 1):
        path = tuple(e["path"])
        state = play(game, pieces, player, history, path)
        if state is None:
            raise ValueError(f"lance {i} ilegal para o jogador {player}: {list(path)}")
        moves.append(Move(player, state["actions"], e.get("comment", ""), state["status"]))
        pieces = [Piece(**p) for p in state["pieces"]]
        player, history = state["player"], History.from_json(state["history"])
    return replace(game, moves=moves)
