import random

def random_slideshow(slides):
    slideshow = slides.copy()
    random.shuffle(slideshow)
    return slideshow
