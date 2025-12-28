#!/usr/bin/env python3
"""Budowa slajdów oraz zapis submission."""

from __future__ import annotations

import random
from typing import List

from usefull_functions import (
    load_photos_from_json,
    create_horizontal_slides,
    create_vertical_slides)

from vertical_photos_combining_methods import (
    random_pair_vertical_photos,
    similar_pair_vertical_photos,
    different_pair_vertical_photos)


def build_slides(pairing: str, data_dir: str) -> List[dict]:
    """Buduje listę slajdów zgodnie z wybraną metodą parowania."""
    h = load_photos_from_json(f"{data_dir}/horizontal_photos.json")
    v = load_photos_from_json(f"{data_dir}/vertical_photos.json")

    if pairing == "random":
        pairing_func = random_pair_vertical_photos
    elif pairing == "similar":
        pairing_func = similar_pair_vertical_photos
    elif pairing == "different":
        pairing_func = different_pair_vertical_photos
    else:
        raise ValueError(f"Nieznana metoda parowania: {pairing}")

    slides: List[dict] = []
    slides.extend(create_horizontal_slides(h))
    slides.extend(create_vertical_slides(pairing_func, v))

    random.shuffle(slides)
    return slides


def write_submission(slides: List[dict], order: List[int], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(str(len(order)) + "\n")
        for sid in order:
            photos = slides[sid]["photos"]
            f.write(" ".join(map(str, photos)) + "\n")
