import random
from usefull_functions import delta_swap, delta_2opt

def hill_climbing(slides, iters=10000):
    slides = slides.copy()
    best_score = 0

    for _ in range(iters):
        i, j = random.sample(range(len(slides)), 2)
        delta = delta_swap(slides, i, j)

        if delta > 0:
            slides[i], slides[j] = slides[j], slides[i]
            best_score += delta

    return slides


def two_opt(slides, iters=5000):
    slides = slides.copy()

    for _ in range(iters):
        i, j = sorted(random.sample(range(len(slides)), 2))
        if j - i < 2:
            continue

        delta = delta_2opt(slides, i, j)
        if delta > 0:
            slides[i:j+1] = reversed(slides[i:j+1])

    return slides


def simulated_annealing(
    slides,
    iters=20000,
    T0=1.0,
    alpha=0.999
):
    slides = slides.copy()
    T = T0

    for _ in range(iters):
        i, j = random.sample(range(len(slides)), 2)
        delta = delta_swap(slides, i, j)

        if delta > 0 or random.random() < math.exp(delta / T):
            slides[i], slides[j] = slides[j], slides[i]

        T *= alpha

    return slides

