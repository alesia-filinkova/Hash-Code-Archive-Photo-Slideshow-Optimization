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


def similar_pair_vertical_photos(vertical_photos):
    """
    Returns a list of pairs of vertical photos, 
    combining photos with the most common tags 
    and the least difference in tag size.
    """
    photos = vertical_photos.copy()
    
    if len(photos) % 2 == 1:
        photos = photos[:-1]
    
    pairs = []
    used = set()

    while len(used) < len(photos):
        best_score = -1
        best_diff = None
        best_pair = None

        for i in range(len(photos)):
            if photos[i]["id"] in used:
                continue
            for j in range(i+1, len(photos)):
                if photos[j]["id"] in used:
                    continue
                tags_i = photos[i]["tags"]
                tags_j = photos[j]["tags"]

                common = len(tags_i & tags_j)
                diff_len = abs(len(tags_i) - len(tags_j))

                if common > best_score or (common == best_score and diff_len < best_diff):
                    best_score = common
                    best_diff = diff_len
                    best_pair = (photos[i], photos[j])

        if best_pair is None:
            break

        pairs.append(best_pair)
        used.add(best_pair[0]["id"])
        used.add(best_pair[1]["id"])

    return pairs


def different_pair_vertical_photos(vertical_photos):
    """
    Returns a list of pairs of vertical photos, 
    combining photos with the fewest common tags 
    (the most different tags).
    """
    photos = vertical_photos.copy()
    
    if len(photos) % 2 == 1:
        photos = photos[:-1]
    
    pairs = []
    used = set()

    while len(used) < len(photos):
        best_score = float('inf')
        best_pair = None

        for i in range(len(photos)):
            if photos[i]["id"] in used:
                continue
            for j in range(i+1, len(photos)):
                if photos[j]["id"] in used:
                    continue
                common = len(photos[i]["tags"] & photos[j]["tags"])
                
                if common < best_score:
                    best_score = common
                    best_pair = (photos[i], photos[j])

        if best_pair is None:
            break

        pairs.append(best_pair)
        used.add(best_pair[0]["id"])
        used.add(best_pair[1]["id"])

    return pairs
