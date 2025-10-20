# =============================================================
# interface_grafica.py — Interface otimizada com comparação H₁ × H₂
# =============================================================

import os, time, math, pygame, io, sys
from src.tabuleiro import Tabuleiro, Terreno
from src.busca_a_estrela import busca_a_estrela

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
    """Tela inicial para escolher a heurística antes da execução."""
    pygame.init()
    largura, altura = 820, 540
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Seleção de Heurística")

    fonte_titulo = pygame.font.SysFont("Arial", 36, bold=True)
    fonte_botao = pygame.font.SysFont("Arial", 22, bold=True)

    botoes = {
        "h1": pygame.Rect(largura//2 - 230, 170, 460, 60),
        "h2": pygame.Rect(largura//2 - 230, 260, 460, 60),
        "nula": pygame.Rect(largura//2 - 230, 350, 460, 60),
        "comparar": pygame.Rect(largura//2 - 230, 440, 460, 60),
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
        tela.blit(titulo, (largura//2 - titulo.get_width()//2, 70))

        for heur, rect in botoes.items():
            hover = rect.collidepoint(pygame.mouse.get_pos())
            cor = (120, 160, 240) if hover else (80, 120, 200)
            pygame.draw.rect(tela, cor, rect, border_radius=15)
            texto = fonte_botao.render({
                "h1": "H1 - Fraca (Distância × Custo Mínimo)",
                "h2": "H2 - Forte (Movimentos × Custo Mínimo)",
                "nula": "Sem Heurística (Dijkstra)",
                "comparar": "Comparar H1 × H2 (modo visual)"
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


# ------------------- RELATÓRIO SOBREPOSTO (com rolagem) -------------------
def mostrar_relatorio_sobreposto(tela, tabuleiro, caminho, custo, heuristica):
    from src.relatorio_custos import gerar_relatorio_caminho
    fonte = pygame.font.SysFont("Consolas", 14)
    fonte_titulo = pygame.font.SysFont("Arial", 24, bold=True)
    largura, altura = tela.get_size()
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
                if e.key == pygame.K_UP: scroll_y += 20
                elif e.key == pygame.K_DOWN: scroll_y -= 20
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if botao_rect.collidepoint(e.pos):
                    rodando = False

        tela.fill(cor_fundo)
        titulo = fonte_titulo.render("Relatório Analítico do Caminho", True, (0,0,0))
        tela.blit(titulo, (largura//2 - titulo.get_width()//2, 20))
        y = 70 + scroll_y
        for linha in linhas:
            txt = fonte.render(linha, True, cor_texto)
            tela.blit(txt, (40, y))
            y += 20
        mouse = pygame.mouse.get_pos()
        cor = cor_botao_hover if botao_rect.collidepoint(mouse) else cor_botao
        pygame.draw.rect(tela, cor, botao_rect, border_radius=10)
        txt_btn = fonte_titulo.render("Voltar", True, (255,255,255))
        tela.blit(txt_btn, (botao_rect.centerx - txt_btn.get_width()//2,
                            botao_rect.centery - txt_btn.get_height()//2))
        pygame.display.flip()
        clock.tick(30)


# ------------------- MODO COMPARATIVO H₁ × H₂ -------------------
def comparar_heuristicas(tabuleiro: Tabuleiro, inicio, objetivo, velocidade=0.35):
    import heapq
    from src.busca_a_estrela import No, reconstruir_caminho, heuristica_h1, heuristica_h2
    from src.cavalo import Cavalo

    pygame.init()
    largura_total, altura_total = 1150, 700
    tela = pygame.display.set_mode((largura_total, altura_total))
    pygame.display.set_caption("Comparativo de Heurísticas — H1 × H2")

    fonte_titulo = pygame.font.SysFont("Arial", 24, bold=True)
    fonte_info = pygame.font.SysFont("Arial", 18, bold=True)
    rel_font = pygame.font.SysFont("Arial", 22, bold=True)
    clock = pygame.time.Clock()

    celula = 48
    margem = 40
    offset_y = 100
    largura_tab = 8 * celula
    imgs = carregar_imagens_terreno(celula)
    cavalo_img = carregar_cavalo()

    # --- Função de busca padrão para ambas as heurísticas ---
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
                if tab.bloqueado(viz): continue
                novo_g = atual.g + tab.custo(viz)
                if viz not in g or novo_g < g[viz]:
                    g[viz] = novo_g
                    h = heur(viz, objetivo, tab)
                    f = novo_g + h
                    heapq.heappush(fila, No(f, viz, novo_g, h, pos))
                    pais[viz] = pos
        return [], float("inf"), explorados

    # --- Executa buscas e mede tempo ---
    t0 = time.time()
    caminho_h1, custo_h1, expl_h1 = executar_busca(tabuleiro, heuristica_h1)
    tempo_h1 = time.time() - t0

    t0 = time.time()
    caminho_h2, custo_h2, expl_h2 = executar_busca(tabuleiro, heuristica_h2)
    tempo_h2 = time.time() - t0

    # --- Loop de animação ---
    etapa, max_etapas = 0, max(len(expl_h1), len(expl_h2))
    rodando = True
    terminou = False

    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False

        tela.fill((240,240,240))
        pygame.draw.rect(tela, (30,30,30), (0,0,largura_total,60))
        titulo = fonte_titulo.render("Comparação Visual — H1 (esquerda) × H2 (direita)", True, (255,255,255))
        tela.blit(titulo, (largura_total//2 - titulo.get_width()//2, 15))

        # --- Função auxiliar de desenho de tabuleiro ---
        def desenhar_tab(x_offset, explorados, caminho, label, cor_titulo):
            titulo = fonte_titulo.render(label, True, cor_titulo)
            tela.blit(titulo, (x_offset + largura_tab//2 - titulo.get_width()//2, 70))
            for lin in range(8):
                for col in range(8):
                    cor = (238,238,210) if (lin+col)%2==0 else (118,150,86)
                    pygame.draw.rect(tela, cor, (x_offset+col*celula, offset_y+lin*celula, celula, celula))
                    img = imgs.get(tabuleiro.grade[lin][col])
                    if img:
                        tela.blit(img, (x_offset+col*celula, offset_y+lin*celula))
            for (lin,col) in explorados[:min(etapa, len(explorados))]:
                cx = x_offset + col*celula + celula//2
                cy = offset_y + lin*celula + celula//2
                pygame.draw.circle(tela, (255,0,0), (cx,cy), 5)
            pygame.draw.rect(tela, (0,200,0),
                             (x_offset+inicio[1]*celula+4, offset_y+inicio[0]*celula+4, celula-8, celula-8))
            pygame.draw.rect(tela, (200,0,0),
                             (x_offset+objetivo[1]*celula+4, offset_y+objetivo[0]*celula+4, celula-8, celula-8))
            pos = explorados[min(etapa, len(explorados)-1)] if explorados else inicio
            cx = x_offset + pos[1]*celula + celula//2
            cy = offset_y + pos[0]*celula + celula//2
            if cavalo_img:
                img_r = pygame.transform.scale(cavalo_img, (celula-6, celula-6))
                tela.blit(img_r, (cx - img_r.get_width()//2, cy - img_r.get_height()//2))
            if terminou:
                for i,(lin,col) in enumerate(caminho):
                    cx1 = x_offset + col*celula + celula//2
                    cy1 = offset_y + lin*celula + celula//2
                    pygame.draw.circle(tela, (255,255,0), (cx1, cy1), 7)
                    if i < len(caminho)-1:
                        lin2,col2 = caminho[i+1]
                        cx2 = x_offset + col2*celula + celula//2
                        cy2 = offset_y + lin2*celula + celula//2
                        pygame.draw.line(tela, (255,255,0), (cx1,cy1),(cx2,cy2),3)

        # --- Desenha ambos os tabuleiros ---
        desenhar_tab(margem, expl_h1, caminho_h1, "H1 - Fraca", (60,120,255))
        desenhar_tab(margem + largura_tab + 80, expl_h2, caminho_h2, "H2 - Forte", (255,120,60))

        # --- Informações de desempenho ---
        info1 = f"H1 → Custo: {custo_h1:.2f} | Nós: {len(expl_h1)} | Tempo: {tempo_h1:.3f}s"
        info2 = f"H2 → Custo: {custo_h2:.2f} | Nós: {len(expl_h2)} | Tempo: {tempo_h2:.3f}s"
        tela.blit(fonte_info.render(info1, True, (30,30,30)), (largura_total//2 - 250, altura_total - 70))
        tela.blit(fonte_info.render(info2, True, (30,30,30)), (largura_total//2 - 250, altura_total - 45))

        pygame.display.flip()
        clock.tick(30)
        time.sleep(velocidade)

        if not terminou:
            etapa += 1
            if etapa >= max_etapas:
                terminou = True
                etapa = max_etapas

        # --- Após terminar, mostra relatório final e botão ---
        if terminou:
            # cálculo comparativo
            ganho_nos = 100 * (1 - len(expl_h2) / len(expl_h1)) if len(expl_h1) else 0
            ganho_tempo = 100 * (1 - tempo_h2 / tempo_h1) if tempo_h1 else 0
            rel1 = f"H2 expandiu {abs(ganho_nos):.1f}% {'menos' if ganho_nos>0 else 'mais'} nós"
            rel2 = f"H2 foi {abs(ganho_tempo):.1f}% {'mais rápida' if ganho_tempo>0 else 'mais lenta'} que H1"

            botao_rect = pygame.Rect(largura_total//2 - 100, altura_total - 100, 200, 45)
            rodando_relatorio = True
            while rodando_relatorio:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        rodando_relatorio = rodando = False
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        if botao_rect.collidepoint(e.pos):
                            rodando_relatorio = False

                pygame.draw.rect(tela, (245,245,245), (0, altura_total - 180, largura_total, 180))
                linha1 = rel_font.render("=== RESULTADO COMPARATIVO ===", True, (0,0,0))
                linha2 = rel_font.render(rel1, True, (40,40,40))
                linha3 = rel_font.render(rel2, True, (40,40,40))
                tela.blit(linha1, (largura_total//2 - linha1.get_width()//2, altura_total - 160))
                tela.blit(linha2, (largura_total//2 - linha2.get_width()//2, altura_total - 120))
                tela.blit(linha3, (largura_total//2 - linha3.get_width()//2, altura_total - 85))

                cor_btn = (100,150,230) if botao_rect.collidepoint(pygame.mouse.get_pos()) else (80,120,200)
                pygame.draw.rect(tela, cor_btn, botao_rect, border_radius=10)
                txt_btn = rel_font.render("Voltar", True, (255,255,255))
                tela.blit(txt_btn, (botao_rect.centerx - txt_btn.get_width()//2,
                                    botao_rect.centery - txt_btn.get_height()//2))
                pygame.display.flip()
                clock.tick(30)
            rodando = False

    pygame.quit()


# ------------------- INTERFACE PRINCIPAL -------------------
def mostrar_busca_animada(tabuleiro: Tabuleiro, inicio, objetivo, velocidade=VELOCIDADE_PADRAO):
    from src.gerador_tabuleiro import gerar_tabuleiro_aleatorio

    tipo_heuristica = selecionar_heuristica()
    print(f"\nHeurística escolhida: {tipo_heuristica.upper()}")
    if tipo_heuristica == "comparar":
        comparar_heuristicas(tabuleiro, inicio, objetivo)
        return

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Caminho do Cavalo - A* (interface interativa)")
    fonte_status = pygame.font.SysFont("Arial", 18, bold=True)
    fonte_rotulo = pygame.font.SysFont("Arial", 18, bold=True)
    fonte_passos = pygame.font.SysFont("Arial", 22, bold=True)
    fonte_caminho = pygame.font.SysFont("Consolas", 18)
    imgs_terreno = carregar_imagens_terreno(CELULA)
    img_cavalo = carregar_cavalo()

    cor_inicio, cor_objetivo = (0,200,0), (200,0,0)
    cor_caminho, cor_explorado = (255,255,0), (220,0,0)
    x0, y0 = origem_tabuleiro()
    clock = pygame.time.Clock()

    caminho, custo, explorados, fronteira = busca_a_estrela_animado(tabuleiro, inicio, objetivo, tipo_heuristica)
    etapa, rodando = 0, True
    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: rodando = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                tabuleiro = gerar_tabuleiro_aleatorio()
                caminho, custo, explorados, fronteira = busca_a_estrela_animado(tabuleiro, inicio, objetivo, tipo_heuristica)
                etapa = 0
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and not etapa < len(explorados):
                mostrar_relatorio_sobreposto(tela, tabuleiro, caminho, custo, heuristica=tipo_heuristica)
        tela.fill((255,255,255))
        executando = etapa < len(explorados)
        pygame.draw.rect(tela, (20,20,20), (0,0,LARGURA,BARRA_STATUS_H))
        msg = f"Heurística {tipo_heuristica.upper()}  |  {'Executando...' if executando else 'Concluído!'}  |  Nós: {etapa}/{len(explorados)}  |  Custo: {custo:.2f}"
        texto = fonte_status.render(msg, True, (255,255,255))
        tela.blit(texto, (MARGEM_EXTERNA, (BARRA_STATUS_H - texto.get_height())//2))

        for lin in range(BOARD_N):
            for col in range(BOARD_N):
                cor = (238,238,210) if (lin+col)%2==0 else (118,150,86)
                pygame.draw.rect(tela, cor, (x0+col*CELULA, y0+lin*CELULA, CELULA, CELULA))
                img = imgs_terreno.get(tabuleiro.grade[lin][col])
                if img: tela.blit(img, (x0 + col*CELULA, y0 + lin*CELULA))
        if executando:
            for (lin,col) in explorados[:etapa]:
                cx = x0 + col*CELULA + CELULA//2
                cy = y0 + lin*CELULA + CELULA//2
                pygame.draw.circle(tela, cor_explorado, (cx, cy), 6)

        pygame.draw.rect(tela, cor_inicio,(x0 + inicio[1]*CELULA + 6, y0 + inicio[0]*CELULA + 6, CELULA-12, CELULA-12))
        pygame.draw.rect(tela, cor_objetivo,(x0 + objetivo[1]*CELULA + 6, y0 + objetivo[0]*CELULA + 6, CELULA-12, CELULA-12))
        pos = explorados[etapa] if etapa < len(explorados) else (caminho[-1] if caminho else inicio)
        cx, cy = x0 + pos[1]*CELULA + CELULA//2, y0 + pos[0]*CELULA + CELULA//2
        tela.blit(img_cavalo, (cx - img_cavalo.get_width()//2, cy - img_cavalo.get_height()//2))

        if not executando and caminho:
            for i,(lin,col) in enumerate(caminho):
                cx1 = x0 + col*CELULA + CELULA//2
                cy1 = y0 + lin*CELULA + CELULA//2
                pygame.draw.circle(tela, cor_caminho, (cx1, cy1), 10)
                num = fonte_passos.render(str(i+1), True, (0,0,0))
                tela.blit(num, (cx1 - num.get_width()//2, cy1 - num.get_height()//2))
                if i < len(caminho)-1:
                    lin2,col2 = caminho[i+1]
                    cx2 = x0 + col2*CELULA + CELULA//2
                    cy2 = y0 + lin2*CELULA + CELULA//2
                    pygame.draw.line(tela, (255,255,0), (cx1,cy1),(cx2,cy2),4)
            letras = ["A","B","C","D","E","F","G","H"]
            caminho_texto = " → ".join([f"{letras[c]}{8-l}" for l,c in caminho])
            tela.blit(fonte_caminho.render(f"Caminho final: {caminho_texto}", True, (0,0,0)), (MARGEM_EXTERNA, ALTURA - 30))

        pygame.display.flip()
        clock.tick(30)
        time.sleep(velocidade)
        if etapa < len(explorados): etapa += 1

    pygame.quit()
