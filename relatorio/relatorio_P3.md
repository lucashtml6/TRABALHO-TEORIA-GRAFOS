# Trabalho de Teoria dos Grafos — Parte 3

**Universidade:** Universidade Federal de Viçosa

**Código-fonte:** _<inserir URL do repositório>_

---

## 1. Decisões de projeto e implementação

A Parte 3 estende a **mesma biblioteca** das Partes 1 e 2 para suportar **grafos direcionados com pesos** e adiciona o algoritmo de **Bellman-Ford**. O objetivo de projeto continuou sendo o mesmo das partes anteriores: escrever os algoritmos **uma única vez** sobre a interface abstrata `Graph` e fazê-los funcionar, sem alteração, em qualquer combinação de representação (lista/matriz) e orientação (direcionado/não-direcionado).

### 1.1. Suporte a grafos direcionados

A direção foi introduzida com **uma única flag** `directed` no construtor de `Graph`, propagada às duas implementações concretas e ao leitor de arquivos. A diferença é localizada e mínima:

- **`GraphList.add_edge(u, v, w)`**: num grafo **não-direcionado** a aresta é registrada nas duas pontas (`_adj[u]` e `_adj[v]`); num grafo **direcionado** registramos **apenas o arco `u → v`** em `_adj[u]`. Assim, `neighbors(v)` passa a devolver os **sucessores** (vizinhos de saída) de `v`.
- **`load_graph(..., directed=True)`**: conforme o enunciado, a direção de cada aresta segue a ordem dos vértices na linha — `u v w` é o arco `u → v` de peso `w`. O formato do arquivo é idêntico ao da Parte 2; o parâmetro `directed` (passado pelo usuário) é que decide a interpretação.

Como **BFS, DFS e Dijkstra percorrem o grafo apenas por `neighbors`/`neighbors_with_weights`** (arestas de saída), eles funcionam **imediatamente** em grafos direcionados, sem nenhuma modificação no código dos algoritmos — exatamente o que o enunciado pede ("adapte sua BFS, DFS e Dijkstra"). A adaptação foi, na prática, garantir que a *representação* respeitasse a direção.

Um efeito colateral positivo: como cada arco é armazenado **uma só vez** (e não duas, como no caso não-direcionado), a representação direcionada consome **metade da memória** de adjacência — relevante para os grafos grandes desta parte.

### 1.2. Grafo invertido (transposto)

Para responder "distância **de** vários vértices **até** um vértice-alvo `t`" com um algoritmo de **fonte única**, usamos o **grafo transposto** (todas as arestas invertidas): rodar a busca a partir de `t` no grafo invertido devolve `d(v → t)` para **todo** `v` de uma só vez, pois `d(v → t) = d_invertido(t → v)`.

Implementamos isso de duas formas: `GraphList.reverse()` constrói o transposto em memória, e — mais importante para grafos grandes — `load_graph(..., reverse=True)` **inverte cada arco já na carga** (`u → v` vira `v → u`), sem custo de memória adicional nem uma segunda passada.

### 1.3. Algoritmo de Bellman-Ford com as duas otimizações

O Bellman-Ford clássico executa sempre **V−1 varreduras completas** de todas as `E` arestas — custo Θ(V·E) — e detecta ciclos negativos com uma varredura extra. Implementamos as **duas otimizações discutidas em aula**, que se combinam na versão baseada em **fila** (conhecida como SPFA):

**Otimização 1 — parada antecipada.** Trabalhamos por **rodadas**: cada rodada relaxa as arestas e calcula o conjunto de vértices melhorados. Se uma rodada não melhora **nenhuma** estimativa (conjunto ativo vazio), o algoritmo já convergiu e paramos imediatamente, sem completar as V−1 passadas.

**Otimização 2 — processar apenas vértices atualizados (conjunto ativo).** Em vez de relaxar **todas** as arestas em toda passada, mantemos o conjunto dos vértices cuja estimativa mudou na rodada anterior: somente as arestas de saída desses vértices podem produzir melhora na rodada seguinte (é a ideia da fila/SPFA, aqui organizada por camadas). As duas ideias se encaixam naturalmente — **quando o conjunto ativo esvazia, não há mais melhora possível**, que é precisamente o critério da parada antecipada.

O núcleo do laço cabe em poucas linhas:

```python
while active:
    nxt = []
    for u in active:
        in_active[u] = 0
        du = dist[u]
        for v, w in graph.neighbors_with_weights(u):
            alt = du + w
            if alt < dist[v]:
                if check_cycles and _is_ancestor(parent, v, u, n):
                    has_negative_cycle = True; break   # fecharia um ciclo
                dist[v] = alt
                parent[v] = u
                if not in_active[v]:
                    in_active[v] = 1; nxt.append(v)
    active = nxt
```

