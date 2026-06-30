# Trabalho de Teoria dos Grafos — Parte 1
   
---

## 1. Decisões de projeto e implementação

A biblioteca foi implementada em **Python 3** (com NumPy para a matriz). Optou-se por uma arquitetura orientada a objetos com uma interface comum (`Graph`) e duas implementações concretas (`GraphList` e `GraphMatrix`), de modo que os algoritmos (BFS, DFS, componentes, distâncias e diâmetro) sejam escritos uma única vez sobre a interface e funcionem com qualquer representação.

**Estrutura do código:**
```
src/
├── graph_base.py        # interface abstrata Graph
├── graph_list.py        # lista de adjacência (list[list[int]])
├── graph_matrix.py      # matriz de adjacência (numpy bool)
├── algorithms.py        # BFS, DFS, componentes, distâncias, diâmetro
└── io_utils.py          # leitura de grafos e geração de relatórios
estudos/
├── ec1_memoria.py … ec7_diametro.py
└── run_all.py
```

**Convenções principais:**
- Vértices indexados em **1..n**.
- Buscas **iterativas** (BFS com `deque`, DFS com pilha explícita) para evitar estouro de pilha em grafos com milhões de vértices.
- DFS lexicograficamente **determinística**: empilha vizinhos em ordem reversa para que o de menor id seja o próximo visitado.
- Vértices não alcançados em uma busca recebem `parent = 0` e `level = -1`.
- Distâncias entre vértices em componentes distintas são reportadas como `∞`.
- Self-loops e arestas duplicadas no arquivo de entrada são descartados na carga (deduplicação por vértice).

**Decisão de viabilidade:** a matriz de adjacência ocupa Θ(n²) bytes; para grafos com mais de ~60.000 vértices ela passa de 3 GB. Os scripts dos estudos de caso reconhecem isso e marcam essas medições como `INVIÁVEL` em vez de tentar e travar a máquina.

**Ambiente das medições:** Windows 11, Python 3.14, NumPy 2.4. Todas as medidas de tempo usam `time.perf_counter()` e excluem o tempo de I/O (carga e escrita).

---

## 2. Estudos de caso

### EC1 — Memória das duas representações

| grafo | n | m | mem. lista (MB) | mem. matriz (MB) | razão |
|---|---:|---:|---:|---:|:---:|
| grafo_1 | 10 000 | 109 921 | 10,6 | 95,4 | 9,0× |
| grafo_2 | 49 948 | 1 298 710 | 110,2 | 2 152,7 | 19,5× |
| grafo_3 | 375 000 | 765 615 | 99,4 | INVIÁVEL | – |
| grafo_4 | 375 000 | 8 186 986 | 757,1 | INVIÁVEL | – |
| grafo_5 | 4 843 750 | 13 168 911 | 1 591,5 | INVIÁVEL | – |
| grafo_6 | 4 843 750 | 46 469 479 | 4 584,3 | INVIÁVEL | – |

**Discussão.** A matriz de adjacência ocupa Θ(n²) bytes independentemente do número de arestas, enquanto a lista ocupa Θ(n + m). Para o grafo_2 (50 mil vértices), a matriz já consome **2,1 GB** — quase 20× a lista. A partir do grafo_3 (375 mil vértices), a matriz exigiria ~140 GB e foi marcada como inviável. Note também que a vantagem da matriz **cresce com n**: a razão matriz/lista passou de 9,0× (grafo_1) para 19,5× (grafo_2) ao multiplicarmos n por 5. Para os grafos do mundo real, a lista é praticamente obrigatória.

---

### EC2 — Tempo médio de 100 BFSs

| grafo | n | m | BFS lista (ms) | BFS matriz (ms) |
|---|---:|---:|---:|---:|
| grafo_1 | 10 000 | 109 921 | 8,61 | 38,94 |
| grafo_2 | 49 948 | 1 298 710 | 61,28 | 188,98 |
| grafo_3 | 375 000 | 765 615 | 240,59 | INVIÁVEL |
| grafo_4 | 375 000 | 8 186 986 | 855,27 | INVIÁVEL |
| grafo_5 | 4 843 750 | 13 168 911 | 3 117,54 | INVIÁVEL |
| grafo_6 | 4 843 750 | 46 469 479 | 7 812,81 | INVIÁVEL |

