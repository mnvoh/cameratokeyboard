# pylint: disable=missing-function-docstring,protected-access,redefined-outer-name,unused-argument
from unittest.mock import call, patch, MagicMock

import pytest

from cameratokeyboard.core.detected_frame import DetectedFrame
from cameratokeyboard.types import FrameState


@pytest.fixture
def detection_results():
    detection_results = MagicMock()
    detection_results.orig_img = MagicMock()
    return MagicMock()


@pytest.fixture
def config():
    return MagicMock()


@pytest.fixture
def calibration_strategy():
    with patch(
        "cameratokeyboard.core.detected_frame.AdjacentNeighborCalibrationStrategy"
    ) as mock:
        mock.return_value.is_calibrated = False
        yield mock.return_value


@pytest.fixture
def down_detector():
    with patch("cameratokeyboard.core.detected_frame.FingerDownDetector") as mock:
        yield mock


@pytest.fixture
@patch("cameratokeyboard.core.detected_frame.KeyboardLayout")
def keyboard_layout(mock_layout):
    return mock_layout.return_value


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
def calculate_euler_angles_from_markers():
    with patch(
        "cameratokeyboard.core.detected_frame.calculate_euler_angles_from_markers"
    ) as mock:
        yield mock


@pytest.fixture
def detected_frame(
    detected_markers,
    detected_fingers_and_thumbs,
    detection_results,
    config,
    calibration_strategy,
    calculate_euler_angles_from_markers,
    down_detector,
):
    return DetectedFrame(detection_results, config)


@pytest.fixture
def detected_frame_missing_markers(
    partial_detected_markers,
    detected_fingers_and_thumbs,
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


def test_current_frame(detected_frame, detection_results):
    assert detected_frame.current_frame == detection_results.orig_img


def test_markers(
    detected_markers,
    detected_frame,
):
    assert detected_frame.markers == detected_markers.return_value


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


def test_down_finger_coordinates(detected_frame, down_detector, finger_coordinates):
    pass


def test_down_keys(detected_frame):
    pass


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


def test_requires_calibration(detected_frame, calibration_strategy):
    assert detected_frame.requires_calibration == (
        not calibration_strategy.is_calibrated
    )


def test_calibration_progress(detected_frame, calibration_strategy):
    assert (
        detected_frame.calibration_progress == calibration_strategy.calibration_progress
    )


def test_camera_angle(
    detected_frame,
    calculate_euler_angles_from_markers,
    detected_markers,
    detection_results,
):
    assert (
        detected_frame.camera_angle == calculate_euler_angles_from_markers.return_value
    )
    assert calculate_euler_angles_from_markers.call_args_list == [
        call(
            detected_markers.return_value.top_left_marker,
            detected_markers.return_value.top_right_marker,
            detected_markers.return_value.bottom_right_marker,
            detected_markers.return_value.bottom_left_marker,
            detection_results.orig_img.shape[1::-1],
        )
    ]


def test_start_calibrating(
    detection_results,
    detected_frame,
    calibration_strategy,
    detected_fingers_and_thumbs,
):
    on_calibration_complete = MagicMock()
    detected_frame.start_calibration(on_calibration_complete)
    assert detected_frame._is_calibrating
    assert detected_frame._on_calibration_complete == on_calibration_complete

    detected_frame.update(detection_results)

    assert calibration_strategy.append.call_args_list == [
        call(detected_fingers_and_thumbs.return_value)
    ]

    calibration_strategy.is_calibrated = True
    detected_frame.update(detection_results)
    assert not detected_frame._is_calibrating
    assert on_calibration_complete.called
