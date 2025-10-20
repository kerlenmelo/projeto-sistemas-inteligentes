# =============================================================
# interface_grafica.py — Interface otimizada com seleção de heurística
# =============================================================

import os
import time
import math
import pygame
import io
import sys
from src.tabuleiro import Tabuleiro, Terreno
from src.busca_a_estrela import busca_a_estrela  # (mantido por compatibilidade)

# -------------------- CONFIGURAÇÕES VISUAIS --------------------
CELULA = 65
BOARD_N = 8
BARRA_STATUS_H = 40
MARGEM_EXTERNA = 25
AREA_ROTULO = 28
SETA_TAM = 18
VELOCIDADE_PADRAO = 0.35

os.environ["SDL_VIDEO_CENTERED"] = "1"  # centraliza a janela

def origem_tabuleiro():
    x0 = MARGEM_EXTERNA + AREA_ROTULO
    y0 = BARRA_STATUS_H + MARGEM_EXTERNA + AREA_ROTULO
    return x0, y0

LARGURA = (2*MARGEM_EXTERNA)+(2*AREA_ROTULO)+(BOARD_N*CELULA)
ALTURA  = BARRA_STATUS_H+(2*MARGEM_EXTERNA)+(2*AREA_ROTULO)+(BOARD_N*CELULA)


