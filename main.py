# Script para testar manualmente o tabuleiro
import json
from src.tabuleiro import Tabuleiro

with open("cenarios/cenario_basico.json", encoding="utf-8") as f:
    dados = json.load(f)

tabuleiro = Tabuleiro.carregar_de_json(dados)

print("Terreno em (2,1):", tabuleiro.tipo_terreno((2,1)))
print("Custo em (2,1):", tabuleiro.custo((2,1)))
print("Bloqueado (3,1):", tabuleiro.bloqueado((3,1)))
print("Menor custo possível:", tabuleiro.menor_custo_transponivel())
print("Vizinhos do cavalo em (7,0):", tabuleiro.vizinhos_cavalo((7,0)))
