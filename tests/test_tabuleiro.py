import json
from src.board import Tabuleiro, Terreno

def carregar_tabuleiro():
    with open("scenarios/cenario_basico.json", encoding="utf-8") as f:
        dados = json.load(f)
    return Tabuleiro.carregar_de_json(dados)

def test_formato_grade():
    t = carregar_tabuleiro()
    assert len(t.grade) == 8 and all(len(l) == 8 for l in t.grade)

def test_custos():
    t = carregar_tabuleiro()
    assert t.custo((2,1)) == 0.5   # estrada
    assert t.custo((1,3)) == 5.0   # lama
    assert t.custo((0,0)) == 1.0   # terra

def test_barreiras():
    t = carregar_tabuleiro()
    assert t.bloqueado((3,1)) is True

def test_menor_custo():
    t = carregar_tabuleiro()
    assert t.menor_custo_transponivel() == 0.5
