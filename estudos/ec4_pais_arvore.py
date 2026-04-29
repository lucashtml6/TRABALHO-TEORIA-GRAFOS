"""Estudo de Caso 4 - Pai de 10, 20 e 30 nas arvores BFS e DFS.

Para cada grafo, calcula a arvore geradora induzida pela BFS e pela DFS
partindo dos vertices 1, 2 e 3, e reporta o pai dos vertices 10, 20 e 30
em cada combinacao. "-" significa que o vertice de destino nao foi
alcancado a partir daquela raiz (componente diferente).
"""

from __future__ import annotations

from utils import (  # type: ignore
    GRAFOS,
    GRAFOS_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    write_csv,
)

from src import bfs, dfs, load_graph

ROOTS = [1, 2, 3]
TARGETS = [10, 20, 30]


def parent_or_dash(result, v: int) -> str:
    if v >= len(result.parent) or result.level[v] == -1:
        return "-"
    return str(result.parent[v])


def main() -> None:
    banner("EC4 - Pais de 10/20/30 nas arvores BFS e DFS")

    headers = ["grafo", "algoritmo", "raiz"] + [f"pai({v})" for v in TARGETS]
    rows: list[list] = []

    for name in GRAFOS:
        path = GRAFOS_DIR / name
        if not path.exists():
            continue
        g = load_graph(path, "list")

        for raiz in ROOTS:
            if raiz > g.n_vertices:
                continue
            r_bfs = bfs(g, raiz)
            r_dfs = dfs(g, raiz)
            rows.append(
                [name, "BFS", raiz] + [parent_or_dash(r_bfs, v) for v in TARGETS]
            )
            rows.append(
                [name, "DFS", raiz] + [parent_or_dash(r_dfs, v) for v in TARGETS]
            )
        print(f"  {name} processado")

    write_csv(RESULTADOS_DIR / "ec4_pais_arvore.csv", headers, rows)
    md = format_markdown_table(headers, rows)
    (RESULTADOS_DIR / "ec4_pais_arvore.md").write_text(md + "\n", encoding="utf-8")
    print("\nResultados salvos em:")
    print(f"  {RESULTADOS_DIR / 'ec4_pais_arvore.csv'}")
    print(f"  {RESULTADOS_DIR / 'ec4_pais_arvore.md'}")
    print()
    print(md)


if __name__ == "__main__":
    main()
