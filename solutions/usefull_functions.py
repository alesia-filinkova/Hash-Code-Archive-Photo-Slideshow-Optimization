import json

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
