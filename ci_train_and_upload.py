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

logger = get_logger()
config = Config()
s3_client = boto3.client("s3", region_name=config.remote_models_bucket_region)


def get_next_version():
    logger.info("Calculating the checksum of the current dataset")

    if not os.path.exists(config.raw_dataset_path) or not os.listdir(
        config.raw_dataset_path
    ):
        logger.info("Raw dataset not found.")
        return None

    checksums = []
    for file in os.listdir(config.raw_dataset_path):
        with open(os.path.join(config.raw_dataset_path, file), "rb") as f:
            checksums.append(hashlib.md5(f.read()).hexdigest())

    return hashlib.md5("".join(checksums).encode("utf-8")).hexdigest()


def version_already_exists(version: str) -> bool:
    logger.info("Checking for changes")

    objects = s3_client.list_objects_v2(
        Bucket=config.remote_models_bucket_name, Prefix=f"models/{version}.pt"
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
        "Uploading %s to s3://%s/%s%s",
        model_path,
        config.remote_models_bucket_name,
        config.remote_models_prefix,
        model_name,
    )

    s3_client.upload_file(
        model_path,
        config.remote_models_bucket_name,
        f"{config.remote_models_prefix}{model_name}",
    )


def main():
    if sys.argv[1] == "train":
        train()
    elif sys.argv[1] == "upload":
        upload_model()


if __name__ == "__main__":
    main()
