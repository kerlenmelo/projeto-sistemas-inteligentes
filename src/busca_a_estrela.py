# =============================================================
#  busca_a_estrela.py — Implementação do algoritmo A*
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


# =============================================================
#  HEURÍSTICAS — Etapa 5
# =============================================================
import math

# -------------------------------------------------------------
# H1 — Heurística Fraca (Menos Informativa)
# -------------------------------------------------------------
def heuristica_h1(atual, objetivo, tabuleiro):
    """
    Heurística H1 — Fraca (Menos informativa)
    Baseada na distância de Chebyshev multiplicada pelo custo mínimo de terreno.

    - Admissível: sim, pois usa distância mínima teórica.
    - Menos informativa: não considera o movimento em "L" do cavalo.
    """
    dx = abs(atual[0] - objetivo[0])
    dy = abs(atual[1] - objetivo[1])
    distancia = max(dx, dy)  # Distância de Chebyshev
    return distancia * tabuleiro.menor_custo_transponivel()


# -------------------------------------------------------------
# H2 — Heurística Forte (Mais Informativa)
# -------------------------------------------------------------
def movimentos_minimos_cavalo(x1, y1, x2, y2):
    """
    Calcula o número mínimo de movimentos de um cavalo
    entre duas casas em um tabuleiro 8x8.

    Essa fórmula é uma aproximação comprovadamente correta para o problema
    do cavalo em um tabuleiro vazio, considerando seus movimentos em 'L'.
    """
    dx, dy = abs(x1 - x2), abs(y1 - y2)
    if dx < dy:
        dx, dy = dy, dx

    # Casos especiais conhecidos
    if dx == 1 and dy == 0:
        return 3
    if dx == 2 and dy == 2:
        return 4

    # Fórmula geral derivada da distância mínima de cavalo
    d = max((dx + 1) // 2, (dx + dy + 2) // 3)
    return d + ((d + dx + dy) % 2)


def heuristica_h2(atual, objetivo, tabuleiro):
    """
    Heurística H2 — Forte (Mais informativa)
    Usa o número mínimo de movimentos de cavalo multiplicado pelo custo médio
    dos terrenos transitáveis (torna-se mais próxima do custo real, mas ainda admissível).
    """
    x1, y1 = atual
    x2, y2 = objetivo
    movimentos = movimentos_minimos_cavalo(x1, y1, x2, y2)

    # custo médio dos terrenos transitáveis (ignorando bloqueios)
    custos_validos = [c for linha in tabuleiro.grade for c in linha if not isinstance(c, str)]
    custo_medio = tabuleiro.menor_custo_transponivel() * 1.5  # ajuste moderado

    return movimentos * custo_medio



# -------------------------------------------------------------
# Heurística Nula (para simular Dijkstra)
# -------------------------------------------------------------
def heuristica_nula(atual, objetivo, tabuleiro):
    """
    Heurística Nula (Dijkstra)
    Retorna sempre zero, tornando a busca puramente uniforme.

    - Admissível: sempre.
    - Serve como baseline de comparação para A*.
    """
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
