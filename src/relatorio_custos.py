# =============================================================
# relatorio_custos.py — Relatório analítico dos custos do caminho
# =============================================================

from src.tabuleiro import Terreno

def gerar_relatorio_caminho(tabuleiro, caminho, custo_total):
    """
    Gera um relatório detalhado do caminho encontrado e seus custos acumulados.
    """
    if not caminho:
        print("\n[⚠] Nenhum caminho encontrado.")
        return

    print("\n=== RELATÓRIO ANALÍTICO DO CAMINHO ENCONTRADO ===\n")
    custo_acumulado = 0
    menor_custo = tabuleiro.menor_custo_transponivel()
    custo_teorico_min = menor_custo * (len(caminho) - 1)
    custo_teorico_max = max(tabuleiro.custos.values()) * (len(caminho) - 1)

    print(f"Menor custo possível por terreno: {menor_custo:.2f}")
    print(f"Custo teórico mínimo admissível: {custo_teorico_min:.2f}")
    print(f"Custo teórico máximo admissível: {custo_teorico_max:.2f}")
    print("\nPassos percorridos:\n")

    for i, pos in enumerate(caminho):
        tipo = tabuleiro.tipo_terreno(pos)
        custo = tabuleiro.custo(pos)
        custo_acumulado += custo
        print(f"{i+1:02d}. {pos} → Terreno: {tipo.name:<8} | Custo: {custo:>5.2f} | Acumulado: {custo_acumulado:>6.2f}")

    print("\n--- RESULTADOS ---")
    print(f"Custo total calculado pelo A*: {custo_total:.2f}")
    print(f"Soma de custos percorridos:     {custo_acumulado:.2f}")

    if custo_total <= custo_teorico_max:
        print(f"[✅] O custo total está dentro do limite admissível ({custo_total:.2f} ≤ {custo_teorico_max:.2f}).")
    else:
        print(f"[⚠] O custo total excedeu o máximo admissível! ({custo_total:.2f} > {custo_teorico_max:.2f})")

    print("========================================================\n")
