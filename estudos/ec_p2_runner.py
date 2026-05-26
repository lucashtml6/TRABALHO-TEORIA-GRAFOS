"""Runner consolidado da Parte 2: carrega cada grafo UMA VEZ e roda
EC8 (Dijkstra de 10 -> {20,30,40,50,60}) e EC9 (tempo medio vetor vs heap)
em sequencia. Salva os resultados consolidados, e permite saltar grafos
muito grandes via --max-n.
"""

from __future__ import annotations

import argparse
import gc
import math
import random
import time
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

from src import dijkstra_heap, dijkstra_vector, load_graph


# EC8
SOURCE = 10
TARGETS = [20, 30, 40, 50, 60]

# EC9
K_HEAP_DEFAULT = 100


def vector_k_for(n: int) -> int:
    """Dijkstra-vetor e Theta(V^2). Ajustamos k segundo o n."""
    if n <= 15_000:
        return 100
    if n <= 60_000:
        return 30
    if n <= 200_000:
        return 5
    return 1


def format_path(path: list[int], max_inner: int = 6) -> str:
    if not path:
        return "-"
    if len(path) <= max_inner + 2:
        return " -> ".join(str(v) for v in path)
    head = path[:max_inner // 2]
    tail = path[-max_inner // 2:]
    return " -> ".join(str(v) for v in head) + f" -> ... ({len(path) - max_inner} omit.) -> " + " -> ".join(str(v) for v in tail)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max-n",
        type=int,
        default=None,
        help="pula grafos com mais de N vertices (util pra testar so os menores)",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="restringe aos grafos cujo nome contenha esses sufixos (ex.: 1 2 3)",
    )
    parser.add_argument(
        "--skip-vector",
        action="store_true",
        help="pula Dijkstra-vetor (so heap)",
    )
    parser.add_argument(
        "--load-timeout",
        type=float,
        default=None,
        help="(informativo) se a carga ultrapassar X segundos, marca como inviavel",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)

    ec8_rows_md: list[list[str]] = []
    ec8_rows_csv: list[list] = []
    ec9_rows_md: list[list[str]] = []
    ec9_rows_csv: list[list] = []
    inviabilidades: list[tuple[str, str]] = []

    for name in GRAFOS_W:
        if args.only and not any(s in name for s in args.only):
            continue
        path = GRAFOS_W_DIR / name
        if not path.exists():
            print(f"[skip] {name} nao encontrado")
            continue

        banner(f"Parte 2 — {name}")
        t0 = time.perf_counter()
        g = load_graph(path)
        t_load = time.perf_counter() - t0
        n = g.n_vertices
        m = g.n_edges
        print(f"carga: {t_load:.2f}s  n={n:,}  m={m:,}  weighted={g.is_weighted}")

        if args.max_n is not None and n > args.max_n:
            print(f"[skip] n={n:,} > max-n={args.max_n:,}")
            inviabilidades.append((name, f"n={n:,} > limite {args.max_n:,}"))
            del g
            gc.collect()
            continue

        if g.has_negative_weight:
            print("[skip] grafo com aresta negativa — Dijkstra inaplicavel")
            inviabilidades.append((name, "aresta negativa"))
            del g
            gc.collect()
            continue

        # ============= EC8: 10 -> {20,30,40,50,60} ============================
        print("\n  >> EC8: dist + caminho a partir de 10")
        if not (1 <= SOURCE <= n):
            print(f"  [skip] fonte {SOURCE} fora do intervalo")
        else:
            t_run, res = time_block(dijkstra_heap, g, SOURCE)
            print(f"  Dijkstra (heap) de {SOURCE}: {t_run:.3f}s")
            for tgt in TARGETS:
                if tgt > n:
                    d_str = "fora"
                    p_str = "-"
                else:
                    d = res.dist[tgt]
                    if d == math.inf:
                        d_str = "inf"
                        p_str = "-"
                    else:
                        d_str = f"{d:.4f}"
                        p_str = format_path(res.path_to(tgt))
                ec8_rows_md.append([name, str(SOURCE), str(tgt), d_str, p_str])
                ec8_rows_csv.append([name, SOURCE, tgt, d_str, p_str])
                print(f"    {SOURCE} -> {tgt}: dist={d_str}")
            del res

        # ============= EC9: tempo medio vetor vs heap =========================
        print("\n  >> EC9: tempo medio Dijkstra")
        all_sources = rng.sample(range(1, n + 1), min(K_HEAP_DEFAULT, n))
        k_heap = len(all_sources)
        k_vec = min(vector_k_for(n), k_heap)

        print(f"  heap com k={k_heap}...")
        t0 = time.perf_counter()
        for s in all_sources:
            dijkstra_heap(g, s)
        t_heap = time.perf_counter() - t0
        avg_heap_ms = (t_heap / k_heap) * 1000
        print(f"    total {t_heap:.2f}s  medio {avg_heap_ms:.2f} ms/fonte")

        if args.skip_vector or k_vec == 0:
            avg_vec_ms = float("nan")
            k_vec_used = 0
            speedup_str = "—"
        else:
            print(f"  vetor com k={k_vec}...")
            t0 = time.perf_counter()
            for s in all_sources[:k_vec]:
                dijkstra_vector(g, s)
            t_vec = time.perf_counter() - t0
            avg_vec_ms = (t_vec / k_vec) * 1000
            k_vec_used = k_vec
            speedup = avg_vec_ms / avg_heap_ms
            speedup_str = f"{speedup:.1f}×"
            print(f"    total {t_vec:.2f}s  medio {avg_vec_ms:.2f} ms/fonte ({speedup:.1f}× mais lento)")

        ec9_rows_md.append([
            name,
            f"{n:,}",
            f"{m:,}",
            f"{avg_heap_ms:.2f}",
            f"{k_heap}",
            (f"{avg_vec_ms:.2f}" if avg_vec_ms == avg_vec_ms else "—"),
            f"{k_vec_used}" if k_vec_used > 0 else "—",
            speedup_str,
        ])
        ec9_rows_csv.append([name, n, m, avg_heap_ms, k_heap, avg_vec_ms, k_vec_used])

        # libera o grafo entre iteracoes
        del g
        gc.collect()

    # ============= Escreve resultados ==========================================
    ec8_headers = ["grafo", "origem", "destino", "distancia", "caminho"]
    write_csv(RESULTADOS_DIR / "ec8_dijkstra_caminhos.csv", ec8_headers, ec8_rows_csv)
    with (RESULTADOS_DIR / "ec8_dijkstra_caminhos.md").open("w", encoding="utf-8") as f:
        f.write("# EC8 — Distancia e caminho minimo do vertice 10\n\n")
        f.write(format_markdown_table(ec8_headers, ec8_rows_md))
        f.write("\n")

    ec9_headers_md = [
        "grafo", "n", "m",
        "heap (ms/fonte)", "k_heap",
        "vetor (ms/fonte)", "k_vetor",
        "speedup vec/heap",
    ]
    ec9_headers_csv = ["grafo", "n", "m", "heap_ms", "k_heap", "vetor_ms", "k_vetor"]
    write_csv(RESULTADOS_DIR / "ec9_dijkstra_tempo.csv", ec9_headers_csv, ec9_rows_csv)
    with (RESULTADOS_DIR / "ec9_dijkstra_tempo.md").open("w", encoding="utf-8") as f:
        f.write("# EC9 — Tempo medio do Dijkstra (vetor vs heap)\n\n")
        f.write(format_markdown_table(ec9_headers_md, ec9_rows_md))
        f.write("\n\nObservacao: a versao com vetor e Theta(V^2). Em grafos grandes\n"
                "reduzimos `k_vetor` para que o estudo termine — o tempo *medio* por\n"
                "fonte permanece comparavel entre as colunas.\n")
        if inviabilidades:
            f.write("\n### Grafos pulados\n\n")
            for name, motivo in inviabilidades:
                f.write(f"- **{name}**: {motivo}\n")

    print()
    print("=" * 70)
    print("  Concluido")
    print("=" * 70)
    print(f"EC8 -> {RESULTADOS_DIR / 'ec8_dijkstra_caminhos.md'}")
    print(f"EC9 -> {RESULTADOS_DIR / 'ec9_dijkstra_tempo.md'}")
    if inviabilidades:
        print(f"\nInviabilidades:")
        for name, motivo in inviabilidades:
            print(f"  {name}: {motivo}")


if __name__ == "__main__":
    main()
