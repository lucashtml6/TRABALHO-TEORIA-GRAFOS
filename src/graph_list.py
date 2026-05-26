from typing import Iterable

from .graph_base import Graph


class GraphList(Graph):
    """Grafo nao-direcionado representado por lista de adjacencia.

    Cada posicao self._adj[v] e uma lista de tuplas (vizinho, peso). A
    BFS/DFS da Parte 1 chama `neighbors(v)`, que devolve so os ids; o
    Dijkstra chama `neighbors_with_weights(v)`, que devolve os pares.
    """

    def __init__(self, n_vertices: int) -> None:
        super().__init__(n_vertices)
        self._adj: list[list[tuple[int, float]]] = [[] for _ in range(n_vertices + 1)]

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> bool:
        """
        Adiciona aresta {u, v} com peso. NAO verifica duplicatas (rapido para
        carga de arquivos grandes). Self-loops sao ignorados.
        """
        self._validate_vertex(u)
        self._validate_vertex(v)
        if u == v:
            return False
        w = float(weight)
        self._adj[u].append((v, w))
        self._adj[v].append((u, w))
        self._m += 1
        if w != 1.0:
            self._is_weighted = True
        if w < 0.0:
            self._has_negative_weight = True
        return True

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
        # cada aresta foi contada duas vezes (uma em cada extremidade)
        self._m = sum(len(self._adj[v]) for v in range(1, self._n + 1)) // 2
        return removed // 2
