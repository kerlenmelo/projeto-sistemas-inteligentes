# =============================================================
# gerador_tabuleiro.py — Cria tabuleiros aleatórios jogáveis
# =============================================================

import random
from src.tabuleiro import Tabuleiro, Terreno, CUSTOS_PADRAO
from src.busca_a_estrela import busca_a_estrela

def gerar_tabuleiro_aleatorio(prob_barreira=0.12, prob_lama=0.18, prob_estrada=0.25, max_tentativas=50):
    """
    Gera um tabuleiro aleatório 8x8 com terrenos variados.
    Garante que exista um caminho possível do início (7,0) ao objetivo (0,7).
    """
    inicio = (7, 0)
    objetivo = (0, 7)

    for tentativa in range(1, max_tentativas + 1):
        grid = []

        # cria a matriz com terrenos aleatórios
        for lin in range(8):
            linha = []
            for col in range(8):
                r = random.random()
                if r < prob_barreira:
                    linha.append(Terreno.BARREIRA)
                elif r < prob_barreira + prob_lama:
                    linha.append(Terreno.LAMA)
                elif r < prob_barreira + prob_lama + prob_estrada:
                    linha.append(Terreno.ESTRADA)
                else:
                    linha.append(Terreno.TERRA)
            grid.append(linha)

        # cria objeto Tabuleiro com custos padrão
        tabuleiro = Tabuleiro(grid, dict(CUSTOS_PADRAO))

        # garante início e fim livres
        tabuleiro.grade[inicio[0]][inicio[1]] = Terreno.TERRA
        tabuleiro.grade[objetivo[0]][objetivo[1]] = Terreno.TERRA

        # tenta encontrar caminho
        caminho, custo = busca_a_estrela(tabuleiro, inicio, objetivo)

        if caminho and custo < float("inf"):
            print(f"[✔] Tabuleiro válido encontrado (tentativa {tentativa}) — Custo estimado: {custo:.2f}")
            return tabuleiro
        else:
            print(f"[✖] Tentativa {tentativa}: tabuleiro inviável, gerando novo...")

    # fallback — terreno livre se todas falharem
    print("[⚠] Nenhum tabuleiro válido encontrado após várias tentativas. Gerando terreno livre.")
    grid = [[Terreno.TERRA for _ in range(8)] for _ in range(8)]
    return Tabuleiro(grid, dict(CUSTOS_PADRAO))
