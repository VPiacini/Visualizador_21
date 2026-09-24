"""Registro central de jogos. Novo jogo = um módulo em models/games/ + uma entrada aqui."""
from .amazonas import AMAZONAS
from .game import Game
from .rastros import RASTROS

GAMES: dict[str, Game] = {g.id: g for g in [RASTROS, AMAZONAS]}


def get_game(game_id: str) -> Game | None:
    return GAMES.get(game_id)


def list_games() -> list[Game]:
    return list(GAMES.values())
