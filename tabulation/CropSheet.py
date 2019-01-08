import cv2
import numpy as np


lower_black = np.array([0, 0, 0], dtype="uint16")
upper_black = np.array([200, 200, 200], dtype="uint16")


class Rect:
    def __init__(self, top_l, bot_r):
        self.tl = top_l
        self.br = bot_r

    def __lt__(self, other):
        """(Rect, Rect) -> bool
        Create a comparator for rectangles.
        """
        # This gives each rectangle a value based on their x and y coords of their top left point.
        # Values y much higher than x values, as we want to order from top left to bottom right.
        return self.tl[0] + self.tl[1]*30 < other.tl[0] + other.tl[1]*30


def new_clean(img):
    black_mask = cv2.inRange(img, lower_black, upper_black)
    blur = cv2.GaussianBlur(black_mask, (5, 5), 0)
    return blur


def find_squares(in_file, num_rounds):
    """(str, int) -> list of np.ndarray
    Returns a list of all squares needed from in_file, in MNIST format(or to the best ability).
    """
    cropped_images = list()
    image = cv2.imread(in_file, 1)
    image_gray = cv2.imread(in_file, 0)

    # Edit image_gray to make it easier to find contours.
    image_gray = np.where(image_gray > 240, 255, image_gray)
    image_gray = np.where(image_gray <= 240, 0, image_gray)

    image_gray = cv2.blur(image_gray, (5, 5))
    im_th = cv2.adaptiveThreshold(image_gray, 255,
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 115, 1)

    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_OPEN, kernal, iterations=3)

    _, contours, _ = cv2.findContours(im_th.copy(), cv2.RETR_LIST,
                                      cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    contours.remove(contours[0])  # remove the biggest contour

    square_rects = []
    square_areas = []
    for i, cnt in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(cnt)
        ar = w / float(h)
        if 0.9 < ar < 1.1:
            square_rects.append(((x, y), (x + w, y + h)))
            square_areas.append(w * h)  # store area information

    import statistics
    median_size_limit = statistics.median(square_areas) * 0.8
    square_rects = [rect for i, rect in enumerate(square_rects)
                    if square_areas[i] > median_size_limit]

    # Create rectangle objects so we can work with them easily.
    rects = []
    for rect in square_rects:
        rects.append(Rect(rect[0], rect[1]))
    # Sort them from top left to bottom right.
    sorted_rects = sorted(rects)
    # Crop each rectangle out, clean it up, and resize it.
    last_x = 0
    for rect in sorted_rects:
        # If the current row is missing some images, add some filler ones in.
        # Not an ideal solution, but not a common problem, only arises when decimals are placed outside the boxes.
        if last_x != 0 and last_x - rect.tl[0] not in range(-500, 500):
            while len(cropped_images) % (4 + 3 * num_rounds) != 0:
                img = cv2.imread("filler.png")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cropped_images.append(img)
        last_x = rect.tl[0]
        cropped = new_clean(image[rect.tl[1]:rect.br[1], rect.tl[0]:rect.br[0]])
        cropped = cv2.resize(cropped, (28, 28))
        cropped_images.append(cropped)
    return cropped_images