**Discussão.** Em ambas as representações, BFS é Θ(n + m) — mas o **fator constante** é muito pior na matriz. Para visitar os vizinhos de um vértice na matriz é preciso varrer uma linha inteira (n elementos), mesmo que o vértice tenha grau pequeno; na lista basta percorrer os vizinhos de fato. No grafo_1 a matriz já é ~4,5× mais lenta que a lista; no grafo_2 (n = 50k) é ~3,1×. Para n ≥ 375k a matriz nem sequer cabe em memória, então a comparação não foi feita. Na lista o tempo cresce linearmente com (n + m): grafo_6 (~46M arestas) tem BFS médio de ~7,8 s — um custo aceitável dado o tamanho.

---

### EC3 — Tempo médio de 100 DFSs

| grafo | n | m | DFS lista (ms) | DFS matriz (ms) |
|---|---:|---:|---:|---:|
| grafo_1 | 10 000 | 109 921 | 16,86 | 47,55 |
| grafo_2 | 49 948 | 1 298 710 | 137,33 | 247,49 |
| grafo_3 | 375 000 | 765 615 | 483,47 | INVIÁVEL |
| grafo_4 | 375 000 | 8 186 986 | 3 125,23 | INVIÁVEL |
| grafo_5 | 4 843 750 | 13 168 911 | 4 695,80 | INVIÁVEL |
| grafo_6 | 4 843 750 | 46 469 479 | 19 205,32 | INVIÁVEL |

**Discussão.** A complexidade assintótica é a mesma da BFS, mas com **fator constante 2-3× maior**: a DFS empilha vizinhos em ordem reversa (para visitar o de menor id primeiro, garantindo determinismo) e o custo de manipulação da pilha cresce com m.

**Aprendizado de implementação.** Numa primeira versão da DFS, empilhávamos tuplas `(vertice, pai)`. Em grafos densos isso dispara milhões de alocações de tupla (cada tupla custa ~64 B em CPython). No grafo_4, isso resultava em ~25 s por busca. Trocando o esquema para *guardar o pai em um array antes do push e empilhar apenas o id do vértice*, o tempo caiu para ~3 s — ganho de **~8×**. Em grafos esparsos (grafo_3, grau médio 4) o ganho é desprezível, pois quase não há tuplas para alocar.

---

### EC4 — Pais dos vértices 10, 20, 30 nas árvores BFS e DFS (raízes 1, 2, 3)

| grafo | algoritmo | raiz | pai(10) | pai(20) | pai(30) |
|---|:---:|:---:|---:|---:|---:|
| grafo_1 | BFS | 1 | 2042 | 8382 | 2394 |
| grafo_1 | DFS | 1 | 709 | 666 | 86 |
| grafo_1 | BFS | 2 | 8935 | 9071 | 3555 |
| grafo_1 | DFS | 2 | 709 | 666 | 86 |
| grafo_1 | BFS | 3 | 7685 | 9543 | 5783 |
| grafo_1 | DFS | 3 | 709 | 666 | 86 |
| grafo_2 | BFS | 1 | – | – | – |
| grafo_2 | DFS | 1 | – | – | – |
| grafo_2 | BFS | 2 | 1351 | – | – |
| grafo_2 | DFS | 2 | 3946 | – | – |
| grafo_2 | BFS | 3 | – | 46738 | 12999 |
| grafo_2 | DFS | 3 | – | 217 | 3513 |
| grafo_3 | BFS | 1 | – | – | 141597 |
| grafo_3 | DFS | 1 | – | – | 141597 |
| grafo_3 | BFS | 2 | 158403 | 75471 | – |
| grafo_3 | DFS | 2 | 192218 | 141526 | – |
| grafo_3 | BFS | 3 | 158403 | 319691 | – |
| grafo_3 | DFS | 3 | 106718 | 141526 | – |
| grafo_4 | BFS | 1 | 243865 | 370783 | 136244 |
| grafo_4 | DFS | 1 | 12269 | 10738 | 1531 |
| grafo_4 | BFS | 2 | – | – | – |
| grafo_4 | DFS | 2 | – | – | – |
| grafo_4 | BFS | 3 | – | – | – |
| grafo_4 | DFS | 3 | – | – | – |
| grafo_5 | BFS | 1 | 1888350 | – | 2502539 |
| grafo_5 | DFS | 1 | 1888350 | – | 191713 |
| grafo_5 | BFS | 2 | – | – | – |
| grafo_5 | DFS | 2 | – | – | – |
| grafo_5 | BFS | 3 | 1888350 | – | 191713 |
| grafo_5 | DFS | 3 | 1888350 | – | 2502539 |
| grafo_6 | BFS | 1 | – | – | – |
| grafo_6 | DFS | 1 | – | – | – |
| grafo_6 | BFS | 2 | 1677854 | 3607226 | 3898629 |
| grafo_6 | DFS | 2 | 381031 | 431008 | 446011 |
| grafo_6 | BFS | 3 | – | – | – |
| grafo_6 | DFS | 3 | – | – | – |

