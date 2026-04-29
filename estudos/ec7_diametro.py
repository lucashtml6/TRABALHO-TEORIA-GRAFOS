"""Estudo de Caso 7 - Diametro do grafo (exato e aproximado).

O diametro exato e calculado apenas para grafos com n <= EXACT_LIMIT
(custa O(n*(n+m))). Para os demais, reportamos so a aproximacao por
double-sweep com varias amostras aleatorias.
"""

from __future__ import annotations

import time

from utils import (  # type: ignore
    GRAFOS,
    GRAFOS_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    write_csv,
)

from src import diameter, diameter_approx, load_graph

# Diametro exato exige n BFSs. Acima desse limite, pulamos o exato.
EXACT_LIMIT = 12_000

APPROX_SAMPLES = 5
APPROX_SEED = 0


def main() -> None:
    banner(
        f"EC7 - Diametro (exato p/ n <= {EXACT_LIMIT}, aproximado p/ todos)"
    )

    headers = [
        "grafo", "n", "diametro_exato", "tempo_exato_s",
        "diametro_aprox", "tempo_aprox_s",
    ]
    rows: list[list] = []

    for name in GRAFOS:
        path = GRAFOS_DIR / name
        if not path.exists():
            continue
        g = load_graph(path, "list")
        n = g.n_vertices

        # Aproximado (sempre)
        t0 = time.perf_counter()
        da = diameter_approx(g, samples=APPROX_SAMPLES, seed=APPROX_SEED)
        dt_a = time.perf_counter() - t0

        # Exato (apenas se viavel)
        if n <= EXACT_LIMIT:
            t0 = time.perf_counter()
            de = diameter(g)
            dt_e = time.perf_counter() - t0
            de_str, dt_e_str = str(de), f"{dt_e:.2f}"
        else:
            de_str, dt_e_str = "INVIAVEL", "-"

        row = [name, n, de_str, dt_e_str, da, f"{dt_a:.2f}"]
        rows.append(row)
        print(
            f"  {name}: exato={de_str} ({dt_e_str}s), "
            f"aprox={da} ({dt_a:.2f}s)"
        )

    write_csv(RESULTADOS_DIR / "ec7_diametro.csv", headers, rows)
    md = format_markdown_table(headers, rows)
    (RESULTADOS_DIR / "ec7_diametro.md").write_text(md + "\n", encoding="utf-8")
    print("\nResultados salvos em:")
    print(f"  {RESULTADOS_DIR / 'ec7_diametro.csv'}")
    print(f"  {RESULTADOS_DIR / 'ec7_diametro.md'}")
    print()
    print(md)


if __name__ == "__main__":
    main()
