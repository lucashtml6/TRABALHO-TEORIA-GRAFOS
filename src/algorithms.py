"""Algoritmos sobre grafos: BFS, DFS, distancias, componentes, Dijkstra."""

import heapq
import math
import random
from collections import deque
from dataclasses import dataclass, field

from .graph_base import Graph

# Sentinelas para vertices nao alcancados pela busca
UNVISITED_PARENT = 0   # 0 nao e um vertice valido (vertices vao de 1 a n)
UNVISITED_LEVEL = -1


@dataclass
class SearchResult:
    """Resultado de uma busca (BFS ou DFS) a partir de um vertice raiz.

    parent[v] = pai de v na arvore de busca; 0 se v nao foi visitado
                (ou se v e a raiz, por convencao).
    level[v]  = nivel de v na arvore (raiz tem nivel 0); -1 se v nao foi
                visitado.
    Ambos os arrays tem tamanho n+1; o indice 0 nao e usado.
    """
    root: int
    algorithm: str            # "bfs" ou "dfs"
    parent: list[int]
    level: list[int]

    def visited(self, v: int) -> bool:
        return self.level[v] != UNVISITED_LEVEL

    def reached_vertices(self) -> list[int]:
        """Lista de vertices alcancados, em ordem crescente."""
        return [v for v in range(1, len(self.level)) if self.level[v] != UNVISITED_LEVEL]


def bfs(graph: Graph, root: int) -> SearchResult:
    """Busca em largura iterativa a partir de `root`.

    Retorna a arvore de busca (pai e nivel de cada vertice).
    Vertices nao alcancados ficam com parent=0 e level=-1.
    """
    n = graph.n_vertices
    if not (1 <= root <= n):
        raise ValueError(f"raiz {root} fora do intervalo [1, {n}]")

    parent = [UNVISITED_PARENT] * (n + 1)
    level = [UNVISITED_LEVEL] * (n + 1)

    level[root] = 0
    parent[root] = 0  # convencao: raiz nao tem pai
    queue = deque([root])

    while queue:
        v = queue.popleft()
        next_level = level[v] + 1
        for w in graph.neighbors(v):
            if level[w] == UNVISITED_LEVEL:
                level[w] = next_level
                parent[w] = v
                queue.append(w)

    return SearchResult(root=root, algorithm="bfs", parent=parent, level=level)


def dfs(graph: Graph, root: int) -> SearchResult:
    """Busca em profundidade iterativa a partir de `root`.

    Implementacao com pilha explicita (evita estouro de recursao em
    grafos grandes). O pai de cada vertice e gravado no array `parent`
    no momento do empilhamento — assim, a pilha guarda apenas inteiros
    em vez de tuplas (vertice, pai), economizando milhoes de alocacoes
    em grafos densos.

    Para reproduzir a ordem da DFS recursiva, os vizinhos sao empilhados
    em ordem reversa: o primeiro vizinho (menor id) acaba no topo da
    pilha e e o proximo a ser visitado.

    Em LIFO, o ultimo push de um vertice e o primeiro a ser desempilhado;
    portanto parent[w] = ultimo valor escrito antes de w ser processado.
    Isso reproduz exatamente a arvore da implementacao com tuplas, sem
    o custo de alocacao.
    """
    n = graph.n_vertices
    if not (1 <= root <= n):
        raise ValueError(f"raiz {root} fora do intervalo [1, {n}]")

    parent = [UNVISITED_PARENT] * (n + 1)
    level = [UNVISITED_LEVEL] * (n + 1)

    parent[root] = 0
    stack: list[int] = [root]

    while stack:
        v = stack.pop()
        if level[v] != UNVISITED_LEVEL:
            continue  # ja visitado por outro caminho
        p = parent[v]
        level[v] = 0 if p == 0 else level[p] + 1
        # empilha vizinhos em ordem reversa para que o menor id seja
        # processado primeiro (DFS lexicograficamente determinista).
        # `reversed` cria apenas um iterador; nao copia a lista de
        # adjacencia (que ja vem ordenada).
        viz = graph.neighbors(v)
        if not isinstance(viz, list):
            viz = list(viz)
        for w in reversed(viz):
            if level[w] == UNVISITED_LEVEL:
                parent[w] = v
                stack.append(w)

    return SearchResult(root=root, algorithm="dfs", parent=parent, level=level)


