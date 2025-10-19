from enum import Enum

# ---------------------------------------------------------
# 1. Tipos e limites básicos
# ---------------------------------------------------------

Coordenada = tuple[int, int] # Representa uma coordenada no tabuleiro como (linha, coluna)

def dentro_dos_limites(coord: Coordenada)-> bool:
    """Verifica se a coordenada está dentro dos limites do tabuleiro."""
    linha, coluna = coord
    return 0 <= linha < 8 and 0 <= coluna < 8


# ---------------------------------------------------------
# 2. Definir tipos de terreno e custos
# ---------------------------------------------------------

class Terreno(str, Enum):
    ESTRADA  = "estrada"
    TERRA    = "terra"
    LAMA     = "lama"
    BARREIRA = "barreira"   # intransponível

DEFAULT_COSTS = {
    Terreno.ESTRADA: 0.5,
    Terreno.TERRA:   1.0,
    Terreno.LAMA:    5.0,
    Terreno.BARREIRA: float("inf")  # barreira = custo infinito
}