**Discussão.** O traço `–` indica que o vértice de destino está em uma componente diferente da raiz (consistente com o EC6). Dois fenômenos chamam atenção:

1. **No grafo_1 a DFS retorna o mesmo pai (709, 666, 86) para qualquer raiz** entre 1, 2 e 3. Isso não é bug: como a DFS é lexicograficamente determinística, a busca rapidamente desce até a "espinha" formada pelos vértices de menor id (com vizinhos densos) e, dali em diante, percorre os mesmos caminhos independentemente da raiz inicial.

2. **No grafo_2, com 10 componentes desbalanceadas**, raízes diferentes alcançam vértices de destino diferentes. Por exemplo, partindo do vértice 1 (que está numa componente pequena), nenhum dos três alvos é atingido; partindo do vértice 3 (componente maior), 20 e 30 são atingidos mas 10 não.

---

### EC5 — Distâncias entre os pares (10, 20), (10, 30), (20, 30)

| grafo | n | d(10,20) | d(10,30) | d(20,30) |
|---|---:|:---:|:---:|:---:|
| grafo_1 | 10 000 | 3 | 3 | 4 |
| grafo_2 | 49 948 | ∞ | ∞ | 3 |
| grafo_3 | 375 000 | 9 | ∞ | ∞ |
| grafo_4 | 375 000 | 4 | 3 | 4 |
| grafo_5 | 4 843 750 | ∞ | 9 | ∞ |
| grafo_6 | 4 843 750 | 5 | 5 | 5 |

**Discussão.** O símbolo `∞` aparece exatamente quando os dois vértices estão em componentes distintas — confirmação cruzada com o EC6. Note que, mesmo nos grafos com milhões de vértices, as distâncias finitas são sempre pequenas (≤ 9). Isso é o efeito de **mundo pequeno** ("small world"): em grafos onde cada vértice tem um grau razoável, qualquer par de vértices conectados está a poucos passos um do outro.

---

### EC6 — Componentes conexas

| grafo | n | nº componentes | maior | menor | tempo (s) |
|---|---:|:---:|---:|---:|---:|
| grafo_1 | 10 000 | 1 | 10 000 | 10 000 | 0,01 |
| grafo_2 | 49 948 | 10 | 25 000 | 48 | 0,22 |
| grafo_3 | 375 000 | 2 | 250 000 | 125 000 | 0,43 |
| grafo_4 | 375 000 | 2 | 250 000 | 125 000 | 1,71 |
| grafo_5 | 4 843 750 | 5 | 2 500 000 | 156 250 | 9,03 |
| grafo_6 | 4 843 750 | 5 | 2 500 000 | 156 250 | 18,57 |

