import os

import boto3

from cameratokeyboard.logger import get_logger

logger = get_logger()


class ModelDownloader:
    """
    Checks for model updates and downloads the latest version if available.
    """

    def __init__(self, config):
        self.client = boto3.client("s3")
        self.config = config

    def run(self) -> None:
        """
        Runs the checker and downloader
        """
        logger.info("Checking for new models...")

        os.makedirs(self.config.models_dir, exist_ok=True)

        latest_version = self._get_latest_version()

        if not latest_version:
            logger.warning("No remote models found!")
            return

        if self._is_latest_version_downloaded(latest_version):
            logger.info("Latest model already downloaded.")
            return

        logger.info("Found a new model version: %s", latest_version)

        downloaded_path = self._download_model(latest_version)

        logger.info("Model downloaded to %s", downloaded_path)

    def _get_latest_version(self):
        """
        Retrieves the latest available model version
        """
        objects_response = self.client.list_objects_v2(
            Bucket=self.config.remote_models_bucket_name,
            Prefix=self.config.remote_models_prefix,
        )
        try:
            latest_object_response = sorted(
                [
                    x
                    for x in objects_response["Contents"]
                    if x["Key"] != self.config.remote_models_prefix
                ],
                key=lambda x: x["LastModified"],
            )[-1]
            return latest_object_response["Key"].split("/")[-1]
        except (KeyError, IndexError):
            return None

    def _is_latest_version_downloaded(self, latest_version: str) -> bool:
        """
        Checks whether the latest model has already been downloaded
        """
        return latest_version in os.listdir(self.config.models_dir)

    def _download_model(self, version: str) -> str:
        """
        Downloads the model
        """
        bucket = self.config.remote_models_bucket_name
        prefix = self.config.remote_models_prefix
        model_path = f"{self.config.models_dir}/{version}"

        self.client.download_file(bucket, f"{prefix}{version}", model_path)

        return model_path
