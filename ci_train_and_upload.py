# pylint: disable=missing-function-docstring

import os
import subprocess

import boto3

from cameratokeyboard.config import Config
from cameratokeyboard.model.train import Trainer

REGION = os.environ["AWS_REGION"]
BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]
RUNS_DIR = os.path.join("runs", "detect")
REMOTE_MODELS_DIR = "models"
REMOTE_MODEL_NAME_PREFIX = "c2k_model"
VERSION_LENGTH = 7

s3_client = boto3.client("s3", region_name=REGION)


def are_there_new_data():
    diff_output = subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD~1..HEAD"]
    )
    changed_files = diff_output.decode("utf-8").splitlines()

    for filename in changed_files:
        if filename.startswith("raw_dataset"):
            return True

    return False


def get_next_version():
    objects = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="models/c2k_model_")
    models = [x["Key"] for x in objects["Contents"]]
    models = [x.split(".")[0] for x in models]
    models = [x.split("/")[-1] for x in models]
    model_versions = [int(x.split("_")[-1]) for x in models]

    next_version = sorted(model_versions)[-1] + 1

    return f"{next_version:07d}"


def train() -> str:
    config = Config()
    config.processing_device = "cpu"
    trainer = Trainer(config)

    trainer.run()

    def sort_key(p):
        os.path.getctime(os.path.join(RUNS_DIR, p))

    last_created_dir = max(os.listdir(RUNS_DIR), key=sort_key)

    return os.path.join(RUNS_DIR, last_created_dir, "weights", "best.pt")


def upload_model(path: str):
    existing_objects = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME, Prefix=f"{REMOTE_MODELS_DIR}/{REMOTE_MODEL_NAME_PREFIX}"
    )
    try:
        existing_model_names = [
            x["Key"].split(".")[0] for x in existing_objects["Contents"]
        ]
        last_model_version = sorted(
            [x.split("_")[-1] for x in existing_model_names], reverse=True
        )[0]
    except (KeyError, StopIteration):
        last_model_version = 0

    next_version = int(last_model_version) + 1
    next_model_name = f"{REMOTE_MODEL_NAME_PREFIX}_{next_version:0{VERSION_LENGTH}d}.pt"

    s3_client.upload_file(path, BUCKET_NAME, f"{REMOTE_MODELS_DIR}/{next_model_name}")


def main():
    if not are_there_new_data():
        return

    trained_model_path = train()
    upload_model(trained_model_path)


if __name__ == "__main__":
    main()
