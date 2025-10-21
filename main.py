# =============================================================
# main.py — Execução principal do projeto Caminho do Cavalo
# =============================================================

import json
import pygame
import sys
from src.tabuleiro import Tabuleiro
from src.interface_grafica import mostrar_busca_animada
from src.gerador_tabuleiro import gerar_tabuleiro_aleatorio


# ------------------- MENU INICIAL -------------------
def menu_inicial():
    pygame.init()
    largura, altura = 720, 480
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Caminho do Cavalo — Menu Inicial")

    fonte_titulo = pygame.font.SysFont("Arial", 40, bold=True)
    fonte_botao = pygame.font.SysFont("Arial", 24, bold=True)

    botoes = {
        "fixo": pygame.Rect(largura//2 - 160, 160, 320, 60),
        "aleatorio": pygame.Rect(largura//2 - 160, 250, 320, 60),
        "sair": pygame.Rect(largura//2 - 160, 340, 320, 60),
    }

    clock = pygame.time.Clock()
    escolha = None
    rodando = True
    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for modo, rect in botoes.items():
                    if rect.collidepoint(e.pos):
                        escolha = modo
                        rodando = False

        tela.fill((245, 245, 245))
        titulo = fonte_titulo.render("Caminho do Cavalo", True, (0, 0, 0))
        tela.blit(titulo, (largura//2 - titulo.get_width()//2, 70))

        for modo, rect in botoes.items():
            hover = rect.collidepoint(pygame.mouse.get_pos())
            cor = (100, 150, 250) if hover else (70, 110, 210)
            pygame.draw.rect(tela, cor, rect, border_radius=12)
            texto = {
                "fixo": "Cenário Fixo (JSON)",
                "aleatorio": "Cenário Aleatório",
                "sair": "Sair do Jogo"
            }[modo]
            label = fonte_botao.render(texto, True, (255, 255, 255))
            tela.blit(label, (rect.centerx - label.get_width()//2,
                              rect.centery - label.get_height()//2))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return escolha


# ------------------- EXECUÇÕES -------------------
def executar_tabuleiro_fixo():
    """Executa o algoritmo e a interface com o cenário JSON fixo."""
    with open("cenarios/cenario_basico.json", encoding="utf-8") as f:
        dados = json.load(f)
    tabuleiro = Tabuleiro.carregar_de_json(dados)
    inicio = (7, 0)
    objetivo = (0, 7)
    mostrar_busca_animada(tabuleiro, inicio, objetivo, velocidade=0.4)


def executar_tabuleiro_aleatorio():
    """Executa o algoritmo e a interface com um tabuleiro gerado aleatoriamente."""
    tabuleiro = gerar_tabuleiro_aleatorio()
    inicio = (7, 0)
    objetivo = (0, 7)
    mostrar_busca_animada(tabuleiro, inicio, objetivo, velocidade=0.35)


# ------------------- PONTO DE ENTRADA -------------------
if __name__ == "__main__":
    while True:
        escolha = menu_inicial()
        if escolha == "fixo":
            executar_tabuleiro_fixo()
        elif escolha == "aleatorio":
            executar_tabuleiro_aleatorio()
        elif escolha == "sair":
            print("Encerrando Caminho do Cavalo...")
            sys.exit()
