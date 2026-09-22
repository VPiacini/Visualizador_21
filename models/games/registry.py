"""
Registro de jogos disponíveis no visualizador.

Para adicionar um novo jogo do livro: criar um novo módulo em
models/games/<jogo>.py definindo um Game (configuração inicial +
moves + comentários) e incluí-lo na lista GAMES abaixo. Nenhum outro
arquivo do projeto precisa ser alterado — essa é a prova de que o
motor genérico não conhece as regras de nenhum jogo específico.
"""
from .amazonas import AMAZONAS
from .game import Game
from .rastros import RASTROS

GAMES: dict[str, Game] = {g.id: g for g in [RASTROS, AMAZONAS]}


def get_game(game_id: str) -> Game | None:
    return GAMES.get(game_id)


def list_games() -> list[Game]:
    return list(GAMES.values())
