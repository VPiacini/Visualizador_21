# Visualizador — 21 Jogos no Mesmo Tabuleiro

Visualizador genérico de partidas anotadas em tabuleiro 8x8, escrito em
Python com Flask, seguindo arquitetura MVC.

## Estrutura (MVC)

```
visualizador_jogos/
├── app.py                        # cria e configura a aplicação Flask
├── models/                       # MODEL — regras e dados, sem nenhuma dependência do Flask
│   ├── piece.py                  #   peça genérica {id, type, position, player}
│   ├── board.py                  #   coordenadas do tabuleiro 8x8
│   ├── move.py                   #   estrutura de jogada + motor genérico (apply_move/build_history)
│   └── games/
│       ├── game.py               #   dataclass Game = config inicial + moves + comentários
│       ├── rastros.py            #   dados do jogo Rastros (cap. 2 do livro)
│       ├── amazonas.py           #   dados do jogo Amazonas (cap. 3 do livro)
│       └── registry.py           #   registro central: adicionar um jogo novo = 1 arquivo aqui
├── controllers/
│   └── game_controller.py        # CONTROLLER — rotas Flask, único lugar que conhece o Flask
├── templates/
│   └── index.html                # VIEW (estrutura da página, Jinja2)
└── static/
    ├── css/style.css             # VIEW (aparência)
    └── js/board.js                # VIEW (renderização do tabuleiro e navegação)
```

- **Model**: Base de dados e motor genérico de tabuleiro 8x8.
- **Controller**: traduz requisições HTTP em chamadas ao Model e decide o que
  devolver (página HTML ou JSON).
- **View**: template Jinja2 + CSS + JS. O JS busca os dados já processados via
  `/api/games/<id>` e cuida apenas de desenhar o tabuleiro e navegar entre jogadas.

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Acesse http://127.0.0.1:5000

## Adicionando um novo jogo do livro

1. Criar `models/games/<jogo>.py` com um `Game` (posição inicial + `moves` com
   comentários), seguindo `rastros.py` ou `amazonas.py` como exemplo.
2. Adicionar o jogo à lista em `models/games/registry.py`.

