"""EC10 — Rede de colaboracao academica.

Calcula a distancia e o caminho minimo entre Edsger W. Dijkstra e os
pesquisadores listados pelo PDF, usando o peso da aresta = 1/(numero de
artigos em coautoria) — i.e. dois pesquisadores com muitas coautorias
estao "perto", e o caminho minimo e a sequencia de coautorias mais
densas que ligam dois pesquisadores.

Arquivos:
    GRAFOS 2/REDES/rede_colaboracao.txt          (grafo ponderado, ids 1..N)
    GRAFOS 2/REDES/rede_colaboracao_vertices.txt (mapeamento id,nome)
"""

from __future__ import annotations

import math
from pathlib import Path

from utils import (
    REDES_DIR,
    RESULTADOS_DIR,
    banner,
    format_markdown_table,
    time_block,
    write_csv,
)

from src import dijkstra_heap, load_graph, load_vertex_labels


SOURCE_NAME = "Edsger W. Dijkstra"
TARGET_NAMES = [
    "Alan M. Turing",
    "J. B. Kruskal",
    "Jon M. Kleinberg",
    "Éva Tardos",
    "Daniel R. Figueiredo",
]


def name_chain(path_ids: list[int], id_to_name: dict[int, str]) -> str:
    """Mostra o caminho como cadeia de nomes (com truncagem)."""
    if not path_ids:
        return "-"
    names = [id_to_name.get(v, f"<id {v}>") for v in path_ids]
    if len(names) <= 6:
        return " -> ".join(names)
    return " -> ".join(names[:3]) + f" -> ... ({len(names) - 6} omit.) -> " + " -> ".join(names[-3:])


def main() -> None:
    graph_path = REDES_DIR / "rede_colaboracao.txt"
    labels_path = REDES_DIR / "rede_colaboracao_vertices.txt"
    if not graph_path.exists() or not labels_path.exists():
        print(f"[erro] arquivos nao encontrados em {REDES_DIR}")
        return

    banner("EC10 — Rede de colaboracao")
    t_lbl, (id_to_name, name_to_id) = time_block(load_vertex_labels, labels_path)
    print(f"vertices nomeados: {len(id_to_name):,}  ({t_lbl:.2f}s)")
    t_load, g = time_block(load_graph, graph_path)
    print(f"grafo: n={g.n_vertices:,}  m={g.n_edges:,}  ({t_load:.2f}s)")
    if g.has_negative_weight:
        print("[erro] grafo da rede tem aresta negativa — incompativel com Dijkstra")
        return

    # Aceita variacoes acentuadas para "Eva Tardos" (Éva Tardos no arquivo).
    def resolve(name: str) -> int | None:
        if name in name_to_id:
            return name_to_id[name]
        # tenta com acento
        candidates = [n for n in name_to_id if n.replace("É", "E").replace("é", "e") == name]
        if len(candidates) == 1:
            print(f"[ok] '{name}' resolvido para '{candidates[0]}'")
            return name_to_id[candidates[0]]
        return None

    src = resolve(SOURCE_NAME)
    if src is None:
        print(f"[erro] fonte '{SOURCE_NAME}' nao encontrada na rede")
        return
    print(f"fonte: '{SOURCE_NAME}' -> id {src}")

    t_run, res = time_block(dijkstra_heap, g, src)
    print(f"Dijkstra (heap): {t_run:.2f}s")

    rows_md: list[list[str]] = []
    rows_csv: list[list] = []
    for nm in TARGET_NAMES:
        tgt = resolve(nm)
        if tgt is None:
            rows_md.append([nm, "—", "nao encontrado", "—"])
            rows_csv.append([nm, "", "nao encontrado", ""])
            print(f"  [{nm}] nao encontrado")
            continue
        d = res.dist[tgt]
        path_ids = res.path_to(tgt)
        if d == math.inf:
            rows_md.append([nm, str(tgt), "inf (sem caminho)", "-"])
            rows_csv.append([nm, tgt, "inf", ""])
            print(f"  [{nm}] inf (componentes distintas)")
        else:
            rows_md.append([nm, str(tgt), f"{d:.4f}", name_chain(path_ids, id_to_name)])
            rows_csv.append([nm, tgt, f"{d:.4f}", " -> ".join(id_to_name.get(v, str(v)) for v in path_ids)])
            print(f"  [{nm}] dist = {d:.4f}  ({len(path_ids)} vertices no caminho)")

    headers = ["pesquisador (destino)", "id", "distancia", "caminho"]
    write_csv(RESULTADOS_DIR / "ec10_rede_colaboracao.csv", headers, rows_csv)

    md_path = RESULTADOS_DIR / "ec10_rede_colaboracao.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# EC10 — Caminhos minimos a partir de {SOURCE_NAME}\n\n")
        f.write(f"n = {g.n_vertices:,}, m = {g.n_edges:,}, fonte id = {src}\n\n")
        f.write(format_markdown_table(headers, rows_md))
        f.write("\n")
    print(f"\nCSV : {RESULTADOS_DIR / 'ec10_rede_colaboracao.csv'}")
    print(f"MD  : {md_path}")


if __name__ == "__main__":
    main()
