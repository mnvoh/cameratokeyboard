# pylint: disable=missing-function-docstring

import hashlib
import os
import sys

import boto3

from cameratokeyboard.config import Config
from cameratokeyboard.logger import get_logger
from cameratokeyboard.model.train import Trainer

REGION = os.environ["AWS_REGION"]
BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]
RAW_DATASET_PATH = "raw_dataset"
REMOTE_MODELS_DIR = "models"

logger = get_logger()
s3_client = boto3.client("s3", region_name=REGION)


def get_next_version():
    logger.info("Calculating the checksum of the current dataset")

    if not os.path.exists(RAW_DATASET_PATH) or not os.listdir(RAW_DATASET_PATH):
        logger.info("Raw dataset not found.")
        return None

    checksums = []
    for file in os.listdir(RAW_DATASET_PATH):
        with open(os.path.join(RAW_DATASET_PATH, file), "rb") as f:
            checksums.append(hashlib.md5(f.read()).hexdigest())

    return hashlib.md5("".join(checksums).encode("utf-8")).hexdigest()


def version_already_exists(version: str) -> bool:
    logger.info("Checking for changes")

    objects = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME, Prefix=f"models/{version}.pt"
    )
    return objects and objects.get("KeyCount", 0) > 0


def train() -> str:
    logger.info("Training the model")

    config = Config()
    config.processing_device = "cpu"
    trainer = Trainer(config)

    results = trainer.run()

    return os.path.join(results.save_dir, "weights", "best.pt")


def upload_model(path: str, version: str):
    remote_model_name = f"{version}.pt"
    logger.info(
        "Uploading %s to s3://%s/%s/%s",
        path,
        BUCKET_NAME,
        REMOTE_MODELS_DIR,
        remote_model_name,
    )

    s3_client.upload_file(path, BUCKET_NAME, f"{REMOTE_MODELS_DIR}/{remote_model_name}")


def main():
    current_version = get_next_version()

    if not current_version:
        sys.exit(0)

    logger.info("Current data version: %s", current_version)
    exists = version_already_exists(current_version)

    if exists:
        logger.info(
            "Model version %s already exists. Skipping the pipeline.", current_version
        )
        return

    trained_model_path = train()
    upload_model(trained_model_path, current_version)


if __name__ == "__main__":
    main()