**Discussão.** Os grafos exibem um padrão peculiar: em vários deles os tamanhos das componentes formam uma **progressão geométrica** decrescendo aproximadamente pela metade (grafo_2: 25 000 → 12 500 → 6 250 → … → 48; grafo_5: 2,5M → 1,25M → 625k → 312,5k → 156,25k). A soma sempre fecha com o n exato — confirmando que foram gerados por um processo determinístico controlado.

Note também que **grafo_3 e grafo_4 têm exatamente a mesma estrutura de componentes** (2 componentes, 250k e 125k vértices), apesar de o grafo_4 ter ~10× mais arestas. O mesmo vale para grafo_5 e grafo_6 (5 componentes, mesmos tamanhos): são *o mesmo conjunto de vértices* com densidades de aresta diferentes — o que se confirma visualmente nos resultados de diâmetro do EC7.

---

### EC7 — Diâmetro

| grafo | n | exato | tempo exato (s) | aprox | tempo aprox (s) |
|---|---:|:---:|---:|:---:|---:|
| grafo_1 | 10 000 | **5** | 82,59 | 4 | 0,08 |
| grafo_2 | 49 948 | INVIÁVEL | – | 20 | 1,75 |
| grafo_3 | 375 000 | INVIÁVEL | – | 20 | 4,65 |
| grafo_4 | 375 000 | INVIÁVEL | – | 5 | 16,50 |
| grafo_5 | 4 843 750 | INVIÁVEL | – | 59 | 95,51 |
| grafo_6 | 4 843 750 | INVIÁVEL | – | 19 | 207,00 |

**Discussão.** O diâmetro **exato** é Θ(n·(n+m)): exige uma BFS partindo de cada vértice. Já é proibitivo para grafos com 50k+ vértices (estimativa para o grafo_2: ~3 horas).

Implementamos também uma **aproximação por *double sweep* com sampling**: pega-se um vértice arbitrário r, BFS encontra o mais distante u, BFS de u encontra o mais distante v; d(u, v) é um *limite inferior* do diâmetro. Repetindo a partir de várias amostras aleatórias e tomando o máximo, costuma-se obter o diâmetro real ou um valor muito próximo.

**Observação importante:** no grafo_1 a aproximação retornou 4 enquanto o exato é 5 — subestimou por 1, mas em **~1000× menos tempo** (0,08 s vs 82,6 s). Esse *gap* não fechou nem com 50 amostras: o grafo_1 tem uma estrutura específica em que o *double sweep* converge para um par de vértices a distância 4, "perdendo" o par real a distância 5. **Reportamos a aproximação honestamente como limite inferior.**

**Comparação grafo_5 × grafo_6** (mesmo conjunto de vértices, ambos com 4,8M):
- grafo_5: 13M arestas → diâmetro ≈ 59
- grafo_6: 46M arestas (3,5× mais densa) → diâmetro ≈ 19

A densidade de arestas é o fator dominante para o diâmetro — característica clássica de grafos do tipo "small world".

---

## 3. Conclusão

Implementamos a Parte 1 da biblioteca atendendo a todas as funcionalidades exigidas (entrada, saída com estatísticas, duas representações, BFS, DFS, distâncias, diâmetro e componentes conexas). A interface comum permite que os algoritmos sejam escritos uma única vez e usem qualquer representação. Os principais aprendizados foram:

1. **Escolha de representação importa muito**: a matriz é simples e elegante, mas só é prática para grafos pequenos. A lista é o "default" para grafos do mundo real.
2. **Iteratividade não é detalhe**: em grafos com milhões de vértices, recursão Python estoura a pilha. Buscas iterativas são obrigatórias.
3. **Algoritmos aproximados para o diâmetro** são, na prática, o único caminho viável para grafos grandes — e mesmo um *double sweep* simples já oferece um excelente limite inferior em milissegundos.
4. **Os grafos de teste exibem um padrão geométrico** nos tamanhos de componentes que sugere geração sintética; e o grafo_5/grafo_6 compartilham o mesmo conjunto de vértices (apenas a densidade muda), permitindo isolar o efeito da densidade no diâmetro.
