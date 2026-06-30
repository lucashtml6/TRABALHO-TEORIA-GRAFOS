from abc import ABC, abstractmethod
from typing import Iterable


class Graph(ABC):
    """
    Interface comum das duas representacoes de grafo.
    Convencao: vertices indexados de 1 ate n (o indice 0 nao e usado).

    A partir da Parte 2, as arestas podem ter peso (float). Quando o grafo
    e carregado de um arquivo sem coluna de peso, todas as arestas recebem
    peso 1.0 e a flag `is_weighted` permanece False (mantendo a
    compatibilidade com a Parte 1 — BFS/DFS sao indiferentes ao peso).

    A partir da Parte 3, o grafo pode ser direcionado (`directed=True`). Numa
    aresta direcionada `u -> v`, apenas `u` lista `v` como vizinho; `neighbors`
    devolve, portanto, os *sucessores* (vizinhos de saida). BFS, DFS, Dijkstra
    e Bellman-Ford percorrem o grafo seguindo essas arestas de saida, de modo
    que os algoritmos da Parte 1/2 funcionam sem alteracao tanto em grafos
    direcionados quanto nao-direcionados.
    """

    def __init__(self, n_vertices: int, directed: bool = False) -> None:
        if n_vertices < 1:
            raise ValueError("numero de vertices deve ser >= 1")
        self._n = n_vertices
        self._m = 0
        self._is_weighted = False
        self._has_negative_weight = False
        self._directed = directed

    @property
    def n_vertices(self) -> int:
        return self._n

    @property
    def n_edges(self) -> int:
        return self._m

    @property
    def is_directed(self) -> bool:
        return self._directed

    @property
    def is_weighted(self) -> bool:
        """True se pelo menos uma aresta foi inserida com peso != 1.0
        (ou se o carregador explicitamente marcou o grafo como ponderado)."""
        return self._is_weighted

    @property
    def has_negative_weight(self) -> bool:
        return self._has_negative_weight

    def _mark_weighted(self) -> None:
        self._is_weighted = True

    def _validate_vertex(self, v: int) -> None:
        if not (1 <= v <= self._n):
            raise ValueError(f"vertice {v} fora do intervalo [1, {self._n}]")

    @abstractmethod
    def add_edge(self, u: int, v: int, weight: float = 1.0) -> bool:
        """Adiciona aresta {u, v} com peso opcional. Retorna True se a aresta era nova."""

    @abstractmethod
    def has_edge(self, u: int, v: int) -> bool: ...

    @abstractmethod
    def neighbors(self, v: int) -> Iterable[int]:
        """Itera apenas pelos ids dos vizinhos de v (sem pesos).
        Usado por BFS, DFS, componentes — algoritmos da Parte 1."""

    @abstractmethod
    def neighbors_with_weights(self, v: int) -> Iterable[tuple[int, float]]:
        """Itera por pares (vizinho, peso). Usado pelo Dijkstra."""

    @abstractmethod
    def weight(self, u: int, v: int) -> float:
        """Peso da aresta {u, v}. Levanta KeyError se a aresta nao existe."""

    @abstractmethod
    def degree(self, v: int) -> int: ...

    def deduplicate(self) -> int:
        """Remove arestas duplicadas. Implementacoes podem sobrescrever.

        Retorna o numero de arestas duplicadas removidas.
        """
        return 0

    def __repr__(self) -> str:
        kind = "weighted" if self._is_weighted else "unweighted"
        orient = "directed" if self._directed else "undirected"
        return f"{type(self).__name__}({orient}, {kind}, n={self._n}, m={self._m})"
