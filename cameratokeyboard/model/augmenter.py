# DEPRECATED: This and all related files will be removed once we move to the new data pipeline
# pylint: skip-file

from ast import literal_eval
import os
from typing import List

import cv2
from tqdm import tqdm

from cameratokeyboard.config import Config
from cameratokeyboard.model import augmenters, ImageAugmenter
from cameratokeyboard.logger import getLogger


LOGGER = getLogger()
STRATEGIES = [
    "Scale:0.5,1.2",
    "Rotation:-45,45",
    "VerticalFlip",
    "HorizontalFlip",
    "Blur:2.5,6.0",
    "Shear:-30,30",
    "Perspective:0.1,0.2",
]


class ImageAugmenterStrategy:
    def __init__(self, config: Config) -> None:
        self.augmentation_strategies = []

        self._resolve_strategies()
        train_path = config.split_paths[0]
        self.images_path = os.path.join(config.dataset_path, "images", train_path)
        self.labels_path = os.path.join(config.dataset_path, "labels", train_path)
        self.files = [f for f in os.listdir(self.images_path)]

    def run(self) -> None:
        for strategy in self.augmentation_strategies:
            self._run_strategy(strategy)

    def _resolve_strategies(self) -> None:
        for augmentation_strategy in STRATEGIES:
            augmenters_in_strategy = []

            for augmenter in augmentation_strategy.split(";"):
                augmenter_name, args = (
                    augmenter.split(":") if ":" in augmenter else (augmenter, "")
                )
                args = args.split(",")
                augmenter_class = getattr(augmenters, f"{augmenter_name}Augmenter")

                augmenters_in_strategy.append(
                    augmenter_class(*[literal_eval(arg) for arg in args if arg != ""])
                )

            self.augmentation_strategies.append(augmenters_in_strategy)

    def _run_strategy(self, strategy: List[ImageAugmenter]) -> None:

        LOGGER.info("Running augmentation strategy %s", strategy)

        index = len(os.listdir(self.images_path))

        for file in tqdm(sorted(self.files)):

            filename, ext = os.path.splitext(os.path.basename(file))

            image_path = os.path.join(self.images_path, file)
            label_path = os.path.join(self.labels_path, f"{filename}.txt")

            image = cv2.imread(image_path)
            with open(label_path, "r", encoding="utf-8") as lf:
                bounding_boxes = lf.read()

            for augmenter in strategy:
                image, new_coordinates = augmenter.apply(image, bounding_boxes)

            out_name = f"{index:05d}"

            target_image_path = os.path.join(self.images_path, f"{out_name}{ext}")
            target_label_path = os.path.join(self.labels_path, f"{out_name}.txt")

            cv2.imwrite(target_image_path, image)

            with open(target_label_path, "a", encoding="utf-8") as lf:
                lf.write(f"{new_coordinates}\n")

            index += 1
