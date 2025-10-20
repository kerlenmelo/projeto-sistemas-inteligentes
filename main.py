# =============================================================
# main.py — Execução principal do projeto Caminho do Cavalo
# =============================================================

import json
from src.tabuleiro import Tabuleiro
from src.interface_grafica import mostrar_busca_animada
from src.gerador_tabuleiro import gerar_tabuleiro_aleatorio


# -------------------------------------------------------------
# EXECUÇÃO COM TABULEIRO FIXO
# -------------------------------------------------------------
def executar_tabuleiro_fixo():
    """Executa o algoritmo e a interface com o cenário JSON fixo."""
    with open("cenarios/cenario_basico.json", encoding="utf-8") as f:
        dados = json.load(f)

    tabuleiro = Tabuleiro.carregar_de_json(dados)

    print("\n=== TESTE: TABULEIRO FIXO (cenario_basico.json) ===")
    print("Terreno em (2,1):", tabuleiro.tipo_terreno((2, 1)))
    print("Custo em (2,1):", tabuleiro.custo((2, 1)))
    print("Bloqueado (3,1):", tabuleiro.bloqueado((3, 1)))
    print("Menor custo possível:", tabuleiro.menor_custo_transponivel())
    print("Vizinhos do cavalo em (7,0):", tabuleiro.vizinhos_cavalo((7, 0)))

    inicio = (7, 0)
    objetivo = (0, 7)

    print("\n--- Execução visual com tabuleiro fixo ---")
    mostrar_busca_animada(tabuleiro, inicio, objetivo, velocidade=0.4)


# -------------------------------------------------------------
# EXECUÇÃO COM TABULEIRO ALEATÓRIO
# -------------------------------------------------------------
def executar_tabuleiro_aleatorio():
    """Executa o algoritmo e a interface com um tabuleiro gerado aleatoriamente."""
    print("\n=== TESTE: TABULEIRO ALEATÓRIO ===")
    tabuleiro = gerar_tabuleiro_aleatorio()

    inicio = (7, 0)
    objetivo = (0, 7)

    print("\n--- Execução visual com tabuleiro aleatório ---")
    mostrar_busca_animada(tabuleiro, inicio, objetivo, velocidade=0.35)


# -------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# -------------------------------------------------------------
if __name__ == "__main__":
    # Escolha o modo de execução:
    #   "fixo"      → usa o cenário JSON
    #   "aleatorio" → gera novo tabuleiro a cada execução
    modo = "aleatorio"

    if modo == "fixo":
        executar_tabuleiro_fixo()
    else:
        executar_tabuleiro_aleatorio()
