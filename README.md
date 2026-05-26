# Trabalho de Teoria dos Grafos — Partes 1 e 2

Biblioteca em Python 3 para representação e análise de grafos não-direcionados, desenvolvida para a disciplina **COS 242 — Teoria dos Grafos (2025/2)** da Universidade Federal de Viçosa.

Implementa duas representações (lista e matriz de adjacência) sob uma interface comum, e os algoritmos:

- **Parte 1**: BFS, DFS, componentes conexas, distâncias (não-ponderadas) e diâmetro.
- **Parte 2**: grafos com pesos reais nas arestas e algoritmo de **Dijkstra em duas formas** (vetor Θ(V²) e heap O((V+E) log V) com lazy deletion). Detecção e recusa de pesos negativos. Suporte a rótulos de vértices (`nome → id`) para a rede de colaboração entre pesquisadores.

## Estrutura do projeto

```
TRABALHO/
├── src/                    # Biblioteca
│   ├── graph_base.py       # interface abstrata Graph
│   ├── graph_list.py       # lista de adjacência
│   ├── graph_matrix.py     # matriz de adjacência (numpy bool)
│   ├── algorithms.py       # BFS, DFS, componentes, distâncias, diâmetro
│   └── io_utils.py         # leitura de grafos e geração de relatórios
├── estudos/                # Estudos de caso (EC1 a EC7)
│   ├── ec1_memoria.py
│   ├── ec2_tempo_bfs.py
│   ├── ...
│   └── run_all.py          # roda todos os estudos em sequência
├── exemplos/               # Grafos pequenos para teste
├── GRAFOS/                 # Grafos de teste (NÃO incluídos no repo — ver abaixo)
├── saidas/                 # Saídas geradas pelo main.py
├── relatorio/
│   ├── relatorio.md        # Relatório completo com análise dos resultados
│   └── resultados/         # CSVs/MDs gerados pelos estudos de caso
└── main.py                 # Demo: lê um grafo de exemplo e roda BFS/DFS
```

## Requisitos

- Python 3.10+
- NumPy

```bash
pip install numpy
```

## Arquivos de grafo

As pastas `GRAFOS/` (Parte 1) e `GRAFOS 2/` (Parte 2) **não estão no repositório** (~2.5 GB no total). Para a Parte 1, baixe `grafo_1.txt` ... `grafo_6.txt` em `GRAFOS/`. Para a Parte 2, baixe `grafo_W_1.txt` ... `grafo_W_5.txt` em `GRAFOS 2/`, e `rede_colaboracao.txt` + `rede_colaboracao_vertices.txt` em `GRAFOS 2/REDES/`.

**Formato de entrada** (texto):
```
n
u1 v1 [w1]
u2 v2 [w2]
...
```
Onde `n` é o número de vértices e cada linha seguinte representa uma aresta entre `u` e `v`. A terceira coluna (peso `w`, real) é **opcional**: se presente, o grafo é ponderado; se ausente, é não-ponderado. O loader detecta o formato automaticamente.

## Como rodar

### Demo (grafo pequeno do PDF)

```bash
python main.py
```

Lê [exemplos/grafo_pdf.txt](exemplos/grafo_pdf.txt), descreve o grafo nas duas representações e roda BFS e DFS a partir do vértice 1. As árvores de busca são escritas em `saidas/`.

### Estudos de caso

```bash
# Roda todos os estudos
python estudos/run_all.py

# Roda apenas alguns
python estudos/run_all.py --only ec1 ec2

# Pula alguns
python estudos/run_all.py --skip ec7
```

Cada estudo gera um `.csv` e um `.md` em `relatorio/resultados/`.

| Estudo | Descrição |
|--------|-----------|
| EC1 | Memória das duas representações |
| EC2 | Tempo médio de 100 BFSs |
| EC3 | Tempo médio de 100 DFSs |
| EC4 | Pais nas árvores de BFS/DFS |
| EC5 | Distâncias entre pares de vértices |
| EC6 | Componentes conexas |
| EC7 | Diâmetro |
| EC8 | (Parte 2) Distância + caminho mínimo do vértice 10 → {20, 30, 40, 50, 60} nos grafos_W |
| EC9 | (Parte 2) Tempo médio de Dijkstra (vetor vs heap), k=100 fontes aleatórias |
| EC10 | (Parte 2) Rede de colaboração: distância de E. W. Dijkstra a outros pesquisadores |

Para rodar a Parte 2:

```bash
# Demo do grafo da figura 1 do PDF da Parte 2
python main_p2.py

# Estudos EC8+EC9 nos grafos_W (grandes graphs podem ser pulados com --max-n)
python estudos/ec_p2_runner.py --only 1 2 3

# Estudo separado para os grafos enormes (heap-only)
python estudos/ec_p2_runner_grandes.py --only 4 5

# Rede de colaboração
python estudos/ec10_rede_colaboracao.py
```

## Relatório

- Parte 1: [relatorio/relatorio.md](relatorio/relatorio.md)
- Parte 2: [relatorio/relatorio_P2.md](relatorio/relatorio_P2.md)

## Observações de implementação

- Vértices indexados em **1..n**.
- Buscas **iterativas** (BFS com `deque`, DFS com pilha explícita) para evitar estouro de pilha em grafos com milhões de vértices.
- DFS **lexicograficamente determinística** (vizinho de menor id é visitado primeiro).
- Vértices não alcançados em uma busca recebem `parent = 0` e `level = -1`.
- Distâncias entre vértices em componentes diferentes são reportadas como `∞`.
- Self-loops e arestas duplicadas são descartados na carga.
- A matriz de adjacência é marcada como **INVIÁVEL** para grafos com mais de ~60.000 vértices (Θ(n²) bytes).
