from abc import ABC, abstractmethod
from typing import Iterable


class Graph(ABC):
    """
    Interface comum das duas representacoes de grafo nao-direcionado.
    Convencao: vertices indexados de 1 ate n (o indice 0 nao e usado).
    """

    def __init__(self, n_vertices: int) -> None:
        if n_vertices < 1:
            raise ValueError("numero de vertices deve ser >= 1")
        self._n = n_vertices
        self._m = 0

    @property
    def n_vertices(self) -> int:
        return self._n

    @property
    def n_edges(self) -> int:
        return self._m

    def _validate_vertex(self, v: int) -> None:
        if not (1 <= v <= self._n):
            raise ValueError(f"vertice {v} fora do intervalo [1, {self._n}]")

    @abstractmethod
    def add_edge(self, u: int, v: int) -> bool:
        """Adiciona aresta {u, v}. Retorna True se a aresta era nova."""

    @abstractmethod
    def has_edge(self, u: int, v: int) -> bool: ...

    @abstractmethod
    def neighbors(self, v: int) -> Iterable[int]: ...

    @abstractmethod
    def degree(self, v: int) -> int: ...

    def deduplicate(self) -> int:
        """Remove arestas duplicadas. Implementacoes podem sobrescrever.

        Retorna o numero de arestas duplicadas removidas.
        """
        return 0

    def __repr__(self) -> str:
        return f"{type(self).__name__}(n={self._n}, m={self._m})"
