import random
from usefull_functions import interest_score, group_slides_by_tag, nearest_neighbor_group, order_groups_nn


def random_slideshow(slides):
    slideshow = slides.copy()
    random.shuffle(slideshow)
    return slideshow


def nearest_neighbor_slideshow(slides, k=100):
    slides_left = slides.copy()
    random.shuffle(slides_left)

    current = slides_left.pop()
    slideshow = [current]

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
        slideshow.append(current)

    return slideshow



def grouped_slideshow(slides):
    groups = group_slides_by_tag(slides)
    random.shuffle(groups)

    slideshow = []

    for group in groups:
        random.shuffle(group)
        slideshow.extend(group)

    return slideshow


def mixed_slideshow(slides):
    groups = group_slides_by_tag(slides)

    processed_groups = [
        nearest_neighbor_group(group)
        for group in groups
    ]

    ordered_groups = order_groups_nn(processed_groups)

    slideshow = []
    for group in ordered_groups:
        slideshow.extend(group)

    return slideshow
