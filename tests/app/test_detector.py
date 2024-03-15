# pylint: disable=missing-class-docstring,missing-function-docstring,redefined-outer-name,unused-argument
from unittest.mock import call, patch, Mock, MagicMock
import pytest

from cameratokeyboard.app.detector import Detector


class YoloMock:
    def __init__(self, *args, **kwargs):
        self.instance = MagicMock()

    def __call__(self, *args, **kwargs):
        return self.instance


@pytest.fixture
def config():
    return Mock(iou=0.5, processing_device=0)


@pytest.fixture
def config_with_cpu():
    return Mock(iou=0.5, processing_device="cpu")


@pytest.fixture
def frame():
    return MagicMock()


@pytest.fixture
def yolo_mock():
    with patch(
        "cameratokeyboard.app.detector.ultralytics.YOLO", new_callable=YoloMock
    ) as yolo:
        yield yolo


@pytest.fixture
def detected_frame():
    return MagicMock()


@pytest.fixture
def detected_frame_class():
    with patch("cameratokeyboard.app.detector.DetectedFrame") as detected_frame_class:
        yield detected_frame_class


def test_detect(yolo_mock, config, frame, detected_frame_class):
    detector = Detector(config)

    # first call
    detector.detect(frame)
    assert yolo_mock.instance.call_args_list == [
        call(frame, int(config.processing_device), iou=config.iou)
    ]
    assert detected_frame_class.call_args_list == [
        call(yolo_mock.instance()[0], config=config)
    ]

    # second call
    detector.detect(frame)
    assert detected_frame_class.return_value.update.call_args_list == [
        call(yolo_mock.instance()[0])
    ]


def test_detect_with_cpu(yolo_mock, config_with_cpu, frame, detected_frame_class):
    detector = Detector(config_with_cpu)

    detector.detect(frame)
    assert detected_frame_class.call_args_list == [
        call(yolo_mock.instance()[0], config=config_with_cpu)
    ]
