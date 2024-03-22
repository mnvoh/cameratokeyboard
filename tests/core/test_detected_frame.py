# pylint: disable=missing-function-docstring,protected-access,redefined-outer-name,unused-argument
from unittest.mock import call, patch, MagicMock

import pytest

from cameratokeyboard.core.detected_frame import DetectedFrame
from cameratokeyboard.types import FrameState, Fingers

DOWN_KEYS = ["a", " "]


@pytest.fixture
def detection_results():
    detection_results = MagicMock()
    detection_results.orig_img = MagicMock()
    detection_results.boxes = MagicMock()
    detection_results.boxes.cls = [1] * 8 + [2] * 2 + [3] * 4
    detection_results.boxes.conf = [1.0] * 14

    boxes = []
    for i in range(14):
        boxes.append([i, i, 2, 2])

    detection_results.boxes.xywh = boxes

    detection_results.names = {1: "finger", 2: "thumb", 3: "marker"}

    return detection_results


@pytest.fixture
def config():
    return MagicMock(
        keyboard_layout="qwerty",
        markers_min_confidence=0.5,
        fingers_min_confidence=0.5,
        thumbs_min_confidence=0.5,
    )


@pytest.fixture
def mock_calibration_strategy():
    with patch(
        "cameratokeyboard.core.detected_frame.AdjacentNeighborCalibrationStrategy"
    ) as mock:
        mock.return_value.is_calibrated = True
        yield mock.return_value


@pytest.fixture
def mock_down_detector():
    def mock_is_finger_down(_, finger):
        return finger in [Fingers.LEFT_PINKY, Fingers.LEFT_THUMB]

    with patch("cameratokeyboard.core.detected_frame.FingerDownDetector") as mock:
        mock.return_value.is_finger_down = mock_is_finger_down
        yield mock


@pytest.fixture
def mock_finger_to_keyboard_coordinates():
    with patch(
        "cameratokeyboard.core.detected_frame.finger_to_keyboard_fractional_coordinates"
    ) as mock:
        a_key_coordinates = (0.118 + 0.05, 0.2 * 2 + 0.1)
        mock.return_value = a_key_coordinates

        yield mock


@pytest.fixture
def all_marker_coordiantes():
    return [MagicMock(x=1, y=1) for _ in range(4)]


@pytest.fixture
def finger_coordinates():
    return [MagicMock(x=1, y=1) for _ in range(8)]


@pytest.fixture
def thumb_coordinates():
    return [MagicMock(x=1, y=1) for _ in range(2)]


@pytest.fixture
def detected_markers(all_marker_coordiantes):
    with patch("cameratokeyboard.core.detected_frame.DetectedMarkers") as mock:
        mock.return_value.all_marker_coordinates = all_marker_coordiantes
        yield mock


@pytest.fixture
def partial_detected_markers(all_marker_coordiantes):
    with patch("cameratokeyboard.core.detected_frame.DetectedMarkers") as mock:
        mock.return_value.all_marker_coordinates = all_marker_coordiantes[:2]
        yield mock


@pytest.fixture
def no_detected_markers(all_marker_coordiantes):
    with patch("cameratokeyboard.core.detected_frame.DetectedMarkers") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def detected_fingers_and_thumbs(finger_coordinates, thumb_coordinates):
    with patch("cameratokeyboard.core.detected_frame.DetectedFingersAndThumbs") as mock:
        mock.return_value.finger_coordinates = finger_coordinates
        mock.return_value.thumb_coordinates = thumb_coordinates
        yield mock


@pytest.fixture
def partial_fingers(finger_coordinates, thumb_coordinates):
    with patch("cameratokeyboard.core.detected_frame.DetectedFingersAndThumbs") as mock:
        mock.return_value.finger_coordinates = finger_coordinates[:4]
        mock.return_value.thumb_coordinates = thumb_coordinates
        yield mock


@pytest.fixture
def partial_thumbs(finger_coordinates, thumb_coordinates):
    with patch("cameratokeyboard.core.detected_frame.DetectedFingersAndThumbs") as mock:
        mock.return_value.finger_coordinates = finger_coordinates
        mock.return_value.thumb_coordinates = thumb_coordinates[:1]
        yield mock


@pytest.fixture
def detected_frame(
    detected_markers,
    detected_fingers_and_thumbs,
    detection_results,
    config,
    mock_calibration_strategy,
    mock_down_detector,
    mock_finger_to_keyboard_coordinates,
):
    return DetectedFrame(detection_results, config)


@pytest.fixture
def detected_frame_missing_markers(
    partial_detected_markers,
    detection_results,
    config,
):
    return DetectedFrame(detection_results, config)


