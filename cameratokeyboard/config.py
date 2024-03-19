from dataclasses import dataclass
import os

EXCLUDED_KEYS = ["command"]


@dataclass
class Config:  # pylint: disable=too-many-instance-attributes
    """
    Application wide configuration.
    """

    training_epochs: int = 40
    training_image_size: tuple = (640, 640)
    training_batch: int = -1
    raw_dataset_path: str = "raw_dataset"
    dataset_path: str = "../datasets/c2k"
    split_paths: list = ("train", "test", "val")
    split_ratios: list = (0.7, 0.15, 0.15)
    image_extension: str = "jpg"
    iou: float = 0.5

    model_path: str = os.path.join("cameratokeyboard", "model.pt")

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

    @classmethod
    def from_args(cls, args: dict) -> "Config":
        """
        Builds a Config object from the given arguments.
        """
        return cls(**{k: v for k, v in args.items() if k not in EXCLUDED_KEYS})
