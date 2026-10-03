# Visualizador — 21 Jogos no Mesmo Tabuleiro

Visualizador de partidas anotadas dos 21 jogos do livro *21 Jogos no Mesmo
Tabuleiro*, todos num tabuleiro 8x8. Escrito em Python com Flask, seguindo
arquitetura MVC.

Aplicação publicada em https://visualizador-21.onrender.com

## Estrutura (MVC)

```
visualizador_jogos/
├── app.py                        # cria a app Flask (create_app + app para o gunicorn)
├── requirements.txt              # Flask e gunicorn
├── models/                       # regras e dados — sem Flask
│   ├── piece.py                  #   peça genérica {id, type, position, player}
│   ├── board.py                  #   coordenadas do tabuleiro 8x8
│   ├── move.py                   #   jogada + motor genérico (apply_move/build_history)
│   └── games/
│       ├── game.py               #   Game = config inicial + moves + comentários
│       ├── helpers.py            #   coordenadas, construtores de ação e Builder
│       ├── <jogo>.py             #   um módulo por jogo (regras + partida de exemplo)
│       └── registry.py           #   registro central dos 21 jogos, na ordem do livro
├── controllers/
│   └── game_controller.py        # rotas Flask (página + API JSON)
├── templates/
│   └── index.html                # estrutura da página (Jinja2)
├── static/
│   ├── css/style.css             # aparência
│   └── js/board.js               # renderização do tabuleiro e navegação
└── tests/                        # pytest (só local — ignorado pelo .gitignore)
```

- **Model**: dados, regras de cada jogo e motor genérico do tabuleiro 8x8.
- **Controller**: traduz requisições HTTP em chamadas ao Model e decide o que
  devolver (página HTML ou JSON).
- **View**: template Jinja2 + CSS + JS. O JS busca os dados já processados via
  `/api/games/<id>` e cuida de desenhar o tabuleiro e navegar entre jogadas
  (botões ou setas ← → do teclado).

## Jogos incluídos

Os 21 jogos do livro, na ordem dos capítulos (2 a 22):

| # | Jogo | # | Jogo | # | Jogo |
|---|------|---|------|---|------|
| 2 | Rastros | 9 | Campanha | 16 | Mak-Yek |
| 3 | Amazonas | 10 | Interseções | 17 | Ming Mang |
| 4 | Konane | 11 | Halma | 18 | Othello |
| 5 | Gomoku e Quina | 12 | Batalha dos Peões | 19 | Linhas de Ação |
| 6 | Ligue 4 | 13 | Gogol | 20 | Se Liga |
| 7 | Pah Tum | 14 | Dama Turca | 21 | Epaminondas |
| 8 | Dai Hasami Shogi | 15 | Hasami Shogi | 22 | Sz'kwa |

Cada partida é gerada a partir de uma lista de lances (`SCRIPT`) validada pelas
regras do próprio módulo: lance ilegal levanta `AssertionError` ao importar.
Posições iniciais de Mak-Yek e Ming Mang são adaptadas (a figura do livro não
está no texto) — marcadas com `ponytail:`.

## Modelo de jogada

Uma jogada (`Move`) tem `player`, `comment`, `status` (texto livre: placar,
situação) e uma lista de `actions`, aplicadas em ordem pelo motor genérico:

| Ação | Campos | Efeito |
|------|--------|--------|
| `move` | `pieceId`, `to` | move uma peça |
| `place` | `position`, `piece: {type, player}` | coloca uma peça nova |
| `remove` | `position` | retira a peça da casa |
| `flip` | `position`, `player` | troca o dono da peça (Othello, capturas por conversão) |

Jogada sem `actions` = passar a vez. Os construtores `move()`, `place()`,
`remove()` e `flip()` de `helpers.py` montam essas ações.

## API

| Rota | Retorno |
|------|---------|
| `GET /` | página do visualizador |
| `GET /api/games` | lista `[{id, name, subtitle}]` |
| `GET /api/games/<id>` | jogo completo: metadados, `moves` e `history` (estado do tabuleiro após cada jogada); 404 se o id não existir |

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Acesse http://127.0.0.1:5000

## Deploy (Render)

Build: `pip install -r requirements.txt` · Start: `gunicorn app:app`

## Testes

A pasta `tests/` fica fora do repositório (`.gitignore`). Localmente:

```bash
pip install pytest
pytest tests/ -v
```

## Adicionando um novo jogo

1. Criar `models/games/<jogo>.py` com as regras, um `SCRIPT` de lances e um
   `Game` montado com o `Builder` de `helpers.py` (veja `othello.py` ou
   `ligue4.py` como exemplo).
2. Adicionar o jogo à lista em `models/games/registry.py`.
3. Opcional: um validador de regra em `tests/test_game_data.py`
   (`GAME_RULE_VALIDATORS`).

## Licença

MIT — veja [LICENSE](LICENSE).
