"""Estudo de Caso 3 - Tempo medio de 100 DFSs.

Mesma logica do EC2, com DFS.
"""

from __future__ import annotations

import gc
import random
import time

from utils import (  # type: ignore
    GRAFOS,
    GRAFOS_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    matrix_feasible,
    write_csv,
)

from src import dfs, load_graph

N_BUSCAS = 100
SEED = 42


def avg_dfs_time(graph, sources: list[int]) -> float:
    t0 = time.perf_counter()
    for s in sources:
        dfs(graph, s)
    total = time.perf_counter() - t0
    return total / len(sources)


def main() -> None:
    banner(f"EC3 - Tempo medio de {N_BUSCAS} DFSs")

    headers = ["grafo", "n", "m", "dfs_lista_ms", "dfs_matriz_ms"]
    rows: list[list] = []
    rng = random.Random(SEED)

    for name in GRAFOS:
        path = GRAFOS_DIR / name
        if not path.exists():
            continue

        gl = load_graph(path, "list")
        n, m = gl.n_vertices, gl.n_edges
        sources = rng.sample(range(1, n + 1), k=min(N_BUSCAS, n))

        avg_list = avg_dfs_time(gl, sources)
        del gl
        gc.collect()

        if matrix_feasible(n):
            gm = load_graph(path, "matrix")
            avg_mat = avg_dfs_time(gm, sources)
            del gm
            gc.collect()
            mat_str = f"{avg_mat * 1000:.2f}"
        else:
            mat_str = "INVIAVEL"

        row = [name, n, m, f"{avg_list * 1000:.2f}", mat_str]
        rows.append(row)
        print(f"  {name}: lista {avg_list*1000:.2f} ms | matriz {mat_str} ms")

    write_csv(RESULTADOS_DIR / "ec3_tempo_dfs.csv", headers, rows)
    md = format_markdown_table(headers, rows)
    (RESULTADOS_DIR / "ec3_tempo_dfs.md").write_text(md + "\n", encoding="utf-8")
    print("\nResultados salvos em:")
    print(f"  {RESULTADOS_DIR / 'ec3_tempo_dfs.csv'}")
    print(f"  {RESULTADOS_DIR / 'ec3_tempo_dfs.md'}")
    print()
    print(md)


if __name__ == "__main__":
    main()
