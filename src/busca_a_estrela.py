# =============================================================
#  busca_a_estrela.py — Implementação do algoritmo A*
# =============================================================

from __future__ import annotations
import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
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
# Função heurística — (Etapa 5 vai substituir)
# -------------------------------------------------------------
def heuristica_nula(a: Coordenada, b: Coordenada) -> float:
    """Retorna 0 (usado nesta etapa para validar o A* como Dijkstra)."""
    return 0.0


# -------------------------------------------------------------
# Algoritmo A*
# -------------------------------------------------------------
def busca_a_estrela(tabuleiro: Tabuleiro,
                    inicio: Coordenada,
                    objetivo: Coordenada,
                    func_heuristica=heuristica_nula) -> Tuple[List[Coordenada], float]:
    """
    Executa o algoritmo A* no tabuleiro.
    Retorna (caminho, custo_total) se encontrar, senão ([], ∞).
    """
    # fila de prioridade (f, nó)
    fila_aberta: List[No] = []
    heapq.heappush(fila_aberta, No(0, inicio, 0, 0, None))

    # dicionários de controle
    custo_g: Dict[Coordenada, float] = {inicio: 0}
    pais: Dict[Coordenada, Optional[Coordenada]] = {inicio: None}
    visitados: set[Coordenada] = set()

    while fila_aberta:
        atual = heapq.heappop(fila_aberta)
        pos = atual.posicao

        # se chegou ao destino → reconstruir caminho
        if pos == objetivo:
            caminho = reconstruir_caminho(pais, pos)
            return caminho, atual.g

        # evitar revisitar nós
        if pos in visitados:
            continue
        visitados.add(pos)

        # gerar vizinhos usando movimentos do cavalo
        cavalo = Cavalo(pos)
        for viz in cavalo.movimentos_possiveis(tabuleiro):
            if tabuleiro.bloqueado(viz):
                continue

            novo_custo = atual.g + tabuleiro.custo(viz)
            if viz not in custo_g or novo_custo < custo_g[viz]:
                custo_g[viz] = novo_custo
                h = func_heuristica(viz, objetivo)
                f = novo_custo + h
                heapq.heappush(fila_aberta, No(f, viz, novo_custo, h, pos))
                pais[viz] = pos

    # se não encontrou caminho
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
