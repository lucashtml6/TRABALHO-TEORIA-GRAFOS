"""Runner para grafos grandes (W_4 com n=1M, W_5 com n=10M).

Aqui rodamos APENAS Dijkstra com heap, com k_heap reduzido em proporcao
ao tamanho do grafo. A versao com vetor (Theta(V^2)) e inviavel nessas
escalas e seria omitida (cf. relatorio).

Tambem fazemos a chamada Dijkstra de 10 -> {20,30,40,50,60} (EC8) para
completar a tabela.
"""

from __future__ import annotations

import argparse
import gc
import math
import random
import time
from pathlib import Path

from utils import (
    GRAFOS_W_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    write_csv,
)

from src import dijkstra_heap, load_graph


SOURCE = 10
TARGETS = [20, 30, 40, 50, 60]


def k_for(n: int) -> int:
    """Quantas fontes amostrar para o heap."""
    if n <= 200_000:
        return 100
    if n <= 2_000_000:
        return 10
    return 3  # >= 10M


def format_path(path: list[int], max_inner: int = 6) -> str:
    if not path:
        return "-"
    if len(path) <= max_inner + 2:
        return " -> ".join(str(v) for v in path)
    head = path[:max_inner // 2]
    tail = path[-max_inner // 2:]
    return " -> ".join(str(v) for v in head) + f" -> ... ({len(path) - max_inner} omit.) -> " + " -> ".join(str(v) for v in tail)


def run_one(name: str, seed: int) -> tuple[list, list]:
    path = GRAFOS_W_DIR / name
    banner(f"Parte 2 — {name}")
    if not path.exists():
        print(f"[skip] arquivo nao existe")
        return [], []

    t0 = time.perf_counter()
    g = load_graph(path)
    t_load = time.perf_counter() - t0
    n, m = g.n_vertices, g.n_edges
    print(f"carga: {t_load:.2f}s  n={n:,}  m={m:,}")

    if g.has_negative_weight:
        print("[skip] grafo com aresta negativa")
        return [], []

    # EC8
    ec8_rows = []
    if 1 <= SOURCE <= n:
        t0 = time.perf_counter()
        res = dijkstra_heap(g, SOURCE)
        t_run = time.perf_counter() - t0
        print(f"Dijkstra (heap) de {SOURCE}: {t_run:.2f}s")
        for tgt in TARGETS:
            if tgt > n:
                d_str, p_str = "fora", "-"
            else:
                d = res.dist[tgt]
                if d == math.inf:
                    d_str, p_str = "inf", "-"
                else:
                    d_str = f"{d:.4f}"
                    p_str = format_path(res.path_to(tgt))
            ec8_rows.append([name, SOURCE, tgt, d_str, p_str])
            print(f"  {SOURCE} -> {tgt}: dist={d_str}")
        del res

    # EC9 - so heap, com k adaptativo
    k = k_for(n)
    rng = random.Random(seed)
    sources = rng.sample(range(1, n + 1), min(k, n))
    print(f"\nEC9 heap com k={len(sources)} (vetor INVIAVEL para n={n:,})...")
    t0 = time.perf_counter()
    for s in sources:
        dijkstra_heap(g, s)
    t_total = time.perf_counter() - t0
    avg_ms = (t_total / len(sources)) * 1000
    print(f"  total {t_total:.2f}s  medio {avg_ms:.2f} ms/fonte")
    ec9_row = [name, n, m, avg_ms, len(sources), "INVIAVEL", 0]

    del g
    gc.collect()
    return ec8_rows, [ec9_row]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="+", default=["4", "5"])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    ec8_all = []
    ec9_all = []
    for suffix in args.only:
        name = f"grafo_W_{suffix}.txt"
        ec8, ec9 = run_one(name, args.seed)
        ec8_all.extend(ec8)
        ec9_all.extend(ec9)

    # Acrescenta aos arquivos existentes (sem sobrescrever resultados anteriores)
    if ec8_all:
        with (RESULTADOS_DIR / "ec8_dijkstra_caminhos_grandes.csv").open("w", encoding="utf-8", newline="") as f:
            import csv
            w = csv.writer(f)
            w.writerow(["grafo", "origem", "destino", "distancia", "caminho"])
            w.writerows(ec8_all)
        with (RESULTADOS_DIR / "ec8_dijkstra_caminhos_grandes.md").open("w", encoding="utf-8") as f:
            f.write("# EC8 — Grafos grandes (somente heap)\n\n")
            f.write(format_markdown_table(
                ["grafo", "origem", "destino", "distancia", "caminho"],
                [[str(c) for c in r] for r in ec8_all],
            ))
            f.write("\n")
    if ec9_all:
        with (RESULTADOS_DIR / "ec9_dijkstra_tempo_grandes.csv").open("w", encoding="utf-8", newline="") as f:
            import csv
            w = csv.writer(f)
            w.writerow(["grafo", "n", "m", "heap_ms", "k_heap", "vetor_ms", "k_vetor"])
            w.writerows(ec9_all)
        with (RESULTADOS_DIR / "ec9_dijkstra_tempo_grandes.md").open("w", encoding="utf-8") as f:
            f.write("# EC9 — Grafos grandes (somente heap)\n\n")
            f.write(format_markdown_table(
                ["grafo", "n", "m", "heap (ms/fonte)", "k_heap", "vetor", "k_vetor"],
                [[str(c) for c in r] for r in ec9_all],
            ))
            f.write("\n\nVetor INVIAVEL nestes grafos (Theta(V^2) com V >= 10^6).\n")
    print("\nFeito.")


if __name__ == "__main__":
    main()
