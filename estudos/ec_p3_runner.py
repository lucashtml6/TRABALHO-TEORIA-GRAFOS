"""Runner dos estudos de caso da Parte 3 (grafos direcionados com pesos).

Para cada grafo `grafo_W_k` (interpretado como DIRECIONADO):

  EC-P3.1  Distancia dos vertices 10, 20 e 30 ATE o vertice 100, via
           Bellman-Ford. Como Bellman-Ford e de fonte unica, computamos
           "distancia ATE 100" rodando o algoritmo sobre o grafo com as
           arestas INVERTIDAS a partir da fonte 100: uma unica execucao
           devolve d(v -> 100) para todo v. Tambem reportamos se ha ciclo
           negativo alcancavel.

  EC-P3.2  Tempo medio do Bellman-Ford (media de 10 rodadas, sem I/O).

  EC-P3.3  Para grafos SEM pesos negativos, resolvemos o mesmo problema com
           Dijkstra (sobre o mesmo grafo invertido, fonte 100). Comparamos
           distancias e tempo medio (10 rodadas) com o Bellman-Ford.

O grafo invertido e construido direto na carga (load_graph(..., reverse=True)),
sem custo de memoria adicional. Carregamos cada grafo UMA vez.
"""

from __future__ import annotations

import argparse
import gc
import math
import time
from pathlib import Path

from utils import (
    GRAFOS_3,
    GRAFOS_3_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    write_csv,
)

from src import bellman_ford, dijkstra_heap, load_graph

SOURCES = [10, 20, 30]   # vertices de origem
TARGET = 100             # vertice de destino
ROUNDS = 10              # rodadas para o tempo medio


def fmt_dist(d: float) -> str:
    if d == math.inf:
        return "inf"
    return f"{d:.4f}"


