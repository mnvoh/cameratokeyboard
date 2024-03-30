# pylint: disable=missing-function-docstring,redefined-outer-name

from datetime import datetime, timedelta
from unittest.mock import call, patch, MagicMock

import pytest

from cameratokeyboard.model.model_downloader import ModelDownloader
from tests.fixtures import s3_objects_response

MODELS_DIR = "/path/to/models"
BUCKET_NAME = "bucket_name"
REGION = "eu-west-2"
PREFIX = "models/"
LATEST_MODEL = "file1.pt"


@pytest.fixture
def config_mock():
    return MagicMock(
        models_dir=MODELS_DIR,
        remote_models_bucket_name=BUCKET_NAME,
        remote_models_bucket_region=REGION,
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
def requests_mock():
    def get_mock(url, *args, **kwargs):
        if url == "https://bucket_name.s3.eu-west-2.amazonaws.com":
            return MagicMock(content=s3_objects_response.encode("utf-8"))
        else:
            return MagicMock(content="thefilecontents".encode("utf-8"))

    with patch("cameratokeyboard.model.model_downloader.requests") as mock:
        mock.get.side_effect = get_mock
        yield mock


def test_run(config_mock, os_mock, requests_mock):
    model_downloader = ModelDownloader(config_mock)
    model_downloader.run()

    assert os_mock.makedirs.call_args_list == [call("/path/to/models", exist_ok=True)]
    print(requests_mock.get.call_args_list)
    assert requests_mock.get.call_args_list == [
        call("https://bucket_name.s3.eu-west-2.amazonaws.com", timeout=10.0),
        call(
            "https://bucket_name.s3.eu-west-2.amazonaws.com/models/72cf8b59b60538ba46cdda79bd38afaa.pt",
            timeout=10.0,
            stream=True,
        ),
    ]


# def test_run_no_remote_models(config_mock, os_mock, boto3_client_no_models_mock):
#    model_downloader = ModelDownloader(config_mock)
#    model_downloader.run()
#
#    assert not boto3_client_no_models_mock.return_value.download_file.called
#
#
# def test_run_model_already_downloaded(
#    config_mock, os_model_exists_mock, boto3_client_mock
# ):
#    model_downloader = ModelDownloader(config_mock)
#    model_downloader.run()
#
#    assert not boto3_client_mock.return_value.download_file.called
