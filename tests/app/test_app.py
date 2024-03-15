# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access,unused-argument

import time
from unittest.mock import patch, MagicMock

import cv2
import pytest

from cameratokeyboard.config import Config
from cameratokeyboard.app.app import App, RepeatingKeysThrottler
from cameratokeyboard.app.detector import Detector


@pytest.fixture
def mock_ui_class():
    with patch("cameratokeyboard.app.app.UI") as mock_ui:
        yield mock_ui


@pytest.fixture
def config():
    return Config()


@pytest.fixture
@patch("cameratokeyboard.app.detector.ultralytics.YOLO")
def app(yolo, config, mock_ui_class):
    yolo.return_value = MagicMock()
    return App(config)


def test_app_initialization(app, config, mock_ui_class):
    assert app._config == config
    assert isinstance(app._cap, cv2.VideoCapture)
    assert isinstance(app._detector, Detector)
    assert app._ui is mock_ui_class.return_value
    assert isinstance(app._throttler, RepeatingKeysThrottler)
    assert app._detected_frame is None


def test_key_press_allowed():
    throttler = RepeatingKeysThrottler(delay=0.5)

    assert throttler.key_press_allowed("a") is True

    throttler.key_press_allowed("a")
    assert throttler.key_press_allowed("a") is False

    with patch("time.time", return_value=time.time() + 0.6):
        assert throttler.key_press_allowed("a") is True
