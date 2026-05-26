"""EC8 — Distancia e caminho minimo do vertice 10 para 20, 30, 40, 50, 60.

Para cada grafo_W_k disponivel em GRAFOS 2/, executa Dijkstra (heap) a partir
do vertice 10 e reporta distancia + caminho ate cada um dos alvos. Salva CSV
e Markdown em relatorio/resultados/.
"""

from __future__ import annotations

import math
from pathlib import Path

from utils import (
    GRAFOS_W,
    GRAFOS_W_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    time_block,
    write_csv,
)

from src import load_graph, dijkstra_heap


SOURCE = 10
TARGETS = [20, 30, 40, 50, 60]


def format_path(path: list[int], max_inner: int = 6) -> str:
    """Formata um caminho como '1 -> 2 -> ... -> 99'. Trunca o miolo se for grande."""
    if not path:
        return "-"
    if len(path) <= max_inner + 2:
        return " -> ".join(str(v) for v in path)
    head = path[:max_inner // 2]
    tail = path[-max_inner // 2:]
    return " -> ".join(str(v) for v in head) + f" -> ... ({len(path) - max_inner} omit.) -> " + " -> ".join(str(v) for v in tail)


def main() -> None:
    rows_md: list[list[str]] = []
    rows_csv: list[list] = []

    for name in GRAFOS_W:
        path = GRAFOS_W_DIR / name
        if not path.exists():
            print(f"[skip] {name} nao encontrado em {GRAFOS_W_DIR}")
            continue

        banner(f"EC8 — {name}")
        t_load, g = time_block(load_graph, path)
        print(f"carga: {t_load:.2f}s  n={g.n_vertices:,}  m={g.n_edges:,}  weighted={g.is_weighted}")

        if g.has_negative_weight:
            print("AVISO: grafo tem aresta negativa — Dijkstra abortara.")
        if not (1 <= SOURCE <= g.n_vertices):
            print(f"[skip] fonte {SOURCE} fora do intervalo")
            continue

        t_run, res = time_block(dijkstra_heap, g, SOURCE)
        print(f"Dijkstra (heap) de {SOURCE}: {t_run:.3f}s")

        for tgt in TARGETS:
            if tgt > g.n_vertices:
                d_str = "fora do grafo"
                p_str = "-"
            else:
                d = res.dist[tgt]
                if d == math.inf:
                    d_str = "inf"
                    p_str = "-"
                else:
                    d_str = f"{d:.4f}"
                    p_str = format_path(res.path_to(tgt))
            rows_md.append([name, str(SOURCE), str(tgt), d_str, p_str])
            rows_csv.append([name, SOURCE, tgt, d_str, p_str])
            print(f"  {SOURCE} -> {tgt:>3}: dist = {d_str}")

    headers = ["grafo", "origem", "destino", "distancia", "caminho"]
    write_csv(RESULTADOS_DIR / "ec8_dijkstra_caminhos.csv", headers, rows_csv)

    md_path = RESULTADOS_DIR / "ec8_dijkstra_caminhos.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# EC8 — Distancia e caminho minimo do vertice 10\n\n")
        f.write(format_markdown_table(headers, rows_md))
        f.write("\n")
    print(f"\nCSV : {RESULTADOS_DIR / 'ec8_dijkstra_caminhos.csv'}")
    print(f"MD  : {md_path}")


if __name__ == "__main__":
    main()
