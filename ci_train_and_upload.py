# pylint: disable=missing-function-docstring

import hashlib
import os
import shutil
import sys
import tempfile

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


def train():
    version = get_next_version()

    if not version:
        return

    logger.info("Current data version: %s", version)

    if version_already_exists(version):
        logger.info("Model version %s already exists. Skipping the pipeline.", version)
        return

    logger.info("Training the model")

    config = Config()
    config.processing_device = "cpu"
    trainer = Trainer(config)

    results = trainer.run()

    model_path = os.path.join(results.save_dir, "weights", "best.pt")
    dest_path = os.path.join(tempfile.tempdir, "c2k")
    os.makedirs(dest_path, exist_ok=True)
    shutil.copyfile(model_path, os.path.join(dest_path, f"{version}.pt"))

    logger.info("Saved trained model to %s/%s.pt", dest_path, version)


def upload_model():
    version = get_next_version()
    model_name = f"{version}.pt"
    model_path = os.path.join(tempfile.tempdir, "c2k", model_name)
    logger.info(
        "Uploading %s to s3://%s/%s/%s",
        model_path,
        BUCKET_NAME,
        REMOTE_MODELS_DIR,
        model_name,
    )

    s3_client.upload_file(model_path, BUCKET_NAME, f"{REMOTE_MODELS_DIR}/{model_name}")


def main():
    if sys.argv[1] == "train":
        train()
    elif sys.argv[1] == "upload":
        upload_model()


if __name__ == "__main__":
    main()
