# pylint: disable=missing-function-docstring,redefined-outer-name,unused-argument
from unittest.mock import patch, call, mock_open

import platformdirs
import pytest

from cameratokeyboard.config import Config
from cameratokeyboard.model.train import Trainer


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def path_exists_mock():
    with patch("cameratokeyboard.model.train.os.path.exists") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def listdir_mock():
    with patch("cameratokeyboard.model.train.os.listdir") as mock:
        mock.return_value = ["file1", "file2"]
        yield mock


@pytest.fixture
def makedirs_mock():
    with patch("cameratokeyboard.model.train.os.makedirs") as mock:
        yield mock


@pytest.fixture
def file_mock():
    with patch("builtins.open", mock_open(read_data="a".encode("utf-8"))) as mock:
        yield mock


@pytest.fixture
def partitioner_mock():
    with patch("cameratokeyboard.model.train.DataPartitioner") as mock:
        yield mock


@pytest.fixture
def augmenter_mock():
    with patch("cameratokeyboard.model.train.ImageAugmenterStrategy") as mock:
        yield mock


@pytest.fixture
def yolo_mock():
    with patch("cameratokeyboard.model.train.YOLO") as mock:
        mock.return_value.train.return_value.save_dir = "/somewhere"
        yield mock


@pytest.fixture
def copyfile_mock():
    with patch("cameratokeyboard.model.train.shutil.copyfile") as mock:
        yield mock


def test_calc_next_version(config, path_exists_mock, listdir_mock, file_mock):
    trainer = Trainer(config)
    assert trainer.calc_next_version() == "f3a0377ce26903122eb91b2851f97c96"


def test_train_default_path(
    config,
    path_exists_mock,
    listdir_mock,
    file_mock,
    makedirs_mock,
    partitioner_mock,
    augmenter_mock,
    yolo_mock,
    copyfile_mock,
):
    trainer = Trainer(config)
    trainer.run()
    target_dir = f"{platformdirs.user_data_dir()}/c2k/models"

    assert partitioner_mock.return_value.partition.called
    assert augmenter_mock.return_value.run.called

    assert makedirs_mock.called and makedirs_mock.call_args_list == [
        call(target_dir, exist_ok=True)
    ]

    assert copyfile_mock.called and copyfile_mock.call_args_list == [
        call(
            "/somewhere/weights/best.pt",
            f"{target_dir}/f3a0377ce26903122eb91b2851f97c96.pt",
        )
    ]
