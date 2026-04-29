"""Estudo de Caso 6 - Componentes conexas: contagem, maior e menor."""

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

from src import connected_components, load_graph


def main() -> None:
    banner("EC6 - Componentes conexas")

    headers = ["grafo", "n", "n_componentes", "maior", "menor", "tempo_s"]
    rows: list[list] = []

    for name in GRAFOS:
        path = GRAFOS_DIR / name
        if not path.exists():
            continue
        g = load_graph(path, "list")
        t0 = time.perf_counter()
        cc = connected_components(g)
        dt = time.perf_counter() - t0
        rows.append(
            [
                name,
                g.n_vertices,
                cc.count,
                len(cc.largest),
                len(cc.smallest),
                f"{dt:.2f}",
            ]
        )
        print(
            f"  {name}: cc={cc.count}, maior={len(cc.largest)}, "
            f"menor={len(cc.smallest)}, tempo={dt:.2f}s"
        )

    write_csv(RESULTADOS_DIR / "ec6_componentes.csv", headers, rows)
    md = format_markdown_table(headers, rows)
    (RESULTADOS_DIR / "ec6_componentes.md").write_text(md + "\n", encoding="utf-8")
    print("\nResultados salvos em:")
    print(f"  {RESULTADOS_DIR / 'ec6_componentes.csv'}")
    print(f"  {RESULTADOS_DIR / 'ec6_componentes.md'}")
    print()
    print(md)


if __name__ == "__main__":
    main()