def avg_time(fn, *args, rounds: int = ROUNDS) -> tuple[float, object]:
    """Roda fn `rounds` vezes, devolve (tempo_medio_s, ultimo_resultado)."""
    res = None
    t0 = time.perf_counter()
    for _ in range(rounds):
        res = fn(*args)
    total = time.perf_counter() - t0
    return total / rounds, res


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="+", default=None,
                        help="restringe aos grafos cujo nome contenha esses sufixos (ex.: 1 2 3)")
    parser.add_argument("--max-n", type=int, default=None,
                        help="pula grafos com mais de N vertices")
    parser.add_argument("--rounds", type=int, default=ROUNDS,
                        help="numero de rodadas para o tempo medio (default 10)")
    args = parser.parse_args()

    dist_rows_md: list[list[str]] = []
    dist_rows_csv: list[list] = []
    time_rows_md: list[list[str]] = []
    time_rows_csv: list[list] = []
    notas: list[str] = []

    for name in GRAFOS_3:
        if args.only and not any(s in name for s in args.only):
            continue
        path = GRAFOS_3_DIR / name
        if not path.exists():
            print(f"[skip] {name} nao encontrado")
            continue

        banner(f"Parte 3 — {name}")

        # peek no header pra respeitar --max-n antes de carregar tudo
        with path.open("r", encoding="utf-8") as f:
            n_peek = int(f.readline().strip())
        if args.max_n is not None and n_peek > args.max_n:
            print(f"[skip] n={n_peek:,} > max-n={args.max_n:,}")
            notas.append(f"**{name}**: n={n_peek:,} acima do limite — INVIAVEL nesta execucao.")
            continue

        # carrega o grafo INVERTIDO direcionado (arestas u->v viram v->u)
        t0 = time.perf_counter()
        grev = load_graph(path, directed=True, reverse=True)
        t_load = time.perf_counter() - t0
        n, m = grev.n_vertices, grev.n_edges
        has_neg = grev.has_negative_weight
        print(f"carga (invertido): {t_load:.2f}s  n={n:,}  m={m:,}  "
              f"pesos_negativos={has_neg}")

        # ---- EC-P3.1 + EC-P3.2: Bellman-Ford (fonte 100 no grafo invertido) ----
        print(f"  >> Bellman-Ford a partir de {TARGET} (grafo invertido)")
        bf_time, bf = avg_time(bellman_ford, grev, TARGET, rounds=args.rounds)
        cyc = "SIM" if bf.has_negative_cycle else "nao"
        bf_d = {s: bf.dist[s] for s in SOURCES if s <= n}
        for s in SOURCES:
            d = fmt_dist(bf.dist[s]) if s <= n else "fora"
            print(f"    d({s} -> {TARGET}) = {d}")
        print(f"    ciclo negativo alcancavel: {cyc}   tempo medio BF: {bf_time*1000:.2f} ms")

        dist_rows_md.append([
            name, "Bellman-Ford",
            fmt_dist(bf.dist[10]) if 10 <= n else "fora",
            fmt_dist(bf.dist[20]) if 20 <= n else "fora",
            fmt_dist(bf.dist[30]) if 30 <= n else "fora",
            cyc,
        ])
        dist_rows_csv.append([name, "bellman-ford",
                              bf.dist[10], bf.dist[20], bf.dist[30],
                              int(bf.has_negative_cycle)])

        # ---- EC-P3.3: Dijkstra (so se nao houver peso negativo) ----
        dj_time = float("nan")
        dj = None
        if has_neg:
            print("  >> Dijkstra: PULADO (grafo tem pesos negativos)")
            notas.append(f"**{name}**: possui arestas negativas — Dijkstra inaplicavel; "
                         f"apenas Bellman-Ford.")
        else:
            print(f"  >> Dijkstra a partir de {TARGET} (grafo invertido)")
            dj_time, dj = avg_time(dijkstra_heap, grev, TARGET, rounds=args.rounds)
            for s in SOURCES:
                if s <= n:
                    match = "=" if dj.dist[s] == bf.dist[s] else "DIVERGE"
                    print(f"    d({s} -> {TARGET}) = {fmt_dist(dj.dist[s])}  [{match} BF]")
            print(f"    tempo medio Dijkstra: {dj_time*1000:.2f} ms")
            dist_rows_md.append([
                name, "Dijkstra",
                fmt_dist(dj.dist[10]) if 10 <= n else "fora",
                fmt_dist(dj.dist[20]) if 20 <= n else "fora",
                fmt_dist(dj.dist[30]) if 30 <= n else "fora",
                "—",
            ])
            dist_rows_csv.append([name, "dijkstra",
                                  dj.dist[10], dj.dist[20], dj.dist[30], 0])

        # ---- Tabela de tempos ----
        razao = (dj_time / bf_time) if (dj is not None and bf_time > 0) else float("nan")
        time_rows_md.append([
            name, f"{n:,}", f"{m:,}",
            f"{bf_time*1000:.2f}",
            (f"{dj_time*1000:.2f}" if dj is not None else "—"),
            (f"{razao:.2f}×" if dj is not None else "—"),
        ])
        time_rows_csv.append([name, n, m, bf_time, dj_time])

        del grev, bf, dj
        gc.collect()

    # ================= escreve resultados =================
    dist_headers_md = ["grafo", "algoritmo", "d(10→100)", "d(20→100)",
                       "d(30→100)", "ciclo neg."]
    dist_headers_csv = ["grafo", "algoritmo", "d_10_100", "d_20_100",
                        "d_30_100", "ciclo_negativo"]
    write_csv(RESULTADOS_DIR / "ec_p3_distancias.csv", dist_headers_csv, dist_rows_csv)
    with (RESULTADOS_DIR / "ec_p3_distancias.md").open("w", encoding="utf-8") as f:
        f.write("# EC-P3 — Distancias dos vertices 10, 20 e 30 ate o vertice 100\n\n")
        f.write("Distancias obtidas rodando o algoritmo de fonte unica a partir do\n"
                "vertice 100 sobre o grafo com as **arestas invertidas** "
                "(d(v→100) = d_invertido(100→v)).\n\n")
        f.write(format_markdown_table(dist_headers_md, dist_rows_md))
        f.write("\n")
        if notas:
            f.write("\n### Notas\n\n")
            for nota in notas:
                f.write(f"- {nota}\n")

    time_headers_md = ["grafo", "n", "m", "Bellman-Ford (ms)",
                       "Dijkstra (ms)", "Dijkstra/BF"]
    time_headers_csv = ["grafo", "n", "m", "bf_s", "dijkstra_s"]
    write_csv(RESULTADOS_DIR / "ec_p3_tempo.csv", time_headers_csv, time_rows_csv)
    with (RESULTADOS_DIR / "ec_p3_tempo.md").open("w", encoding="utf-8") as f:
        f.write("# EC-P3 — Tempo medio de execucao (media de "
                f"{args.rounds} rodadas, sem I/O)\n\n")
        f.write(format_markdown_table(time_headers_md, time_rows_md))
        f.write("\n")

    print()
    banner("Concluido")
    print(f"distancias -> {RESULTADOS_DIR / 'ec_p3_distancias.md'}")
    print(f"tempos     -> {RESULTADOS_DIR / 'ec_p3_tempo.md'}")


if __name__ == "__main__":
    main()