@dataclass
class ConnectedComponents:
    """Resultado da busca por componentes conexas.

    components: lista de componentes em ordem decrescente de tamanho.
                Cada componente e a lista (ordenada) dos seus vertices.
    """
    components: list[list[int]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.components)

    @property
    def sizes(self) -> list[int]:
        return [len(c) for c in self.components]

    @property
    def largest(self) -> list[int]:
        return self.components[0] if self.components else []

    @property
    def smallest(self) -> list[int]:
        return self.components[-1] if self.components else []


def connected_components(graph: Graph) -> ConnectedComponents:
    """Descobre as componentes conexas de um grafo nao-direcionado.

    Usa BFS como primitiva, com array global de visitados para evitar
    realocacoes (importante em grafos grandes). As componentes sao
    retornadas em ordem decrescente de tamanho; vertices dentro de
    cada componente em ordem crescente.
    """
    n = graph.n_vertices
    visited = bytearray(n + 1)  # 1 byte por vertice (0=nao visto, 1=visto)
    components: list[list[int]] = []

    for start in range(1, n + 1):
        if visited[start]:
            continue
        # BFS local a partir de `start`
        comp: list[int] = []
        queue = deque()
        queue.append(start)
        visited[start] = 1
        while queue:
            v = queue.popleft()
            comp.append(v)
            for w in graph.neighbors(v):
                if not visited[w]:
                    visited[w] = 1
                    queue.append(w)
        comp.sort()
        components.append(comp)

    components.sort(key=len, reverse=True)
    return ConnectedComponents(components=components)


# ---------------------------------------------------------------------------
# Distancias e diametro (Funcionalidade 5)
# ---------------------------------------------------------------------------


def _bfs_distances(
    graph: Graph,
    source: int,
    dist: list[int] | None = None,
) -> tuple[int, int, list[int]]:
    """BFS otimizada que computa apenas distancias (sem pais).

    Reaproveita o array `dist` quando passado, evitando realocacoes em
    laços que rodam BFS muitas vezes (ex.: diametro exato).
    Retorna (max_dist, vertice_mais_distante, dist).
    Vertices nao alcancados ficam com dist = -1.
    """
    n = graph.n_vertices
    if dist is None:
        dist = [-1] * (n + 1)
    else:
        # zera so o que precisa ser zerado (custo: O(n))
        for i in range(n + 1):
            dist[i] = -1

    dist[source] = 0
    queue = deque([source])
    max_dist = 0
    farthest = source
    while queue:
        v = queue.popleft()
        d_next = dist[v] + 1
        for w in graph.neighbors(v):
            if dist[w] == -1:
                dist[w] = d_next
                if d_next > max_dist:
                    max_dist = d_next
                    farthest = w
                queue.append(w)
    return max_dist, farthest, dist


def distance(graph: Graph, u: int, v: int) -> int | float:
    """Distancia (em arestas) entre dois vertices, calculada via BFS.

    Retorna math.inf se nao existir caminho entre u e v.
    Usa terminacao antecipada: para a busca assim que encontra v.
    """
    n = graph.n_vertices
    if not (1 <= u <= n) or not (1 <= v <= n):
        raise ValueError(f"vertices fora de [1, {n}]: u={u}, v={v}")
    if u == v:
        return 0

    dist = [-1] * (n + 1)
    dist[u] = 0
    queue = deque([u])
    while queue:
        x = queue.popleft()
        d_next = dist[x] + 1
        for w in graph.neighbors(x):
            if dist[w] == -1:
                if w == v:
                    return d_next
                dist[w] = d_next
                queue.append(w)
    return math.inf


def diameter(graph: Graph, components: ConnectedComponents | None = None) -> int:
    """Diametro exato do grafo: maior distancia entre qualquer par de vertices.

    Em grafos desconexos, retorna o maximo dos diametros das componentes
    (a alternativa formal seria infinito).

    Custo: O(n * (n + m)). Inviavel para grafos com n na casa dos milhoes.
    Para grafos grandes, prefira diameter_approx.
    """
    if components is None:
        components = connected_components(graph)

    n = graph.n_vertices
    dist = [-1] * (n + 1)
    best = 0
    for comp in components.components:
        if len(comp) < 2:
            continue
        for v in comp:
            d, _, _ = _bfs_distances(graph, v, dist)
            if d > best:
                best = d
    return best


