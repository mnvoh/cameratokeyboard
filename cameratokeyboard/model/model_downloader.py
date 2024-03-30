import os

import requests

from cameratokeyboard.config import Config
from cameratokeyboard.logger import get_logger
from cameratokeyboard.utils.s3_response import S3Response

logger = get_logger()
REQUESTS_TIMEOUT = 10.0


class ModelDownloader:
    """
    Checks for model updates and downloads the latest version if available.
    """

    def __init__(self, config: Config):
        self.config = config

    def run(self) -> None:
        """
        Runs the checker and downloader
        """
        logger.info("Checking for new models...")

        os.makedirs(self.config.models_dir, exist_ok=True)

        latest_version_filename = self._get_latest_version_filename()

        if not latest_version_filename:
            logger.warning("No remote models found!")
            return

        if self._is_latest_version_downloaded(latest_version_filename):
            logger.info("Latest model already downloaded.")
            return

        logger.info("Found a new model version: %s", latest_version_filename)

        downloaded_path = self._download_model(latest_version_filename)

        if downloaded_path:
            logger.info("Model downloaded to %s", downloaded_path)

    @property
    def local_path_to_latest_model(self):
        """
        Returns the local path to the latest model
        """
        latest_verison_filename = self._get_latest_version_filename()
        return os.path.join(self.config.models_dir, latest_verison_filename)

    @property
    def _bucket_url(self):
        bucket = self.config.remote_models_bucket_name
        region = self.config.remote_models_bucket_region
        return f"https://{bucket}.s3.{region}.amazonaws.com"

    def _get_latest_version_filename(self) -> str:
        content = requests.get(
            self._bucket_url, timeout=REQUESTS_TIMEOUT
        ).content.decode()
        parsed_content = [
            x
            for x in S3Response(content).get_objects()
            if x.key.startswith(self.config.remote_models_prefix)
        ]
        sorted_content = sorted(parsed_content, key=lambda x: x.last_modified)
        return sorted_content[-1].key.replace(self.config.remote_models_prefix, "")

    def _is_latest_version_downloaded(self, latest_version: str) -> bool:
        return latest_version in os.listdir(self.config.models_dir)

    def _download_model(self, version: str) -> str:
        url = f"{self._bucket_url}/{self.config.remote_models_prefix}{version}"
        model_path = os.path.join(self.config.models_dir, version)

        response = requests.get(url, timeout=REQUESTS_TIMEOUT, stream=True)

        if response.status_code == 200:
            with open(model_path, "wb") as f:
                f.write(response.content)

            return model_path

        logger.error(
            "Could not download model %s: [%d] %s",
            version,
            response.status_code,
            response.content,
        )
        return None
