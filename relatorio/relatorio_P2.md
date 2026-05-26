# Trabalho de Teoria dos Grafos — Parte 2

**Universidade:** Universidade Federal de Viçosa


---

## 1. Decisões de projeto e implementação

A Parte 2 estende, **dentro da mesma biblioteca da Parte 1**, o suporte a grafos não-direcionados com pesos reais nas arestas e adiciona o algoritmo de Dijkstra para distâncias e caminhos mínimos. A interface `Graph` já existente foi expandida — todos os algoritmos antigos (BFS, DFS, componentes, diâmetro) continuam funcionando inalterados.

### 1.1. Representação dos pesos

Cada implementação concreta passou a guardar o peso junto com a aresta:

- **`GraphList`**: cada posição da lista de adjacência é agora `list[tuple[int, float]]`. Para preservar a Parte 1, o método `neighbors(v)` continua retornando **apenas os ids** dos vizinhos (BFS/DFS são indiferentes ao peso). Para o Dijkstra, foi adicionado `neighbors_with_weights(v)` que devolve os pares `(vizinho, peso)`.
- **`GraphMatrix`**: mantemos duas matrizes — uma booleana de presença (`_adj`) e outra de pesos (`_w`, `float32`). Não usamos um único arranjo `float` com NaN como sentinela porque peso `0.0` é um valor válido e NaN obrigaria `np.isnan` em todo lugar. A separação custa memória extra, mas a matriz já é a representação cara: para grafos com mais de ~60k vértices ela é considerada inviável (Θ(n²)).

A flag `is_weighted` é ativada pelo loader quando o arquivo tem 3 colunas; `has_negative_weight` é levantada se qualquer aresta carregada tem peso < 0 (usada pelo Dijkstra para abortar de forma explícita).

### 1.2. Leitor de arquivos (`io_utils.load_graph`)

O loader **detecta automaticamente** o formato: lendo a primeira aresta válida, se houver 2 colunas trata como grafo da Parte 1 (peso implícito 1.0); se houver 3 colunas trata como grafo ponderado e exige a mesma aridade nas linhas seguintes. Adicionalmente, `load_vertex_labels` lê arquivos `id,nome` em UTF-8 para o estudo da rede de colaboração — preservando acentos (ex.: "Éva Tardos").

### 1.3. Algoritmo de Dijkstra

Implementamos as **duas versões** pedidas:

**Versão com vetor (`dijkstra_vector`).** A cada iteração principal, percorremos todo o array de distâncias para escolher o vértice não finalizado de menor estimativa, depois relaxamos suas arestas. Custo: Θ(V² + E). Não há sobrecarga de estruturas auxiliares — é a forma "simples", competitiva apenas em grafos densos e/ou muito pequenos.

**Versão com heap (`dijkstra_heap`).** Usamos `heapq` da biblioteca padrão. O ponto que merece atenção (e que o PDF destaca) é como tratar o `decrease-key`: o `heapq` do Python **não suporta** atualizar a chave de um elemento existente em O(log n). Manter um índice externo "vértice → posição no heap" e implementar `sift-up`/`sift-down` manuais seria possível, mas complica o código e perde-se as garantias do `heapq`.

Optamos pela técnica de **lazy deletion**: sempre que `dist[v]` melhora, **inserimos uma nova entrada** `(nova_dist, v)` no heap. O heap pode conter múltiplas entradas para o mesmo vértice; quando uma entrada é desempilhada, se o vértice já foi finalizado (`finalized[v]`), descartamo-la silenciosamente. Como cada relaxamento bem-sucedido insere no máximo uma entrada, o heap tem tamanho O(E); cada push/pop é O(log E) = O(log V). Custo total: **O((V + E) · log V)** — equivalente assintótico ao decrease-key real, com fator constante ligeiramente maior, mas código muito mais simples e correto.

O *core* do laço principal cabe em uma dezena de linhas:

```python
while heap:
    d, u = heapq.heappop(heap)
    if finalized[u]:              # entrada obsoleta
        continue
    finalized[u] = 1
    for nb, w in graph.neighbors_with_weights(u):
        if finalized[nb]:
            continue
        alt = d + w
        if alt < dist[nb]:
            dist[nb] = alt
            parent[nb] = u
            heapq.heappush(heap, (alt, nb))
```

