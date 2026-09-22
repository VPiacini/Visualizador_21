"""
Tabuleiro 8x8 — apenas coordenadas, nenhuma regra de jogo aqui.
Casas nomeadas como a1..h8 (a1 = canto inferior esquerdo).
"""
FILES = ["a", "b", "c", "d", "e", "f", "g", "h"]
RANKS = [1, 2, 3, 4, 5, 6, 7, 8]


def square_to_coord(square: str) -> tuple[int, int]:
    """'d4' -> (col=3, row=3), com col/row começando em 0."""
    col = FILES.index(square[0])
    row = int(square[1:]) - 1
    return col, row


def all_squares() -> list[str]:
    return [f"{f}{r}" for r in RANKS for f in FILES]
