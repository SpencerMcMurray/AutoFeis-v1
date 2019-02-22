import DigitClassifierCNN as dc
import tensorflow as tf
import os.path
import numpy as np

saver = tf.train.Saver()
save_dir = '../../static/tabulation/checkpoints/'
save_path = os.path.join(save_dir, 'best_validation')


def array_to_digit(images):
    """(list of np.ndarray) -> list of int
    Turns each array of pixels between 0 and 1 into a guess of which digit it represents using the digit classifier
    created using a convolutional neural network.
    """
    results = list()

    # Reload our best performance and push through the given array.
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    saver.restore(sess=sess, save_path=save_path)

    # Get each prediction and store them in a list.
    for img in images:
        image = np.reshape(img, (1, 784))
        results.append(sess.run(dc.y_pred_cls, feed_dict={dc.x: image})[0])
    sess.close()
    return results


def get_all(images):
    """(list of np.ndarray) -> list of list of int
    Returns a formatted list of all digits from the original mark sheet.
    """
    all_digits, digits, dance_num, r1, r2, r3 = list(), 0, '', '', '', ''
    all_white = 0.05
    img_size = len(images[0])

    # Turn the images into digit guesses.
    digit = array_to_digit(images)

    # Allow blank space(and crossed out numbers).
    for i in range(len(images)):
        # Counts the number of ~0s in an image
        count = 0
        for j in range(len(images[i])):
            for k in range(len(images[i])):
                count += (1 if images[i][j, k] <= 255*all_white else 0)

        # Creates the rate of ~0s
        blank_rate = count/(img_size**2)
        if blank_rate >= 1 - all_white:
            if digits in {0, 4, 7, 10}:
                digit[i] = 0
            else:
                digit[i] = ''

        # Sections the digits off into dancer number, rounds 1,2 and 3 scores.
        if digits in range(0, 4):
            dance_num += str(digit[i])
        elif digits in range(4, 7):
            r1 += str(digit[i])
        elif digits in range(7, 10):
            r2 += str(digit[i])
        else:
            r3 += str(digit[i])
        digits += 1

        if digits == 13:
            all_digits.append([int(dance_num), int(r1), int(r2), int(r3)])
            digits = 0
            dance_num, r1, r2, r3 = '', '', '', ''
    return all_digits
