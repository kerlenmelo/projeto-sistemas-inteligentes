# Caminho Tático com Cavalo no Xadrez — Etapa 1 (Requisitos + Critérios)

> Versão: 2025-10-18 18:46  
> Escopo desta etapa: **fixar requisitos, critérios de aceitação e entregáveis** do projeto, com base no PDF anexado *“Projeto_ Caminho Tático com Cavalo no Xadrez.pdf”*. Nada de implementação ainda — só alinhar exatamente **o que** será entregue e **quando consideramos pronto**.

---

## 1) Visão Geral do Projeto
Implementar o **A\*** para encontrar o **caminho de menor custo total** para a peça **Cavalo** em um **tabuleiro 8×8** com **tipos de terreno**. O custo acumulado do caminho é a **soma dos custos de terreno de todas as casas visitadas** (o custo é para **entrar** na casa). Há **barreiras** (proibidas). O projeto exige **duas heurísticas admissíveis (H1 e H2)** e uma **interface gráfica** com duas frentes: **visualização estática do resultado** e **visualização dinâmica da busca**. Ao final, produzir **análise/relatório** com evidências e **apresentação em sala**.

---

## 2) Regras do Domínio (Problema)
- **Tabuleiro:** 8×8 (coordenadas inteiras).  
- **Peça:** **Cavalo**, movimentos em “L” (até 8 vizinhos válidos).  
- **Terrenos e custos típicos (exemplos do PDF):**
  - **Estrada:** custo **0.5** (baixo).
  - **Terra:** custo **1.0** (padrão).
  - **Lama:** custo **5.0** (alto).
  - **Barreira:** **proibido** (custo ∞); casas **intransponíveis**.
- **Custo do caminho:** soma dos custos das casas **percorridas/entradas**.
- **Entrada do problema (por cenário):**
  - Mapa 8×8 com **tipo de terreno por casa** (e.g., arquivo JSON).
  - **Origem (x,y)** e **Destino (x,y)** para o Cavalo.
- **Saída esperada:**
  - Caminho ótimo (sequência de coordenadas) **ou “sem solução”** se bloqueado.
  - **Custo total** do caminho.
  - **Métricas da busca** (ver Seção 6).

---

## 3) Algoritmo de Busca
- Implementar **A\*** com avaliação **F(n) = G(n) + H(n)**.
- **G(n):** custo acumulado para alcançar **n** (somando custos de terreno ao entrar nas casas).
- **Suporte a bloqueios:** casas de **Barreira** não podem ser expandidas/entradas.
- **Reconstrução do caminho** ao encontrar o destino.
- **Fallback (validação):** executar com **H=0** (equivale a Dijkstra) para validar custo ótimo em cenários de teste.

---

## 4) Heurísticas (H1 e H2) — ambas **admissíveis**
- **H1 (genérica, simples):**
  - Distância **Manhattan** *ou* **Chebyshev** entre (x,y) e o objetivo **multiplicada pelo menor custo de terreno existente no tabuleiro** (p.ex., 0.5).  
  - Motivação: não considera a cinemática do cavalo — **subestima** o custo real, logo é admissível.
- **H2 (mais informativa, específica do cavalo):**
  - **Número mínimo de saltos do Cavalo** entre dois pontos **em tabuleiro vazio** × (menor custo de terreno).  
  - Motivação: aproxima o número real de saltos; multiplicar pelo menor custo garante **não superestimar**.
- **Requisito crítico:** **nenhuma heurística pode superestimar** o custo real (admissibilidade).

---

## 5) Interface Gráfica (GUI)
### A) Visualização **Estática** (resultado final)
- Renderizar o tabuleiro 8×8 com **cores por tipo de terreno** (legenda).
- Desenhar o **caminho ótimo** encontrado pelo A\*.
- Exibir **heatmap do G(n)** ao longo do caminho (e/ou sobre todo o tabuleiro).

### B) Visualização **Dinâmica** (processo da busca)
- Mostrar, por passo/iteração, **Lista Aberta** (candidatos) e **Lista Fechada** (expandidos).
- Controles: **play/pause**, **passo a passo** e **velocidade**.
- **Comparação H1 vs H2** (modo lado a lado ou alternância rápida) para evidenciar a **diferença de área de busca**.

