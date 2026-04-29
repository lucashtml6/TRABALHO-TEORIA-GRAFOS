from pathlib import Path

from src import bfs, dfs, load_graph, write_search_tree

ROOT = Path(__file__).parent
EXEMPLO = ROOT / "exemplos" / "grafo_pdf.txt"
SAIDAS = ROOT / "saidas"
SAIDAS.mkdir(exist_ok=True)


"""Recebe um grafo e imprime: quantos vértices tem, 
quantas arestas tem, e os vizinhos e o grau de cada vértice."""
def descrever(graph) -> None:
    print(f"  {graph!r}")
    print(f"  vertices = {graph.n_vertices}, arestas = {graph.n_edges}")
    for v in range(1, graph.n_vertices + 1):
        viz = list(graph.neighbors(v))
        print(f"  vizinhos({v}) = {viz}  grau = {graph.degree(v)}")


"""Recebe o resultado de uma busca (BFS ou DFS) e 
imprime uma tabelinha mostrando, para cada vértice,
 quem é seu pai na árvore e em qual nível ele está."""
def imprimir_arvore(result) -> None:
    print(f"  algoritmo = {result.algorithm.upper()}, raiz = {result.root}")
    print(f"  {'v':>2s} {'pai':>3s} {'nivel':>5s}")
    for v in range(1, len(result.level)):
        if result.level[v] != -1:
            print(f"  {v:>2d} {result.parent[v]:>3d} {result.level[v]:>5d}")


def main() -> None:
    print(f"Lendo: {EXEMPLO}\n")

    print("[Lista de adjacencia]") # representação em LISTA
    g_list = load_graph(EXEMPLO, representation="list")
    descrever(g_list)

    print("\n[Matriz de adjacencia]") # representação em MATRIZ
    g_mat = load_graph(EXEMPLO, representation="matrix")
    descrever(g_mat)

    # Funcionalidade 4: BFS e DFS a partir do vertice 1
    print("\n[BFS a partir de 1] (usando lista)")
    r_bfs = bfs(g_list, root=1)  
    imprimir_arvore(r_bfs)
    write_search_tree(r_bfs, SAIDAS / "exemplo_bfs_raiz1.txt")

    print("\n[DFS a partir de 1] (usando lista)")
    r_dfs = dfs(g_list, root=1)
    imprimir_arvore(r_dfs)
    write_search_tree(r_dfs, SAIDAS / "exemplo_dfs_raiz1.txt")

    # Coerencia: lista e matriz devem produzir o mesmo resultado
    r_bfs_m = bfs(g_mat, root=1)
    r_dfs_m = dfs(g_mat, root=1)
    assert r_bfs.parent == r_bfs_m.parent and r_bfs.level == r_bfs_m.level
    assert r_dfs.parent == r_dfs_m.parent and r_dfs.level == r_dfs_m.level
    print("\nOK - BFS e DFS coincidem entre lista e matriz.")
    print(f"Arvores escritas em {SAIDAS}")


if __name__ == "__main__":
    main()
