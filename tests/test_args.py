# pylint: disable=missing-function-docstring


from cameratokeyboard.args import parse_args


def test_parse_args():
    argv = [
        "-e",
        "50",
        "-ts",
        "800",
        "600",
        "-b",
        "32",
        "-rp",
        "custom_dataset",
        "-dp",
        "../datasets/custom",
        "-sp",
        "train",
        "test",
        "val",
        "-sr",
        "0.6",
        "0.2",
        "0.2",
        "-ie",
        "png",
        "-p",
        "custom_model.pt",
        "-r",
        "1920",
        "1080",
        "-f",
        "60",
        "-i",
        "1",
        "-d",
        "1",
        "-mc",
        "0.5",
        "-fc",
        "0.5",
        "-tc",
        "0.5",
        "-s",
        "0.8",
        "-rd",
        "0.5",
    ]
    expected_args = {
        "command": None,
        "training_epochs": 50,
        "training_image_size": [800, 600],
        "training_batch": 32,
        "raw_dataset_path": "custom_dataset",
        "dataset_path": "../datasets/custom",
        "split_paths": ["train", "test", "val"],
        "split_ratios": [0.6, 0.2, 0.2],
        "image_extension": "png",
        "model_path": "custom_model.pt",
        "resolution": [1920, 1080],
        "app_fps": 60,
        "video_input_device": 1,
        "processing_device": "1",
        "markers_min_confidence": 0.5,
        "fingers_min_confidence": 0.5,
        "thumbs_min_confidence": 0.5,
        "key_down_sensitivity": 0.8,
        "keyboard_layout": "qwerty",
        "repeating_keys_delay": 0.5,
    }

    args = parse_args(argv)

    assert args == expected_args
