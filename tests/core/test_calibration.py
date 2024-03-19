# pylint: disable=missing-function-docstring,protected-access
import pytest

from cameratokeyboard.core.detected_objects import DetectedFingersAndThumbs
from cameratokeyboard.core.calibration import AdjacentNeighborCalibrationStrategy
from cameratokeyboard.types import Fingers

from tests.mock_data import mock_data_for_fingers_and_thumbs


def test_append():
    strategy = AdjacentNeighborCalibrationStrategy(history_size=5)
    assert len(strategy._historical_coordinates) == 0

    # happy
    finger_boxes, thumb_boxes = mock_data_for_fingers_and_thumbs()[0]
    strategy.append(DetectedFingersAndThumbs(finger_boxes, thumb_boxes))

    assert len(strategy._historical_coordinates) == 1

    # sad
    strategy.append(DetectedFingersAndThumbs(finger_boxes[:-1], thumb_boxes[:-1]))
    assert len(strategy._historical_coordinates) == 1


def test_is_calibrated():
    count = 5
    strategy = AdjacentNeighborCalibrationStrategy(history_size=count)
    assert not strategy.is_calibrated

    boxes = mock_data_for_fingers_and_thumbs(count)
    for finger_boxes, thumb_boxes in boxes:
        strategy.append(DetectedFingersAndThumbs(finger_boxes, thumb_boxes))

    assert strategy.is_calibrated


def test_get_calibration_for():
    count = 5
    strategy = AdjacentNeighborCalibrationStrategy(history_size=5)
    assert strategy.calibration_progress == 0.0

    boxes = mock_data_for_fingers_and_thumbs(count)
    for finger_boxes, thumb_boxes in boxes:
        strategy.append(DetectedFingersAndThumbs(finger_boxes, thumb_boxes))

    assert strategy.get_calibration_for(Fingers.LEFT_PINKY) == -28.4
    assert strategy.get_calibration_for(Fingers.LEFT_RING) == -16.6
    assert strategy.get_calibration_for(Fingers.LEFT_MIDDLE) == 11.6
    assert strategy.get_calibration_for(Fingers.LEFT_INDEX) == -11.6
    assert strategy.get_calibration_for(Fingers.LEFT_THUMB) == 27.0
    assert strategy.get_calibration_for(Fingers.RIGHT_THUMB) == 31.6
    assert strategy.get_calibration_for(Fingers.RIGHT_INDEX) == -15.6
    assert strategy.get_calibration_for(Fingers.RIGHT_MIDDLE) == 15.6
    assert strategy.get_calibration_for(Fingers.RIGHT_RING) == 1.0
    assert strategy.get_calibration_for(Fingers.RIGHT_PINKY) == -26.0


def test_calibration_progress():
    count = 5
    strategy = AdjacentNeighborCalibrationStrategy(history_size=5)
    assert strategy.calibration_progress == 0.0

    boxes = mock_data_for_fingers_and_thumbs(count)
    for finger_boxes, thumb_boxes in boxes:
        strategy.append(DetectedFingersAndThumbs(finger_boxes, thumb_boxes))

    assert strategy.calibration_progress == 1.0
