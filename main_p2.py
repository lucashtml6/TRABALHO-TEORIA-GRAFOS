"""Demonstra a Parte 2 da biblioteca: grafos com peso + Dijkstra.

Usa o grafo da figura 1 do PDF da Parte 2 (versao com pesos positivos) e
mostra a distancia / caminho minimo do vertice 1 para todos os outros,
nas duas implementacoes do Dijkstra (vetor e heap).
"""

from pathlib import Path

from src import (
    NegativeWeightError,
    dijkstra_heap,
    dijkstra_vector,
    load_graph,
    shortest_path,
)

ROOT = Path(__file__).parent
EXEMPLO_POS = ROOT / "exemplos" / "grafo_pdf_W_pos.txt"
EXEMPLO_NEG = ROOT / "exemplos" / "grafo_pdf_W.txt"


def imprimir_resultado(res, n: int) -> None:
    print(f"  algoritmo = {res.algorithm}, fonte = {res.source}")
    print(f"  {'v':>2s} {'pai':>3s} {'dist':>8s}  caminho")
    for v in range(1, n + 1):
        path = res.path_to(v)
        path_str = " -> ".join(str(x) for x in path) if path else "(inalcancavel)"
        print(f"  {v:>2d} {res.parent[v]:>3d} {res.dist[v]:>8.2f}  {path_str}")


def main() -> None:
    print(f"Carregando: {EXEMPLO_POS}")
    g = load_graph(EXEMPLO_POS)
    print(f"  {g!r}\n")

    print("[Dijkstra com VETOR (Theta(V^2))]")
    res_v = dijkstra_vector(g, source=1)
    imprimir_resultado(res_v, g.n_vertices)

    print("\n[Dijkstra com HEAP (O((V+E) log V))]")
    res_h = dijkstra_heap(g, source=1)
    imprimir_resultado(res_h, g.n_vertices)

    # checagem cruzada: as distancias devem ser identicas
    assert res_v.dist == res_h.dist, "vetor e heap divergiram!"
    print("\nOK - vetor e heap concordam em todas as distancias.\n")

    # atalho `shortest_path` para um par especifico
    d, path = shortest_path(g, 1, 3, method="heap")
    print(f"shortest_path(1, 3) = {d:.2f} via {path}")

    # grafo com aresta negativa -> NegativeWeightError
    print(f"\nCarregando: {EXEMPLO_NEG}")
    g_neg = load_graph(EXEMPLO_NEG)
    print(f"  {g_neg!r} (has_negative_weight={g_neg.has_negative_weight})")
    try:
        dijkstra_heap(g_neg, source=1)
    except NegativeWeightError as e:
        print(f"  OK - levantou NegativeWeightError: {e}")


if __name__ == "__main__":
    main()