@pytest.fixture
def detected_frame_with_no_markers(
    no_detected_markers,
    detection_results,
    config,
):
    return DetectedFrame(detection_results, config)


@pytest.fixture
def detected_frame_missing_fingers(
    detected_markers,
    partial_fingers,
    detection_results,
    config,
):
    return DetectedFrame(detection_results, config)


@pytest.fixture
def detected_frame_missing_thumbs(
    detected_markers,
    partial_thumbs,
    detection_results,
    config,
):
    return DetectedFrame(detection_results, config)


def test_update(detected_frame, detection_results):
    detected_frame.update(detection_results)
    assert detected_frame._markers.update.call_args_list == [
        call(
            [
                [10.0, 10.0, 2.0, 2.0],
                [11.0, 11.0, 2.0, 2.0],
                [12.0, 12.0, 2.0, 2.0],
                [13.0, 13.0, 2.0, 2.0],
            ]
        )
    ]
    assert detected_frame._fingers_and_thumbs.update.call_args_list == [
        call(
            [
                [0.0, 0.0, 2.0, 2.0],
                [1.0, 1.0, 2.0, 2.0],
                [2.0, 2.0, 2.0, 2.0],
                [3.0, 3.0, 2.0, 2.0],
                [4.0, 4.0, 2.0, 2.0],
                [5.0, 5.0, 2.0, 2.0],
                [6.0, 6.0, 2.0, 2.0],
                [7.0, 7.0, 2.0, 2.0],
            ],
            [[8.0, 8.0, 2.0, 2.0], [9.0, 9.0, 2.0, 2.0]],
        )
    ]
    assert detected_frame._down_keys == DOWN_KEYS


def test_current_frame(detected_frame, detection_results):
    assert detected_frame.current_frame == detection_results.orig_img


def test_markers(
    detected_markers,
    detected_frame,
):
    assert detected_frame.markers == detected_markers.return_value


def test_no_markers(
    no_detected_markers,
    detected_frame_with_no_markers,
):
    assert detected_frame_with_no_markers.marker_coordinates == []


def test_all_marker_coordinates(
    detected_frame,
    all_marker_coordiantes,
):
    assert detected_frame.marker_coordinates == all_marker_coordiantes


def test_finger_coordinates(
    detected_frame, detected_fingers_and_thumbs, finger_coordinates
):
    assert detected_frame.finger_coordinates == finger_coordinates


def test_thumb_coordinates(
    detected_frame, detected_fingers_and_thumbs, thumb_coordinates
):
    assert detected_frame.thumb_coordinates == thumb_coordinates


def test_down_finger_coordinates(
    detected_frame, mock_down_detector, finger_coordinates
):
    detected_frame._down_fingers = [("a", "blahblehblew")]

    assert detected_frame.down_finger_coordinates == ["blahblehblew"]


def test_down_keys(detected_frame):
    down_keys = ["a", "b"]
    detected_frame._down_keys = down_keys
    assert detected_frame.down_keys == down_keys


def test_state_valid(detected_frame, detected_markers, detected_fingers_and_thumbs):
    assert detected_frame.state == FrameState.VALID


def test_state_missing_markers(
    detected_frame_missing_markers, partial_detected_markers
):
    assert detected_frame_missing_markers.state == FrameState.MISSING_MARKERS


def test_state_missing_fingers(detected_frame_missing_fingers, partial_fingers):
    assert detected_frame_missing_fingers.state == FrameState.MISSING_FINGERS


def test_state_missing_thumbs(detected_frame_missing_thumbs, partial_thumbs):
    assert detected_frame_missing_thumbs.state == FrameState.MISSING_THUMBS


def test_requires_calibration(detected_frame, mock_calibration_strategy):
    assert detected_frame.requires_calibration == (
        not mock_calibration_strategy.is_calibrated
    )


def test_calibration_progress(detected_frame, mock_calibration_strategy):
    assert (
        detected_frame.calibration_progress
        == mock_calibration_strategy.calibration_progress
    )


def test_start_calibrating(
    detection_results,
    detected_frame,
    mock_calibration_strategy,
    detected_fingers_and_thumbs,
):
    on_calibration_complete = MagicMock()
    detected_frame.start_calibration(on_calibration_complete)
    assert detected_frame._is_calibrating
    assert detected_frame._on_calibration_complete == on_calibration_complete

    detected_frame.update(detection_results)

    assert mock_calibration_strategy.append.call_args_list == [
        call(detected_fingers_and_thumbs.return_value)
    ]

    mock_calibration_strategy.is_calibrated = True
    detected_frame.update(detection_results)
    assert not detected_frame._is_calibrating
    assert on_calibration_complete.called
