# =============================================================
# interface_grafica.py — Visualização A* com tabuleiro realista
# =============================================================

import pygame
import time
from src.tabuleiro import Tabuleiro, Terreno
from src.busca_a_estrela import busca_a_estrela

# -------------------------------------------------------------
# Exibe a animação do cavalo durante a busca
# -------------------------------------------------------------
def mostrar_busca_animada(tabuleiro: Tabuleiro, inicio, objetivo, velocidade=0.4):
    pygame.init()
    tamanho_casa = 80
    margem = 40
    largura, altura = 8 * tamanho_casa + 2 * margem, 8 * tamanho_casa + 2 * margem
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Caminho do Cavalo - A* com Tabuleiro Realista")

    # fontes
    fonte = pygame.font.SysFont("Arial", 24, bold=True)

    # carregar imagem do cavalo (se existir)
    cavalo_img = None
    try:
        cavalo_img = pygame.image.load("assets/cavalo.png")
        cavalo_img = pygame.transform.scale(cavalo_img, (tamanho_casa - 10, tamanho_casa - 10))
    except:
        cavalo_img = None  # usa fallback desenhado

    # paleta de cores
    cor_clara = (238, 238, 210)
    cor_escura = (118, 150, 86)
    cor_caminho = (255, 255, 0)
    cor_inicio = (0, 200, 0)
    cor_objetivo = (200, 0, 0)
    cor_texto = (40, 40, 40)
    cor_fechados = (150, 150, 255)
    cor_abertos = (80, 200, 255)

    # cores de terrenos (sobrepostas)
    tons_terreno = {
        Terreno.ESTRADA: (255, 255, 255, 80),
        Terreno.TERRA:   (139, 69, 19, 100),
        Terreno.LAMA:    (102, 51, 0, 120),
        Terreno.BARREIRA:(0, 0, 0, 180)
    }

    relogio = pygame.time.Clock()
    caminho, custo, explorados, fronteira = busca_a_estrela_animado(tabuleiro, inicio, objetivo)
    etapa = 0
    rodando = True

    # desenha texto auxiliar
    def desenhar_legenda():
        texto = fonte.render(f"Custo atual: {custo:.2f}", True, cor_texto)
        tela.blit(texto, (margem, altura - margem + 5))

    # loop principal
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        # desenha tabuleiro de xadrez
        for lin in range(8):
            for col in range(8):
                x = margem + col * tamanho_casa
                y = margem + lin * tamanho_casa
                # alterna cores do tabuleiro
                if (lin + col) % 2 == 0:
                    base = cor_clara
                else:
                    base = cor_escura
                pygame.draw.rect(tela, base, (x, y, tamanho_casa, tamanho_casa))

                # sobrepõe cor do terreno (com transparência)
                terreno = tabuleiro.grade[lin][col]
                if terreno != Terreno.TERRA:
                    s = pygame.Surface((tamanho_casa, tamanho_casa), pygame.SRCALPHA)
                    s.fill(tons_terreno[terreno])
                    tela.blit(s, (x, y))

        # destaca nós abertos e fechados
        for (lin, col) in fronteira[:etapa]:
            pygame.draw.rect(tela, cor_abertos, (margem + col * tamanho_casa + 8, margem + lin * tamanho_casa + 8, tamanho_casa - 16, tamanho_casa - 16))
        for (lin, col) in explorados[:etapa]:
            pygame.draw.rect(tela, cor_fechados, (margem + col * tamanho_casa + 10, margem + lin * tamanho_casa + 10, tamanho_casa - 20, tamanho_casa - 20))

        # início e objetivo
        pygame.draw.rect(tela, cor_inicio, (margem + inicio[1]*tamanho_casa + 8, margem + inicio[0]*tamanho_casa + 8, tamanho_casa - 16, tamanho_casa - 16))
        pygame.draw.rect(tela, cor_objetivo, (margem + objetivo[1]*tamanho_casa + 8, margem + objetivo[0]*tamanho_casa + 8, tamanho_casa - 16, tamanho_casa - 16))

        # desenha cavalo (posição atual)
        if etapa < len(explorados):
            pos = explorados[etapa]
        else:
            pos = caminho[-1] if caminho else inicio
        x_c = margem + pos[1]*tamanho_casa + tamanho_casa//2
        y_c = margem + pos[0]*tamanho_casa + tamanho_casa//2

        if cavalo_img:
            tela.blit(cavalo_img, (x_c - cavalo_img.get_width()//2, y_c - cavalo_img.get_height()//2))
        else:
            pygame.draw.circle(tela, (255, 255, 255), (x_c, y_c), tamanho_casa//3)
            # desenha símbolo ♞ (unicode)
            fonte_cavalo = pygame.font.SysFont("Arial", 50, bold=True)
            texto = fonte_cavalo.render("♞", True, (0, 0, 0))
            tela.blit(texto, (x_c - 18, y_c - 35))

        # quando termina, desenha o caminho final
        if etapa >= len(explorados):
            for (lin, col) in caminho:
                pygame.draw.rect(tela, cor_caminho,
                                 (margem + col*tamanho_casa + tamanho_casa//4,
                                  margem + lin*tamanho_casa + tamanho_casa//4,
                                  tamanho_casa//2, tamanho_casa//2))

        # desenha legenda inferior
        desenhar_legenda()

        pygame.display.flip()
        relogio.tick(30)
        time.sleep(velocidade)

        if etapa < len(explorados):
            etapa += 1

    pygame.quit()


# -------------------------------------------------------------
# Busca A* modificada para registrar passos
# -------------------------------------------------------------
def busca_a_estrela_animado(tabuleiro, inicio, objetivo):
    import heapq
    from src.busca_a_estrela import No, reconstruir_caminho, heuristica_nula
    from src.cavalo import Cavalo

    fila_aberta = []
    heapq.heappush(fila_aberta, No(0, inicio, 0, 0, None))
    custo_g = {inicio: 0}
    pais = {inicio: None}
    explorados = []
    fronteira = []

    while fila_aberta:
        atual = heapq.heappop(fila_aberta)
        pos = atual.posicao
        explorados.append(pos)

        if pos == objetivo:
            caminho = reconstruir_caminho(pais, pos)
            return caminho, atual.g, explorados, fronteira

        cavalo = Cavalo(pos)
        for viz in cavalo.movimentos_possiveis(tabuleiro):
            if tabuleiro.bloqueado(viz):
                continue
            novo_custo = atual.g + tabuleiro.custo(viz)
            if viz not in custo_g or novo_custo < custo_g[viz]:
                custo_g[viz] = novo_custo
                h = heuristica_nula(viz, objetivo)
                f = novo_custo + h
                heapq.heappush(fila_aberta, No(f, viz, novo_custo, h, pos))
                pais[viz] = pos
                fronteira.append(viz)

    return [], float("inf"), explorados, fronteira
