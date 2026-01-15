import random

def random_pair_vertical_photos(vertical_photos):
    """
    Returns list of random (photo1, photo2) pairs.
    """

    photos = vertical_photos.copy()

    if len(photos) % 2 == 1:
        photos = photos[:-1]

    random.shuffle(photos)

    pairs = []
    for i in range(0, len(photos), 2):
        pairs.append((photos[i], photos[i + 1]))

    return pairs


def similar_pair_vertical_photos(vertical_photos, k=50):
    """
    A fast greedy implementation for large datasets.
    k: number of candidates based on the number of tags for each photo
    """
    photos = sorted(vertical_photos, key=lambda x: len(x["tags"]))
    if len(photos) % 2 == 1:
        photos = photos[:-1]

    used = set()
    pairs = []
    n = len(photos)

    for idx, photo in enumerate(photos):
        if photo["id"] in used:
            continue

        start = max(0, idx - k)
        end = min(n, idx + k)
        best_score = -1
        best_pair = None

        for j in range(start, end):
            candidate = photos[j]
            if candidate["id"] in used or candidate["id"] == photo["id"]:
                continue
            score = len(photo["tags"] & candidate["tags"])
            if score > best_score:
                best_score = score
                best_pair = candidate

        if best_pair is not None:
            pairs.append((photo, best_pair))
            used.add(photo["id"])
            used.add(best_pair["id"])

    return pairs


def different_pair_vertical_photos(vertical_photos, k=300):
    """
    Combines photos with minimal tag intersection.
    k: Number of candidates for finding the minimal intersection
    """
    photos = sorted(vertical_photos, key=lambda x: len(x["tags"]))
    if len(photos) % 2 == 1:
        photos = photos[:-1]

    used = set()
    pairs = []
    n = len(photos)

    for idx, photo in enumerate(photos):
        if photo["id"] in used:
            continue

        start = max(0, idx - k)
        end = min(n, idx + k)
        best_score = float('inf')
        best_pair = None

        for j in range(start, end):
            candidate = photos[j]
            if candidate["id"] in used or candidate["id"] == photo["id"]:
                continue
            score = len(photo["tags"] & candidate["tags"])
            if score < best_score:
                best_score = score
                best_pair = candidate

        if best_pair is not None:
            pairs.append((photo, best_pair))
            used.add(photo["id"])
            used.add(best_pair["id"])

    return pairs