def diameter_approx(
    graph: Graph,
    components: ConnectedComponents | None = None,
    samples: int = 1,
    seed: int | None = 0,
) -> int:
    """Aproximacao do diametro usando o metodo "double sweep".

    Para cada componente:
      1. Escolhe um vertice de partida r (primeiro da componente, e
         depois mais `samples - 1` vertices aleatorios da componente).
      2. BFS de r -> encontra o vertice mais distante u.
      3. BFS de u -> encontra o vertice mais distante v.
      4. d(u, v) e um limite inferior do diametro (frequentemente
         otimo em grafos nao-direcionados).

    O resultado e o maximo dos d(u,v) obtidos em todas as amostras.
    Mais amostras tendem a fechar a folga entre o limite inferior e
    o diametro real, sem custo proibitivo (cada amostra: 2 BFSs).

    Custo: O(samples * (n + m)).
    """
    if components is None:
        components = connected_components(graph)

    rng = random.Random(seed)
    best = 0
    for comp in components.components:
        if len(comp) < 2:
            continue
        # primeiro vertice + amostras aleatorias adicionais
        sources: list[int] = [comp[0]]
        if samples > 1:
            extras = rng.sample(comp, k=min(samples - 1, len(comp) - 1))
            sources.extend(s for s in extras if s != comp[0])

        for s in sources:
            _, u, _ = _bfs_distances(graph, s)
            d, _, _ = _bfs_distances(graph, u)
            if d > best:
                best = d
    return best


# ---------------------------------------------------------------------------
# Caminhos minimos com pesos: Dijkstra (Parte 2)
# ---------------------------------------------------------------------------


class NegativeWeightError(ValueError):
    """Levantada quando se tenta rodar Dijkstra em grafo com aresta negativa."""


@dataclass
class ShortestPathResult:
    """Resultado de uma execucao de Dijkstra a partir de uma fonte.

    dist[v]    = distancia minima de `source` ate v (math.inf se inalcancavel).
    parent[v]  = predecessor de v na arvore de caminhos minimos.
                 0 para a fonte; 0 tambem para vertices inalcancaveis.
    Ambos os arrays tem tamanho n+1 (indice 0 nao e usado).
    """
    source: int
    algorithm: str            # "dijkstra-vector" ou "dijkstra-heap"
    dist: list[float]
    parent: list[int]

    def reached(self, v: int) -> bool:
        return self.dist[v] != math.inf

    def path_to(self, v: int) -> list[int]:
        """Reconstroi o caminho minimo `source -> v` (incluindo extremos).

        Retorna lista vazia se v nao for alcancavel.
        """
        if not (1 <= v < len(self.dist)):
            raise ValueError(f"vertice {v} fora do intervalo [1, {len(self.dist) - 1}]")
        if self.dist[v] == math.inf:
            return []
        path: list[int] = []
        cur = v
        while cur != 0:
            path.append(cur)
            if cur == self.source:
                break
            cur = self.parent[cur]
        path.reverse()
        return path


def _check_dijkstra_preconditions(graph: Graph, source: int) -> None:
    n = graph.n_vertices
    if not (1 <= source <= n):
        raise ValueError(f"fonte {source} fora do intervalo [1, {n}]")
    if graph.has_negative_weight:
        raise NegativeWeightError(
            "a biblioteca ainda nao implementa caminhos minimos com pesos negativos"
        )


def dijkstra_vector(graph: Graph, source: int) -> ShortestPathResult:
    """Dijkstra com vetor de distancias (sem heap).

    A cada iteracao percorre todo o array de estimativas para escolher o
    vertice nao visitado de menor distancia. Custo: Theta(V^2 + E). E
    competitivo em grafos densos e/ou em grafos muito pequenos, onde a
    constante simples do laco linear ganha do overhead do heap.
    """
    _check_dijkstra_preconditions(graph, source)
    n = graph.n_vertices
    INF = math.inf

    dist = [INF] * (n + 1)
    parent = [0] * (n + 1)
    visited = bytearray(n + 1)  # 0 = nao visitado, 1 = finalizado

    dist[source] = 0.0

    for _ in range(n):
        # 1) seleciona u nao visitado com menor dist (varredura linear)
        u = -1
        best = INF
        for v in range(1, n + 1):
            if not visited[v] and dist[v] < best:
                best = dist[v]
                u = v
        if u == -1:
            break  # restantes sao inalcancaveis
        visited[u] = 1

        # 2) relaxa todas as arestas saindo de u
        du = dist[u]
        for nb, w in graph.neighbors_with_weights(u):
            if visited[nb]:
                continue
            alt = du + w
            if alt < dist[nb]:
                dist[nb] = alt
                parent[nb] = u

    return ShortestPathResult(
        source=source, algorithm="dijkstra-vector", dist=dist, parent=parent
    )


