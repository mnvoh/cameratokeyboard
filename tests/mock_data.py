# pylint: skip-file

from random import random

from cameratokeyboard.types import Point


def mock_data_for_marker_boxes():
    return [
        [959.9141845703125, 489.47662353515625, 55.908935546875, 28.44091796875],
        [348.1807861328125, 489.09814453125, 54.27783203125, 27.113555908203125],
        [244.4691619873047, 619.2908935546875, 69.30368041992188, 46.26904296875],
        [1075.73193359375, 619.72998046875, 74.217529296875, 40.921875],
    ]


def mock_data_for_finger_coordinates_down_on(key):
    approximate_finger_coordinates_on_keys = {
        "a": (388, 536),
        "b": (631, 524),
        "c": (530, 521),
        "d": (489, 539),
        "e": (472, 566),
        "g": (591, 535),
        "j": (699, 538),
        "l": (800, 543),
        "m": (717, 521),
        "p": (848, 566),
        "t": (570, 560),
        "z": (424, 515),
    }

    return Point(*approximate_finger_coordinates_on_keys[key])


def mock_data_for_fingers_and_thumbs(count=1):
    def change_values(lst, index):
        return [
            [value + (index * 10 + i) * 10 for i, value in enumerate(values)]
            for values in lst
        ]

    fingers_base_values = [
        [857.584, 395.903, 61.568, 56.43],
        [719.862, 383.436, 53.655, 44.031],
        [412.974, 382.962, 63.202, 56.177],
        [563.882, 390.952, 55.308, 47.553],
        [501.292, 400.624, 59.629, 54.06],
        [329.327, 354.592, 60.993, 56.577],
        [795.109, 396.54, 57.676, 52.011],
        [924.66, 371.737, 59.54, 51.574],
    ]
    thumbs_base_values = [
        [669.632, 344.91, 54.154, 93.647],
        [614.679, 341.849, 54.948, 107.534],
    ]

    results = []
    for i in range(count):
        results.append(
            (
                change_values(fingers_base_values, i),
                change_values(thumbs_base_values, i),
            )
        )

    return results
