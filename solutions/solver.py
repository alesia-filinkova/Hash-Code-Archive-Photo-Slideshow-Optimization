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

    random.seed(args.seed)

    slides = build_slides(args.pairing, args.data_dir)

    order = build_slideshow_order(
        slides,
        method=args.order,
        k=args.k,
        k_group=args.k_group,
        group_key=args.group_key,
    )

    if args.local_iters > 0:
        order = local_improve(slides, order, iters=args.local_iters, seed=args.seed)

    write_submission(slides, order, args.out)

    print(f"Slajdy: {len(slides):,}")
    print(f"Zapisano: {args.out}")

    if args.eval:
        slideshow = [slides[i] for i in order]
        print("Wynik:", total_score(slideshow))


if __name__ == "__main__":
    main()
