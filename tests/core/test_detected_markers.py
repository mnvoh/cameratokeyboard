# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access

import pytest
from cameratokeyboard.core.detected_objects import DetectedMarkers, Point

EXPECTED_MARKER_COORDINATES = [
    Point(3, 6),
    Point(33, 88),
    Point(115, 142),
    Point(164, 84),
]


@pytest.fixture
def detected_markers():
    # Create a sample list of bounding box coordinates
    boxes = [
        [10, 20, 30, 40],
        [50, 60, 70, 80],
        [90, 100, 110, 120],
        [130, 140, 150, 160],
    ]
    return DetectedMarkers(boxes)


def test_bottom_left_marker(detected_markers):
    assert detected_markers.bottom_left_marker == EXPECTED_MARKER_COORDINATES[0]

    detected_markers._bl = None
    assert detected_markers.bottom_left_marker is None


def test_top_left_marker(detected_markers):
    assert detected_markers.top_left_marker == EXPECTED_MARKER_COORDINATES[1]

    detected_markers._tl = None
    assert detected_markers.top_left_marker is None


def test_top_right_marker(detected_markers):
    assert detected_markers.top_right_marker == EXPECTED_MARKER_COORDINATES[2]

    detected_markers._tr = None
    assert detected_markers.top_right_marker is None


def test_bottom_right_marker(detected_markers):
    assert detected_markers.bottom_right_marker == EXPECTED_MARKER_COORDINATES[3]

    detected_markers._br = None
    assert detected_markers.bottom_right_marker is None


def test_all_marker_coordinates(detected_markers):
    assert detected_markers.all_marker_coordinates == EXPECTED_MARKER_COORDINATES


def test_any_markers_missing(detected_markers):
    assert not detected_markers.any_markers_missing


def test_all_markers_present(detected_markers):
    assert detected_markers.all_markers_present
