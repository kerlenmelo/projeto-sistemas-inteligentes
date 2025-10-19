# =============================================================
#  cavalo.py — Movimentos do cavalo no tabuleiro
# =============================================================

from typing import List, Tuple
from src.tabuleiro import Tabuleiro, Coordenada, dentro_dos_limites

# -------------------------------------------------------------
# Classe Cavalo
# -------------------------------------------------------------
class Cavalo:
    """Representa o cavalo e seus movimentos possíveis em um tabuleiro."""
    
    # todos os deslocamentos possíveis em L (linha, coluna)
    MOVIMENTOS: List[Coordenada] = [
        (-2, -1), (-2,  1),
        (-1, -2), (-1,  2),
        ( 1, -2), ( 1,  2),
        ( 2, -1), ( 2,  1)
    ]

    def __init__(self, pos_inicial: Coordenada):
        self.posicao = pos_inicial

    def movimentos_possiveis(self, tabuleiro: Tabuleiro) -> List[Coordenada]:
        """
        Retorna as casas válidas para onde o cavalo pode se mover.
        Ignora casas fora do tabuleiro e casas bloqueadas (barreiras).
        """
        linha, coluna = self.posicao
        destinos: List[Coordenada] = []

        for dl, dc in self.MOVIMENTOS:
            nova_pos = (linha + dl, coluna + dc)
            if dentro_dos_limites(nova_pos) and not tabuleiro.bloqueado(nova_pos):
                destinos.append(nova_pos)

        return destinos
