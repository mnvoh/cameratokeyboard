# pylint: disable=missing-function-docstring,redefined-outer-name
from unittest.mock import MagicMock

import pytest
from cameratokeyboard.core.finger_down_detector import FingerDownDetector
from cameratokeyboard.types import Fingers

TEST_FINGER = Fingers.LEFT_PINKY
FINGERS_AND_THUMBS_WITH_NO_COORDINATES = {TEST_FINGER: None}
FINGERS_AND_THUMBS_WITH_POSITIVE_ACCELERATING_VELOCITY = {
    TEST_FINGER: MagicMock(velocity_y=lambda window: 10.0),
}
FINGERS_AND_THUMBS_WITH_VALID_VALUES = {
    TEST_FINGER: MagicMock(
        y=10.0,
        velocity_y=lambda window: -10.0,
    ),
    Fingers.LEFT_RING: MagicMock(y=5.0),
    Fingers.LEFT_MIDDLE: MagicMock(y=3.0),
    Fingers.LEFT_INDEX: MagicMock(y=3.0),
    Fingers.LEFT_THUMB: MagicMock(y=3.0),
    Fingers.RIGHT_THUMB: MagicMock(y=3.0),
    Fingers.RIGHT_INDEX: MagicMock(y=3.0),
    Fingers.RIGHT_MIDDLE: MagicMock(y=3.0),
    Fingers.RIGHT_RING: MagicMock(y=3.0),
    Fingers.RIGHT_PINKY: MagicMock(y=3.0),
}


@pytest.fixture
def fingers_and_thumbs_with_valid_values():
    mock = MagicMock()
    mock.__getitem__.side_effect = lambda key: FINGERS_AND_THUMBS_WITH_VALID_VALUES[key]
    mock.average_finger_height = 5.0

    yield mock


def get_down_detector(calibration, sensitivity):
    return FingerDownDetector(calibration, sensitivity)


def test_with_no_coordinates():
    down_detector = get_down_detector(FINGERS_AND_THUMBS_WITH_NO_COORDINATES, 0.5)

    assert not down_detector.is_finger_down(
        FINGERS_AND_THUMBS_WITH_NO_COORDINATES, TEST_FINGER
    )


def test_with_positive_accelerating_velocity():
    down_detector = get_down_detector(FINGERS_AND_THUMBS_WITH_NO_COORDINATES, 0.5)

    assert not down_detector.is_finger_down(
        FINGERS_AND_THUMBS_WITH_POSITIVE_ACCELERATING_VELOCITY, TEST_FINGER
    )


def test_with_no_calibration_value():
    calibration = MagicMock(
        get_calibration_for=lambda finger: None,
        calculate_calibration_value=lambda fingers_and_thumbs, finger: 0,
    )
    down_detector = get_down_detector(calibration, 0.5)

    assert not down_detector.is_finger_down(
        FINGERS_AND_THUMBS_WITH_VALID_VALUES, TEST_FINGER
    )


def test_with_valid_values(fingers_and_thumbs_with_valid_values):
    calibration = MagicMock(
        get_calibration_for=lambda finger: 0.0,
        calculate_calibration_value=lambda fingers_and_thumbs, finger: 10,
    )
    down_detector = get_down_detector(calibration, 0.5)

    assert down_detector.is_finger_down(
        fingers_and_thumbs_with_valid_values, TEST_FINGER
    )
