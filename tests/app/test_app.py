# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access,unused-argument
import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from cameratokeyboard.config import Config
from cameratokeyboard.app.app import App, RepeatingKeysThrottler


@pytest.fixture
def mock_cap():
    with patch("cv2.flip"), patch("cv2.VideoCapture") as mock_cap:
        mock_cap.return_value.read.return_value = (True, MagicMock())
        yield mock_cap


@pytest.fixture
def mock_cap_failed():
    with patch("cv2.flip"), patch("cv2.VideoCapture") as mock_cap:
        mock_cap.return_value.read.return_value = (False, None)
        yield mock_cap


@pytest.fixture
def mock_ui_class():
    with patch("cameratokeyboard.app.app.UI") as mock_ui:
        yield mock_ui


@pytest.fixture
def mock_ui_run(mock_ui_class):
    mock = MagicMock()

    async def run():
        mock()
        await asyncio.sleep(0.9)

    mock_ui_class.return_value.run = run

    return mock


@pytest.fixture
def mock_detected_frame():
    mock = MagicMock()

    mock.down_keys = ["a"]

    return mock


@pytest.fixture
def config():
    return Config()


@pytest.fixture
@patch("cameratokeyboard.app.app.Detector")
def app(mock_detector, config, mock_ui_class, mock_detected_frame):
    mock_detector.return_value.detect.return_value = mock_detected_frame
    return App(config)


def test_app_initialization(app, config, mock_ui_class):
    assert app._config == config
    assert app._ui is mock_ui_class.return_value
    assert isinstance(app._throttler, RepeatingKeysThrottler)
    assert app._detected_frame is None


@pytest.mark.asyncio
async def test_app_run(mock_cap, app, mock_ui_run, mock_detected_frame):
    await app.run()

    mock_ui_run.assert_called()
    app._ui.update_data.assert_called()
    app._ui.update_text.assert_called()


@pytest.mark.asyncio
async def test_app_run_failed_frame(mock_cap_failed, app, mock_ui_run):
    await app.run()

    app._ui.update_data.assert_not_called()


def test_key_press_allowed():
    throttler = RepeatingKeysThrottler(delay=0.5)

    assert throttler.key_press_allowed("a") is True

    throttler.key_press_allowed("a")
    assert throttler.key_press_allowed("a") is False

    with patch("time.time", return_value=time.time() + 0.6):
        assert throttler.key_press_allowed("a") is True