# ------------------- TELA DE SELEÇÃO DE HEURÍSTICA -------------------
def selecionar_heuristica():
    """Tela inicial para escolher a heurística antes da execução."""
    pygame.init()
    largura, altura = 800, 480
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Seleção de Heurística")

    fonte_titulo = pygame.font.SysFont("Arial", 36, bold=True)
    fonte_botao = pygame.font.SysFont("Arial", 22, bold=True)

    espacamento_vertical = 100
    botoes = {
        "h1": pygame.Rect(largura//2 - 230, altura//2 - espacamento_vertical//2 - 60, 460, 60),
        "h2": pygame.Rect(largura//2 - 230, altura//2 - 30, 460, 60),
        "nula": pygame.Rect(largura//2 - 230, altura//2 + 60, 460, 60),
    }

    rodando = True
    escolha = None
    clock = pygame.time.Clock()

    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for heur, rect in botoes.items():
                    if rect.collidepoint(e.pos):
                        escolha = heur
                        rodando = False

        tela.fill((245, 245, 245))
        titulo = fonte_titulo.render("Escolha a heurística para o A*", True, (0, 0, 0))
        tela.blit(titulo, (largura//2 - titulo.get_width()//2, 60))

        for heur, rect in botoes.items():
            hovering = rect.collidepoint(pygame.mouse.get_pos())
            cor = (110, 160, 240) if hovering else (80, 120, 200)
            pygame.draw.rect(tela, cor, rect, border_radius=12)
            texto = fonte_botao.render({
                "h1": "H1 - Fraca (Distância × Custo Mínimo)",
                "h2": "H2 - Forte (Movimentos × Custo Mínimo)",
                "nula": "Sem Heurística (Dijkstra)"
            }[heur], True, (255, 255, 255))
            tela.blit(texto, (rect.centerx - texto.get_width()//2,
                              rect.centery - texto.get_height()//2))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return escolha or "h1"


# ------------------- BUSCA A* (ANIMADA) -------------------
def busca_a_estrela_animado(tabuleiro, inicio, objetivo, tipo_heuristica="h1"):
    import heapq
    from src.busca_a_estrela import (
        No, reconstruir_caminho, heuristica_h1, heuristica_h2, heuristica_nula
    )
    from src.cavalo import Cavalo

    heuristicas = {"h1": heuristica_h1, "h2": heuristica_h2, "nula": heuristica_nula}
    h_func = heuristicas.get(tipo_heuristica, heuristica_h1)

    fila = []
    heapq.heappush(fila, No(0, inicio, 0, 0, None))
    g = {inicio: 0}
    pais = {inicio: None}
    explorados = []
    fronteira = []

    while fila:
        atual = heapq.heappop(fila)
        pos = atual.posicao
        explorados.append(pos)

        if pos == objetivo:
            caminho = reconstruir_caminho(pais, pos)
            return caminho, atual.g, explorados, fronteira

        cavalo = Cavalo(pos)
        for viz in cavalo.movimentos_possiveis(tabuleiro):
            if tabuleiro.bloqueado(viz):
                continue
            novo_g = atual.g + tabuleiro.custo(viz)
            if viz not in g or novo_g < g[viz]:
                g[viz] = novo_g
                h = h_func(viz, objetivo, tabuleiro)
                f = novo_g + h
                heapq.heappush(fila, No(f, viz, novo_g, h, pos))
                pais[viz] = pos
                fronteira.append(viz)

    return [], float("inf"), explorados, fronteira


# ------------------- CARREGAMENTO DE IMAGENS -------------------
def carregar_imagens_terreno(tam):
    pasta = "assets"
    imgs = {}
    def load(nome):
        caminho = os.path.join(pasta, nome)
        if os.path.exists(caminho):
            img = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.smoothscale(img, (tam, tam))
        return None
    imgs[Terreno.ESTRADA] = load("areia.jpg")
    imgs[Terreno.LAMA] = load("lama.png")
    imgs[Terreno.BARREIRA] = load("barreira.png")
    imgs[Terreno.TERRA] = None
    return imgs


def carregar_cavalo():
    try:
        img = pygame.image.load("assets/cavalo.png").convert_alpha()
        return pygame.transform.smoothscale(img, (CELULA - 8, CELULA - 8))
    except:
        return None


# ------------------- DESENHO BASE -------------------
def desenhar_tabuleiro_base(tela, fonte_rotulo):
    cor_clara = (238, 238, 210)
    cor_escura = (118, 150, 86)
    x0, y0 = origem_tabuleiro()
    for lin in range(BOARD_N):
        for col in range(BOARD_N):
            x, y = x0 + col*CELULA, y0 + lin*CELULA
            base = cor_clara if (lin + col) % 2 == 0 else cor_escura
            pygame.draw.rect(tela, base, (x, y, CELULA, CELULA))

    letras = ["A","B","C","D","E","F","G","H"]
    numeros = [str(i) for i in range(8,0,-1)]
    cor_txt = (15,15,15)
    for c, letra in enumerate(letras):
        tx = x0 + c*CELULA + CELULA//2
        surf = fonte_rotulo.render(letra, True, cor_txt)
        tela.blit(surf, (tx - surf.get_width()//2, y0 - AREA_ROTULO + 3))
        tela.blit(surf, (tx - surf.get_width()//2, y0 + BOARD_N*CELULA + 4))
    for l, num in enumerate(numeros):
        ty = y0 + l*CELULA + CELULA//2
        surf = fonte_rotulo.render(num, True, cor_txt)
        tela.blit(surf, (x0 - AREA_ROTULO + 6, ty - surf.get_height()//2))
        tela.blit(surf, (x0 + BOARD_N*CELULA + 6, ty - surf.get_height()//2))


def desenhar_status(tela, fonte_status, executando, etapa, total, custo, heuristica="h1"):
    pygame.draw.rect(tela, (20,20,20), (0,0,LARGURA,BARRA_STATUS_H))
    nomes = {"h1":"H1", "h2":"H2", "nula":"Dj."}
    msg = f"[{nomes.get(heuristica,'H')}] " + ("Executando busca A*..." if executando else "Busca concluída!")
    extra = f"  Nós: {etapa}/{total}  |  Custo: {custo:.2f}"
    texto = fonte_status.render(msg + extra, True, (255,255,255))
    tela.blit(texto, (MARGEM_EXTERNA, (BARRA_STATUS_H - texto.get_height())//2))


def desenhar_seta(tela, origem, destino, cor=(255,200,0)):
    ox, oy = origem
    dx, dy = destino
    pygame.draw.line(tela, cor, (ox, oy), (dx, dy), 4)
    ang = math.atan2(dy - oy, dx - ox)
    ponta1 = (dx - SETA_TAM * math.cos(ang - math.pi/6),
              dy - SETA_TAM * math.sin(ang - math.pi/6))
    ponta2 = (dx - SETA_TAM * math.cos(ang + math.pi/6),
              dy - SETA_TAM * math.sin(ang + math.pi/6))
    pygame.draw.polygon(tela, cor, [(dx, dy), ponta1, ponta2])


# ------------------- RELATÓRIO SOBREPOSTO (com rolagem) -------------------
def mostrar_relatorio_sobreposto(tela, tabuleiro, caminho, custo, heuristica):
    """Exibe o relatório como uma tela temporária com rolagem e botão voltar."""
    from src.relatorio_custos import gerar_relatorio_caminho
    fonte = pygame.font.SysFont("Consolas", 14)      # menor para caber melhor
    fonte_titulo = pygame.font.SysFont("Arial", 24, bold=True)
    largura, altura = tela.get_size()

    # captura texto do relatório
    buffer = io.StringIO()
    antigo_stdout = sys.stdout
    sys.stdout = buffer
    gerar_relatorio_caminho(tabuleiro, caminho, custo, heuristica=heuristica)
    sys.stdout = antigo_stdout
    linhas = buffer.getvalue().split("\n")

    scroll_y = 0
    botao_rect = pygame.Rect(largura//2 - 80, altura - 60, 160, 40)
    cor_fundo = (245,245,245)
    cor_texto = (20,20,20)
    cor_botao = (80,120,200)
    cor_botao_hover = (100,150,230)
    clock = pygame.time.Clock()

    rodando = True
    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            elif e.type == pygame.MOUSEWHEEL:
                scroll_y += e.y * 25
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    scroll_y += 20
                elif e.key == pygame.K_DOWN:
                    scroll_y -= 20
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if botao_rect.collidepoint(e.pos):
                    rodando = False

        tela.fill(cor_fundo)
        titulo = fonte_titulo.render("Relatório Analítico do Caminho", True, (0,0,0))
        tela.blit(titulo, (largura//2 - titulo.get_width()//2, 20))

        # linhas com rolagem
        y = 70 + scroll_y
        for linha in linhas:
            txt = fonte.render(linha, True, cor_texto)
            tela.blit(txt, (40, y))
            y += 20

        # botão voltar
        mouse = pygame.mouse.get_pos()
        cor = cor_botao_hover if botao_rect.collidepoint(mouse) else cor_botao
        pygame.draw.rect(tela, cor, botao_rect, border_radius=10)
        txt_btn = fonte_titulo.render("Voltar", True, (255,255,255))
        tela.blit(txt_btn, (botao_rect.centerx - txt_btn.get_width()//2,
                            botao_rect.centery - txt_btn.get_height()//2))

        pygame.display.flip()
        clock.tick(30)


# ------------------- INTERFACE PRINCIPAL -------------------
def mostrar_busca_animada(tabuleiro: Tabuleiro, inicio, objetivo, velocidade=VELOCIDADE_PADRAO):
    from src.gerador_tabuleiro import gerar_tabuleiro_aleatorio

    # 1) Seleção visual da heurística
    tipo_heuristica = selecionar_heuristica()
    print(f"\nHeurística escolhida: {tipo_heuristica.upper()}")

    # 2) Interface principal
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Caminho do Cavalo - A* (interface interativa)")

    fonte_status = pygame.font.SysFont("Arial", 18, bold=True)
    fonte_rotulo = pygame.font.SysFont("Arial", 18, bold=True)
    fonte_passos = pygame.font.SysFont("Arial", 22, bold=True)
    fonte_caminho = pygame.font.SysFont("Consolas", 18)

    imgs_terreno = carregar_imagens_terreno(CELULA)
    img_cavalo = carregar_cavalo()

    cor_inicio = (0,200,0)
    cor_objetivo = (200,0,0)
    cor_caminho = (255,255,0)
    cor_explorado = (220,0,0)

    x0, y0 = origem_tabuleiro()
    clock = pygame.time.Clock()

    caminho, custo, explorados, fronteira = busca_a_estrela_animado(
        tabuleiro, inicio, objetivo, tipo_heuristica
    )
    etapa = 0
    rodando = True

    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            # R → novo tabuleiro mantendo a mesma heurística
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                tabuleiro = gerar_tabuleiro_aleatorio()
                caminho, custo, explorados, fronteira = busca_a_estrela_animado(
                    tabuleiro, inicio, objetivo, tipo_heuristica
                )
                etapa = 0
            # Enter → relatório
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and not etapa < len(explorados):
                mostrar_relatorio_sobreposto(tela, tabuleiro, caminho, custo, heuristica=tipo_heuristica)

        tela.fill((255,255,255))
        executando = etapa < len(explorados)
        desenhar_status(tela, fonte_status, executando, etapa, len(explorados), custo, heuristica=tipo_heuristica)
        desenhar_tabuleiro_base(tela, fonte_rotulo)

        # texturas de terreno
        for lin in range(BOARD_N):
            for col in range(BOARD_N):
                img = imgs_terreno.get(tabuleiro.grade[lin][col])
                if img:
                    tela.blit(img, (x0 + col*CELULA, y0 + lin*CELULA))

        # pontos explorados (apenas durante a busca)
        if executando:
            for (lin, col) in explorados[:etapa]:
                cx = x0 + col*CELULA + CELULA//2
                cy = y0 + lin*CELULA + CELULA//2
                pygame.draw.circle(tela, cor_explorado, (cx, cy), 6)

        # início e objetivo
        pygame.draw.rect(tela, cor_inicio,
                         (x0 + inicio[1]*CELULA + 6, y0 + inicio[0]*CELULA + 6, CELULA-12, CELULA-12))
        pygame.draw.rect(tela, cor_objetivo,
                         (x0 + objetivo[1]*CELULA + 6, y0 + objetivo[0]*CELULA + 6, CELULA-12, CELULA-12))

        # cavalo (na posição atual da etapa)
        pos = explorados[etapa] if etapa < len(explorados) else (caminho[-1] if caminho else inicio)
        cx, cy = x0 + pos[1]*CELULA + CELULA//2, y0 + pos[0]*CELULA + CELULA//2
        if img_cavalo:
            tela.blit(img_cavalo, (cx - img_cavalo.get_width()//2, cy - img_cavalo.get_height()//2))
        else:
            pygame.draw.circle(tela, (255,255,255), (cx,cy), CELULA//3)

        # caminho final com setas e numeração
        if not executando and caminho:
            for i,(lin,col) in enumerate(caminho):
                cx1 = x0 + col*CELULA + CELULA//2
                cy1 = y0 + lin*CELULA + CELULA//2
                pygame.draw.circle(tela, cor_caminho, (cx1, cy1), 10)
                num = fonte_passos.render(str(i+1), True, (0,0,0))
                tela.blit(num, (cx1 - num.get_width()//2, cy1 - num.get_height()//2))
                if i < len(caminho)-1:
                    lin2, col2 = caminho[i+1]
                    cx2 = x0 + col2*CELULA + CELULA//2
                    cy2 = y0 + lin2*CELULA + CELULA//2
                    desenhar_seta(tela, (cx1, cy1), (cx2, cy2))

            # caminho em notação A1–H8
            letras = ["A","B","C","D","E","F","G","H"]
            caminho_texto = " → ".join([f"{letras[c]}{8-l}" for l,c in caminho])
            texto_final = pygame.font.SysFont("Consolas", 18).render(
                f"Caminho final: {caminho_texto}", True, (0,0,0)
            )
            tela.blit(texto_final, (MARGEM_EXTERNA, ALTURA - 30))

        pygame.display.flip()
        clock.tick(30)
        time.sleep(velocidade)
        if etapa < len(explorados):
            etapa += 1

    pygame.quit()