**Detecção de ciclo negativo.** Pelo lema clássico, se em algum momento o grafo de predecessores (vetor `parent`) contém um ciclo, esse ciclo é necessariamente **negativo**. Por isso, *antes* de gravar `parent[v] = u` verificamos se `v` já é ancestral de `u` na floresta de predecessores (`_is_ancestor`): em caso afirmativo, fechar a aresta criaria um ciclo, e abortamos com `has_negative_cycle = True`. Essa abordagem (*subtree-disassembly*) tem duas vantagens sobre a detecção clássica por contagem ("se um vértice é relaxado V vezes, há ciclo"): (i) **detecta no instante exato** em que o ciclo se fecha — em poucas rodadas, e não após V — e (ii) **evita falsos positivos** de ciclos transitórios que surgem com atualização *in-place*. Só ativamos a checagem quando o grafo tem alguma aresta negativa (custo zero nos demais). O algoritmo retorna sempre o vetor de **distâncias**, a **árvore de caminhos mínimos** (`parent`) e a flag, como pede o enunciado.

**Por que a otimização importa.** No pior caso o custo segue Θ(V·E), mas na prática a versão com conjunto ativo é muito mais rápida — próxima de O(k·E) com k = número de rodadas até convergir (pequeno nestes grafos de mundo pequeno). Sem ela, o Bellman-Ford ingênuo em `grafo_W_3` (V=10⁵, E=6,1·10⁶) faria ~6·10¹¹ operações por execução — dezenas de minutos em Python. **As otimizações são o que torna o estudo de caso possível.**

**Ambiente das medições.** Windows 11, Python 3.14. Todas as medidas de tempo usam `time.perf_counter()`, são a **média de 10 rodadas** e **excluem o I/O** (leitura/escrita em disco).

---

## 2. Estudos de caso

Cada `grafo_W_k` foi interpretado como **direcionado** (a direção segue a ordem dos vértices em cada linha). Para obter a distância **dos** vértices 10, 20 e 30 **até** o vértice 100 com um algoritmo de fonte única, rodamos cada algoritmo a partir da fonte **100** sobre o **grafo invertido** — assim uma única execução fornece `d(10→100)`, `d(20→100)` e `d(30→100)` simultaneamente. A mesma construção é usada no Bellman-Ford e no Dijkstra, o que torna a comparação de tempos perfeitamente direta.

Apenas `grafo_W_1` possui **arestas negativas**; nos demais, sem pesos negativos, aplicamos também o Dijkstra (Parte 2) para comparar.

### EC-P3.1 — Distâncias dos vértices 10, 20 e 30 até o vértice 100

| grafo     | algoritmo    | d(10→100)   | d(20→100)   | d(30→100)   | ciclo neg. |
|-----------|--------------|------------:|------------:|------------:|:----------:|
| grafo_W_1 | Bellman-Ford |  *(indef.)* | *(indef.)*  | *(indef.)*  | **SIM**    |
| grafo_W_2 | Bellman-Ford |     10,4700 |      8,4800 |      8,7100 |    não     |
| grafo_W_2 | Dijkstra     |     10,4700 |      8,4800 |      8,7100 |     —      |
| grafo_W_3 | Bellman-Ford |      4,6300 |      5,4200 |      4,6700 |    não     |
| grafo_W_3 | Dijkstra     |      4,6300 |      5,4200 |      4,6700 |     —      |
| grafo_W_4 | —            | INVIÁVEL — ver §2.1 | | | |
| grafo_W_5 | —            | INVIÁVEL — ver §2.1 | | | |

**Discussão.** O resultado mais importante é o de **`grafo_W_1`**: ele é o único com arestas negativas e o Bellman-Ford detecta um **ciclo negativo alcançável** a partir do vértice 100 (no grafo invertido). Na presença de um ciclo negativo, **não existe distância mínima bem definida** — qualquer caminho pode ter seu custo reduzido indefinidamente dando mais voltas no ciclo. Portanto, para `grafo_W_1` a resposta correta não é um número, e sim "indefinido / −∞": é exatamente para isso que o algoritmo retorna a flag `has_negative_cycle`. Esse é também o motivo pelo qual o Dijkstra é **inaplicável** aqui (ele pressupõe pesos não-negativos).

Nos demais grafos, sem pesos negativos, **as distâncias do Bellman-Ford e do Dijkstra coincidem dígito a dígito** — uma validação cruzada forte das duas implementações (e da identidade do grafo invertido, `d(v→100) = d_invertido(100→v)`). Os valores são pequenos e uniformes (todos na faixa ~4–11), coerentes com o efeito de **mundo pequeno** já observado nas Partes 1 e 2: poucos saltos de peso baixo bastam para alcançar o destino. Em `grafo_W_3`, mais denso (m/n ≈ 61), as distâncias caem para a faixa ~4,6–5,4, abaixo das de `grafo_W_2` (~8,5–10,5): **mais arestas competindo ⇒ caminho mínimo mais barato**.

### EC-P3.2 / EC-P3.3 — Tempo de execução e comparação com Dijkstra

Tempo médio de **10 rodadas**, sem I/O. BF e Dijkstra rodam exatamente a mesma tarefa (fonte 100 no grafo invertido), o que torna a comparação direta.

