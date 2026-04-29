"""Estudo de Caso 1 — Memoria utilizada pelas duas representacoes.

Para cada grafo, mede o aumento de memoria residente (RSS) causado
por carregar o grafo em lista de adjacencia e em matriz de adjacencia.
A matriz e pulada para grafos com n > MAX_MATRIX_VERTICES.
"""

from __future__ import annotations

import gc

from utils import (  # type: ignore
    GRAFOS,
    GRAFOS_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    matrix_feasible,
    measure_load_memory,
    write_csv,
)

from src import load_graph


def main() -> None:
    banner("EC1 - Memoria das duas representacoes")
    print(f"Grafos analisados: {GRAFOS}\n")

    headers = ["grafo", "n", "m", "mem_lista_MB", "mem_matriz_MB", "razao"]
    rows: list[list] = []

    for name in GRAFOS:
        path = GRAFOS_DIR / name
        if not path.exists():
            print(f"  [pular] {name} nao encontrado")
            continue

        # ---- Lista ----
        before, after, gl = measure_load_memory(lambda: load_graph(path, "list"))
        mem_lista = after - before
        n = gl.n_vertices
        m = gl.n_edges
        del gl
        gc.collect()

        # ---- Matriz (so se for viavel) ----
        if matrix_feasible(n):
            before, after, gm = measure_load_memory(
                lambda: load_graph(path, "matrix")
            )
            mem_matriz = after - before
            del gm
            gc.collect()
            mem_matriz_str = f"{mem_matriz:.1f}"
            razao_str = f"{mem_matriz / mem_lista:.1f}x" if mem_lista > 0 else "n/a"
        else:
            mem_matriz_str = "INVIAVEL"
            razao_str = "-"

        row = [name, n, m, f"{mem_lista:.1f}", mem_matriz_str, razao_str]
        rows.append(row)
        print(
            f"  {name}: n={n}, m={m} | lista {mem_lista:.1f} MB | matriz {mem_matriz_str} MB"
        )

    # CSV + Markdown
    write_csv(RESULTADOS_DIR / "ec1_memoria.csv", headers, rows)
    md = format_markdown_table(headers, rows)
    (RESULTADOS_DIR / "ec1_memoria.md").write_text(md + "\n", encoding="utf-8")
    print("\nResultados salvos em:")
    print(f"  {RESULTADOS_DIR / 'ec1_memoria.csv'}")
    print(f"  {RESULTADOS_DIR / 'ec1_memoria.md'}")
    print()
    print(md)


if __name__ == "__main__":
    main()
