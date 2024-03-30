# pylint: disable=missing-function-docstring,too-many-instance-attributes
from dataclasses import dataclass
import os

import platformdirs

EXCLUDED_KEYS = ["command"]
PRIVATE_KEYS = ["model_path"]


@dataclass
class Config:
    """
    Application wide configuration.
    """

    training_epochs: int = 20
    training_image_size: tuple = (640, 640)
    training_batch: int = -1
    raw_dataset_path: str = "raw_dataset"
    dataset_path: str = "datasets/c2k"
    split_paths: list = ("train", "test", "val")
    split_ratios: list = (0.7, 0.15, 0.15)
    image_extension: str = "jpg"
    iou: float = 0.5

    resolution: tuple = (1280, 720)
    app_fps: int = 30
    video_input_device: int = 0
    processing_device: str = "0"

    markers_min_confidence: float = 0.3
    fingers_min_confidence: float = 0.3
    thumbs_min_confidence: float = 0.3
    key_down_sensitivity: float = 0.75

    keyboard_layout: str = "qwerty"
    repeating_keys_delay: float = 0.5

    remote_models_bucket_region: str = "eu-west-2"
    remote_models_bucket_name: str = "c2k"
    remote_models_prefix: str = "models/"
    models_dir: str = os.path.join(platformdirs.user_data_dir(), "c2k", "models")
    _model_path: str = None

    @property
    def model_path(self) -> str:
        if self._model_path:
            return self._model_path

        models = [x for x in os.listdir(self.models_dir) if x.endswith(".pt")]

        def sort_key(model_name):
            return os.path.getctime(os.path.join(self.models_dir, model_name))

        models = sorted(models, key=sort_key, reverse=True)
        try:
            return os.path.join(self.models_dir, models[0])
        except IndexError:
            return None

    @model_path.setter
    def model_path(self, value):
        self._model_path = value

    @classmethod
    def from_args(cls, args: dict) -> "Config":
        """
        Builds a Config object from the given arguments.
        """
        processed_args = {k: v for k, v in args.items() if k not in EXCLUDED_KEYS}
        for private_key in PRIVATE_KEYS:
            if private_key in processed_args:
                processed_args[f"_{private_key}"] = processed_args[private_key]
                del processed_args[private_key]

        return cls(**processed_args)