| grafo     | n         | m          | Bellman-Ford (ms) | Dijkstra (ms) | Dijkstra/BF |
|-----------|----------:|-----------:|------------------:|--------------:|:-----------:|
| grafo_W_1 |    25 000 |    549 953 |             0,58¹ |       — (n/a) |     —       |
| grafo_W_2 |    25 000 |    824 964 |            536,29 |        235,57 |   0,44×     |
| grafo_W_3 |   100 000 |  6 099 941 |          4 832,24 |      3 263,40 |   0,68×     |
| grafo_W_4 | 1 000 000 | 30 999 978 |   INVIÁVEL — ver §2.1 | |             |
| grafo_W_5 |10 000 000 | 39 999 995 |   INVIÁVEL — ver §2.1 | |             |

¹ `grafo_W_1` aborta assim que o ciclo negativo é fechado (em poucas rodadas), por isso o tempo é baixíssimo — ele **não** percorre o grafo todo.

**Discussão.** Em todos os grafos sem ciclo negativo, o **Dijkstra é mais rápido** que o Bellman-Ford (Dijkstra/BF < 1), como esperado: o Dijkstra finaliza cada vértice **uma única vez** (cada aresta é relaxada no máximo uma vez), enquanto o Bellman-Ford pode reprocessar um vértice em várias rodadas até as estimativas estabilizarem. A vantagem do Dijkstra **diminui** com a densidade (0,44× em `grafo_W_2` vs 0,68× em `grafo_W_3`): em grafos mais densos o custo passa a ser dominado pela varredura das arestas, que ambos pagam, e o overhead do heap do Dijkstra fica relativamente maior.

O ponto pedagógico central, porém, é o **papel das otimizações**. O Bellman-Ford ingênuo faria sempre V−1 varreduras completas — em `grafo_W_3` isso seria 99 999 × 6,1M ≈ **6×10¹¹ operações por execução**, dezenas de minutos em Python. Com as duas otimizações (conjunto ativo + parada antecipada), o algoritmo converge em **poucas rodadas** (estes grafos têm diâmetro pequeno), e cada execução custa ~4,8 s. **Sem as otimizações, o estudo de caso seria inviável já em `grafo_W_3`** — e completamente impossível em `grafo_W_4`/`W_5`. O caso de `grafo_W_1` ilustra a outra ponta: a detecção de ciclo negativo via *subtree-disassembly* dispara assim que o ciclo se fecha, em frações de milissegundo, sem precisar das V rodadas que a detecção por contagem exigiria.

#### 2.1. Sobre `grafo_W_4` e `grafo_W_5` (inviabilidade)

Como na Parte 2, os dois maiores grafos esbarram no **limite de memória** de uma máquina de 16 GB. A boa notícia é que a representação **direcionada armazena cada arco uma única vez** (metade da memória do caso não-direcionado), o que fez a carga de `grafo_W_4` (31 M de arcos) **avançar mais longe** que na Parte 2 — mas ainda assim o processo Python ultrapassou ~8 GB de RSS com menos de 0,5 GB livres no sistema, entrando em *swap* pesado. Para não arriscar travar a máquina (e seguindo a convenção das partes anteriores), `grafo_W_4` (n = 10⁶) e `grafo_W_5` (n = 10⁷) são marcados como **INVIÁVEL** nesta análise. O gargalo é duplo: o *parsing* texto→objetos de dezenas de milhões de linhas em Python puro e o overhead de ~64–80 B por aresta da estrutura `list[(int, float)]`. A evolução natural (também apontada na Parte 2) seria uma representação **CSR** sobre arrays NumPy contíguos, que cortaria a memória em ~3× e permitiria carregar ambos.

---

## 3. Conclusão

A Parte 3 generalizou a biblioteca para **grafos direcionados com pesos** com uma alteração cirúrgica — uma flag `directed` na representação — preservando integralmente os algoritmos da Parte 1/2: **BFS, DFS e Dijkstra funcionam em grafos direcionados sem nenhuma modificação**, pois sempre percorreram o grafo por suas arestas de saída. O truque do **grafo invertido** permitiu responder "distância até o vértice 100" com uma única execução de um algoritmo de fonte única, e serviu de validação cruzada (as distâncias de BF e Dijkstra coincidiram exatamente).

O **Bellman-Ford** foi implementado com as **duas otimizações** discutidas em aula — processar apenas o conjunto de vértices atualizados e parar quando não há mais melhora — que, juntas, transformam um algoritmo Θ(V·E) em algo próximo de O(k·E) com k pequeno nestes grafos de mundo pequeno. Foi essa diferença que tornou os estudos de caso **viáveis em escala** (milhões de arestas). A **detecção de ciclo negativo** foi feita pela verificação de ancestralidade na floresta de predecessores (*subtree-disassembly*), que detecta o ciclo no instante em que ele se fecha — evitando tanto falsos positivos de ciclos transitórios quanto o custo proibitivo da detecção por contagem de relaxamentos.

O achado mais interessante dos estudos foi `grafo_W_1`: o único com pesos negativos, ele contém um **ciclo negativo alcançável**, de modo que as distâncias mínimas até o vértice 100 **não são bem definidas** — um lembrete concreto de por que o Bellman-Ford (e não o Dijkstra) é necessário quando há pesos negativos, e de por que a detecção de ciclos negativos é parte essencial do algoritmo.
