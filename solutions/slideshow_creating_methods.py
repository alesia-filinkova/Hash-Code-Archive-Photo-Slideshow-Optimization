import random
from usefull_functions import interest_score, group_slides_by_tag


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


def mixed_topics_slideshow(slides):
    groups = group_slides_by_tag(slides)
    random.shuffle(groups)

    slideshow = []
    pointers = [0] * len(groups)

    while True:
        added = False
        for i, group in enumerate(groups):
            if pointers[i] < len(group):
                slideshow.append(group[pointers[i]])
                pointers[i] += 1
                added = True
        if not added:
            break

    return slideshow
