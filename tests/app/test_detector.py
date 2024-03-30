# pylint: disable=missing-class-docstring,missing-function-docstring,redefined-outer-name,unused-argument
from unittest.mock import call, patch, Mock, MagicMock
import pytest

from cameratokeyboard.app.detector import Detector

from tests.fixtures import s3_objects_response

MODELS_DIR = "/path/to/models"
BUCKET_NAME = "bucket_name"
REGION = "eu-west-2"
PREFIX = "models/"


class YoloMock:
    def __init__(self, *args, **kwargs):
        self.instance = MagicMock()

    def __call__(self, *args, **kwargs):
        return self.instance


@pytest.fixture
def base_config():
    return {
        "iou": 0.5,
        "models_dir": MODELS_DIR,
        "remote_models_bucket_name": BUCKET_NAME,
        "remote_models_bucket_region": REGION,
        "remote_models_prefix": PREFIX,
    }


@pytest.fixture
def config(base_config):
    return Mock(processing_device=0, **base_config)


@pytest.fixture
def config_with_cpu(base_config):
    return Mock(processing_device="cpu", **base_config)


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


@pytest.fixture(autouse=True)
def requests_mock():
    with patch("cameratokeyboard.model.model_downloader.requests") as mock:
        mock.get.return_value = MagicMock(content=s3_objects_response.encode("utf-8"))
        yield mock


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
