import hashlib
import os
import shutil

from ultralytics import YOLO, settings

from cameratokeyboard.config import Config
from cameratokeyboard.model.partitioner import DataPartitioner
from cameratokeyboard.model.augmenter import ImageAugmenterStrategy


class Trainer:
    """
    The Trainer class is responsible for training the model using the provided configuration.

    Args:
        config (Config): The configuration object containing the necessary parameters for training.
        target_path (str): Copies the trained model to this location when done. If None,
            defaults to the `models_dir` config value.

    """

    def __init__(self, config: Config, target_path: str = None) -> None:
        self.config = config

        if target_path is None:
            self._target_path = config.models_dir
        else:
            self._target_path = target_path

        self.raw_dataset_path = config.raw_dataset_path
        self.dataset_path = config.dataset_path
        self.split_paths = config.split_paths

        settings.update({"datasets_dir": os.path.join(os.getcwd(), "datasets")})

    def run(self):
        """
        Runs the training process and copies the trained model to target_path when done.
        """
        self._parition_data()
        self._train()

    def calc_next_version(self):
        """
        Calculates the next version based on the checksums of the files in the raw dataset path.

        Returns:
            str: The MD5 hash of the concatenated checksums of all files in the raw dataset path.
                 Returns None if the raw dataset path is empty or does not exist.
        """
        if not os.path.exists(self.config.raw_dataset_path) or not os.listdir(
            self.config.raw_dataset_path
        ):
            return None

        checksums = []
        for file in os.listdir(self.config.raw_dataset_path):
            with open(os.path.join(self.config.raw_dataset_path, file), "rb") as f:
                checksums.append(hashlib.md5(f.read()).hexdigest())

        return hashlib.md5("".join(checksums).encode("utf-8")).hexdigest()

    def _parition_data(self):
        DataPartitioner(self.config).partition()
        ImageAugmenterStrategy(self.config).run()

    def _train(self):
        model = YOLO("yolov8n.yaml")

        results = model.train(
            data=os.path.join("cameratokeyboard", "c2kmodel.yml"),
            imgsz=self.config.training_image_size,
            epochs=self.config.training_epochs,
            batch=self.config.training_batch,
            device=self.config.processing_device,
        )

        version = self.calc_next_version()
        model_path = os.path.join(results.save_dir, "weights", "best.pt")
        os.makedirs(self._target_path, exist_ok=True)
        shutil.copyfile(model_path, os.path.join(self._target_path, f"{version}.pt"))
