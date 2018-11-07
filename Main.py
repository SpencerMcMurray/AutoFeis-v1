from CropSheet import find_squares
from GetDigits import get_all


def run(filepath, num_rounds):
    imgs = find_squares(filepath, num_rounds)
    marks = get_all(imgs)
    return marks