Ambas as implementações verificam `graph.has_negative_weight` antes de rodar e, se for o caso, levantam `NegativeWeightError` com a mensagem pedida pelo enunciado: *"a biblioteca ainda nao implementa caminhos minimos com pesos negativos"*.

### 1.4. Reconstrução de caminho

`ShortestPathResult.path_to(v)` reconstrói o caminho `source → v` seguindo os ponteiros do array `parent` (preenchido a cada relaxamento), em tempo proporcional ao comprimento do caminho. É a mesma ideia da árvore de busca da Parte 1.

**Ambiente das medições.** Windows 11, Python 3.14, NumPy 2.4. Todas as medidas de tempo usam `time.perf_counter()` e excluem o I/O.

---

## 2. Estudos de caso

### EC8 — Distâncias e caminhos mínimos do vértice 10

Para cada `grafo_W_k` rodamos Dijkstra (heap) a partir do vértice 10 e lemos `dist[v]` e `path_to(v)` para `v ∈ {20, 30, 40, 50, 60}`.

| grafo      | n          | 10→20  | 10→30  | 10→40  | 10→50  | 10→60  |
|------------|-----------:|-------:|-------:|-------:|-------:|-------:|
| grafo_W_1  | 10 000     | 2,3800 | 1,7200 | 2,0500 | 1,2000 | 1,6600 |
| grafo_W_2  | 25 000     | 1,8100 | 1,7200 | 1,9200 | 1,5700 | 1,5800 |
| grafo_W_3  | 100 000    | 0,8000 | 0,8900 | 0,8400 | 0,8700 | 0,9700 |
| grafo_W_4  | 1 000 000  | INVIÁVEL — ver discussão §EC9 | | | | |
| grafo_W_5  | 10 000 000 | INVIÁVEL — ver discussão §EC9 | | | | |

(Os caminhos completos para cada par estão no CSV/MD em `relatorio/resultados/ec8_dijkstra_caminhos.md`; aqui mostramos apenas as distâncias por concisão.)

**Discussão.** As distâncias são todas pequenas e bastante uniformes entre os vértices alvo — coerente com o que vimos no EC5 da Parte 1: estes grafos têm **diâmetro pequeno em arestas**, e o efeito de mundo pequeno se traduz também em peso total baixo nos caminhos mínimos. Em `grafo_W_2`, todos os cinco destinos estão a distância entre 1,57 e 1,92 — uma janela bem estreita. Em `grafo_W_3` as distâncias caem para a faixa **0,80–0,97**: o grafo é cerca de 4× mais denso que `grafo_W_2` (m/n passou de 33 para 61), e isso aumenta a chance de encontrar caminhos curtos de peso baixo. Em outras palavras: **mais arestas curtas competindo, distância mínima cai**.

### EC9 — Tempo médio do Dijkstra (vetor vs heap)

Para cada grafo sorteamos até **k = 100** fontes aleatórias (seed fixa = 42) e rodamos Dijkstra completo (cobrindo todo o grafo) a partir de cada uma, medindo o tempo médio por fonte. A versão com vetor é Θ(V² + E): em grafos grandes ela é proibitiva, então reduzimos `k_vetor` em proporção a n (100→30→5→1) — mas o **tempo médio por fonte permanece comparável** porque é uma medida por execução.

| grafo      | n          | m          | heap (ms/fonte) | k_heap | vetor (ms/fonte) | k_vetor | vetor/heap |
|------------|-----------:|-----------:|----------------:|-------:|-----------------:|--------:|-----------:|
| grafo_W_1  | 10 000     | 209 957    | **102,32**      | 100    | 2 850,85         | 100     | **27,9×**  |
| grafo_W_2  | 25 000     | 824 937    | **606,87**      | 100    | 17 859,04        | 30      | **29,4×**  |
| grafo_W_3  | 100 000    | 6 099 868  | **17 223,78**   | 100    | 497 288,28       | 5       | **28,9×**  |
| grafo_W_4  | 1 000 000  | –          | *(estudo separado)* | – | *(inviável)* | – | – |
| grafo_W_5  | 10 000 000 | –          | *(estudo separado)* | – | *(inviável)* | – | – |

