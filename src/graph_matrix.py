from typing import Iterable

import numpy as np

from .graph_base import Graph


class GraphMatrix(Graph):
    """
    Grafo nao-direcionado representado por matriz de adjacencia (numpy bool).

    A matriz tem shape (n+1, n+1) e a linha/coluna 0 e ignorada para
    manter a indexacao 1..n.
    """

    def __init__(self, n_vertices: int) -> None:
        super().__init__(n_vertices)
        self._adj = np.zeros((n_vertices + 1, n_vertices + 1), dtype=bool)

    def add_edge(self, u: int, v: int) -> bool:
        """
        Adiciona aresta {u, v}. Self-loops sao ignorados. Duplicatas
        nao incrementam o contador de arestas (matriz e idempotente).
        """
        self._validate_vertex(u)
        self._validate_vertex(v)
        if u == v:
            return False
        if self._adj[u, v]:
            return False
        self._adj[u, v] = True
        self._adj[v, u] = True
        self._m += 1
        return True

    def deduplicate(self) -> int:
        """No-op de compatibilidade: a matriz ja e livre de duplicatas."""
        return 0

    def has_edge(self, u: int, v: int) -> bool:
        self._validate_vertex(u)
        self._validate_vertex(v)
        return bool(self._adj[u, v])

    def neighbors(self, v: int) -> Iterable[int]:
        self._validate_vertex(v)
        # np.flatnonzero retorna indices onde a linha e True
        return np.flatnonzero(self._adj[v]).tolist()

    def degree(self, v: int) -> int:
        self._validate_vertex(v)
        return int(self._adj[v].sum())

    @property
    def matrix(self) -> np.ndarray:
        """Retorna a matriz subjacente (somente leitura recomendada)."""
        return self._adj
