#!/usr/bin/env python3
"""Logika układania kolejności slajdów (grupy tagów + przeplatanie + wybór zachłanny)."""

from __future__ import annotations

import random
from collections import Counter, defaultdict, deque
from typing import Dict, Iterable, List, Optional, Set, Tuple

from usefull_functions import slide_score


def build_tag_index(slides: List[dict]) -> Dict[str, List[int]]:
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
        # wybór grupy z max_run
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
