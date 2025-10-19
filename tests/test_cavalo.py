import json
from src.board import Tabuleiro
from src.cavalo import Cavalo

def carregar_tabuleiro():
    with open("scenarios/cenario_basico.json", encoding="utf-8") as f:
        dados = json.load(f)
    return Tabuleiro.carregar_de_json(dados)

def test_movimentos_centro():
    tab = carregar_tabuleiro()
    cavalo = Cavalo((4, 4))
    movimentos = cavalo.movimentos_possiveis(tab)
    # cavalo no centro deve ter 8 possíveis (desde que não bloqueados)
    assert all(tab.dentro_dos_limites(m) for m in movimentos)
    assert len(movimentos) <= 8

def test_movimentos_borda():
    tab = carregar_tabuleiro()
    cavalo = Cavalo((7, 0))  # canto inferior esquerdo
    movimentos = cavalo.movimentos_possiveis(tab)
    # borda deve ter no máximo 2 movimentos válidos
    assert len(movimentos) <= 2

def test_barreira_bloqueia():
    tab = carregar_tabuleiro()
    cavalo = Cavalo((2, 0))
    # força uma barreira em (0,1)
    tab.definir_terreno((0, 1), tab.Terreno.BARREIRA)
    movimentos = cavalo.movimentos_possiveis(tab)
    # o cavalo não deve incluir a casa bloqueada
    assert (0, 1) not in movimentos
