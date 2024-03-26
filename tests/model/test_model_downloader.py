# pylint: disable=missing-function-docstring,redefined-outer-name

from datetime import datetime, timedelta
from unittest.mock import call, patch, MagicMock

import pytest

from cameratokeyboard.model.model_downloader import ModelDownloader

MODELS_DIR = "/path/to/models"
BUCKET_NAME = "bucket_name"
PREFIX = "remote/path/"
LATEST_MODEL = "file1.pt"


@pytest.fixture
def config_mock():
    return MagicMock(
        models_dir=MODELS_DIR,
        remote_models_bucket_name=BUCKET_NAME,
        remote_models_prefix=PREFIX,
    )


@pytest.fixture
def os_mock():
    with patch("cameratokeyboard.model.model_downloader.os") as mock:
        mock.listdir.return_value = []
        yield mock


@pytest.fixture
def os_model_exists_mock():
    with patch("cameratokeyboard.model.model_downloader.os") as mock:
        mock.listdir.return_value = [LATEST_MODEL]
        yield mock


@pytest.fixture
def boto3_client_mock():
    two_days_ago = datetime.now() - timedelta(days=2)
    four_days_ago = datetime.now() - timedelta(days=4)

    with patch("cameratokeyboard.model.model_downloader.boto3.client") as mock:
        mock.return_value.list_objects_v2.return_value = {
            "Contents": [
                {"Key": LATEST_MODEL, "LastModified": two_days_ago},
                {"Key": "file2.pt", "LastModified": four_days_ago},
            ]
        }

        yield mock


@pytest.fixture
def boto3_client_no_models_mock():
    with patch("cameratokeyboard.model.model_downloader.boto3.client") as mock:
        mock.return_value.list_objects_v2.return_value = {"Contents": []}

        yield mock


def test_run(config_mock, os_mock, boto3_client_mock):
    model_downloader = ModelDownloader(config_mock)
    model_downloader.run()

    assert os_mock.makedirs.call_args_list == [call("/path/to/models", exist_ok=True)]
    assert boto3_client_mock.return_value.download_file.call_args_list == [
        call(BUCKET_NAME, f"{PREFIX}{LATEST_MODEL}", f"{MODELS_DIR}/{LATEST_MODEL}")
    ]


def test_run_no_remote_models(config_mock, os_mock, boto3_client_no_models_mock):
    model_downloader = ModelDownloader(config_mock)
    model_downloader.run()

    assert not boto3_client_no_models_mock.return_value.download_file.called


def test_run_model_already_downloaded(
    config_mock, os_model_exists_mock, boto3_client_mock
):
    model_downloader = ModelDownloader(config_mock)
    model_downloader.run()

    assert not boto3_client_mock.return_value.download_file.called
