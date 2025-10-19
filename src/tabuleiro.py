# =============================================================
#  board.py — Estrutura do tabuleiro, terrenos e custos
# =============================================================

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Dict

# -------------------------------------------------------------
# Tipos e limites básicos
# -------------------------------------------------------------
Coordenada = Tuple[int, int]  # (linha, coluna)

def dentro_dos_limites(pos: Coordenada) -> bool:
    """Retorna True se (linha, coluna) estiver dentro do tabuleiro 8x8."""
    linha, coluna = pos
    return 0 <= linha < 8 and 0 <= coluna < 8

# -------------------------------------------------------------
# Tipos de terreno e custos
# -------------------------------------------------------------
class Terreno(str, Enum):
    ESTRADA  = "estrada"
    TERRA    = "terra"
    LAMA     = "lama"
    BARREIRA = "barreira"  # intransponível

# custo para ENTRAR em uma casa
CUSTOS_PADRAO: Dict[Terreno, float] = {
    Terreno.ESTRADA: 0.5,
    Terreno.TERRA:   1.0,
    Terreno.LAMA:    5.0,
    Terreno.BARREIRA: float("inf"),  # bloqueio
}

# -------------------------------------------------------------
# Classe principal do tabuleiro
# -------------------------------------------------------------
@dataclass
class Tabuleiro:
    grade: List[List[Terreno]]
    custos: Dict[Terreno, float]

    # ---------- Criação do tabuleiro ----------
    @staticmethod
    def vazio(preencher: Terreno = Terreno.TERRA) -> "Tabuleiro":
        """Cria um tabuleiro 8x8 todo preenchido com o mesmo terreno."""
        grade = [[preencher for _ in range(8)] for _ in range(8)]
        return Tabuleiro(grade, dict(CUSTOS_PADRAO))

    @staticmethod
    def carregar_de_json(dados: dict) -> "Tabuleiro":
        """Cria um tabuleiro a partir de um dicionário (carregado de JSON)."""
        # custos (usa padrão se não vierem no arquivo)
        custos = dict(CUSTOS_PADRAO)
        for k, v in (dados.get("costs") or {}).items():
            custos[Terreno(k)] = float(v)

        # grade 8x8
        grade_bruta = dados["grid"]
        if len(grade_bruta) != 8 or any(len(linha) != 8 for linha in grade_bruta):
            raise ValueError("A grade deve ser 8x8")
        grade = [[Terreno(celula) for celula in linha] for linha in grade_bruta]
        return Tabuleiro(grade, custos)

    # ---------- Consultas básicas ----------
    def tipo_terreno(self, pos: Coordenada) -> Terreno:
        """Retorna o tipo de terreno da casa informada."""
        linha, coluna = pos
        return self.grade[linha][coluna]

    def definir_terreno(self, pos: Coordenada, tipo: Terreno) -> None:
        """Altera o tipo de terreno da casa informada."""
        linha, coluna = pos
        self.grade[linha][coluna] = tipo

    def custo(self, pos: Coordenada) -> float:
        """Retorna o custo para ENTRAR na casa informada."""
        return float(self.custos[self.tipo_terreno(pos)])

    def bloqueado(self, pos: Coordenada) -> bool:
        """Retorna True se a casa for uma barreira."""
        return self.custo(pos) == float("inf")

    def menor_custo_transponivel(self) -> float:
        """Retorna o menor custo entre terrenos que não são barreira."""
        return min(v for k, v in self.custos.items() if k != Terreno.BARREIRA)

    # ---------- Prévia para Etapa 3 ----------
    MOVIMENTOS_CAVALO = [
        (-2, -1), (-2, 1),
        (-1, -2), (-1, 2),
        (1, -2),  (1, 2),
        (2, -1),  (2, 1),
    ]

    def vizinhos_cavalo(self, pos: Coordenada) -> List[Coordenada]:
        """Retorna os movimentos válidos do cavalo (já checa bordas e barreiras)."""
        linha, coluna = pos
        vizinhos = []
        for dl, dc in self.MOVIMENTOS_CAVALO:
            destino = (linha + dl, coluna + dc)
            if dentro_dos_limites(destino) and not self.bloqueado(destino):
                vizinhos.append(destino)
        return vizinhos
