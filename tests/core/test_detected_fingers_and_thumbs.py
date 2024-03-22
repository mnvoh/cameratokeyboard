# pylint: disable=missing-function-docstring,redefined-outer-name

import pytest
from cameratokeyboard.core.detected_objects import (
    DetectedFingersAndThumbs,
    Point,
)


@pytest.fixture
def detected_fingers_and_thumbs():
    finger_boxes = [
        [0, 0, 10, 10],
        [20, 20, 30, 30],
        [40, 40, 50, 50],
        [60, 60, 70, 70],
        [80, 80, 90, 90],
        [100, 100, 110, 110],
        [120, 120, 130, 130],
        [140, 140, 150, 150],
    ]
    thumb_boxes = [[100, 100, 110, 110], [120, 120, 130, 130]]
    return DetectedFingersAndThumbs(finger_boxes, thumb_boxes)


def test_finger_coordinates(detected_fingers_and_thumbs):
    finger_coordinates = detected_fingers_and_thumbs.finger_coordinates
    assert len(finger_coordinates) == 8
    assert finger_coordinates[0] == Point(0, 3)
    assert finger_coordinates[1] == Point(20, 30)
    assert finger_coordinates[2] == Point(40, 56)
    assert finger_coordinates[3] == Point(60, 83)
    assert finger_coordinates[4] == Point(80, 110)


def test_thumb_coordinates(detected_fingers_and_thumbs):
    thumb_coordinates = detected_fingers_and_thumbs.thumb_coordinates
    assert len(thumb_coordinates) == 2
    assert thumb_coordinates[0] == Point(100, 155)
    assert thumb_coordinates[1] == Point(120, 185)


def test_average_finger_width(detected_fingers_and_thumbs):
    average_finger_width = detected_fingers_and_thumbs.average_finger_width
    assert average_finger_width == 80


def test_average_finger_height(detected_fingers_and_thumbs):
    average_finger_height = detected_fingers_and_thumbs.average_finger_height
    assert average_finger_height == 80.0
