from typing import Iterable

import numpy as np

from .graph_base import Graph


class GraphMatrix(Graph):
    """
    Grafo nao-direcionado representado por matriz de adjacencia.

    Mantemos duas matrizes (n+1) x (n+1) para preservar a indexacao 1..n:
      - self._adj   (bool) : True se existe aresta {u, v}
      - self._w     (float): peso da aresta (so faz sentido onde _adj e True)

    Optei por duas matrizes em vez de uma so com sentinela porque peso 0.0
    e um valor valido de aresta; NaN seria valido mas obriga uso de np.isnan
    em todo lugar e dificulta a vetorizacao.
    """

    def __init__(self, n_vertices: int) -> None:
        super().__init__(n_vertices)
        self._adj = np.zeros((n_vertices + 1, n_vertices + 1), dtype=bool)
        self._w = np.zeros((n_vertices + 1, n_vertices + 1), dtype=np.float32)

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> bool:
        """
        Adiciona aresta {u, v} com peso. Self-loops sao ignorados; duplicatas
        nao incrementam o contador (matriz e idempotente — mantem o primeiro peso).
        """
        self._validate_vertex(u)
        self._validate_vertex(v)
        if u == v:
            return False
        if self._adj[u, v]:
            return False
        w = float(weight)
        self._adj[u, v] = True
        self._adj[v, u] = True
        self._w[u, v] = w
        self._w[v, u] = w
        self._m += 1
        if w != 1.0:
            self._is_weighted = True
        if w < 0.0:
            self._has_negative_weight = True
        return True

    def deduplicate(self) -> int:
        """No-op de compatibilidade: a matriz ja e livre de duplicatas."""
        return 0

    def has_edge(self, u: int, v: int) -> bool:
        self._validate_vertex(u)
        self._validate_vertex(v)
        return bool(self._adj[u, v])

    def neighbors(self, v: int) -> Iterable[int]:
        """Ids dos vizinhos (sem pesos). Usado por BFS/DFS."""
        self._validate_vertex(v)
        return np.flatnonzero(self._adj[v]).tolist()

    def neighbors_with_weights(self, v: int) -> Iterable[tuple[int, float]]:
        """Pares (vizinho, peso). Usado pelo Dijkstra."""
        self._validate_vertex(v)
        idx = np.flatnonzero(self._adj[v])
        ws = self._w[v, idx]
        return list(zip(idx.tolist(), ws.tolist()))

    def weight(self, u: int, v: int) -> float:
        self._validate_vertex(u)
        self._validate_vertex(v)
        if not self._adj[u, v]:
            raise KeyError(f"aresta ({u}, {v}) nao existe")
        return float(self._w[u, v])

    def degree(self, v: int) -> int:
        self._validate_vertex(v)
        return int(self._adj[v].sum())

    @property
    def matrix(self) -> np.ndarray:
        """Retorna a matriz de adjacencia booleana (somente leitura recomendada)."""
        return self._adj

    @property
    def weights(self) -> np.ndarray:
        """Retorna a matriz de pesos (so valida onde matrix e True)."""
        return self._w
