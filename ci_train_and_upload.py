# pylint: disable=missing-function-docstring

import os
import sys
import tempfile

import boto3

from cameratokeyboard.config import Config
from cameratokeyboard.logger import get_logger
from cameratokeyboard.model.train import Trainer

logger = get_logger()
config = Config(processing_device="cpu")
s3_client = boto3.client("s3", region_name=config.remote_models_bucket_region)

MODEL_TARGET_DIR = os.path.join(tempfile.tempdir, "c2k")

trainer = Trainer(config, target_path=MODEL_TARGET_DIR)


def version_already_exists(version: str) -> bool:
    logger.info("Checking for changes")

    objects = s3_client.list_objects_v2(
        Bucket=config.remote_models_bucket_name, Prefix=f"models/{version}.pt"
    )
    return objects and objects.get("KeyCount", 0) > 0


def train():
    version = trainer.calc_next_version()

    if not version:
        return

    logger.info("Current data version: %s", version)

    if version_already_exists(version):
        logger.info("Model version %s already exists. Skipping the pipeline.", version)
        return

    logger.info("Training the model")

    trainer.run()

    logger.info("Saved trained model to %s/%s.pt", MODEL_TARGET_DIR, version)


def upload_model():
    version = trainer.calc_next_version()
    model_name = f"{version}.pt"
    model_path = os.path.join(MODEL_TARGET_DIR, model_name)

    if not os.path.exists(model_path):
        return

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
