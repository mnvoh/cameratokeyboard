import argparse
import os

from cameratokeyboard.model.train import Trainer

CMD_TRAIN = "train"

COMMANDS = {
    CMD_TRAIN: Trainer,
}


def parse_args(argv) -> dict:
    parser = argparse.ArgumentParser(description="Camera To Keyboard")

    parser.add_argument(
        "command",
        choices=COMMANDS.keys(),
        nargs="?",
        help="Specify the command to execute. Omit to run the main app.",
    )

    parser.add_argument(
        "-e",
        "--training_epochs",
        type=int,
        default=40,
        help="Specify the number of training epochs. Default: 40",
    )

    parser.add_argument(
        "-ts",
        "--training_image_size",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=(640, 640),
        help="The dimensions of the training images. Default: 640 640",
    )

    parser.add_argument(
        "-b",
        "--training_batch",
        type=int,
        default=-1,
        help="The batch size for training. Default: -1 (automatic)",
    )

    parser.add_argument(
        "-rp",
        "--raw_dataset_path",
        type=str,
        default="raw_dataset",
        help="The path to the raw dataset. Default: raw_dataset",
    )

    parser.add_argument(
        "-dp",
        "--dataset_path",
        type=str,
        default="../datasets/c2k",
        help="The path to the partitioned and augmented dataset. Default: ../datasets/c2k",
    )

    parser.add_argument(
        "-sp",
        "--split_paths",
        type=str,
        nargs=3,
        default=("train", "test", "val"),
        metavar=("TRAIN", "TEST", "VAL"),
        help="The paths to the train, test and validation datasets. Default: train test val",
    )

    parser.add_argument(
        "-sr",
        "--split_ratios",
        type=float,
        nargs=3,
        default=(0.7, 0.15, 0.15),
        metavar=("TRAIN", "TEST", "VAL"),
        help="The ratios for the train, test and validation datasets. Default: 0.7 0.15 0.15",
    )

    parser.add_argument(
        "-ie",
        "--image_extension",
        type=str,
        default="jpg",
        help="The extension of the images in the dataset. Default: jpg",
    )

    parser.add_argument(
        "-p",
        "--model_path",
        type=str,
        default=os.path.join("cameratokeyboard", "model.pt"),
        help="The path to the model. Default: cameratokeyboard/model.pt",
    )

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        nargs=2,
        default=(1280, 720),
        metavar=("WIDTH", "HEIGHT"),
        help="The resolution of the images taken from the camera. Default: 1280 720",
    )

    parser.add_argument(
        "-f",
        "--app_fps",
        type=int,
        default=30,
        help="The refresh rate of the app. Default: 30",
    )

    parser.add_argument(
        "-i",
        "--video_input_device",
        type=int,
        default=0,
        help="The device number of the input camera. Default: 0",
    )

    parser.add_argument(
        "-d",
        "--processing_device",
        type=str,
        default="0",
        help=(
            "The device index to use for training and inference or enter 'cpu' to use "
            "CPU. Default: 0."
        ),
    )

    parser.add_argument(
        "-mc",
        "--markers_min_confidence",
        type=float,
        default=0.3,
        help="The minimum confidence for the markers. Default: 0.3",
    )

    parser.add_argument(
        "-fc",
        "--fingers_min_confidence",
        type=float,
        default=0.3,
        help="The minimum confidence for the fingers. Default: 0.3",
    )

    parser.add_argument(
        "-tc",
        "--thumbs_min_confidence",
        type=float,
        default=0.3,
        help="The minimum confidence for the thumbs. Default: 0.3",
    )

    parser.add_argument(
        "-s",
        "--key_down_sensitivity",
        type=float,
        default=0.75,
        help="The sensitivity for the key down action. Default: 0.75",
    )

    parser.add_argument(
        "-rd",
        "--repeating_keys_delay",
        type=float,
        default=0.4,
        help="The delay for repeating keys. Default: 0.4",
    )

    args = parser.parse_args(argv)

    args_dict = args.__dict__
    if args_dict.get("command", None) is not None:
        args_dict["command"] = COMMANDS[args_dict["command"]]

    return args_dict
