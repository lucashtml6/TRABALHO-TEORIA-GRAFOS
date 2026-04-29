"""Algoritmos sobre grafos: BFS, DFS, distancias, componentes."""

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
