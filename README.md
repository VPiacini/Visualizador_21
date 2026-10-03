# Visualizador — 21 Jogos no Mesmo Tabuleiro

Visualizador genérico de partidas anotadas em tabuleiro 8x8, escrito em
Python com Flask, seguindo arquitetura MVC.

Aplicação publicada em https://visualizador-21.onrender.com

## Estrutura (MVC)

```
visualizador_jogos/
├── app.py                        # cria a app Flask
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
│   └── game_controller.py        # rotas Flask
├── templates/
│   └── index.html                # estrutura da página (Jinja2)
└── static/
    ├── css/style.css             # aparência
    └── js/board.js               # renderização do tabuleiro e navegação
```

- **Model**: dados e motor genérico do tabuleiro 8x8.
- **Controller**: traduz requisições HTTP em chamadas ao Model e decide o que
  devolver (página HTML ou JSON).
- **View**: template Jinja2 + CSS + JS. O JS busca os dados já processados via
  `/api/games/<id>` e cuida de desenhar o tabuleiro e navegar entre jogadas.

## Jogos incluídos

Os 21 jogos do livro (capítulos 2 a 22): Rastros, Amazonas, Konane, Gomoku e Quina,
Ligue 4, Pah Tum, Dai Hasami Shogi, Campanha, Interseções, Halma, Batalha dos Peões,
Gogol, Dama Turca, Hasami Shogi, Mak-Yek, Ming Mang, Othello, Linhas de Ação,
Se Liga, Epaminondas e Sz'kwa. Cada partida é gerada a partir de uma lista
de lances (`SCRIPT`) validada pelas regras do próprio módulo: lance ilegal
levanta `AssertionError` ao importar. Posições iniciais de Mak-Yek e Ming Mang
são adaptadas (a figura do livro não está no texto) — marcadas com `ponytail:`.

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Acesse http://127.0.0.1:5000

## Testes

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Adicionando um novo jogo do livro

1. Criar `models/games/<jogo>.py` com um `Game` (posição inicial + `moves` com
   comentários), seguindo `rastros.py` ou `amazonas.py` como exemplo.
2. Adicionar o jogo à lista em `models/games/registry.py`.
3. Escrever o validador de regra correspondente em `tests/test_game_data.py`.
