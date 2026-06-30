"""Utilitarios compartilhados pelos scripts dos estudos de caso."""

from __future__ import annotations

import csv
import gc
import os
import sys
import time
from pathlib import Path

import psutil

# Garante que o pacote `src` seja importavel quando os scripts sao
# executados como python estudos/ec1_memoria.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GRAFOS_DIR = ROOT / "GRAFOS"
GRAFOS_W_DIR = ROOT / "GRAFOS 2"
GRAFOS_3_DIR = ROOT / "GRAFOS 3"
REDES_DIR = ROOT / "GRAFOS 2" / "REDES"
RESULTADOS_DIR = ROOT / "relatorio" / "resultados"
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

# Lista padrao de grafos analisados (ordem de tamanho crescente)
GRAFOS = [f"grafo_{i}.txt" for i in range(1, 7)]

# Grafos com pesos da Parte 2
GRAFOS_W = [f"grafo_W_{i}.txt" for i in range(1, 6)]

# Grafos direcionados com pesos da Parte 3
GRAFOS_3 = [f"grafo_W_{i}.txt" for i in range(1, 6)]

# Limite de seguranca para representacao por matriz: numero maximo de
# vertices acima do qual a matriz e considerada inviavel.
# A matriz numpy bool ocupa n^2 bytes; 60_000^2 ~= 3.4 GB.
MAX_MATRIX_VERTICES = 60_000


def rss_mb() -> float:
    """Memoria residente (Resident Set Size) atual do processo, em MB."""
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def measure_load_memory(loader_fn) -> tuple[float, float, object]:
    """Mede o aumento de memoria causado por loader_fn().

    Retorna (mb_antes, mb_depois, valor_carregado).
    O caller deve descartar o valor para liberar memoria entre medicoes.
    """
    gc.collect()
    before = rss_mb()
    obj = loader_fn()
    gc.collect()
    after = rss_mb()
    return before, after, obj


def matrix_feasible(n_vertices: int) -> bool:
    return n_vertices <= MAX_MATRIX_VERTICES


def time_block(fn, *args, **kwargs) -> tuple[float, object]:
    """Executa fn(*args, **kwargs) e retorna (tempo_em_segundos, resultado)."""
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    return time.perf_counter() - t0, result


def write_csv(path: Path, headers: list[str], rows: list[list]) -> None:
    """Escreve um CSV simples com os dados."""
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for row in rows:
            w.writerow(row)


def format_markdown_table(headers: list[str], rows: list[list]) -> str:
    """Formata uma tabela em Markdown, alinhando colunas pelo conteudo."""
    str_rows = [[str(c) for c in r] for r in rows]
    widths = [
        max(len(h), max((len(r[i]) for r in str_rows), default=0))
        for i, h in enumerate(headers)
    ]
    line = lambda cells: "| " + " | ".join(
        c.ljust(widths[i]) for i, c in enumerate(cells)
    ) + " |"
    sep = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    out = [line(headers), sep]
    out.extend(line(r) for r in str_rows)
    return "\n".join(out)


def banner(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
