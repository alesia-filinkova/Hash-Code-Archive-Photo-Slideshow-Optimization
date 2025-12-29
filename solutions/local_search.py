#!/usr/bin/env python3
"""Poprawki lokalne na kolejności slajdów."""

from __future__ import annotations

import random
from typing import List, Optional

from usefull_functions import slide_score


def edge(slides: List[dict], order: List[int], k: int) -> int:
    """Score dla krawędzi i -> i+1 w bieżącym porządku."""
    return slide_score(slides[order[k]], slides[order[k + 1]])


def local_improve(
    slides: List[dict],
    order: List[int],
    iters: int = 40000,
    seed: Optional[int] = None) -> List[int]:
    """Prosty hill-climbing na kolejności slajdów.
    - swap sąsiadów,
    - swap losowy,
    - krótki 2-opt.
    Zysk liczymy tylko na dotkniętych krawędziach.
    """
    if seed is not None:
        random.seed(seed)

    n = len(order)
    if n < 4 or iters <= 0:
        return order

    for _ in range(iters):
        r = random.random()

        if r < 0.60:
            i = random.randrange(0, n - 1)
            a, b = order[i], order[i + 1]

            before = 0
            after = 0
            if i - 1 >= 0:
                before += slide_score(slides[order[i - 1]], slides[a])
                after += slide_score(slides[order[i - 1]], slides[b])

            before += slide_score(slides[a], slides[b])
            after += slide_score(slides[b], slides[a])

            if i + 2 < n:
                before += slide_score(slides[b], slides[order[i + 2]])
                after += slide_score(slides[a], slides[order[i + 2]])

            if after > before:
                order[i], order[i + 1] = order[i + 1], order[i]

        elif r < 0.90:
            i = random.randrange(0, n)
            j = random.randrange(0, n)
            if i == j:
                continue
            if i > j:
                i, j = j, i

            affected = set()
            for k in (i - 1, i, j - 1, j):
                if 0 <= k < n - 1:
                    affected.add(k)

            before = sum(edge(slides, order, k) for k in affected)
            order[i], order[j] = order[j], order[i]
            after = sum(edge(slides, order, k) for k in affected)

            if after <= before:
                order[i], order[j] = order[j], order[i]

        else:
            i = random.randrange(0, n - 2)
            j = random.randrange(i + 1, min(n - 1, i + 2000))

            before = 0
            after = 0
            if i - 1 >= 0:
                before += slide_score(slides[order[i - 1]], slides[order[i]])
                after += slide_score(slides[order[i - 1]], slides[order[j]])
            if j + 1 < n:
                before += slide_score(slides[order[j]], slides[order[j + 1]])
                after += slide_score(slides[order[i]], slides[order[j + 1]])

            if after > before:
                order[i : j + 1] = reversed(order[i : j + 1])

    return order
