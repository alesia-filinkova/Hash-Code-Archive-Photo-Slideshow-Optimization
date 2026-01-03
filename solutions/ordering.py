#!/usr/bin/env python3

from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, List, Optional

from usefull_functions import slide_score

def _group_key(slide: dict, mode: str = "min") -> str:
    """Wybór tagu-reprezentanta grupy.
    - mode="min": deterministycznie najmniejszy tag
    - mode="first": pierwszy z iteracji po zbiorze
    Jeśli slajd nie ma tagów, zwracamy pusty string.
    """
    tags = slide.get("tags", set())
    if not tags:
        return ""
    if mode == "first":
        return next(iter(tags))
    return min(tags)


def order_random(slides: List[dict]) -> List[int]:
    order = list(range(len(slides)))
    random.shuffle(order)
    return order

def order_nn(slides: List[dict], k: int = 100) -> List[int]:
    """
    - start: losowy slajd,
    - krok: losujemy k kandydatów z pozostałych i wybieramy najlepszy transition.
    """
    n = len(slides)
    if n == 0:
        return []

    remaining = list(range(n))
    random.shuffle(remaining)

    cur = remaining.pop()
    order = [cur]

    while remaining:
        m = min(max(1, k), len(remaining))
        pos_sample = random.sample(range(len(remaining)), m)

        best_pos: Optional[int] = None
        best_sc = -1
        cur_slide = slides[cur]

        for pos in pos_sample:
            sid = remaining[pos]
            sc = slide_score(cur_slide, slides[sid])
            if sc > best_sc:
                best_sc = sc
                best_pos = pos

        assert best_pos is not None
        nxt = remaining[best_pos]
        remaining[best_pos] = remaining[-1]
        remaining.pop()

        order.append(nxt)
        cur = nxt

    return order

def order_grouped(slides: List[dict], group_key: str = "min") -> List[int]:
    """Grouped: grupujemy slajdy po tagu-reprezentancie, potem sklejamy grupy."""
    groups: Dict[str, List[int]] = defaultdict(list)
    for sid, s in enumerate(slides):
        groups[_group_key(s, group_key)].append(sid)

    group_list = list(groups.values())
    random.shuffle(group_list)

    order: List[int] = []
    for g in group_list:
        random.shuffle(g)
        order.extend(g)

    return order

def _order_group_nn(slides: List[dict], group: List[int], k: int) -> List[int]:
    """NN(k) ograniczone do jednej grupy."""
    if not group:
        return []
    if len(group) == 1:
        return group[:]

    remaining = group[:]
    random.shuffle(remaining)
    cur = remaining.pop()
    ordered = [cur]

    while remaining:
        m = min(max(1, k), len(remaining))
        pos_sample = random.sample(range(len(remaining)), m)

        best_pos: Optional[int] = None
        best_sc = -1
        cur_slide = slides[cur]

        for pos in pos_sample:
            sid = remaining[pos]
            sc = slide_score(cur_slide, slides[sid])
            if sc > best_sc:
                best_sc = sc
                best_pos = pos

        assert best_pos is not None
        nxt = remaining[best_pos]
        remaining[best_pos] = remaining[-1]
        remaining.pop()

        ordered.append(nxt)
        cur = nxt

    return ordered


def _order_groups_nn(slides: List[dict], groups: List[List[int]], k_group: int) -> List[List[int]]:
    """NN na poziomie grup: dopasowujemy kolejność grup po przejściu last->first."""
    if not groups:
        return []
    if len(groups) == 1:
        return groups

    remaining = groups[:]
    random.shuffle(remaining)
    cur_g = remaining.pop()
    ordered = [cur_g]

    while remaining:
        m = min(max(1, k_group), len(remaining))
        pos_sample = random.sample(range(len(remaining)), m)

        best_pos: Optional[int] = None
        best_sc = -1
        last_slide = slides[ordered[-1][-1]]

        for pos in pos_sample:
            g = remaining[pos]
            sc = slide_score(last_slide, slides[g[0]])
            if sc > best_sc:
                best_sc = sc
                best_pos = pos

        assert best_pos is not None
        nxt = remaining[best_pos]
        remaining[best_pos] = remaining[-1]
        remaining.pop()

        ordered.append(nxt)

    return ordered


def order_mixed(
    slides: List[dict],
    k: int = 100,
    k_group: int = 10,
    group_key: str = "min",
) -> List[int]:
    groups: Dict[str, List[int]] = defaultdict(list)
    for sid, s in enumerate(slides):
        groups[_group_key(s, group_key)].append(sid)

    group_list = list(groups.values())

    processed = [_order_group_nn(slides, g, k=k) for g in group_list]
    ordered_groups = _order_groups_nn(slides, processed, k_group=k_group)

    order: List[int] = []
    for g in ordered_groups:
        order.extend(g)

    return order

def build_slideshow_order(
    slides: List[dict],
    method: str = "mixed",
    k: int = 100,
    k_group: int = 10,
    group_key: str = "min",
) -> List[int]:
    """Zwraca listę indeksów slajdów w kolejności zgodnej z wybraną metodą."""
    if method == "random":
        return order_random(slides)
    if method == "nn":
        return order_nn(slides, k=k)
    if method == "grouped":
        return order_grouped(slides, group_key=group_key)
    if method == "mixed":
        return order_mixed(slides, k=k, k_group=k_group, group_key=group_key)

    raise ValueError(f"Unknown ordering method: {method}")
