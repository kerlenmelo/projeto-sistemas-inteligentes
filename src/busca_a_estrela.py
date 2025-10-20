# =============================================================
#  busca_a_estrela.py — Implementação do algoritmo A* (Etapa 5)
# =============================================================

from __future__ import annotations
import heapq
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import deque
from src.tabuleiro import Tabuleiro, Coordenada
from src.cavalo import Cavalo


# -------------------------------------------------------------
# Estrutura de um nó na busca
# -------------------------------------------------------------
@dataclass(order=True)
class No:
    f: float
    posicao: Coordenada = field(compare=False)
    g: float = field(compare=False)
    h: float = field(compare=False)
    pai: Optional[Coordenada] = field(compare=False, default=None)


# -------------------------------------------------------------
# HEURÍSTICAS — Etapa 5
# -------------------------------------------------------------
def heuristica_h1(atual: Coordenada, objetivo: Coordenada, tabuleiro: Tabuleiro) -> float:
    """
    H₁: Heurística simples (distância geométrica × menor custo de terreno).
    Usa distância de Chebyshev (movimentos em grade) multiplicada
    pelo menor custo transponível do tabuleiro.
    """
    dx = abs(atual[0] - objetivo[0])
    dy = abs(atual[1] - objetivo[1])
    distancia = max(dx, dy)
    menor_custo = tabuleiro.menor_custo_transponivel()
    return distancia * menor_custo


def movimentos_minimos_cavalo(inicio: Coordenada, objetivo: Coordenada) -> int:
    """
    Calcula o número mínimo de movimentos do cavalo entre duas posições.
    Usa BFS (busca em largura) pura.
    """
    if inicio == objetivo:
        return 0

    movimentos = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                  (-2, -1), (-1, -2), (1, -2), (2, -1)]

    visitados = {inicio}
    fila = deque([(inicio, 0)])

    while fila:
        (x, y), dist = fila.popleft()
        for dx, dy in movimentos:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) not in visitados:
                if (nx, ny) == objetivo:
                    return dist + 1
                visitados.add((nx, ny))
                fila.append(((nx, ny), dist + 1))

    return 8  # valor máximo possível de movimentos (backup)


def heuristica_h2(atual: Coordenada, objetivo: Coordenada, tabuleiro: Tabuleiro) -> float:
    """
    H₂: Heurística informada (mínimo de movimentos reais do cavalo × menor custo).
    É mais forte e eficiente que H₁, mas ainda admissível.
    """
    menor_custo = tabuleiro.menor_custo_transponivel()
    min_movimentos = movimentos_minimos_cavalo(atual, objetivo)
    return min_movimentos * menor_custo


def heuristica_nula(a: Coordenada, b: Coordenada, tabuleiro: Tabuleiro | None = None) -> float:
    """Retorna 0 (usada para simular Dijkstra)."""
    return 0.0


# -------------------------------------------------------------
# Algoritmo A* com escolha de heurística
# -------------------------------------------------------------
def busca_a_estrela(tabuleiro: Tabuleiro,
                    inicio: Coordenada,
                    objetivo: Coordenada,
                    tipo_heuristica: str = "h1") -> Tuple[List[Coordenada], float]:
    """
    Executa o algoritmo A* no tabuleiro com a heurística selecionada.
    Parâmetro tipo_heuristica pode ser: "h1", "h2" ou "nula".
    Retorna (caminho, custo_total).
    """
    heuristicas = {
        "h1": heuristica_h1,
        "h2": heuristica_h2,
        "nula": heuristica_nula
    }
    func_heuristica = heuristicas.get(tipo_heuristica, heuristica_h1)

    fila_aberta: List[No] = []
    heapq.heappush(fila_aberta, No(0, inicio, 0, 0, None))

    custo_g: Dict[Coordenada, float] = {inicio: 0}
    pais: Dict[Coordenada, Optional[Coordenada]] = {inicio: None}
    visitados: set[Coordenada] = set()

    while fila_aberta:
        atual = heapq.heappop(fila_aberta)
        pos = atual.posicao

        # chegou ao objetivo
        if pos == objetivo:
            caminho = reconstruir_caminho(pais, pos)
            return caminho, atual.g

        if pos in visitados:
            continue
        visitados.add(pos)

        cavalo = Cavalo(pos)
        for viz in cavalo.movimentos_possiveis(tabuleiro):
            if tabuleiro.bloqueado(viz):
                continue

            novo_custo = atual.g + tabuleiro.custo(viz)
            if viz not in custo_g or novo_custo < custo_g[viz]:
                custo_g[viz] = novo_custo
                h = func_heuristica(viz, objetivo, tabuleiro)
                f = novo_custo + h
                heapq.heappush(fila_aberta, No(f, viz, novo_custo, h, pos))
                pais[viz] = pos

    return [], float("inf")


# -------------------------------------------------------------
# Reconstrução do caminho
# -------------------------------------------------------------
def reconstruir_caminho(pais: Dict[Coordenada, Optional[Coordenada]],
                        destino: Coordenada) -> List[Coordenada]:
    """Reconstrói o caminho de trás pra frente a partir do dicionário de pais."""
    caminho: List[Coordenada] = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = pais.get(atual)
    caminho.reverse()
    return caminho
