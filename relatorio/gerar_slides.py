"""Gera apresentacao .pptx com base no relatorio."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

PRIMARY = RGBColor(0x1F, 0x3A, 0x68)
ACCENT = RGBColor(0x2E, 0x86, 0xAB)
LIGHT = RGBColor(0xEE, 0xF3, 0xF8)
DARK = RGBColor(0x22, 0x22, 0x22)
GRAY = RGBColor(0x66, 0x66, 0x66)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]


def add_title(slide, text, subtitle=None):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.9))
    tf = box.text_frame
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(16)
        p2.font.color.rgb = GRAY


def add_bar(slide):
    from pptx.enum.shapes import MSO_SHAPE
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.15), Inches(12.3), Inches(0.04))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()


def add_table(slide, data, left, top, width, height, header_color=PRIMARY, font_size=12, col_widths=None):
    rows = len(data)
    cols = len(data[0])
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    if col_widths:
        total = sum(col_widths)
        for i, w in enumerate(col_widths):
            table.columns[i].width = int(width * w / total)
    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = ""
            tf = cell.text_frame
            tf.margin_left = Inches(0.08)
            tf.margin_right = Inches(0.08)
            tf.margin_top = Inches(0.04)
            tf.margin_bottom = Inches(0.04)
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = str(data[r][c])
            run.font.size = Pt(font_size)
            if r == 0:
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_color
            else:
                run.font.color.rgb = DARK
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT if r % 2 == 0 else RGBColor(0xFF, 0xFF, 0xFF)
            p.alignment = PP_ALIGN.CENTER
    return table


def add_bullets(slide, bullets, left, top, width, height, font_size=16):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(font_size)
        p.font.color.rgb = DARK
        p.space_after = Pt(8)


# Slide 1 - Capa
s = prs.slides.add_slide(BLANK)
from pptx.enum.shapes import MSO_SHAPE
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = PRIMARY
bg.line.fill.background()

box = s.shapes.add_textbox(Inches(0.8), Inches(2.4), Inches(11.7), Inches(2.5))
tf = box.text_frame
p = tf.paragraphs[0]
p.text = "Teoria dos Grafos"
p.font.size = Pt(48)
p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

p2 = tf.add_paragraph()
p2.text = "Trabalho — Parte 1: Biblioteca de grafos"
p2.font.size = Pt(28)
p2.font.color.rgb = RGBColor(0xCF, 0xE2, 0xF3)
p2.space_before = Pt(12)

p3 = tf.add_paragraph()
p3.text = "COS 242 — 2025/2 | UFV"
p3.font.size = Pt(20)
p3.font.color.rgb = RGBColor(0xAE, 0xC6, 0xCF)
p3.space_before = Pt(20)


# Slide 2 - Decisoes de projeto
s = prs.slides.add_slide(BLANK)
add_title(s, "Decisões de projeto", "Arquitetura e convenções")
add_bar(s)
add_bullets(s, [
    "Python 3 + NumPy; arquitetura OO com interface comum (Graph)",
    "Duas implementações: GraphList e GraphMatrix",
    "Vértices indexados em 1..n",
    "Buscas iterativas (BFS com deque, DFS com pilha) — evita estouro de pilha",
    "DFS lexicograficamente determinística (empilha vizinhos em ordem reversa)",
    "Vértices não alcançados: parent = 0, level = -1",
    "Distâncias entre componentes distintas: ∞",
    "Self-loops e arestas duplicadas descartados na carga",
], Inches(0.7), Inches(1.5), Inches(12), Inches(5.5), font_size=18)


# Slide 3 - Viabilidade e ambiente
s = prs.slides.add_slide(BLANK)
add_title(s, "Viabilidade e ambiente", "Decisões que limitam medições")
add_bar(s)
add_bullets(s, [
    "Matriz de adjacência ocupa Θ(n²) bytes",
    "Para n > ~60 000 vértices, ultrapassa 3 GB",
    "Scripts marcam essas medições como INVIÁVEL em vez de travar a máquina",
    "",
    "Ambiente: Windows 11, Python 3.14, NumPy 2.4",
    "Tempos com time.perf_counter()",
    "Medidas excluem I/O (carga e escrita)",
], Inches(0.7), Inches(1.5), Inches(12), Inches(5.5), font_size=18)


# Slide 4 - EC1 Memoria
s = prs.slides.add_slide(BLANK)
add_title(s, "EC1 — Memória das duas representações", "Lista vs. matriz de adjacência")
add_bar(s)
data = [
    ["grafo", "n", "m", "lista (MB)", "matriz (MB)", "razão"],
    ["grafo_1", "10 000", "109 921", "10,6", "95,4", "9,0×"],
    ["grafo_2", "49 948", "1 298 710", "110,2", "2 152,7", "19,5×"],
    ["grafo_3", "375 000", "765 615", "99,4", "INVIÁVEL", "–"],
    ["grafo_4", "375 000", "8 186 986", "757,1", "INVIÁVEL", "–"],
    ["grafo_5", "4 843 750", "13 168 911", "1 591,5", "INVIÁVEL", "–"],
    ["grafo_6", "4 843 750", "46 469 479", "4 584,3", "INVIÁVEL", "–"],
]
add_table(s, data, Inches(0.6), Inches(1.4), Inches(8.5), Inches(3.6), font_size=12)
add_bullets(s, [
    "Matriz: Θ(n²)",
    "Lista: Θ(n + m)",
    "Razão cresce com n: 9× → 19,5×",
    "Para grafos reais, a lista é praticamente obrigatória",
], Inches(9.4), Inches(1.5), Inches(3.7), Inches(5), font_size=15)


# Slide 5 - EC2 BFS
s = prs.slides.add_slide(BLANK)
add_title(s, "EC2 — Tempo médio de 100 BFSs", "Lista vs. matriz")
add_bar(s)
data = [
    ["grafo", "n", "m", "lista (ms)", "matriz (ms)"],
    ["grafo_1", "10 000", "109 921", "8,61", "38,94"],
    ["grafo_2", "49 948", "1 298 710", "61,28", "188,98"],
    ["grafo_3", "375 000", "765 615", "240,59", "INVIÁVEL"],
    ["grafo_4", "375 000", "8 186 986", "855,27", "INVIÁVEL"],
    ["grafo_5", "4 843 750", "13 168 911", "3 117,54", "INVIÁVEL"],
    ["grafo_6", "4 843 750", "46 469 479", "7 812,81", "INVIÁVEL"],
]
add_table(s, data, Inches(0.6), Inches(1.4), Inches(8.5), Inches(3.6), font_size=12)
add_bullets(s, [
    "BFS é Θ(n + m) em ambas",
    "Matriz tem fator constante pior: varre n elementos por vértice",
    "Lista escala linearmente com (n + m)",
    "grafo_6 (~46M arestas): ~7,8 s — aceitável",
], Inches(9.4), Inches(1.5), Inches(3.7), Inches(5), font_size=14)


# Slide 6 - EC3 DFS
s = prs.slides.add_slide(BLANK)
add_title(s, "EC3 — Tempo médio de 100 DFSs", "Lista vs. matriz")
add_bar(s)
data = [
    ["grafo", "n", "m", "lista (ms)", "matriz (ms)"],
    ["grafo_1", "10 000", "109 921", "16,86", "47,55"],
    ["grafo_2", "49 948", "1 298 710", "137,33", "247,49"],
    ["grafo_3", "375 000", "765 615", "483,47", "INVIÁVEL"],
    ["grafo_4", "375 000", "8 186 986", "3 125,23", "INVIÁVEL"],
    ["grafo_5", "4 843 750", "13 168 911", "4 695,80", "INVIÁVEL"],
    ["grafo_6", "4 843 750", "46 469 479", "19 205,32", "INVIÁVEL"],
]
add_table(s, data, Inches(0.6), Inches(1.4), Inches(8.5), Inches(3.6), font_size=12)
add_bullets(s, [
    "Mesma complexidade da BFS",
    "Fator constante 2-3× maior",
    "Otimização: guardar pai em array antes do push",
    "grafo_4: 25 s → 3 s (ganho de ~8×)",
], Inches(9.4), Inches(1.5), Inches(3.7), Inches(5), font_size=14)


# Slide 7 - EC4 Pais (parte 1: grafos 1, 2, 3)
s = prs.slides.add_slide(BLANK)
add_title(s, "EC4 — Pais nos vértices 10, 20, 30", "Árvores BFS e DFS — grafos 1, 2 e 3")
add_bar(s)
data = [
    ["grafo", "alg", "raiz", "pai(10)", "pai(20)", "pai(30)"],
    ["grafo_1", "BFS", "1", "2042", "8382", "2394"],
    ["grafo_1", "DFS", "1", "709", "666", "86"],
    ["grafo_1", "BFS", "2", "8935", "9071", "3555"],
    ["grafo_1", "DFS", "2", "709", "666", "86"],
    ["grafo_1", "BFS", "3", "7685", "9543", "5783"],
    ["grafo_1", "DFS", "3", "709", "666", "86"],
    ["grafo_2", "BFS", "2", "1351", "–", "–"],
    ["grafo_2", "DFS", "2", "3946", "–", "–"],
    ["grafo_2", "BFS", "3", "–", "46738", "12999"],
    ["grafo_2", "DFS", "3", "–", "217", "3513"],
    ["grafo_3", "BFS", "1", "–", "–", "141597"],
    ["grafo_3", "DFS", "2", "192218", "141526", "–"],
    ["grafo_3", "BFS", "3", "158403", "319691", "–"],
]
add_table(s, data, Inches(0.6), Inches(1.4), Inches(7.5), Inches(5.6), font_size=11)
add_bullets(s, [
    "DFS no grafo_1: mesmos pais (709, 666, 86) p/ qualquer raiz",
    "Determinismo lexicográfico: desce pela 'espinha' de menor id",
    "",
    "'–' = vértice em outra componente",
    "grafo_2: 10 componentes desbalanceadas alteram resultado",
], Inches(8.4), Inches(1.5), Inches(4.7), Inches(5), font_size=14)


# Slide 8 - EC4 Pais (parte 2: grafos 4, 5, 6)
s = prs.slides.add_slide(BLANK)
add_title(s, "EC4 — Pais nos vértices 10, 20, 30", "Árvores BFS e DFS — grafos 4, 5 e 6")
add_bar(s)
data = [
    ["grafo", "alg", "raiz", "pai(10)", "pai(20)", "pai(30)"],
    ["grafo_4", "BFS", "1", "243865", "370783", "136244"],
    ["grafo_4", "DFS", "1", "12269", "10738", "1531"],
    ["grafo_5", "BFS", "1", "1888350", "–", "2502539"],
    ["grafo_5", "DFS", "1", "1888350", "–", "191713"],
    ["grafo_5", "BFS", "3", "1888350", "–", "191713"],
    ["grafo_5", "DFS", "3", "1888350", "–", "2502539"],
    ["grafo_6", "BFS", "2", "1677854", "3607226", "3898629"],
    ["grafo_6", "DFS", "2", "381031", "431008", "446011"],
]
add_table(s, data, Inches(0.6), Inches(1.4), Inches(8.0), Inches(4.5), font_size=12)
add_bullets(s, [
    "Vários pares raiz/destino caem em componentes distintas",
    "BFS e DFS retornam pais diferentes — caminhos distintos",
    "Consistente com EC6 (componentes)",
], Inches(8.9), Inches(1.5), Inches(4.2), Inches(5), font_size=14)


# Slide 9 - EC5 Distancias
s = prs.slides.add_slide(BLANK)
add_title(s, "EC5 — Distâncias entre pares", "(10,20), (10,30), (20,30)")
add_bar(s)
data = [
    ["grafo", "n", "d(10,20)", "d(10,30)", "d(20,30)"],
    ["grafo_1", "10 000", "3", "3", "4"],
    ["grafo_2", "49 948", "∞", "∞", "3"],
    ["grafo_3", "375 000", "9", "∞", "∞"],
    ["grafo_4", "375 000", "4", "3", "4"],
    ["grafo_5", "4 843 750", "∞", "9", "∞"],
    ["grafo_6", "4 843 750", "5", "5", "5"],
]
add_table(s, data, Inches(0.6), Inches(1.4), Inches(8.5), Inches(3.8), font_size=13)
add_bullets(s, [
    "∞ = componentes distintas (cruza com EC6)",
    "Distâncias finitas sempre ≤ 9",
    "",
    "Efeito small world:",
    "vértices conectados estão a poucos passos",
], Inches(9.4), Inches(1.5), Inches(3.7), Inches(5), font_size=15)


# Slide 10 - EC6 Componentes
s = prs.slides.add_slide(BLANK)
add_title(s, "EC6 — Componentes conexas", "Quantidade, maior, menor e tempo")
add_bar(s)
data = [
    ["grafo", "n", "nº comp.", "maior", "menor", "tempo (s)"],
    ["grafo_1", "10 000", "1", "10 000", "10 000", "0,01"],
    ["grafo_2", "49 948", "10", "25 000", "48", "0,22"],
    ["grafo_3", "375 000", "2", "250 000", "125 000", "0,43"],
    ["grafo_4", "375 000", "2", "250 000", "125 000", "1,71"],
    ["grafo_5", "4 843 750", "5", "2 500 000", "156 250", "9,03"],
    ["grafo_6", "4 843 750", "5", "2 500 000", "156 250", "18,57"],
]
add_table(s, data, Inches(0.6), Inches(1.4), Inches(8.5), Inches(3.8), font_size=12)
add_bullets(s, [
    "Tamanhos em progressão geométrica (~/2)",
    "Soma fecha exatamente com n",
    "→ geração sintética determinística",
    "",
    "grafo_3 ≡ grafo_4 (mesmas componentes)",
    "grafo_5 ≡ grafo_6 (densidade muda)",
], Inches(9.4), Inches(1.5), Inches(3.7), Inches(5), font_size=14)


# Slide 11 - EC7 Diametro
s = prs.slides.add_slide(BLANK)
add_title(s, "EC7 — Diâmetro", "Exato vs. aproximação por double sweep")
add_bar(s)
data = [
    ["grafo", "n", "exato", "tempo exato (s)", "aprox", "tempo aprox (s)"],
    ["grafo_1", "10 000", "5", "82,59", "4", "0,08"],
    ["grafo_2", "49 948", "INVIÁVEL", "–", "20", "1,75"],
    ["grafo_3", "375 000", "INVIÁVEL", "–", "20", "4,65"],
    ["grafo_4", "375 000", "INVIÁVEL", "–", "5", "16,50"],
    ["grafo_5", "4 843 750", "INVIÁVEL", "–", "59", "95,51"],
    ["grafo_6", "4 843 750", "INVIÁVEL", "–", "19", "207,00"],
]
add_table(s, data, Inches(0.5), Inches(1.4), Inches(8.6), Inches(3.8), font_size=12)
add_bullets(s, [
    "Exato: Θ(n·(n+m)) — proibitivo",
    "Aproximação: limite inferior",
    "grafo_1: aprox 4 vs. exato 5",
    "(~1000× mais rápido)",
    "",
    "grafo_5 (13M arestas): ≈ 59",
    "grafo_6 (46M arestas): ≈ 19",
    "→ densidade domina o diâmetro",
], Inches(9.3), Inches(1.4), Inches(3.8), Inches(5.8), font_size=13)


# Slide 12 - Conclusao
s = prs.slides.add_slide(BLANK)
add_title(s, "Conclusão", "Principais aprendizados")
add_bar(s)
add_bullets(s, [
    "Escolha de representação importa: matriz é elegante mas só prática para grafos pequenos",
    "Iteratividade é obrigatória: recursão estoura a pilha em milhões de vértices",
    "Algoritmos aproximados para diâmetro são o único caminho viável em grafos grandes",
    "Double sweep simples já oferece excelente limite inferior em milissegundos",
    "Grafos de teste exibem padrão geométrico — sugere geração sintética controlada",
    "grafo_5/grafo_6 compartilham vértices: permite isolar efeito da densidade no diâmetro",
], Inches(0.7), Inches(1.5), Inches(12), Inches(5.5), font_size=18)


# Slide 13 - Obrigado
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = PRIMARY
bg.line.fill.background()

box = s.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.7), Inches(2.5))
tf = box.text_frame
p = tf.paragraphs[0]
p.text = "Obrigado!"
p.font.size = Pt(60)
p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p.alignment = PP_ALIGN.CENTER

p2 = tf.add_paragraph()
p2.text = "Perguntas?"
p2.font.size = Pt(28)
p2.font.color.rgb = RGBColor(0xCF, 0xE2, 0xF3)
p2.alignment = PP_ALIGN.CENTER
p2.space_before = Pt(20)


out = r"c:\Users\lucas\OneDrive\Desktop\UFV\TEORIA DOS GRAFOS\TRABALHO\relatorio\apresentacao.pptx"
prs.save(out)
print("Salvo em:", out)
