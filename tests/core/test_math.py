# pylint: disable=missing-function-docstring
import pytest
import yaml

from cameratokeyboard.core.detected_objects import DetectedMarkers
from cameratokeyboard.core.math import (
    calculate_box_width_without_perspective_distortion,
    finger_to_keyboard_fractional_coordinates,
)

from tests.helpers import assert_within_tolerance
from tests.mock_data import (
    mock_data_for_marker_boxes,
    mock_data_for_finger_coordinates_down_on,
)


def _load_layout():
    with open(
        "cameratokeyboard/core/keyboard_layouts/qwerty.yaml", "r", encoding="utf-8"
    ) as file:
        return yaml.safe_load(file)


def _actual_key_bounding_box(key):
    layout = _load_layout()

    for row, keys in layout["keys"].items():
        row_index = int(row.split("_")[-1]) - 1

        x = 0
        for key_data in keys:
            if key_data["name"] == key:
                y = row_index * layout["key_height"]
                return (
                    round(x, 3),
                    round(y, 3),
                    round(x + key_data["width"], 3),
                    round(y + layout["key_height"], 3),
                )
            else:
                x += key_data["width"]

    return None


def test_calculate_box_width_without_perspective_distortion():
    # sad
    with pytest.raises(ValueError):
        calculate_box_width_without_perspective_distortion(None, None)

    # happy
    markers = mock_data_for_marker_boxes()
    actual = calculate_box_width_without_perspective_distortion(markers[1], markers[2])

    assert_within_tolerance(actual, 27, 5)


def test_finger_to_keyboard_fractional_coordinates():
    keys = ["a", "b", "c", "d", "e", "g", "j", "l", "m", "p", "t", "z"]
    test_cases = [
        (mock_data_for_finger_coordinates_down_on(key), _actual_key_bounding_box(key))
        for key in keys
    ]

    # sad
    markers = DetectedMarkers(mock_data_for_marker_boxes())
    with pytest.raises(ValueError):
        finger_to_keyboard_fractional_coordinates(markers, None)

    markers = DetectedMarkers(mock_data_for_marker_boxes()[:-1])
    with pytest.raises(ValueError):
        finger_to_keyboard_fractional_coordinates(markers, test_cases[0][0])

    # happy
    markers = DetectedMarkers(mock_data_for_marker_boxes())
    for finger_coordinates, expected_bounding_box in test_cases:
        actual = finger_to_keyboard_fractional_coordinates(
            markers,
            finger_coordinates,
        )
        assert (
            actual[0] > expected_bounding_box[0]
            and actual[0] < expected_bounding_box[0] + expected_bounding_box[2]
            and actual[1] > expected_bounding_box[1]
            and actual[1] < expected_bounding_box[1] + expected_bounding_box[3]
        )
