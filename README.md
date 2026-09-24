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
│       ├── rastros.py            #   dados do jogo Rastros (cap. 2)
│       ├── amazonas.py           #   dados do jogo Amazonas (cap. 3)
│       └── registry.py           #   registro central de jogos
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
