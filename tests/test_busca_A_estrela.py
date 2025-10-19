import json
from src.board import Tabuleiro
from src.busca_A_estrela import busca_a_estrela

def carregar_tabuleiro():
    with open("cenarios/cenario_basico.json", encoding="utf-8") as f:
        dados = json.load(f)
    return Tabuleiro.carregar_de_json(dados)

def test_busca_basica():
    tab = carregar_tabuleiro()
    inicio = (7, 0)
    objetivo = (0, 7)
    caminho, custo = busca_a_estrela(tab, inicio, objetivo)
    # o caminho deve começar e terminar nos pontos certos
    assert caminho[0] == inicio
    assert caminho[-1] == objetivo
    # o custo deve ser finito (existe caminho)
    assert custo < float("inf")
