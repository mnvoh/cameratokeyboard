# pylint: disable=missing-function-docstring
import os
from unittest.mock import patch

import platformdirs

from cameratokeyboard.config import Config


@patch("cameratokeyboard.config.os.path.getctime")
@patch("cameratokeyboard.config.os.listdir")
def test_config_defaults(listdir_mock, getctime_mock):
    model_name = "latest_model.pt"
    listdir_mock.return_value = [model_name]
    getctime_mock.return_value = 0

    config = Config()
    assert config.training_epochs == 20
    assert config.training_image_size == (640, 640)
    assert config.training_batch == -1
    assert config.raw_dataset_path == "raw_dataset"
    assert config.dataset_path == "datasets/c2k"
    assert config.split_paths == ("train", "test", "val")
    assert config.split_ratios == (0.7, 0.15, 0.15)
    assert config.image_extension == "jpg"
    assert config.iou == 0.5
    assert config.resolution == (1280, 720)
    assert config.app_fps == 30
    assert config.video_input_device == 0
    assert config.processing_device == "0"
    assert config.markers_min_confidence == 0.3
    assert config.fingers_min_confidence == 0.3
    assert config.thumbs_min_confidence == 0.3
    assert config.key_down_sensitivity == 0.75
    assert config.repeating_keys_delay == 0.5
    assert config.models_dir == os.path.join(
        platformdirs.user_data_dir(), "c2k", "models"
    )
    assert config.model_path == os.path.join(config.models_dir, model_name)


def test_config_builder():
    args = {
        "training_epochs": 10,
        "training_image_size": (320, 320),
        "training_batch": 16,
        "raw_dataset_path": "raw",
        "dataset_path": "datasets",
        "split_paths": ("a", "b", "c"),
        "split_ratios": (0.5, 0.25, 0.25),
        "image_extension": "png",
        "iou": 0.75,
        "model_path": "model.pt",
        "resolution": (1920, 1080),
        "app_fps": 60,
        "video_input_device": 1,
        "processing_device": "1",
        "markers_min_confidence": 0.5,
        "fingers_min_confidence": 0.5,
        "thumbs_min_confidence": 0.5,
        "key_down_sensitivity": 0.5,
        "repeating_keys_delay": 0.25,
    }
    config = Config.from_args(args)
    assert config.training_epochs == 10
    assert config.training_image_size == (320, 320)
    assert config.training_batch == 16
    assert config.raw_dataset_path == "raw"
    assert config.dataset_path == "datasets"
    assert config.split_paths == ("a", "b", "c")
    assert config.split_ratios == (0.5, 0.25, 0.25)
    assert config.image_extension == "png"
    assert config.iou == 0.75
    assert config.model_path == "model.pt"
    assert config.resolution == (1920, 1080)
    assert config.app_fps == 60
    assert config.video_input_device == 1
    assert config.processing_device == "1"
    assert config.markers_min_confidence == 0.5
    assert config.fingers_min_confidence == 0.5
    assert config.thumbs_min_confidence == 0.5
    assert config.key_down_sensitivity == 0.5
    assert config.repeating_keys_delay == 0.25
