"""Registro central de jogos. Novo jogo = um módulo em models/games/ + uma entrada aqui."""
from .amazonas import AMAZONAS
from .campanha import CAMPANHA
from .daihasami import DAIHASAMI
from .game import Game
from .gogol import GOGOL
from .gomoku import GOMOKU
from .intersecoes import INTERSECOES
from .konane import KONANE
from .ligue4 import LIGUE4
from .peoes import PEOES
from .pahtum import PAHTUM
from .rastros import RASTROS

GAMES: dict[str, Game] = {g.id: g for g in [RASTROS, AMAZONAS, GOMOKU, LIGUE4, PAHTUM, CAMPANHA, INTERSECOES, KONANE, DAIHASAMI, PEOES, GOGOL]}


def get_game(game_id: str) -> Game | None:
    return GAMES.get(game_id)


def list_games() -> list[Game]:
    return list(GAMES.values())
