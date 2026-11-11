# Visualizador — 21 Jogos no Mesmo Tabuleiro

Visualizador de partidas anotadas dos 21 jogos do livro *21 Jogos no Mesmo
Tabuleiro*, todos num tabuleiro 8x8. Escrito em Python com Flask, seguindo
arquitetura MVC.

Aplicação publicada em https://visualizador-21.onrender.com

## Estrutura (MVC)

```
visualizador_jogos/
├── app.py                        # cria a app Flask (create_app + app para o gunicorn)
├── LICENSE                       # MIT
├── requirements.txt              # Flask e gunicorn
├── models/                       # regras e dados — sem Flask
│   ├── piece.py                  #   peça genérica {id, type, position, player}
│   ├── board.py                  #   coordenadas do tabuleiro 8x8
│   ├── move.py                   #   jogada + motor genérico (apply_move/build_history)
│   ├── play.py                   #   valida um lance pelas regras e calcula o próximo estado
│   ├── replay.py                 #   reproduz uma partida real (lista de lances) com as regras
│   └── games/
│       ├── game.py               #   Game, Rules (plays/status) e History
│       ├── helpers.py            #   coordenadas, construtores de ação e Builder (consulta ao tabuleiro)
│       ├── <jogo>.py             #   um módulo por jogo (regras e posição inicial)
│       └── registry.py           #   registro dos 21 jogos, na ordem do livro, e JOGAVEIS
├── partidas/                     # dados das partidas, sem código
│   ├── livro/<jogo>.json         #   partida de exemplo de cada jogo do livro
│   └── modelo.json               #   modelo para quem quer mostrar a própria partida
├── controllers/
│   └── game_controller.py        # rotas Flask (página + API JSON)
├── templates/
│   └── index.html                # estrutura da página (Jinja2)
├── static/
│   ├── css/style.css             # aparência
│   └── js/
│       ├── board.js              # tabuleiro, navegação, modo Jogar e partidas enviadas
│       ├── timeline.js           # passos de animação de cada jogada (sem DOM)
│       └── animator.js           # anima as peças (Web Animations API)
└── tests/                        # pytest (só local — ignorado pelo .gitignore)
```

- **Model**: dados, regras de cada jogo e motor genérico do tabuleiro 8x8.
- **Controller**: traduz requisições HTTP em chamadas ao Model e decide o que
  devolver (página HTML ou JSON).
- **View**: template Jinja2 + CSS + JS. O JS não conhece as regras: busca os
  dados já processados via `/api/games/<id>`, desenha o tabuleiro, anima as
  peças e navega entre jogadas. No modo Jogar, cada clique vira um lance que o
  servidor valida.

## Navegação

- ← e → (botões ou setas do teclado) voltam e avançam uma jogada, com animação.
- ⏭ vai para o final e ↻ volta ao início, sem animação.
- ▶ reproduz a partida sozinha, em 0.5x, 1x ou 2x.
- Abaixo do tabuleiro ficam a situação da partida (placar, vez, fim de jogo), a
  notação da jogada (`d4→e5` mover, `+e5` colocar, `×e5` remover, `⟳e5` virar)
  e o comentário do livro.
- A casa de origem e as casas afetadas pela última jogada ficam destacadas.

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

Cada partida do livro é um arquivo `partidas/livro/<jogo>.json` com a lista de
lances (`path` e `comment`). O `registry.py` reproduz cada lista com as regras do
próprio jogo: lance ilegal levanta `ValueError` ao importar. Posições iniciais
de Mak-Yek e Ming Mang são adaptadas (a figura do livro não está no texto) —
marcadas com `ponytail:`.

## Regras

Cada jogo declara `rules=Rules(plays, status)`: `plays(pieces, player, history)`
devolve as jogadas legais como `(caminho, ações)` e `status(pieces, mover, history)`
devolve o texto de situação e se a partida acabou. `History` guarda as posições
anteriores (`n`, `last`, `seen`) para regras como en passant e repetição de posição.
É com essas regras que o servidor valida cada lance das partidas do livro e das
partidas enviadas, resolve passes de vez e detecta o fim da partida.

## Modo Jogar

Rastros, Amazonas, Konane e Gomoku e Quina, os quatro primeiros do livro, têm o
switch **Visualizar / Jogar** no topo; no modo Jogar o fundo fica num verde mais
claro e os controles de reprodução e de partidas somem. Dois jogadores se
alternam no mesmo navegador.

- O lance é montado clicando nas casas em sequência: colocar = 1 clique, mover =
  origem e destino, flecha ou saltos = o caminho inteiro. As casas possíveis
  ficam marcadas; havendo lances mais longos, clicar de novo na última casa
  confirma.
