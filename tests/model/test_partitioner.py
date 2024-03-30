# pylint: disable=missing-function-docstring,redefined-outer-name

from unittest.mock import patch, MagicMock, call

import pytest

from cameratokeyboard.config import Config
from cameratokeyboard.model.partitioner import DataPartitioner

IMAGES_LIST = ["image1.jpg", "image2.jpg", "image3.jpg", "image4.jpg"]
LABELS_LIST = ["image1.txt", "image2.txt", "image3.txt", "image4.txt"]


@pytest.fixture
def config():
    config = Config()
    config.split_ratios = [0.5, 0.25, 0.25]

    return config


def makedirs_call_args(config):
    return [
        call(path)
        for path in [
            f"{config.dataset_path}/images/train",
            f"{config.dataset_path}/labels/train",
            f"{config.dataset_path}/images/test",
            f"{config.dataset_path}/labels/test",
            f"{config.dataset_path}/images/val",
            f"{config.dataset_path}/labels/val",
        ]
    ]


def copyfile_call_args(config):
    return [
        call(
            f"{config.raw_dataset_path}/image1.jpg",
            f"{config.dataset_path}/images/train/00000.jpg",
        ),
        call(
            f"{config.raw_dataset_path}/image1.txt",
            f"{config.dataset_path}/labels/train/00000.txt",
        ),
        call(
            f"{config.raw_dataset_path}/image2.jpg",
            f"{config.dataset_path}/images/train/00001.jpg",
        ),
        call(
            f"{config.raw_dataset_path}/image2.txt",
            f"{config.dataset_path}/labels/train/00001.txt",
        ),
        call(
            f"{config.raw_dataset_path}/image3.jpg",
            f"{config.dataset_path}/images/test/00002.jpg",
        ),
        call(
            f"{config.raw_dataset_path}/image3.txt",
            f"{config.dataset_path}/labels/test/00002.txt",
        ),
        call(
            f"{config.raw_dataset_path}/image4.jpg",
            f"{config.dataset_path}/images/val/00003.jpg",
        ),
        call(
            f"{config.raw_dataset_path}/image4.txt",
            f"{config.dataset_path}/labels/val/00003.txt",
        ),
    ]


@pytest.fixture
def os_mock_all_paths_exist():
    def join(*args):
        return "/".join(args)

    with patch("cameratokeyboard.model.partitioner.os") as mock:
        mock.listdir.return_value = IMAGES_LIST
        mock.path.exists.return_value = True
        mock.path.join = join
        yield mock


@pytest.fixture
def os_mock_some_paths_dont_exist(os_mock_all_paths_exist):
    def exists(file):
        if file.endswith("txt"):
            return False
        return True

    os_mock_all_paths_exist.path.exists = exists

    yield os_mock_all_paths_exist


@pytest.fixture
def shutil_mock():
    with patch("cameratokeyboard.model.partitioner.shutil") as mock:
        yield mock


@pytest.fixture
def shuffle_mock():
    def shuffle(iterable):
        return iterable

    with patch("cameratokeyboard.model.partitioner.shuffle", shuffle) as mock:
        yield mock


def test_partition(config, os_mock_all_paths_exist, shutil_mock, shuffle_mock):
    DataPartitioner(config).partition()

    assert shutil_mock.rmtree.call_args_list == [call(config.dataset_path)]
    assert os_mock_all_paths_exist.makedirs.call_args_list == makedirs_call_args(config)

    print(shutil_mock.copyfile.call_args_list)
    assert shutil_mock.copyfile.call_args_list == copyfile_call_args(config)


def test_partition_labels_missing(config, os_mock_some_paths_dont_exist, shutil_mock):
    partitioner = DataPartitioner(config)

    with pytest.raises(ValueError):
        partitioner.partition()
