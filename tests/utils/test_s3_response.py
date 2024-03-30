# pylint: disable=missing-function-docstring
from datetime import datetime
from cameratokeyboard.utils.s3_response import S3Response
from cameratokeyboard.types import S3ContentsItem

from tests.fixtures import s3_objects_response


def test_get_objects():
    parsed_response = S3Response(s3_objects_response)

    print(parsed_response.get_objects())
    assert parsed_response.get_objects() == [
        S3ContentsItem(
            key="20240323-131619.txt",
            last_modified=datetime(2024, 3, 23, 13, 16, 21),
        ),
        S3ContentsItem(key="models/", last_modified=datetime(2024, 3, 23, 13, 59, 13)),
        S3ContentsItem(
            key="models/72cf8b59b60538ba46cdda79bd38afaa.pt",
            last_modified=datetime(2024, 3, 25, 1, 7, 33),
        ),
        S3ContentsItem(
            key="models/daab7a39b2f4cea3e435dc12e89cbe9d.pt",
            last_modified=datetime(2024, 3, 24, 23, 20, 26),
        ),
        S3ContentsItem(key="test.txt", last_modified=datetime(2024, 3, 23, 11, 38, 1)),
        S3ContentsItem(key="test2.txt", last_modified=datetime(2024, 3, 23, 11, 52, 7)),
    ]
