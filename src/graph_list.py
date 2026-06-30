from typing import Iterable

from .graph_base import Graph


class GraphList(Graph):
    """Grafo representado por lista de adjacencia (direcionado ou nao).

    Cada posicao self._adj[v] e uma lista de tuplas (vizinho, peso). A
    BFS/DFS da Parte 1 chama `neighbors(v)`, que devolve so os ids; o
    Dijkstra/Bellman-Ford chamam `neighbors_with_weights(v)`, que devolve
    os pares.

    Num grafo direcionado, a aresta `u -> v` so e registrada em `_adj[u]`,
    de modo que `neighbors(u)` lista os sucessores de u (vizinhos de saida).
    """

    def __init__(self, n_vertices: int, directed: bool = False) -> None:
        super().__init__(n_vertices, directed)
        self._adj: list[list[tuple[int, float]]] = [[] for _ in range(n_vertices + 1)]

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> bool:
        """
        Adiciona a aresta com peso. NAO verifica duplicatas (rapido para
        carga de arquivos grandes). Self-loops sao ignorados.

        Num grafo nao-direcionado registra {u, v} nas duas pontas; num grafo
        direcionado registra apenas o arco u -> v.
        """
        self._validate_vertex(u)
        self._validate_vertex(v)
        if u == v:
            return False
        w = float(weight)
        self._adj[u].append((v, w))
        if not self._directed:
            self._adj[v].append((u, w))
        self._m += 1
        if w != 1.0:
            self._is_weighted = True
        if w < 0.0:
            self._has_negative_weight = True
        return True

    def reverse(self) -> "GraphList":
        """Constroi o grafo transposto (todas as arestas invertidas).

        Para grafos direcionados, a aresta u -> v vira v -> u. Util para
        responder "distancia DE varios vertices PARA um alvo t" com um unico
        algoritmo de fonte unica: rodar a busca a partir de t no grafo
        invertido devolve d(v -> t) para todo v. Em grafos nao-direcionados
        o transposto e identico ao original (devolve uma copia).
        """
        rev = GraphList(self._n, directed=self._directed)
        adj = self._adj
        radj = rev._adj
        if self._directed:
            for u in range(1, self._n + 1):
                for v, w in adj[u]:
                    radj[v].append((u, w))
            rev._m = self._m
        else:
            for u in range(1, self._n + 1):
                radj[u] = list(adj[u])
            rev._m = self._m
        rev._is_weighted = self._is_weighted
        rev._has_negative_weight = self._has_negative_weight
        return rev

    def has_edge(self, u: int, v: int) -> bool:
        self._validate_vertex(u)
        self._validate_vertex(v)
        return any(nb == v for nb, _ in self._adj[u])

    def neighbors(self, v: int) -> Iterable[int]:
        """Itera somente pelos ids dos vizinhos. Usado pela Parte 1."""
        self._validate_vertex(v)
        return [nb for nb, _ in self._adj[v]]

    def neighbors_with_weights(self, v: int) -> Iterable[tuple[int, float]]:
        """Itera pelos pares (vizinho, peso). Usado pelo Dijkstra."""
        self._validate_vertex(v)
        return self._adj[v]

    def weight(self, u: int, v: int) -> float:
        self._validate_vertex(u)
        self._validate_vertex(v)
        for nb, w in self._adj[u]:
            if nb == v:
                return w
        raise KeyError(f"aresta ({u}, {v}) nao existe")

    def degree(self, v: int) -> int:
        self._validate_vertex(v)
        return len(self._adj[v])

    def sort_adjacencies(self) -> None:
        """Ordena cada lista de adjacencia em ordem crescente de id.

        Util para tornar deterministicas as buscas BFS/DFS quando
        a ordem de visita dos vizinhos importa (ex.: arvores).
        """
        for v in range(1, self._n + 1):
            self._adj[v].sort(key=lambda pair: pair[0])

    def deduplicate(self) -> int:
        """Remove arestas duplicadas, self-loops e ordena cada lista.

        Em caso de duplicata, mantem a primeira ocorrencia do peso
        (idempotente em re-leituras do mesmo arquivo). Retorna o numero
        de arestas removidas (uma por par de extremidades).
        """
        removed = 0
        for v in range(1, self._n + 1):
            original = self._adj[v]
            if not original:
                continue
            seen: dict[int, float] = {}
            for nb, w in original:
                if nb == v:
                    continue  # remove self-loop residual
                if nb not in seen:
                    seen[nb] = w
            unique = sorted(seen.items(), key=lambda pair: pair[0])
            removed += len(original) - len(unique)
            self._adj[v] = unique
        total = sum(len(self._adj[v]) for v in range(1, self._n + 1))
        if self._directed:
            # cada arco aparece uma unica vez em _adj
            self._m = total
            return removed
        # nao-direcionado: cada aresta foi contada duas vezes (uma por ponta)
        self._m = total // 2
        return removed // 2
