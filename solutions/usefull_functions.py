import json
import random
from collections import defaultdict


def load_photos_from_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        photos = json.load(f)
    for p in photos:
        p["tags"] = set(p["tags"])
    return photos


def interest_score(tags_a: set, tags_b: set) -> int:
    common = len(tags_a & tags_b)
    only_a = len(tags_a - tags_b)
    only_b = len(tags_b - tags_a)
    return min(common, only_a, only_b)

def slide_score(slide_a, slide_b):
    return interest_score(slide_a["tags"], slide_b["tags"])

def create_horizontal_slides(horizontal_photos):
    return [{
        "photos": [p["id"]],
        "tags": p["tags"]
    } for p in horizontal_photos]


def create_vertical_slide(photo1, photo2): 
    return {
        "photos": [photo1["id"], photo2["id"]],
        "tags": photo1["tags"] | photo2["tags"]
    }

def create_vertical_slides(pairing_func, vertical_photos):
    pairs = pairing_func(vertical_photos)
    return [create_vertical_slide(p1, p2) for p1, p2 in pairs]


def total_score(slideshow):
    return sum(
        slide_score(slideshow[i], slideshow[i+1])
        for i in range(len(slideshow) - 1)
    )


from collections import defaultdict

def group_slides_by_tag(slides):
    groups = defaultdict(list)

    for slide in slides:
        main_tag = next(iter(slide["tags"]))
        groups[main_tag].append(slide)

    return list(groups.values())


def nearest_neighbor_group(slides, k=300):
    if not slides:
        return []

    slides_left = slides.copy()
    random.shuffle(slides_left)

    current = slides_left.pop()
    ordered = [current]

    while slides_left:
        best_score = -1
        best_idx = None

        candidates = random.sample(
            slides_left, 
            min(k, len(slides_left))
        )

        for candidate in candidates:
            score = interest_score(current["tags"], candidate["tags"])
            if score > best_score:
                best_score = score
                best_idx = slides_left.index(candidate)

        current = slides_left.pop(best_idx)
        ordered.append(current)

    return ordered


def order_groups_nn(groups, k=10):
    groups_left = groups.copy()
    random.shuffle(groups_left)

    current = groups_left.pop()
    ordered_groups = [current]

    while groups_left:
        best_score = -1
        best_idx = None

        candidates = random.sample(
            groups_left,
            min(k, len(groups_left))
        )

        for group in candidates:
            score = interest_score(
                ordered_groups[-1][-1]["tags"],
                group[0]["tags"]
            )
            if score > best_score:
                best_score = score
                best_idx = groups_left.index(group)

        ordered_groups.append(groups_left.pop(best_idx))

    return ordered_groups


def delta_swap(slides, i, j):
    """Zmiana score po zamianie slajdów i oraz j"""
    n = len(slides)
    delta = 0

    def score(a, b):
        return interest_score(a["tags"], b["tags"])

    for idx in [i-1, i, j-1, j]:
        if 0 <= idx < n-1:
            delta -= score(slides[idx], slides[idx+1])

    slides[i], slides[j] = slides[j], slides[i]

    for idx in [i-1, i, j-1, j]:
        if 0 <= idx < n-1:
            delta += score(slides[idx], slides[idx+1])

    slides[i], slides[j] = slides[j], slides[i]
    return delta


def delta_2opt(slides, i, j):
    """Zmiana score po odwróceniu fragmentu [i:j]"""
    if i == 0:
        before = 0
    else:
        before = interest_score(slides[i-1]["tags"], slides[i]["tags"])

    if j == len(slides) - 1:
        after = 0
    else:
        after = interest_score(slides[j]["tags"], slides[j+1]["tags"])

    middle = interest_score(slides[i-1]["tags"], slides[j]["tags"]) + \
             interest_score(slides[i]["tags"], slides[j+1]["tags"])

    return middle - (before + after)