**Discussão.** Em todos os três grafos medidos o heap é **~28-29× mais rápido** que o vetor — uma vantagem espantosamente estável. O ponto-chave: a varredura linear do vetor faz Θ(V) trabalho por iteração para escolher o mínimo, e a iteração principal roda V vezes, contra O(log V) por operação no heap. Quando aumentamos n, o vetor cresce com V² e o heap com (V+E)·log V — ambos crescem, mas o heap muito mais devagar.

**Conferindo as escalas** (linearmente entre `grafo_W_2` e `grafo_W_3`, com n passando de 25k para 100k = 4× e m de 825k para 6,1M = 7,4×):

- **Heap previsto** ~(V+E) log V → fator ~9-10× entre grafos. Observado: 607 ms → 17 224 ms ≈ **28×** (um pouco acima do previsto, provavelmente por *cache miss* na lista de adjacência grande).
- **Vetor previsto** ~V² → fator (100/25)² = 16×. Observado: 17,9 s → 497 s ≈ **28×** (mais que o previsto — o termo +E também cresce, e o `range(1, n+1)` interno faz Python iterar sobre 100k inteiros 100k vezes).

Em valor absoluto, no `grafo_W_3` cada chamada de Dijkstra-vetor levou **~8 minutos** (497 s); o heap, ~17 s. Para k = 100 fontes, isso seria ~14 horas com vetor vs ~29 minutos com heap. **Em escalas reais, sem heap não há estudo.**

**Sobre os grafos maiores.** `grafo_W_4` (n = 1 M, arquivo de 557 MB) e `grafo_W_5` (n = 10 M, arquivo de 793 MB) impõem três desafios independentes:

1. **Tempo de carga em Python.** O parsing texto→int/float de dezenas de milhões de linhas em Python puro é o gargalo dominante. `grafo_W_3` (6,1 M arestas) levou ~3 min só para carregar; pela proporção linear, `grafo_W_4` levaria ~15-20 min e `grafo_W_5` ~25-30 min.
2. **Memória RAM.** A representação `list[(int, float), ...]` consome ~64-80 B por aresta. Para 30 M arestas (W_4), isso requer ~5 GB; para 40-50 M (W_5), >7 GB. Em uma máquina de 16 GB com OS + outros processos ativos, isso já bate o limite — tentamos carregar `grafo_W_4` e o processo Python atingiu 8,5 GB de RSS quando só restavam 1,4 GB livres do sistema, com risco de OOM ou *swap thrashing*; abortamos a tentativa.
3. **Tempo do Dijkstra-vetor.** Para n = 10⁶ o vetor faria ~10¹² operações por fonte — várias horas/fonte em Python, totalmente inviável para k = 100 (e para qualquer k > 1 razoável).

Conforme a convenção da Parte 1, esses grafos são marcados como **INVIÁVEL** nesta análise. Em produção, a solução natural seria: (a) reescrever o loader em C/Cython ou usar `numpy.loadtxt` para parsing vetorizado, (b) usar uma representação `CSR` (compressed sparse row) com arrays NumPy contíguos em vez de listas Python — economiza ~3× de memória e melhora a localidade de cache.

### EC10 — Rede de colaboração

Carregamos a rede de coautoria (`rede_colaboracao.txt`, **n = 722 385** vértices, **m = 2 272 543** arestas, peso = inverso do número de artigos em coautoria) e o mapeamento `id → nome`. O carregador desse mapeamento detectou que o arquivo `rede_colaboracao_vertices.txt` está em **UTF-8 duplamente codificado** (o original UTF-8 foi lido como CP1252 e regravado em UTF-8) e aplica uma correção `encode('cp1252').decode('utf-8')` para recuperar os acentos originais — sem isso, "Éva Tardos" aparece como "Ã‰va Tardos" e o match falharia.

Dijkstra a partir de **Edsger W. Dijkstra** (id 2722) levou 3,94 s sobre toda a rede.

