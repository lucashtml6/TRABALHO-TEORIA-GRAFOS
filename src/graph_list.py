from typing import Iterable

from .graph_base import Graph


class GraphList(Graph):
    """Grafo nao-direcionado representado por lista de adjacencia."""

    def __init__(self, n_vertices: int) -> None:
        super().__init__(n_vertices)
        self._adj: list[list[int]] = [[] for _ in range(n_vertices + 1)]

    def add_edge(self, u: int, v: int) -> bool:
        """
        Adiciona aresta {u, v}. NAO verifica duplicatas (rapido para
        carga de arquivos grandes). Self-loops sao ignorados.
        """
        self._validate_vertex(u)
        self._validate_vertex(v)
        if u == v:
            return False
        self._adj[u].append(v)
        self._adj[v].append(u)
        self._m += 1
        return True

    def has_edge(self, u: int, v: int) -> bool:
        self._validate_vertex(u)
        self._validate_vertex(v)
        return v in self._adj[u]

    def neighbors(self, v: int) -> Iterable[int]:
        self._validate_vertex(v)
        return self._adj[v]

    def degree(self, v: int) -> int:
        self._validate_vertex(v)
        return len(self._adj[v])

    def sort_adjacencies(self) -> None:
        """Ordena cada lista de adjacencia em ordem crescente.

        Util para tornar deterministicas as buscas BFS/DFS quando
        a ordem de visita dos vizinhos importa (ex.: arvores).
        """
        for v in range(1, self._n + 1):
            self._adj[v].sort()

    def deduplicate(self) -> int:
        """Remove arestas duplicadas, self-loops e ordena cada lista.

        Faz dedup por vertice (memoria O(grau_max)), recalcula self._m.
        Apos esta operacao, neighbors(v) retorna vizinhos em ordem
        crescente, igualando a representacao por matriz.
        Retorna o numero de arestas removidas.
        """
        removed = 0
        for v in range(1, self._n + 1):
            original = self._adj[v]
            if not original:
                continue
            unique = sorted(set(original))
            if unique and unique[0] <= v <= unique[-1]:
                # remove self-loop residual se houver
                try:
                    unique.remove(v)
                except ValueError:
                    pass
            removed += len(original) - len(unique)
            self._adj[v] = unique
        # cada aresta foi contada duas vezes (uma em cada extremidade)
        self._m = sum(len(self._adj[v]) for v in range(1, self._n + 1)) // 2
        return removed // 2
