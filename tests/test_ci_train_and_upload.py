# pylint: disable=missing-function-docstring,redefined-outer-name,unused-argument
from unittest.mock import patch, call
import tempfile

import pytest

from ci_train_and_upload import version_already_exists, train, upload_model

MODEL_VERSION = "model_version"


@pytest.fixture
def s3_client_mock_model_exists():
    with patch("ci_train_and_upload.s3_client") as s3_mock:
        s3_mock.list_objects_v2.return_value = {"KeyCount": 1}
        yield s3_mock


@pytest.fixture
def s3_client_mock_model_does_not_exists():
    with patch("ci_train_and_upload.s3_client") as s3_mock:
        s3_mock.list_objects_v2.return_value = {"KeyCount": 0}
        yield s3_mock


@pytest.fixture
def trainer_mock():
    with patch("ci_train_and_upload.trainer") as mock:
        mock.calc_next_version.return_value = MODEL_VERSION
        yield mock


@pytest.fixture
def os_mock_model_exists():
    with patch("ci_train_and_upload.os.path.exists") as os_mock:
        os_mock.return_value = True
        yield os_mock


@pytest.fixture
def os_mock_model_does_not_exists():
    with patch("ci_train_and_upload.os.path.exists") as os_mock:
        os_mock.return_value = False
        yield os_mock


def test_version_already_exists_true(s3_client_mock_model_exists):
    assert version_already_exists(MODEL_VERSION)
    assert s3_client_mock_model_exists.list_objects_v2.called


def test_version_already_exists_false(s3_client_mock_model_does_not_exists):
    assert not version_already_exists(MODEL_VERSION)


def test_train(s3_client_mock_model_does_not_exists, trainer_mock):
    train()
    assert trainer_mock.run.called


def test_train_version_already_exists(s3_client_mock_model_exists, trainer_mock):
    train()
    assert not trainer_mock.run.called


def test_upload(
    s3_client_mock_model_does_not_exists, trainer_mock, os_mock_model_exists
):
    upload_model()
    assert s3_client_mock_model_does_not_exists.upload_file.called
    assert s3_client_mock_model_does_not_exists.upload_file.call_args_list == [
        call(
            f"{tempfile.tempdir}/c2k/model_version.pt", "c2k", "models/model_version.pt"
        )
    ]


def test_upload_model_does_not_exist(
    s3_client_mock_model_does_not_exists, trainer_mock, os_mock_model_does_not_exists
):
    upload_model()
    assert not s3_client_mock_model_does_not_exists.upload_file.called
