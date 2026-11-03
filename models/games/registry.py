"""Registro central de jogos. Novo jogo = um módulo em models/games/ + uma entrada aqui."""
from .amazonas import AMAZONAS
from .campanha import CAMPANHA
from .daihasami import DAIHASAMI
from .damaturca import DAMATURCA
from .epaminondas import EPAMINONDAS
from .game import Game
from .gogol import GOGOL
from .gomoku import GOMOKU
from .halma import HALMA
from .hasami import HASAMI
from .intersecoes import INTERSECOES
from .konane import KONANE
from .ligue4 import LIGUE4
from .linhasacao import LINHASACAO
from .makyek import MAKYEK
from .mingmang import MINGMANG
from .othello import OTHELLO
from .pahtum import PAHTUM
from .peoes import PEOES
from .rastros import RASTROS
from .seliga import SELIGA
from .szkwa import SZKWA

# mesma ordem dos capítulos do livro (2 a 22)
GAMES: dict[str, Game] = {
    g.id: g
    for g in [
        RASTROS, AMAZONAS, KONANE, GOMOKU, LIGUE4, PAHTUM, DAIHASAMI, CAMPANHA,
        INTERSECOES, HALMA, PEOES, GOGOL, DAMATURCA, HASAMI, MAKYEK, MINGMANG,
        OTHELLO, LINHASACAO, SELIGA, EPAMINONDAS, SZKWA,
    ]
}


def get_game(game_id: str) -> Game | None:
    return GAMES.get(game_id)


def list_games() -> list[Game]:
    return list(GAMES.values())
