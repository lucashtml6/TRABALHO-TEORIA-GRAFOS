"""EC9 — Tempo medio do Dijkstra (vetor vs heap) sobre k fontes aleatorias.

Para cada grafo_W_k, sorteia k vertices iniciais e mede o tempo medio de
uma execucao completa de Dijkstra (computa distancia para *todos* os outros
vertices). Compara as duas implementacoes (vetor vs heap).

Observacao importante: a versao com vetor e Theta(V^2) por execucao. Para
grafos grandes ela e proibitiva com k=100 — nesse caso reduzimos o k da
versao com vetor (e reportamos esse k explicitamente). A versao com heap
sempre usa k=100 (ou todo o intervalo permitido pelo grafo).
"""

from __future__ import annotations

import argparse
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

from src import load_graph, dijkstra_vector, dijkstra_heap


# Por padrao usamos 100 fontes; mas o Dijkstra-vetor e Theta(V^2): para
# grafos com muitos vertices isso fica horas. As tabelas abaixo definem
# quantas fontes usar por grafo (uma para o heap, outra para o vetor).
K_HEAP_DEFAULT = 100

# vetor scanea V vertices em cada um dos V passos -> custo ~ V^2 ops Python.
# Em Python ~10^7 ops/s, V=10k => ~10s/exec; V=100k => ~16min/exec.
def vector_budget(n: int) -> int:
    """Numero seguro de fontes a usar com Dijkstra-vetor dado n."""
    if n <= 15_000:
        return 100
    if n <= 60_000:
        return 30
    if n <= 200_000:
        return 5
    return 1  # so para confirmar que roda; tempo medio com k=1


def measure_avg(fn, graph, sources: list[int]) -> tuple[float, int]:
    """Roda fn(graph, src) para cada src; retorna (tempo_total_s, k)."""
    t0 = time.perf_counter()
    for s in sources:
        fn(graph, s)
    return time.perf_counter() - t0, len(sources)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="restringe aos grafos cujos nomes contenham esses sufixos (ex: 1 2)",
    )
    parser.add_argument(
        "--skip-vector",
        action="store_true",
        help="pula totalmente a versao com vetor",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    rows_md: list[list[str]] = []
    rows_csv: list[list] = []

    for name in GRAFOS_W:
        if args.only and not any(s in name for s in args.only):
            continue
        path = GRAFOS_W_DIR / name
        if not path.exists():
            print(f"[skip] {name} nao encontrado")
            continue

        banner(f"EC9 — {name}")
        t_load, g = time_block(load_graph, path)
        n = g.n_vertices
        print(f"carga: {t_load:.2f}s  n={n:,}  m={g.n_edges:,}")

        if g.has_negative_weight:
            print("[skip] grafo tem aresta negativa — Dijkstra inaplicavel")
            continue

        # Sorteia ate K_HEAP_DEFAULT fontes (ou todas, se grafo menor)
        all_sources = rng.sample(range(1, n + 1), min(K_HEAP_DEFAULT, n))
        k_heap = len(all_sources)
        k_vec = min(vector_budget(n), k_heap)
        sources_vec = all_sources[:k_vec]

        print(f"executando heap com k={k_heap}...")
        t_heap, _ = measure_avg(dijkstra_heap, g, all_sources)
        avg_heap_ms = (t_heap / k_heap) * 1000
        print(f"  total {t_heap:.2f}s  medio {avg_heap_ms:.2f} ms/fonte")

        if args.skip_vector:
            avg_vec_ms = float("nan")
            k_vec = 0
            t_vec = 0.0
        else:
            print(f"executando vetor com k={k_vec}...")
            t_vec, _ = measure_avg(dijkstra_vector, g, sources_vec)
            avg_vec_ms = (t_vec / k_vec) * 1000
            print(f"  total {t_vec:.2f}s  medio {avg_vec_ms:.2f} ms/fonte")

        speedup = avg_vec_ms / avg_heap_ms if avg_vec_ms == avg_vec_ms else float("nan")
        rows_md.append([
            name,
            f"{n:,}",
            f"{g.n_edges:,}",
            f"{avg_heap_ms:.2f}",
            f"{k_heap}",
            (f"{avg_vec_ms:.2f}" if avg_vec_ms == avg_vec_ms else "—"),
            f"{k_vec}" if k_vec > 0 else "—",
            (f"{speedup:.1f}×" if speedup == speedup else "—"),
        ])
        rows_csv.append([name, n, g.n_edges, avg_heap_ms, k_heap, avg_vec_ms, k_vec])

        # libera memoria entre grafos
        del g

    headers_md = [
        "grafo", "n", "m",
        "heap (ms/fonte)", "k_heap",
        "vetor (ms/fonte)", "k_vetor",
        "speedup vec/heap",
    ]
    headers_csv = ["grafo", "n", "m", "heap_ms", "k_heap", "vetor_ms", "k_vetor"]
    write_csv(RESULTADOS_DIR / "ec9_dijkstra_tempo.csv", headers_csv, rows_csv)

    md_path = RESULTADOS_DIR / "ec9_dijkstra_tempo.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# EC9 — Tempo medio do Dijkstra (vetor vs heap)\n\n")
        f.write(format_markdown_table(headers_md, rows_md))
        f.write("\n\n")
        f.write(
            "Observacao: a versao com vetor e Theta(V^2). Em grafos grandes\n"
            "usamos um k menor (coluna `k_vetor`) para que o estudo termine\n"
            "em tempo razoavel; o tempo medio reportado e por fonte, entao\n"
            "permanece comparavel entre as colunas.\n"
        )
    print(f"\nCSV : {RESULTADOS_DIR / 'ec9_dijkstra_tempo.csv'}")
    print(f"MD  : {md_path}")


if __name__ == "__main__":
    main()