- O servidor valida cada lance, resolve passes de vez e detecta o fim. O
  navegador guarda só o estado atual (`pieces`, `player`, `history`).
- ← desfaz a última jogada e ↻ recomeça. Os lances também são animados.

Os jogos são liberados aos poucos, na ordem do livro: `JOGAVEIS = 4` em
`models/games/registry.py` marca os primeiros como `playable`. Para liberar mais,
basta aumentar esse número (as regras de todos os 21 jogos já existem). Um jogo
não jogável não mostra o switch e responde 404 em `/start` e `/play`.

## Animações

Ao avançar ou voltar uma jogada, as peças deslizam (passando por cada casa de
saltos em cadeia, como no Halma), surgem, somem, viram de cor (Othello) ou são
promovidas. Voltar anima mais rápido. Pular várias jogadas (⏭, ↻) ou trocar de
jogo muda o tabuleiro sem animação.

- `static/js/timeline.js` não toca no DOM: `forwardSteps(peças, jogada)`
  converte as `actions` e o `path` da jogada em grupos de passos (`move`,
  `place`, `remove`, `flip`, `promote`). Passos do mesmo grupo tocam juntos e os
  grupos tocam em sequência. `backwardSteps(de, para)` compara duas posições
  para voltar uma jogada.
- `static/js/animator.js` mantém um elemento por peça (chave `id`) e toca os
  passos com a Web Animations API. Uma nova jogada no meio de outra termina a
  anterior na hora; na reprodução automática a duração se ajusta à velocidade.
- Com `prefers-reduced-motion` ligado no sistema, o tabuleiro muda sem animação.

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
| `GET /api/games/<id>` | jogo completo: `id`, `name`, `subtitle`, `objective`, `playerGoal`, `playable`, `moves` (cada uma com `player`, `comment`, `status`, `actions` e `path`) e `history` (posição inicial + posição após cada jogada); 404 se o id não existir |
| `GET /api/games/<id>/start` | estado inicial do modo Jogar: `pieces`, `player`, `history`, `plays` (caminhos legais); 404 se o jogo não for jogável |
| `POST /api/games/<id>/play` | recebe `{pieces, player, history, path}` e devolve o próximo estado (`pieces`, `player`, `history`, `status`, `over`, `actions`, `plays`); 400 para lance ou estado inválido |
| `POST /api/replay` | recebe `{game, moves: [{path, comment?}]}` e devolve a partida como `GET /api/games/<id>`; 400 com `error` se um lance for ilegal |

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
pytest tests/ -v                         # regras, partidas do livro e API
node --test tests/timeline.test.mjs      # passos de animação (Node 18+)
```

## Visualizando uma partida sua

O formato é o mesmo de `partidas/livro/`. Qualquer um dos 21 jogos pode mostrar uma partida real. Copie
[`partidas/modelo.json`](partidas/modelo.json), troque `game` pelo id do jogo
(`ligue4`, `othello`, `rastros`... os mesmos de `/api/games`) e liste os lances
em ordem. Cada lance é o `path`, a sequência de casas do lance: 1 casa =
colocar, 2 = mover (origem e destino), mais = flecha ou saltos em cadeia. O
jogador 1 começa, os turnos alternam sozinhos e `comment` é opcional.

No site, clique em **Carregar partida** e escolha o arquivo. O servidor valida
cada lance com as regras do jogo e responde 400 com o número do lance ilegal.
Limites: 1 MB por arquivo, 500 lances e 2000 caracteres por comentário. Se o
campo `game` for de outro jogo que o aberto, o site pergunta se deve abrir esse jogo.

Cada jogo mostra os botões **Livro** e **Minha partida** acima do tabuleiro. A
partida enviada fica guardada no `localStorage` do navegador (uma por jogo) e é
revalidada pelo servidor a cada abertura; o **✕** a remove. O servidor não
guarda nada: `POST /api/replay` com o mesmo JSON devolve a partida no formato de
`GET /api/games/<id>`.

## Adicionando um novo jogo

1. Criar `models/games/<jogo>.py` com as regras, a posição inicial e um `Game`
   com `rules=Rules(plays, status)` (veja `othello.py` ou `ligue4.py`).
2. Criar `partidas/livro/<jogo>.json` com a partida de exemplo.
3. Adicionar o jogo à lista em `models/games/registry.py`, na posição do
   capítulo. Ele fica jogável se estiver entre os `JOGAVEIS` primeiros.
4. Opcional: um validador de regra em `tests/test_game_data.py`
   (`GAME_RULE_VALIDATORS`).

## Licença

MIT — veja [LICENSE](LICENSE).
