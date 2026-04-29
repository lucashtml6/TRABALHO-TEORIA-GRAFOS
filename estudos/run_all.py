"""Roda todos os estudos de caso em sequencia.

Cada estudo gera CSV e Markdown em relatorio/resultados/.
Use `python estudos/run_all.py` (ou estudos/run_all.py --skip ec7) para
pular alguns estudos especificos.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time

import utils  # type: ignore  # noqa: F401  (efeito colateral: ajusta sys.path)

ESTUDOS = [
    ("ec1", "ec1_memoria"),
    ("ec2", "ec2_tempo_bfs"),
    ("ec3", "ec3_tempo_dfs"),
    ("ec4", "ec4_pais_arvore"),
    ("ec5", "ec5_distancias"),
    ("ec6", "ec6_componentes"),
    ("ec7", "ec7_diametro"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--skip",
        nargs="*",
        default=[],
        help="ids dos estudos para pular (ex.: ec7 ec3)",
    )
    ap.add_argument(
        "--only",
        nargs="*",
        default=[],
        help="ids dos estudos para rodar exclusivamente",
    )
    args = ap.parse_args()

    selected = [
        (eid, mod) for eid, mod in ESTUDOS
        if (not args.only or eid in args.only) and eid not in args.skip
    ]
    print(f"Rodando: {[eid for eid, _ in selected]}")

    for eid, modname in selected:
        t0 = time.perf_counter()
        try:
            mod = importlib.import_module(modname)
            mod.main()
        except Exception as e:
            print(f"[{eid}] FALHOU: {e}", file=sys.stderr)
            continue
        dt = time.perf_counter() - t0
        print(f"\n[{eid}] concluido em {dt:.1f}s\n")


if __name__ == "__main__":
    main()
