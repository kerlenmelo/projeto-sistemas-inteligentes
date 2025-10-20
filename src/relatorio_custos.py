# =============================================================
# relatorio_custos.py — Relatório analítico dos custos do caminho
# =============================================================

from src.tabuleiro import Terreno

def gerar_relatorio_caminho(tabuleiro, caminho, custo_total, heuristica="h1"):
    """
    Gera um relatório detalhado do caminho encontrado e seus custos acumulados.
    Inclui também a heurística utilizada (H1, H2 ou nula).
    """

    if not caminho:
        print("\nNenhum caminho encontrado.")
        return

    # ---------------------------------------------------------
    # Identificação da heurística utilizada
    # ---------------------------------------------------------
    nomes_heuristicas = {
        "h1": "H1 - Distância simples × menor custo (heurística fraca)",
        "h2": "H2 - Movimentos mínimos do cavalo × menor custo (heurística forte)",
        "nula": "Sem heurística (A* equivalente ao Dijkstra)"
    }

    heuristica_texto = nomes_heuristicas.get(heuristica, "Desconhecida")

    print("\n=== RELATÓRIO ANALÍTICO DO CAMINHO ENCONTRADO ===\n")
    print(f"Heurística utilizada: {heuristica_texto}\n")

    # ---------------------------------------------------------
    # Cálculos de custos teóricos e acumulados
    # ---------------------------------------------------------
    custo_acumulado = 0
    menor_custo = tabuleiro.menor_custo_transponivel()
    custo_teorico_min = menor_custo * (len(caminho) - 1)
    custo_teorico_max = max(tabuleiro.custos.values()) * (len(caminho) - 1)

    print(f"Menor custo possível por terreno: {menor_custo:.2f}")
    print(f"Custo teórico mínimo admissível: {custo_teorico_min:.2f}")
    print(f"Custo teórico máximo admissível: {custo_teorico_max:.2f}")
    print("\nPassos percorridos:\n")

    # ---------------------------------------------------------
    # Lista de passos detalhada
    # ---------------------------------------------------------
    for i, pos in enumerate(caminho):
        tipo = tabuleiro.tipo_terreno(pos)
        custo = tabuleiro.custo(pos)
        custo_acumulado += custo
        print(f"{i+1:02d}. {pos} → Terreno: {tipo.name:<8} | "
              f"Custo: {custo:>5.2f} | Acumulado: {custo_acumulado:>6.2f}")

    # ---------------------------------------------------------
    # Resumo final e validação da admissibilidade
    # ---------------------------------------------------------
    print("\n--- RESULTADOS ---")
    print(f"Custo total calculado pelo A*: {custo_total:.2f}")
    print(f"Soma de custos percorridos:     {custo_acumulado:.2f}")

    if custo_total <= custo_teorico_max:
        print(f"O custo total está dentro do limite admissível "
              f"({custo_total:.2f} ≤ {custo_teorico_max:.2f}).")
    else:
        print(f"O custo total excedeu o máximo admissível! "
              f"({custo_total:.2f} > {custo_teorico_max:.2f})")

    print("========================================================\n")