---

## 6) Instrumentação e Métricas (para a análise)
Para **cada execução**:
- **Nós expandidos**.
- **Tempo de execução** (ms).
- **Tamanho máximo** das listas **Aberta** e **Fechada** (opcional, recomendado).
- **Custo do caminho**.
- **Comprimento do caminho** (nº de saltos).
- **Capturas de tela** da GUI (estática e dinâmica) quando aplicável.
- Exportar **CSV/JSON** com as métricas (por cenário/heurística).

---

## 7) Cenários de Teste (mínimos recomendados)
1. **Homogêneo (todas as casas = Terra 1.0)** — validação básica.
2. **Com “estradas” baratas** cercadas por terrenos mais caros — incentiva desvio ótimo.
3. **Região de lama (5.0)** forçando caminho alternativo.
4. **Barreiras** bloqueando rota direta (verificar “sem solução” e caminhos desviando).
5. Origem/Destino em **cantos** e no **centro** (variação de distâncias).
6. **Cenário de referência** para comparar H1 × H2 (screenshots e métricas).

---

## 8) Critérios de Aceitação (DoD — Definition of Done)
- **Correto:** A\* retorna **caminho ótimo** (ou “sem solução” quando apropriado).
- **Heurísticas:** H1 e H2 **implementadas, documentadas e admissíveis**, com breve justificativa.
- **Métricas:** logs/arquivos contendo **nós expandidos, tempo e custo** por execução.
- **GUI (Estática):** tabuleiro colorido + caminho + **legenda** + **heatmap de G**.
- **GUI (Dinâmica):** animação da busca com **Lista Aberta/Fechada** e controles de execução.
- **Comparação:** execução com **H1** e **H2** exibindo **diferenças** (visuais e métricas).
- **Relatório:** documento com **descrição do problema**, **provas/argumentos de admissibilidade**, **tabelas/gráficos** das métricas, **capturas** da GUI e **conclusões**.
- **Apresentação:** slides curtos e claros, prontos para apresentação em sala.

---

## 9) Entregáveis
- Código-fonte organizado (`src/`, `gui/`, `tests/`, `docs/`, `experiments/`).
- **Cenários** (ex.: `scenarios/*.json`) e **instruções de execução**.
- **Relatório (PDF)** com análises e capturas.
- **Slides** da apresentação.
- **README principal** (este arquivo) e um **Guia de Execução**.

---

## 10) Estrutura recomendada do repositório
```
.
├── README.md                # Este arquivo (requisitos+critérios)
├── src/                     # A*, heurísticas, domínio do problema
│   ├── board.py (ou .ts)    # tabuleiro, terrenos, custos, barreiras
│   ├── knight.py            # movimentos do cavalo (neighbors)
│   ├── astar.py             # núcleo do A*
│   ├── heuristics.py        # H1 e H2
│   └── instrumentation.py   # medição de métricas e logs
├── gui/                     # visualização estática e dinâmica
├── scenarios/               # mapas 8×8 em JSON + origem/destino
├── tests/                   # testes unitários e de integração
├── experiments/             # scripts para rodadas e coleta de métricas
└── docs/                    # relatório, figuras, slides
```

---

## 11) Checklist desta etapa (Etapa 1)
- [x] Requisitos funcionais e não funcionais listados.
- [x] Critérios de aceitação definidos (DoD).
- [x] Entregáveis e estrutura de repositório sugeridos.
- [x] Rascunho de cenários de teste.
- [x] Itens de instrumentação/métricas definidos.

---

## 12) Próximos passos (Etapa 2 sugerida)
- Criar `Board` (8×8), tipos de terreno e função `cost(x,y)` (com barreiras).
- Definir formato de **cenário** (JSON) e um **primeiro cenário de teste**.
- Escrever **testes unitários** iniciais para `cost()` e validação de barreiras.

> Quando marcar tudo acima como pronto, seguimos para a **Etapa 2** (modelagem do tabuleiro e custos).

