#!/usr/bin/env python3
"""
1) wczytanie danych z JSON (H i V osobno)
2) budowa slajdów (H pojedynczo, V w parach)
3) ułożenie kolejności (random / nn / grouped / mixed)
4) opcjonalna poprawa lokalna (parametr --local_iters)
5) zapis pliku submission
"""

from __future__ import annotations

import os
import sys
import argparse
import random

sys.path.append(os.path.dirname(__file__))

from usefull_functions import total_score
from io_help import build_slides, write_submission
from ordering import build_slideshow_order
from local_search import local_improve

def run_solver(
    data_dir: str = "../data",
    out: str | None = None,
    seed: int = 42,
    pairing: str = "different",
    order_method: str = "mixed",
    k: int = 100,
    k_group: int = 10,
    group_key: str = "min",
    local_iters: int = 0,
    eval_score: bool = False,
):
    random.seed(seed)

    slides = build_slides(pairing, data_dir)

    order = build_slideshow_order(
        slides,
        method=order_method,
        k=k,
        k_group=k_group,
        group_key=group_key,
    )

    if local_iters > 0:
        order = local_improve(
            slides,
            order,
            iters=local_iters,
            seed=seed
        )

    if out is not None:
        write_submission(slides, order, out)

    score = None
    if eval_score:
        slideshow = [slides[i] for i in order]
        score = total_score(slideshow)

    return slides, order, score


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", default="../data", help="Katalog z horizontal_photos.json i vertical_photos.json")
    ap.add_argument("--out", default="out.txt", help="Ścieżka pliku wynikowego (submission)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--pairing", choices=["random", "similar", "different"], default="different")
    ap.add_argument(
        "--order",
        choices=["random", "nn", "grouped", "mixed"],
        default="mixed",
        help="Metoda budowy kolejności slajdów (zgodna z notebookami)",
    )
    ap.add_argument("--k", type=int, default=100, help="Parametr k dla NN / Mixed")
    ap.add_argument("--k_group", type=int, default=10, help="Parametr dla łączenia grup w Mixed")
    ap.add_argument(
        "--group_key",
        choices=["min", "first"],
        default="min",
        help="Tag-reprezentant grupy w Grouped/Mixed (min = deterministyczny)",
    )
    ap.add_argument("--local_iters", type=int, default=0, help="Ile iteracji poprawy lokalnej (0 wyłącza)")
    ap.add_argument("--eval", action="store_true", help="Policz i wypisz score (może być wolne)")
    args = ap.parse_args()

    slides, order, score = run_solver(
        data_dir=args.data_dir,
        out=args.out,
        seed=args.seed,
        pairing=args.pairing,
        order_method=args.order,
        k=args.k,
        k_group=args.k_group,
        group_key=args.group_key,
        local_iters=args.local_iters,
        eval_score=args.eval,
    )

    print(f"Slajdy: {len(slides):,}")
    print(f"Zapisano: {args.out}")
    if score is not None:
        print("Wynik:", score)


if __name__ == "__main__":
    main()
