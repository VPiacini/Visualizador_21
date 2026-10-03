"""Registro central de jogos. Novo jogo = um módulo em models/games/ + uma entrada aqui."""
from .amazonas import AMAZONAS
from .campanha import CAMPANHA
from .game import Game
from .gomoku import GOMOKU
from .intersecoes import INTERSECOES
from .ligue4 import LIGUE4
from .pahtum import PAHTUM
from .rastros import RASTROS

GAMES: dict[str, Game] = {g.id: g for g in [RASTROS, AMAZONAS, GOMOKU, LIGUE4, PAHTUM, CAMPANHA, INTERSECOES]}


def get_game(game_id: str) -> Game | None:
    return GAMES.get(game_id)


def list_games() -> list[Game]:
    return list(GAMES.values())
