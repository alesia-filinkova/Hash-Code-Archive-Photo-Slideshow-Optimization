#!/usr/bin/env python3
"""
Pipeline:
1) wczytanie danych z JSON (H i V osobno),
2) budowa slajdów: H jako pojedyncze, V jako pary (nierozdzielne),
3) ułożenie kolejności (grupy po tagach + przeplatanie + zachłanny wybór),
4) opcjonalna poprawa lokalna (szybkie ruchy z oceną delty),
5) zapis pliku submission.

Przykład:
  python solver.py --data_dir ../data --out out.txt --seed 42 --pairing different --local_iters 20000 --eval
"""

from __future__ import annotations

import os
import sys
import argparse
import random
import time

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
    ap.add_argument("--max_run", type=int, default=20, help="Maks. długość serii z jednej grupy")
    ap.add_argument("--local_iters", type=int, default=40000, help="Ile iteracji poprawy lokalnej (0 wyłącza)")
    ap.add_argument("--eval", action="store_true", help="Policz i wypisz score (może być wolne)")
    args = ap.parse_args()

    random.seed(args.seed)

    t0 = time.time()
    slides = build_slides(args.pairing, args.data_dir)
    t1 = time.time()

    order = build_slideshow_order(slides, max_run=args.max_run)
    t2 = time.time()

    order = local_improve(slides, order, iters=args.local_iters, seed=args.seed)
    t3 = time.time()

    write_submission(slides, order, args.out)

    print(f"Slajdy: {len(slides):,}")
    print(f"Budowa slajdów: {t1 - t0:.2f}s | Kolejność: {t2 - t1:.2f}s | Poprawa lokalna: {t3 - t2:.2f}s")
    print(f"Zapisano: {args.out}")

    if args.eval:
        slideshow = [slides[i] for i in order]
        print("Wynik:", total_score(slideshow))


if __name__ == "__main__":
    main()
