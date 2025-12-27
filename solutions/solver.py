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
from collections import Counter, defaultdict, deque
from typing import Dict, Iterable, List, Set, Tuple, Optional

sys.path.append(os.path.dirname(__file__))

from usefull_functions import (
    load_photos_from_json,
    create_horizontal_slides,
    create_vertical_slides,
    slide_score,
    total_score)

from vertical_photos_combining_methods import (
    random_pair_vertical_photos,
    similar_pair_vertical_photos,
    different_pair_vertical_photos)


def build_tag_index(slides):
    idx = defaultdict(list)
    for sid, s in enumerate(slides):
        for t in sorted(s["tags"]):
            idx[t].append(sid)
    for t in idx:
        random.shuffle(idx[t])
    return idx


class TagPicker:
    """
    Dobiera kandydatów na następny slajd na podstawie tagów bieżącego slajdu.
    Nie usuwamy elementów z list, tylko pomijamy użyte indeksy.
    """
    def __init__(self, tag_index: Dict[str, List[int]]):
        self.tag_index = tag_index
        self.ptr: Dict[str, int] = {t: 0 for t in tag_index}

    def pick(
        self,
        tags: Iterable[str],
        used: List[bool],
        limit: int = 40,
        per_tag: int = 6) -> List[int]:
        cand: Set[int] = set()

        for t in sorted(tags):
            lst = self.tag_index.get(t)
            if not lst:
                continue

            p = self.ptr.get(t, 0)
            taken = 0

            while p < len(lst) and taken < per_tag and len(cand) < limit:
                sid = lst[p]
                p += 1
                if not used[sid]:
                    cand.add(sid)
                    taken += 1

            self.ptr[t] = p
            if len(cand) >= limit:
                break

        return list(cand)


def group_by_rarest_tag(slides: List[dict]) -> Dict[str, List[int]]:
    """
    Tanie grupowanie "tematyczne": każdy slajd trafia do grupy opisanej
    swoim najrzadszym tagiem.
    """
    tag_freq = Counter()
    for s in slides:
        tag_freq.update(s["tags"])

    groups: Dict[str, List[int]] = defaultdict(list)
    for sid, s in enumerate(slides):
        rarest = min(s["tags"], key=lambda t: (tag_freq[t], t))
        groups[rarest].append(sid)

    for g in groups.values():
        random.shuffle(g)

    return groups


def best_transition(slides: List[dict], cur_id: int, cand_ids: List[int]) -> Optional[int]:
    """Zwraca kandydata maksymalizującego score(cur, cand) w podanym zbiorze."""
    if not cand_ids:
        return None
    cur = slides[cur_id]

    best_id = None
    best_sc = -1
    for sid in cand_ids:
        sc = slide_score(cur, slides[sid])
        if sc > best_sc:
            best_sc = sc
            best_id = sid

    return best_id


def build_slideshow_order(
    slides: List[dict],
    max_run: int = 20,
    tag_cands: int = 40,
    group_probe: int = 25) -> List[int]:
    """
    Buduje kolejność slajdów:
    - dzieli na grupy po najrzadszym tagu,
    - przeplata grupy (round-robin) z limitem max_run,
    - wybiera kolejny slajd zachłannie z próby z bieżącej grupy,
      a gdy to słabe, bierze kandydatów z indeksu tagów.
    """
    n = len(slides)
    if n == 0:
        return []

    used = [False] * n
    picker = TagPicker(build_tag_index(slides))
    groups = group_by_rarest_tag(slides)

    group_keys = list(groups.keys())
    random.shuffle(group_keys)

    queues: Dict[str, deque[int]] = {k: deque(v) for k, v in groups.items()}

    def clean_front(q: deque[int]) -> None:
        while q and used[q[0]]:
            q.popleft()

    def pop_any() -> Optional[Tuple[str, int]]:
        for k in group_keys:
            q = queues[k]
            clean_front(q)
            if q:
                return k, q.popleft()
        return None

    start_group = next((k for k in group_keys if queues[k]), group_keys[0])
    cur_id = queues[start_group].popleft()
    used[cur_id] = True

    order = [cur_id]
    last_group = start_group
    run_len = 1
    gi = 0

    while len(order) < n:
        #wybór grupy z max_run
        chosen_group = None
        for _ in range(len(group_keys)):
            k = group_keys[gi % len(group_keys)]
            gi += 1

            q = queues[k]
            clean_front(q)
            if not q:
                continue

            if k == last_group and run_len >= max_run:
                continue

            chosen_group = k
            break

        if chosen_group is None:
            any_pick = pop_any()
            if any_pick is None:
                break
            chosen_group, next_id = any_pick
            used[next_id] = True
            order.append(next_id)

            if chosen_group == last_group:
                run_len += 1
            else:
                last_group = chosen_group
                run_len = 1

            cur_id = next_id
            continue

        q = queues[chosen_group]
        clean_front(q)

        probe: List[int] = []
        while q and len(probe) < group_probe:
            sid = q.popleft()
            if not used[sid]:
                probe.append(sid)

        for sid in reversed(probe):
            q.appendleft(sid)

        best_in_group = best_transition(slides, cur_id, probe)

        best_global = None
        if best_in_group is None or slide_score(slides[cur_id], slides[best_in_group]) == 0:
            cands = picker.pick(slides[cur_id]["tags"], used, limit=tag_cands)
            best_global = best_transition(slides, cur_id, cands)

        next_id = best_in_group
        if best_global is not None:
            if next_id is None:
                next_id = best_global
            else:
                if slide_score(slides[cur_id], slides[best_global]) > slide_score(slides[cur_id], slides[next_id]):
                    next_id = best_global

        if next_id is None:
            any_pick = pop_any()
            if any_pick is None:
                break
            chosen_group, next_id = any_pick

        used[next_id] = True
        order.append(next_id)

        if chosen_group == last_group:
            run_len += 1
        else:
            last_group = chosen_group
            run_len = 1

        cur_id = next_id

    return order


def edge(slides: List[dict], order: List[int], i: int) -> int:
    """Score dla krawędzi i -> i+1 w bieżącym porządku."""
    return slide_score(slides[order[i]], slides[order[i + 1]])


def local_improve(
    slides: List[dict],
    order: List[int],
    iters: int = 40000,
    seed: Optional[int] = None) -> List[int]:
    """
    Prosty hill-climbing na kolejności slajdów:
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


# IO + budowa slajdów

def write_submission(slides: List[dict], order: List[int], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{len(order)}\n")
        for sid in order:
            f.write(" ".join(map(str, slides[sid]["photos"])) + "\n")


def build_slides(pairing: str, data_dir: str) -> List[dict]:
    h = load_photos_from_json(os.path.join(data_dir, "horizontal_photos.json"))
    v = load_photos_from_json(os.path.join(data_dir, "vertical_photos.json"))

    pairing_func = {
        "random": random_pair_vertical_photos,
        "similar": similar_pair_vertical_photos,
        "different": different_pair_vertical_photos}.get(pairing)

    if pairing_func is None:
        raise ValueError(f"Nieznana metoda parowania: {pairing}")

    slides: List[dict] = []
    slides.extend(create_horizontal_slides(h))
    slides.extend(create_vertical_slides(pairing_func, v))

    random.shuffle(slides)
    return slides


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
