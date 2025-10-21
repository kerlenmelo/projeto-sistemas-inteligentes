# =============================================================
# interface_grafica.py — Interface otimizada com comparação H₁ × H₂
# =============================================================

import os, time, pygame, io, sys
from src.gerador_tabuleiro import gerar_tabuleiro_aleatorio
from src.tabuleiro import Tabuleiro, Terreno

# -------------------- CONFIGURAÇÕES VISUAIS --------------------
CELULA = 65
BOARD_N = 8
BARRA_STATUS_H = 40
MARGEM_EXTERNA = 25
AREA_ROTULO = 28
SETA_TAM = 18
VELOCIDADE_PADRAO = 0.35
os.environ["SDL_VIDEO_CENTERED"] = "1"

def origem_tabuleiro():
    x0 = MARGEM_EXTERNA + AREA_ROTULO
    y0 = BARRA_STATUS_H + MARGEM_EXTERNA + AREA_ROTULO
    return x0, y0

LARGURA = (2*MARGEM_EXTERNA)+(2*AREA_ROTULO)+(BOARD_N*CELULA)
ALTURA  = BARRA_STATUS_H+(2*MARGEM_EXTERNA)+(2*AREA_ROTULO)+(BOARD_N*CELULA)


# ------------------- TELA DE SELEÇÃO DE HEURÍSTICA -------------------
def selecionar_heuristica():
    pygame.init()
    largura, altura = 820, 590
    tela = pygame.display.set_mode((largura, altura), pygame.RESIZABLE)
    pygame.display.set_caption("Seleção de Heurística")

    fonte_titulo = pygame.font.SysFont("Arial", 36, bold=True)
    fonte_botao = pygame.font.SysFont("Arial", 22, bold=True)

    botoes = {
        "h1": pygame.Rect(largura//2 - 230, 170, 460, 60),
        "h2": pygame.Rect(largura//2 - 230, 260, 460, 60),
        "nula": pygame.Rect(largura//2 - 230, 350, 460, 60),
        "comparar": pygame.Rect(largura//2 - 230, 440, 460, 60),
        "voltar": pygame.Rect(largura//2 - 230, 520, 460, 60)
    }

    escolha = None
    clock = pygame.time.Clock()
    rodando = True
    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for heur, rect in botoes.items():
                    if rect.collidepoint(e.pos):
                        if heur == "voltar":
                            rodando = False  # Voltar ao menu inicial
                        else:
                            escolha = heur
                            rodando = False

        tela.fill((245,245,245))
        titulo = fonte_titulo.render("Escolha a heurística para o A*", True, (0,0,0))
        tela.blit(titulo, (largura//2 - titulo.get_width()//2, 70))
        for heur, rect in botoes.items():
            hover = rect.collidepoint(pygame.mouse.get_pos())
            cor = (120,160,240) if hover else (80,120,200)
            pygame.draw.rect(tela, cor, rect, border_radius=15)
            label = {
                "h1": "H1 - Fraca (Distância × Custo Mínimo)",
                "h2": "H2 - Forte (Movimentos × Custo Mínimo)",
                "nula": "Sem Heurística (Dijkstra)",
                "comparar": "Comparar H1 × H2 (modo visual)",
                "voltar": "Voltar ao Menu"
            }[heur]
            texto = fonte_botao.render(label, True, (255,255,255))
            tela.blit(texto, (rect.centerx - texto.get_width()//2,
                              rect.centery - texto.get_height()//2))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return escolha



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
            if tabuleiro.bloqueado(viz): continue
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
    imgs[Terreno.ESTRADA] = load("areia.png")
    imgs[Terreno.LAMA] = load("lama.png")
    imgs[Terreno.BARREIRA] = load("barreira.png")
    imgs[Terreno.TERRA] = None
    imgs["inicio"] = load("inicio.png")
    imgs["chegada"] = load("chegada.png")
    return imgs


def carregar_cavalo():
    try:
        img = pygame.image.load("assets/cavalo.png").convert_alpha()
        return pygame.transform.smoothscale(img, (CELULA - 8, CELULA - 8))
    except:
        return None


# ------------------- RELATÓRIO SOBREPOSTO -------------------
def mostrar_relatorio_sobreposto_texto(tela, texto, titulo="Relatório"):
    fonte = pygame.font.SysFont("Consolas", 14)
    fonte_titulo = pygame.font.SysFont("Arial", 24, bold=True)
    largura, altura = tela.get_size()
    linhas = texto.split("\n")
    scroll_y = 0
    botao_rect = pygame.Rect(largura//2 - 80, altura - 60, 160, 40)
    clock = pygame.time.Clock()
    rodando = True
    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:  # Fechar a janela
                rodando = False
            elif e.type == pygame.MOUSEWHEEL:  # Scroll
                scroll_y += e.y * 25
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_ESCAPE):  # Pressionar ENTER ou ESC para sair
                    rodando = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if botao_rect.collidepoint(e.pos):
                    rodando = False 
                    return

        tela.fill((245, 245, 245))
        titulo_txt = fonte_titulo.render(titulo, True, (0, 0, 0))
        tela.blit(titulo_txt, (largura//2 - titulo_txt.get_width()//2, 20))
        y = 70 + scroll_y

        for linha in linhas:
            txt = fonte.render(linha, True, (20, 20, 20))
            tela.blit(txt, (40, y))
            y += 20

        # Desenhando o botão Voltar
        pygame.draw.rect(tela, (80, 120, 200), botao_rect, border_radius=10)
        txt_btn = fonte_titulo.render("Voltar", True, (255, 255, 255))
        tela.blit(txt_btn, (botao_rect.centerx - txt_btn.get_width()//2,
                            botao_rect.centery - txt_btn.get_height()//2))

        pygame.display.flip()
        clock.tick(30)


# ------------------- MODO COMPARATIVO -------------------
def comparar_heuristicas(tabuleiro: Tabuleiro, inicio, objetivo, velocidade=0.35):
    import heapq
    from src.busca_a_estrela import No, reconstruir_caminho, heuristica_h1, heuristica_h2
    from src.cavalo import Cavalo
    from src.relatorio_custos import gerar_relatorio_caminho
    from src.gerador_tabuleiro import gerar_tabuleiro_aleatorio

    def executar_busca(tab, heur):
        fila = []
        heapq.heappush(fila, No(0, inicio, 0, 0, None))
        g = {inicio: 0}
        pais = {inicio: None}
        explorados = []
        while fila:
            atual = heapq.heappop(fila)
            pos = atual.posicao
            explorados.append(pos)
            if pos == objetivo:
                caminho = reconstruir_caminho(pais, pos)
                return caminho, atual.g, explorados
            cavalo = Cavalo(pos)
            for viz in cavalo.movimentos_possiveis(tab):
                if tabuleiro.bloqueado(viz): continue
                novo_g = atual.g + tabuleiro.custo(viz)
                if viz not in g or novo_g < g[viz]:
                    g[viz] = novo_g
                    h = heur(viz, objetivo, tabuleiro)
                    f = novo_g + h
                    heapq.heappush(fila, No(f, viz, novo_g, h, pos))
                    pais[viz] = pos
        return [], float("inf"), explorados

    # função que desenha e trata eventos (permite recursão p/ "R")
    def executar_comparativo(tab):
        pygame.init()
        largura_total, altura_total = 1150, 700
        tela = pygame.display.set_mode((largura_total, altura_total))
        pygame.display.set_caption("Comparativo de Heurísticas — H1 × H2")
        fonte_titulo = pygame.font.SysFont("Arial", 24, bold=True)
        fonte_info = pygame.font.SysFont("Arial", 18, bold=True)
        fonte_hint = pygame.font.SysFont("Arial", 16)
        clock = pygame.time.Clock()
        celula, margem, offset_y = 48, 40, 120
        largura_tab = 8 * celula
        imgs = carregar_imagens_terreno(celula)
        cavalo_img = carregar_cavalo()

        # Centralizar os tabuleiros
        tabuleiro_h1_x = (largura_total - 2 * largura_tab - 40) // 2
        tabuleiro_h2_x = tabuleiro_h1_x + largura_tab + 80

        # execuções
        t0 = time.time(); c1, custo1, e1 = executar_busca(tab, heuristica_h1); tempo1 = time.time()-t0
        t0 = time.time(); c2, custo2, e2 = executar_busca(tab, heuristica_h2); tempo2 = time.time()-t0
        etapa, max_etapas, terminou = 0, max(len(e1), len(e2)), False

        # Detalhes do relatório comparativo
        ganho_nos = 100 * (1 - len(e2)/len(e1)) if len(e1) else 0
        ganho_tempo = 100 * (1 - tempo2/tempo1) if tempo1 else 0
        h1_media_custo = custo1 / len(e1) if e1 else 0
        h2_media_custo = custo2 / len(e2) if e2 else 0
        h1_num_movimentos = len(c1)
        h2_num_movimentos = len(c2)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN and terminou:

                        buffer = io.StringIO()
                        antigo = sys.stdout
                        sys.stdout = buffer

                        print("\n=== RELATÓRIO H1 ===\n")
                        gerar_relatorio_caminho(tab, c1, custo1, heuristica="h1")
                        sys.stdout = antigo
                        mostrar_relatorio_sobreposto_texto(tela, buffer.getvalue(), titulo="Relatório H1")

                        buffer = io.StringIO()
                        antigo = sys.stdout
                        sys.stdout = buffer

                        print("\n=== RELATÓRIO H2 ===\n")
                        gerar_relatorio_caminho(tab, c2, custo2, heuristica="h2")
                        sys.stdout = antigo
                        mostrar_relatorio_sobreposto_texto(tela, buffer.getvalue(), titulo="Relatório H2")

                        buffer = io.StringIO()
                        antigo = sys.stdout
                        sys.stdout = buffer

                        print("\n=== RELATÓRIO COMPARATIVO DE HEURÍSTICAS ===\n")
                        # Relatório detalhado comparativo
                        print(f"H1 (Fraca) - Custo: {custo1:.2f} | Nós Expandidos: {len(e1)} | Tempo: {tempo1:.3f}s | Custo Médio por Nó: {h1_media_custo:.2f} | Movimentos: {h1_num_movimentos}")
                        print(f"H2 (Forte) - Custo: {custo2:.2f} | Nós Expandidos: {len(e2)} | Tempo: {tempo2:.3f}s | Custo Médio por Nó: {h2_media_custo:.2f} | Movimentos: {h2_num_movimentos}")
                        print(f"\nComparação entre as heurísticas:")
                        print(f"H2 expandiu {abs(ganho_nos):.1f}% {'menos' if ganho_nos>0 else 'mais'} nós.")
                        print(f"H2 foi {abs(ganho_tempo):.1f}% {'mais rápida' if ganho_tempo>0 else 'mais lenta'} que H1.")
                        print(f"\nResumo Comparativo:")
                        print(f"H1 teve {h1_num_movimentos} movimentos e H2 teve {h2_num_movimentos} movimentos.")
                        print(f"H2 foi {'mais eficiente' if ganho_nos > 0 else 'menos eficiente'} com relação ao número de nós expandidos.")
                        print(f"H1 tem um custo médio de {h1_media_custo:.2f} por nó, enquanto H2 tem {h2_media_custo:.2f}.")
                        sys.stdout = antigo
                        mostrar_relatorio_sobreposto_texto(tela, buffer.getvalue(), titulo="Relatório Comparativo H1 × H2")

                    elif e.key == pygame.K_r:
                        novo = gerar_tabuleiro_aleatorio()
                        executar_comparativo(novo)
                        return

                # Verifica se o botão "Voltar" foi pressionado
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if BOTAO_VOLTAR.collidepoint(e.pos):
                        # Chama a tela de heurísticas novamente
                        tipo = selecionar_heuristica()
                        if tipo == "comparar":
                            comparar_heuristicas(tabuleiro, inicio, objetivo, velocidade)
                        else:
                            mostrar_busca_animada(tabuleiro, inicio, objetivo, velocidade)
                        return

            # desenho
            tela.fill((240,240,240))
            pygame.draw.rect(tela, (30,30,30), (0,0,largura_total,60))
            titulo = fonte_titulo.render("Comparação Visual — H1 (esquerda) × H2 (direita)", True, (255,255,255))
            tela.blit(titulo, (largura_total//2 - titulo.get_width()//2, 15))

            def desenhar(x_off, explorados, caminho, nome, cor):
                titulo = fonte_titulo.render(nome, True, cor)
                tela.blit(titulo, (x_off + largura_tab//2 - titulo.get_width()//2, 70))
                letras = ["A","B","C","D","E","F","G","H"]
                for l in range(8):
                    for c in range(8):
                        corq = (255,255,255) if (l+c)%2==0 else (0,0,0)
                        pygame.draw.rect(tela, corq, (x_off+c*celula, offset_y+l*celula, celula, celula))
                        img = imgs.get(tab.grade[l][c])
                        if img: tela.blit(img, (x_off+c*celula, offset_y+l*celula))
                # rótulos
                fonte_rot = pygame.font.SysFont("Arial", 14, bold=True)
                for i in range(8):
                    letra = fonte_rot.render(letras[i], True, (0,0,0))
                    num = fonte_rot.render(str(8-i), True, (0,0,0))
                    tela.blit(letra, (x_off + i*celula + celula//2 - letra.get_width()//2, offset_y - 20))
                    tela.blit(letra, (x_off + i*celula + celula//2 - letra.get_width()//2, offset_y + 8*celula + 5))
                    tela.blit(num, (x_off - 20, offset_y + i*celula + celula//2 - num.get_height()//2))
                    tela.blit(num, (x_off + 8*celula + 8, offset_y + i*celula + celula//2 - num.get_height()//2))
                # inicio e chegada
                if imgs.get("inicio"):
                    tela.blit(imgs["inicio"], (x_off + inicio[1]*celula, offset_y + inicio[0]*celula))
                if imgs.get("chegada"):
                    tela.blit(imgs["chegada"], (x_off + objetivo[1]*celula, offset_y + objetivo[0]*celula))
                # explorados
                for (l,c) in explorados[:min(etapa, len(explorados))]:
                    cx = x_off + c*celula + celula//2
                    cy = offset_y + l*celula + celula//2
                    pygame.draw.circle(tela, (255,0,0), (cx,cy), 5)
                # cavalo
                pos = explorados[min(etapa, len(explorados)-1)] if explorados else inicio
                cx = x_off + pos[1]*celula + celula//2
                cy = offset_y + pos[0]*celula + celula//2
                if cavalo_img: tela.blit(cavalo_img, (cx - cavalo_img.get_width()//2, cy - cavalo_img.get_height()//2))
                if terminou:
                    for i,(l,c) in enumerate(caminho):
                        cx1 = x_off + c*celula + celula//2
                        cy1 = offset_y + l*celula + celula//2
                        pygame.draw.circle(tela, (255,255,0), (cx1,cy1), 6)
                        if i < len(caminho)-1:
                            l2,c2 = caminho[i+1]
                            cx2 = x_off + c2*celula + celula//2
                            cy2 = offset_y + l2*celula + celula//2
                            pygame.draw.line(tela,(255,255,0),(cx1,cy1),(cx2,cy2),3)

            desenhar(tabuleiro_h1_x, e1, c1, "H1 - Fraca", (60,120,255))
            desenhar(tabuleiro_h2_x, e2, c2, "H2 - Forte", (255,120,60))

            tela.blit(fonte_info.render(f"H1 → Custo {custo1:.2f} | Nós {len(e1)} | Tempo {tempo1:.3f}s", True, (0,0,0)), (tabuleiro_h1_x, altura_total - 160))
            tela.blit(fonte_info.render(f"H2 → Custo {custo2:.2f} | Nós {len(e2)} | Tempo {tempo2:.3f}s", True, (0,0,0)), (tabuleiro_h2_x, altura_total - 160))

            # ====== BOTÃO VOLTAR ======
            BOTAO_VOLTAR = pygame.Rect(largura_total//2 - 80, altura_total - 60, 160, 40)
            mouse = pygame.mouse.get_pos()
            hover = BOTAO_VOLTAR.collidepoint(mouse)
            cor_btn = (100,150,255) if hover else (70,120,200)
            pygame.draw.rect(tela, cor_btn, BOTAO_VOLTAR, border_radius=8)
            texto_voltar = fonte_hint.render("Voltar", True, (255,255,255))
            tela.blit(texto_voltar, (BOTAO_VOLTAR.centerx - texto_voltar.get_width()//2, BOTAO_VOLTAR.centery - texto_voltar.get_height()//2))

            if terminou:
                dica = fonte_hint.render("Pressione ENTER para relatório | R para novo tabuleiro", True, (60,60,60))
                tela.blit(dica, (largura_total//2 - dica.get_width()//2, altura_total - 100))

            pygame.display.flip()
            clock.tick(30)
            time.sleep(velocidade)
            if etapa < max_etapas: etapa += 1
            else: terminou = True

    executar_comparativo(tabuleiro)


def mostrar_busca_animada(tabuleiro: Tabuleiro, inicio, objetivo, velocidade=VELOCIDADE_PADRAO):
    tipo = selecionar_heuristica()

    if tipo is None:
        # Voltar ao menu principal
        pygame.quit()
        return

    if tipo == "comparar":
        comparar_heuristicas(tabuleiro, inicio, objetivo, velocidade)
        return

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Caminho do Cavalo - A* (interface interativa)")
    fonte_status = pygame.font.SysFont("Arial", 18, bold=True)
    fonte_passos = pygame.font.SysFont("Arial", 22, bold=True)
    fonte_caminho = pygame.font.SysFont("Consolas", 18)
    fonte_rotulo = pygame.font.SysFont("Arial", 18, bold=True)
    fonte_botao = pygame.font.SysFont("Arial", 20, bold=True)
    imgs = carregar_imagens_terreno(CELULA)
    cavalo_img = carregar_cavalo()

    # 🎨 Cores
    COR_BEGE = (245, 222, 179)
    COR_MARROM = (101, 67, 33)
    COR_BORDA_EXTERNA = (80, 50, 20)
    COR_BORDA_INTERNA = (212, 175, 55)
    cor_caminho, cor_explorado = (255,255,0), (220,0,0)

    x0, y0 = origem_tabuleiro()
    clock = pygame.time.Clock()

    # botão voltar (superior direito)
    BOTAO_VOLTAR = pygame.Rect(LARGURA - 130, 5, 110, 30)

    caminho, custo, explorados, _ = busca_a_estrela_animado(tabuleiro, inicio, objetivo, tipo)
    etapa, rodando = 0, True
    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                tabuleiro = gerar_tabuleiro_aleatorio()
                caminho, custo, explorados, _ = busca_a_estrela_animado(tabuleiro, inicio, objetivo, tipo)
                etapa = 0
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and etapa >= len(explorados):
                from src.relatorio_custos import gerar_relatorio_caminho
                buffer = io.StringIO()
                antigo = sys.stdout
                sys.stdout = buffer
                gerar_relatorio_caminho(tabuleiro, caminho, custo, heuristica=tipo)
                sys.stdout = antigo
                mostrar_relatorio_sobreposto_texto(tela, buffer.getvalue(), titulo="Relatório Analítico")
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if BOTAO_VOLTAR.collidepoint(e.pos):
                    pygame.quit()
                    # retorna ao menu principal
                    tipo = selecionar_heuristica()
                    if tipo == "comparar":
                        comparar_heuristicas(tabuleiro, inicio, objetivo, velocidade)
                    else:
                        mostrar_busca_animada(tabuleiro, inicio, objetivo, velocidade)
                    return

        tela.fill((255,255,255))
        pygame.draw.rect(tela, (20,20,20), (0,0,LARGURA,BARRA_STATUS_H))
        executando = etapa < len(explorados)
        msg = f"Heurística {tipo.upper()} | {'Executando...' if executando else 'Concluído!'} | Nós: {etapa}/{len(explorados)} | Custo: {custo:.2f}"
        tela.blit(fonte_status.render(msg, True, (255,255,255)), (MARGEM_EXTERNA, 10))

        # ====== BOTÃO VOLTAR (superior direito) ======
        mouse = pygame.mouse.get_pos()
        hover = BOTAO_VOLTAR.collidepoint(mouse)
        cor_btn = (100,150,255) if hover else (70,120,200)
        pygame.draw.rect(tela, cor_btn, BOTAO_VOLTAR, border_radius=8)
        texto_voltar = fonte_botao.render("Voltar", True, (255,255,255))
        tela.blit(texto_voltar, (BOTAO_VOLTAR.centerx - texto_voltar.get_width()//2,
                                 BOTAO_VOLTAR.centery - texto_voltar.get_height()//2))
        # =============================================

        letras = ["A","B","C","D","E","F","G","H"]
        for lin in range(BOARD_N):
            for col in range(BOARD_N):
                cor = COR_BEGE if (lin+col)%2==0 else COR_MARROM
                pygame.draw.rect(tela, cor, (x0+col*CELULA, y0+lin*CELULA, CELULA, CELULA))
                img = imgs.get(tabuleiro.grade[lin][col])
                if img: tela.blit(img, (x0+col*CELULA, y0+lin*CELULA))

        # Rótulos laterais e superiores
        for i in range(BOARD_N):
            letra = fonte_rotulo.render(letras[i], True, (0,0,0))
            num = fonte_rotulo.render(str(8-i), True, (0,0,0))
            tela.blit(letra, (x0 + i*CELULA + CELULA//2 - letra.get_width()//2, y0 - AREA_ROTULO))
            tela.blit(letra, (x0 + i*CELULA + CELULA//2 - letra.get_width()//2, y0 + BOARD_N*CELULA + 5))
            tela.blit(num, (x0 - AREA_ROTULO + 5, y0 + i*CELULA + CELULA//2 - num.get_height()//2))
            tela.blit(num, (x0 + BOARD_N*CELULA + 8, y0 + i*CELULA + CELULA//2 - num.get_height()//2))

        # Borda do tabuleiro
        pygame.draw.rect(tela, COR_BORDA_EXTERNA, (x0 - 4, y0 - 4, BOARD_N*CELULA + 8, BOARD_N*CELULA + 8), 6)
        pygame.draw.rect(tela, COR_BORDA_INTERNA, (x0, y0, BOARD_N*CELULA, BOARD_N*CELULA), 4)

        # Início e chegada
        if imgs.get("inicio"):
            tela.blit(imgs["inicio"], (x0 + inicio[1]*CELULA, y0 + inicio[0]*CELULA))
        if imgs.get("chegada"):
            tela.blit(imgs["chegada"], (x0 + objetivo[1]*CELULA, y0 + objetivo[0]*CELULA))

        # Nós explorados
        if executando:
            for (lin,col) in explorados[:etapa]:
                cx = x0+col*CELULA+CELULA//2
                cy = y0+lin*CELULA+CELULA//2
                pygame.draw.circle(tela, cor_explorado, (cx,cy), 6)

        # Cavalo
        pos = explorados[etapa] if etapa < len(explorados) else (caminho[-1] if caminho else inicio)
        cx, cy = x0+pos[1]*CELULA+CELULA//2, y0+pos[0]*CELULA+CELULA//2
        tela.blit(cavalo_img, (cx-cavalo_img.get_width()//2, cy-cavalo_img.get_height()//2))

        # Caminho final
        if not executando and caminho:
            for i,(lin,col) in enumerate(caminho):
                cx1 = x0+col*CELULA+CELULA//2
                cy1 = y0+lin*CELULA+CELULA//2
                pygame.draw.circle(tela, cor_caminho, (cx1,cy1), 10)
                num = fonte_passos.render(str(i+1), True, (0,0,0))
                tela.blit(num, (cx1 - num.get_width()//2, cy1 - num.get_height()//2))
                if i < len(caminho)-1:
                    lin2,col2 = caminho[i+1]
                    cx2 = x0+col2*CELULA+CELULA//2
                    cy2 = y0+lin2*CELULA+CELULA//2
                    pygame.draw.line(tela,(255,255,0),(cx1,cy1),(cx2,cy2),4)
            txt=f"Caminho final: {' → '.join([f'{letras[c]}{8-l}' for l,c in caminho])}"
            tela.blit(fonte_caminho.render(txt,True,(0,0,0)),(MARGEM_EXTERNA,ALTURA-30))

        pygame.display.flip()
        clock.tick(30)
        time.sleep(velocidade)
        if etapa < len(explorados): etapa += 1

    pygame.quit()
