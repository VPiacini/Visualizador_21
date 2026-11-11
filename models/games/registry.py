"""Registro central de jogos, na ordem dos capítulos do livro.

Novo jogo = um módulo em models/games/ + uma entrada aqui + a partida do livro em
partidas/livro/<id>.json. Ao importar, cada partida do livro é reproduzida com as
regras do jogo (lance ilegal levanta ValueError) e os JOGAVEIS primeiros jogos
ficam liberados no modo Jogar (`playable`).
"""
import json
from dataclasses import replace
from pathlib import Path

from ..replay import replay
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

LIVRO = Path(__file__).resolve().parents[2] / "partidas" / "livro"


def com_partida(g: Game) -> Game:
    entries = json.loads((LIVRO / f"{g.id}.json").read_text(encoding="utf8"))["moves"]
    return replay(g, entries)


# quantos jogos, a partir do primeiro do livro, já podem ser jogados (modo Jogar);
# para liberar mais, basta aumentar
JOGAVEIS = 4

# mesma ordem dos capítulos do livro (2 a 22)
GAMES: dict[str, Game] = {
    g.id: replace(g, playable=i < JOGAVEIS)
    for i, g in enumerate(map(com_partida, [
        RASTROS, AMAZONAS, KONANE, GOMOKU, LIGUE4, PAHTUM, DAIHASAMI, CAMPANHA,
        INTERSECOES, HALMA, PEOES, GOGOL, DAMATURCA, HASAMI, MAKYEK, MINGMANG,
        OTHELLO, LINHASACAO, SELIGA, EPAMINONDAS, SZKWA,
    ]))
}


def get_game(game_id: str) -> Game | None:
    return GAMES.get(game_id)


def list_games() -> list[Game]:
    return list(GAMES.values())
