"""Estudo de Caso 5 - Distancias entre pares (10,20), (10,30), (20,30)."""

from __future__ import annotations

import math

from utils import (  # type: ignore
    GRAFOS,
    GRAFOS_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    write_csv,
)

from src import distance, load_graph

PARES = [(10, 20), (10, 30), (20, 30)]


def fmt(d) -> str:
    return "inf" if d == math.inf else str(d)


def main() -> None:
    banner("EC5 - Distancias entre pares")

    headers = ["grafo", "n"] + [f"d({u},{v})" for u, v in PARES]
    rows: list[list] = []

    for name in GRAFOS:
        path = GRAFOS_DIR / name
        if not path.exists():
            continue
        g = load_graph(path, "list")
        ds = []
        for u, v in PARES:
            if u > g.n_vertices or v > g.n_vertices:
                ds.append("-")
            else:
                ds.append(fmt(distance(g, u, v)))
        rows.append([name, g.n_vertices] + ds)
        print(f"  {name}: " + " ".join(f"d{p}={d}" for p, d in zip(PARES, ds)))

    write_csv(RESULTADOS_DIR / "ec5_distancias.csv", headers, rows)
    md = format_markdown_table(headers, rows)
    (RESULTADOS_DIR / "ec5_distancias.md").write_text(md + "\n", encoding="utf-8")
    print("\nResultados salvos em:")
    print(f"  {RESULTADOS_DIR / 'ec5_distancias.csv'}")
    print(f"  {RESULTADOS_DIR / 'ec5_distancias.md'}")
    print()
    print(md)


if __name__ == "__main__":
    main()
