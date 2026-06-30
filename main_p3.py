"""Demonstra a Parte 3 da biblioteca: grafos DIRECIONADOS com pesos,
Dijkstra/BFS/DFS em grafos direcionados e o algoritmo de Bellman-Ford.

Usa um pequeno grafo direcionado com arestas negativas (sem ciclo negativo)
— o exemplo classico do CLRS — e mostra:

  1. As distancias minimas a partir do vertice 1 com Bellman-Ford.
  2. Que a busca segue apenas as arestas de SAIDA (semantica direcionada).
  3. O truque do grafo invertido para distancia "ATE" um vertice.
  4. A deteccao de ciclo negativo quando uma aresta o cria.
"""

from pathlib import Path

from src import (
    bellman_ford,
    dijkstra_heap,
    load_graph,
    GraphList,
)

ROOT = Path(__file__).parent
EXEMPLO = ROOT / "exemplos" / "grafo_dir_W.txt"


def imprimir(res, n: int) -> None:
    print(f"  algoritmo = {res.algorithm}, fonte = {res.source}")
    print(f"  {'v':>2s} {'pai':>3s} {'dist':>8s}  caminho")
    for v in range(1, n + 1):
        path = res.path_to(v)
        path_str = " -> ".join(str(x) for x in path) if path else "(inalcancavel)"
        print(f"  {v:>2d} {res.parent[v]:>3d} {res.dist[v]:>8.2f}  {path_str}")


def main() -> None:
    print(f"Carregando (DIRECIONADO): {EXEMPLO}")
    g = load_graph(EXEMPLO, directed=True)
    print(f"  {g!r}\n")

    print("[Bellman-Ford a partir do vertice 1]")
    bf = bellman_ford(g, source=1)
    imprimir(bf, g.n_vertices)
    print(f"  ciclo negativo? {bf.has_negative_cycle}\n")

    print("[Semantica direcionada] vizinhos de SAIDA do vertice 1:",
          [nb for nb, _ in g.neighbors_with_weights(1)])

    # truque do grafo invertido: distancia ATE o vertice 1
    print("\n[Grafo invertido] distancia de cada vertice ATE o vertice 1")
    grev = g.reverse()
    bf_rev = bellman_ford(grev, source=1)
    for v in range(1, g.n_vertices + 1):
        print(f"  d({v} -> 1) = {bf_rev.dist[v]:.2f}")

    # grafo sem pesos negativos: Bellman-Ford e Dijkstra concordam
    print("\n[Validacao] grafo direcionado SEM pesos negativos: BF == Dijkstra")
    gp = GraphList(6, directed=True)
    for u, v, w in [(1, 2, 7), (1, 3, 9), (1, 6, 14), (2, 3, 10),
                    (2, 4, 15), (3, 4, 11), (3, 6, 2), (4, 5, 6), (6, 5, 9)]:
        gp.add_edge(u, v, w)
    d_bf = bellman_ford(gp, 1).dist[1:]
    d_dj = dijkstra_heap(gp, 1).dist[1:]
    print(f"  Bellman-Ford: {d_bf}")
    print(f"  Dijkstra    : {d_dj}")
    print(f"  iguais? {d_bf == d_dj}")

    # introduzindo um ciclo negativo
    print("\n[Ciclo negativo] adicionando a aresta 5 -> 4 com peso -10")
    gc = GraphList(5, directed=True)
    edges = [(1, 2, 6), (1, 4, 7), (2, 3, 5), (2, 4, 8), (2, 5, -4),
             (3, 2, -2), (4, 3, -3), (4, 5, 9), (5, 3, 7), (5, 1, 2),
             (5, 4, -10)]
    for u, v, w in edges:
        gc.add_edge(u, v, w)
    bf_cyc = bellman_ford(gc, 1)
    print(f"  ciclo negativo detectado? {bf_cyc.has_negative_cycle}")


if __name__ == "__main__":
    main()
