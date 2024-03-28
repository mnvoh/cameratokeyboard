# pylint: disable=missing-function-docstring,redefined-outer-name

from unittest.mock import patch, MagicMock, mock_open

import pytest

from cameratokeyboard.config import Config
from cameratokeyboard.model.augmenter import ImageAugmenterStrategy

FILES_LIST = ["file1.jpg", "file2.jpg"]
STRATEGIES = ["Scale:0.5,1.2", "Rotation:-45,45"]


@pytest.fixture
def config():
    return Config


@pytest.fixture
def scale_augmenter_mock():
    with patch("cameratokeyboard.model.augmenter.augmenters.ScaleAugmenter") as mock:
        mock.return_value.apply.return_value = ["image", "label"]
        yield mock


@pytest.fixture
def rotation_augmenter_mock():
    with patch("cameratokeyboard.model.augmenter.augmenters.RotationAugmenter") as mock:
        mock.return_value.apply.return_value = ["image", "label"]
        yield mock


@pytest.fixture
def cv2_mock():
    with patch("cameratokeyboard.model.augmenter.cv2") as mock:
        yield mock


@pytest.fixture
def mock_file_open():
    with patch("builtins.open", mock_open(read_data="data")) as mock:
        yield mock


@patch("cameratokeyboard.model.augmenter.STRATEGIES", STRATEGIES)
@patch(
    "cameratokeyboard.model.augmenter.os.listdir", MagicMock(return_value=FILES_LIST)
)
def test_run(
    config, scale_augmenter_mock, rotation_augmenter_mock, mock_file_open, cv2_mock
):
    strategy = ImageAugmenterStrategy(config)
    strategy.run()

    assert cv2_mock.imread.called
    assert scale_augmenter_mock.return_value.apply.called
    assert rotation_augmenter_mock.return_value.apply.called
    assert cv2_mock.imwrite.called