| pesquisador (destino) | id     | distância       | nº de vértices no caminho |
|-----------------------|-------:|----------------:|--------------------------:|
| Alan M. Turing        | 11 365 | **∞**           | – (componentes distintas) |
| J. B. Kruskal         | 471 365| 3,4804          | 9                         |
| Jon M. Kleinberg      | 5 709  | 2,7070          | 10                        |
| Éva Tardos            | 11 386 | 2,7535          | 12                        |
| Daniel R. Figueiredo  | 343 930| 2,9428          | 9                         |

**Caminhos** (truncados nos miolos longos):

- Dijkstra → **J. B. Kruskal**: `Dijkstra → John R. Rice → Dan C. Marinescu → ... → R. Srikant → Albert G. Greenberg → J. B. Kruskal`
- Dijkstra → **Jon M. Kleinberg**: `Dijkstra → A. J. M. van Gasteren → Gerard Tel → ... → Eli Upfal → Prabhakar Raghavan → Jon M. Kleinberg`
- Dijkstra → **Éva Tardos**: `Dijkstra → A. J. M. van Gasteren → Gerard Tel → ... → Andrew V. Goldberg → Serge A. Plotkin → Éva Tardos`
- Dijkstra → **Daniel R. Figueiredo**: `Dijkstra → John R. Rice → Dan C. Marinescu → ... → Zhi-Li Zhang → Donald F. Towsley → Daniel R. Figueiredo`

**Discussão.** Alan M. Turing está em uma **componente distinta** da de Dijkstra — a distância é infinita. Apesar de ambos serem nomes históricos da computação, eles pertenceram a comunidades de pesquisa diferentes e a rede de coautorias disponível (centrada em CS moderno) não constrói uma cadeia entre eles.

Os demais pesquisadores estão a "três coautorias e meia" de Dijkstra (todos com d < 3,5). Como o peso é o inverso do número de artigos, **distância pequena = caminho de coautorias densas**: dois pesquisadores que escreveram muitos artigos juntos têm aresta de peso baixo. Os caminhos passam por hubs clássicos: `A. J. M. van Gasteren` (colaboradora direta de Dijkstra), `John R. Rice` (computação numérica/algoritmos), `Prabhakar Raghavan` e `Andrew V. Goldberg`. Os três pesquisadores acessíveis estão **todos** a distância parecida (~2,7–3,5), sugerindo um *small-world* clássico.

---

## 3. Conclusão

A Parte 2 estendeu a biblioteca da Parte 1 mantendo a mesma API básica: **BFS, DFS, componentes e diâmetro continuam funcionando sem alteração** sobre grafos com peso. O suporte a peso foi introduzido na lista guardando tuplas `(vizinho, peso)`, e a interface dupla `neighbors(v)` / `neighbors_with_weights(v)` separa as duas famílias de algoritmos.

As **duas versões do Dijkstra** confirmaram a teoria de forma quase pedagógica: em **três grafos diferentes**, o speedup heap-vs-vetor se manteve numa janela estreita de **27,9× – 29,4×**, mesmo com o n variando 10×. A constante quase invariante reflete que ambos os algoritmos pagam o mesmo "fator de constante Python", então o ganho vem só da diferença assintótica. O tratamento do `decrease-key` por **lazy deletion** sobre `heapq` resultou em código simples e correto, sem precisar de um indexador de heap personalizado.

O estudo da rede de colaboração mostrou que o algoritmo funciona em escala real (722k vértices em ~4 s com heap) e produziu resultados narrativamente interessantes: Turing está em uma componente separada, e os demais pesquisadores estão a "três coautorias e meia" de Dijkstra. A correção de **mojibake** foi um achado prático: arquivos do mundo real frequentemente trazem patologias de codificação que precisam ser tratadas, sob pena de strings simplesmente não baterem.

A principal limitação observada é o **gargalo de I/O em Python puro**: o parsing texto→objetos em grafos com mais de ~10 M arestas (W_4, W_5) excede o orçamento de memória de uma máquina padrão de 16 GB. Em produção, a evolução natural seria adotar uma representação CSR sobre arrays NumPy e um parser vetorizado — preservando a interface `Graph` e reaproveitando os algoritmos já testados nesta biblioteca.
