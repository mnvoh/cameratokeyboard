import os

from ultralytics import YOLO, settings

from cameratokeyboard.config import Config
from cameratokeyboard.model.partitioner import DataPartitioner
from cameratokeyboard.model.augmenter import ImageAugmenterStrategy


class Trainer:
    """
    The Trainer class is responsible for training the model using the provided configuration.

    Args:
        config (Config): The configuration object containing the necessary parameters for training.

    """

    def __init__(self, config: Config) -> None:
        self.config = config

        self.raw_dataset_path = config.raw_dataset_path
        self.dataset_path = config.dataset_path
        self.split_paths = config.split_paths

        settings.update({"datasets_dir": os.path.join(os.getcwd(), "datasets")})

    def run(self):
        """
        Runs the training process.

        Returns:
            results (ultralytics.utils.metrics.DetMetrics): A dictionary containing the
                training results.

        """
        self._parition_data()
        return self._train()

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

        return results