def dijkstra_heap(graph: Graph, source: int) -> ShortestPathResult:
    """Dijkstra com min-heap binario (`heapq`) e *lazy deletion*.

    A biblioteca-padrao do Python nao oferece `decrease-key` em O(log n);
    para contornar isso, sempre que uma distancia melhora, *inserimos uma
    nova entrada* no heap em vez de atualizar a existente. Quando uma
    entrada e desempilhada com distancia maior que `dist[v]`, ela e
    obsoleta e e descartada.

    O numero de entradas no heap fica em O(E) (cada relaxamento bem-sucedido
    insere uma); cada operacao de pop/push e O(log E) = O(log V). Custo
    total: O((V + E) log V) — equivalente assintotico ao decrease-key real.
    Em troca de constante ligeiramente maior, evitamos manter um indexador
    no heap, mantendo o codigo simples.
    """
    _check_dijkstra_preconditions(graph, source)
    n = graph.n_vertices
    INF = math.inf

    dist = [INF] * (n + 1)
    parent = [0] * (n + 1)
    finalized = bytearray(n + 1)

    dist[source] = 0.0
    heap: list[tuple[float, int]] = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if finalized[u]:
            continue  # entrada obsoleta
        finalized[u] = 1

        for nb, w in graph.neighbors_with_weights(u):
            if finalized[nb]:
                continue
            alt = d + w
            if alt < dist[nb]:
                dist[nb] = alt
                parent[nb] = u
                heapq.heappush(heap, (alt, nb))

    return ShortestPathResult(
        source=source, algorithm="dijkstra-heap", dist=dist, parent=parent
    )


# ---------------------------------------------------------------------------
# Caminhos minimos com pesos negativos: Bellman-Ford (Parte 3)
# ---------------------------------------------------------------------------


@dataclass
class BellmanFordResult:
    """Resultado de uma execucao de Bellman-Ford a partir de uma fonte.

    dist[v]   = distancia minima de `source` ate v (math.inf se inalcancavel).
    parent[v] = predecessor de v na arvore de caminhos minimos (0 para a
                fonte e para vertices inalcancaveis).
    has_negative_cycle = True se existe um ciclo de peso negativo *alcancavel*
                a partir da fonte. Nesse caso as distancias dos vertices
                afetados nao sao bem definidas (podem ser feitas arbitrariamente
                pequenas) e nao devem ser interpretadas.
    """
    source: int
    algorithm: str            # "bellman-ford"
    dist: list[float]
    parent: list[int]
    has_negative_cycle: bool

    def reached(self, v: int) -> bool:
        return self.dist[v] != math.inf

    def path_to(self, v: int) -> list[int]:
        """Reconstroi o caminho minimo `source -> v` (incluindo extremos).

        Retorna lista vazia se v nao for alcancavel. Em presenca de ciclo
        negativo o caminho pode nao ser bem definido — use has_negative_cycle.
        """
        if not (1 <= v < len(self.dist)):
            raise ValueError(f"vertice {v} fora do intervalo [1, {len(self.dist) - 1}]")
        if self.dist[v] == math.inf:
            return []
        path: list[int] = []
        cur = v
        guard = len(self.dist)  # protege contra ciclos no array parent
        while cur != 0 and guard > 0:
            path.append(cur)
            if cur == self.source:
                break
            cur = self.parent[cur]
            guard -= 1
        path.reverse()
        return path


def _is_ancestor(parent: list[int], anc: int, node: int, limit: int) -> bool:
    """True se `anc` e ancestral de `node` na floresta de predecessores
    (seguindo `parent` a partir de `node` chega-se a `anc`).

    Usado antes de gravar parent[v] = u: se v ja e ancestral de u, fechar a
    aresta u -> v criaria um ciclo no grafo de predecessores — e, pelo lema do
    Bellman-Ford, todo ciclo de predecessores e negativo. `limit` (= n) e uma
    rede de seguranca contra caminhar indefinidamente.
    """
    x = node
    steps = 0
    while x != 0:
        if x == anc:
            return True
        x = parent[x]
        steps += 1
        if steps > limit:
            return True
    return False


