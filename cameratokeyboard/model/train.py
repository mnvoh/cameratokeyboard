# DEPRECATED: This and all related files will be removed once we move to the new data pipeline
# pylint: skip-file

import os
import shutil

from ultralytics import YOLO, settings

from cameratokeyboard.config import Config
from cameratokeyboard.model.partitioner import DataPartitioner
from cameratokeyboard.model.augmenter import ImageAugmenterStrategy


class Trainer:
    def __init__(self, config: Config) -> None:
        self.config = config

        self.raw_dataset_path = config.raw_dataset_path
        self.dataset_path = config.dataset_path
        self.split_paths = config.split_paths

        settings.update({"datasets_dir": os.path.join(os.getcwd(), "datasets")})

    def run(self):
        self._parition_data()
        return self._train()

    def _are_training_data_up_to_date(self):
        if not os.path.exists(self.dataset_path):
            return False

        if any(
            not os.path.exists(os.path.join(self.dataset_path, "images", split_name))
            for split_name in self.split_paths
        ):
            return False

        raw_files = set(os.listdir(self.raw_dataset_path))
        files = set(
            os.listdir(os.path.join(self.dataset_path, "images", "train"))
            + os.listdir(os.path.join(self.dataset_path, "images", "test"))
            + os.listdir(os.path.join(self.dataset_path, "images", "val"))
        )
        return raw_files == files

    def _parition_data(self):
        if self._are_training_data_up_to_date():
            return

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

        model_path = os.path.join(results.save_dir, "weights", "best.pt")
        target_model_path = os.path.join("cameratokeyboard", "model.pt")
        shutil.copyfile(model_path, target_model_path)

        return results