def bellman_ford(graph: Graph, source: int) -> BellmanFordResult:
    """Bellman-Ford para caminhos minimos a partir de `source`.

    Diferente do Dijkstra, aceita arestas de peso negativo e detecta a
    existencia de um ciclo negativo alcancavel pela fonte. Aplicamos as
    *duas otimizacoes* discutidas em aula sobre o Bellman-Ford classico
    (que sempre executa V-1 varreduras completas das E arestas, Theta(V*E)):

    Otimizacao 1 — parada antecipada. Trabalhamos por *rodadas*: cada rodada
    relaxa as arestas e calcula o conjunto de vertices melhorados. Se uma
    rodada nao melhora nenhuma estimativa (conjunto ativo vazio), o algoritmo
    ja convergiu e paramos imediatamente, sem completar as V-1 passadas.

    Otimizacao 2 — processar apenas vertices atualizados (conjunto ativo). Em
    vez de relaxar TODAS as arestas a cada rodada, mantemos o conjunto dos
    vertices cuja estimativa mudou na rodada anterior: so as arestas de saida
    desses vertices podem gerar melhora na rodada seguinte (e a ideia da
    fila/SPFA, aqui organizada por camadas).

    Deteccao de ciclo negativo: sem arestas negativas nenhum ciclo negativo
    pode existir e pulamos a checagem (custo zero). Havendo arestas negativas,
    *antes* de gravar parent[v] = u verificamos se v ja e ancestral de u na
    floresta de predecessores (`_is_ancestor`); em caso afirmativo, fechar a
    aresta criaria um ciclo de predecessores — necessariamente negativo —, e
    abortamos. Isso evita ciclos transitorios (falsos positivos de varreduras
    "depois do fato") e detecta o ciclo logo na primeira vez que ele se fecha,
    bem antes do limite de V rodadas mantido como rede de seguranca.

    Custo: O(V*E) no pior caso, mas na pratica muito mais rapido — proximo de
    O(k*E) com k = numero de rodadas ate convergir (pequeno nestes grafos de
    "mundo pequeno"), o que torna o algoritmo viavel nos grafos grandes.
    """
    n = graph.n_vertices
    if not (1 <= source <= n):
        raise ValueError(f"fonte {source} fora do intervalo [1, {n}]")

    INF = math.inf
    dist = [INF] * (n + 1)
    parent = [0] * (n + 1)
    in_active = bytearray(n + 1)    # 1 se o vertice esta no conjunto ativo

    dist[source] = 0.0
    active: list[int] = [source]
    in_active[source] = 1

    # so faz sentido procurar ciclo negativo se ha aresta negativa
    check_cycles = graph.has_negative_weight
    has_negative_cycle = False
    rounds = 0

    while active:
        rounds += 1
        nxt: list[int] = []
        for u in active:
            in_active[u] = 0
            du = dist[u]
            for v, w in graph.neighbors_with_weights(u):
                alt = du + w
                if alt < dist[v]:
                    if check_cycles and _is_ancestor(parent, v, u, n):
                        has_negative_cycle = True
                        break
                    dist[v] = alt
                    parent[v] = u
                    if not in_active[v]:
                        in_active[v] = 1
                        nxt.append(v)
            if has_negative_cycle:
                break
        if has_negative_cycle or (check_cycles and rounds > n):
            has_negative_cycle = True
            break
        active = nxt

    return BellmanFordResult(
        source=source,
        algorithm="bellman-ford",
        dist=dist,
        parent=parent,
        has_negative_cycle=has_negative_cycle,
    )


def shortest_path(
    graph: Graph,
    source: int,
    target: int,
    method: str = "heap",
) -> tuple[float, list[int]]:
    """Conveniencia: distancia minima e caminho de `source` a `target`.

    `method` aceita 'heap' (default) ou 'vector'. Para grafos com pesos
    negativos, levanta NegativeWeightError.
    """
    if method == "heap":
        res = dijkstra_heap(graph, source)
    elif method == "vector":
        res = dijkstra_vector(graph, source)
    else:
        raise ValueError(f"method deve ser 'heap' ou 'vector', recebido: {method!r}")
    return res.dist[target], res.path_to(target)
