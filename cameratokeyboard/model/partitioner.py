# DEPRECATED: This and all related files will be removed once we move to the new data pipeline

import os
from random import shuffle
import shutil

from cameratokeyboard.config import Config
from cameratokeyboard.logger import getLogger

LOGGER = getLogger()


class DataPartitioner:
    """
    A class that distributes files into train, test, and validation sets.

    Args:
        config: The application configuration.

    Methods:
        distribute(): Distributes the files into train, test, and validation sets.

    Raises:
        ValueError: If no files are found or if files without labels are found.
    """

    def __init__(self, config: Config):
        self._raw_dataset_path = config.raw_dataset_path
        self._dataset_path = config.dataset_path
        self._split_paths = config.split_paths
        self._split_ratios = dict(zip(config.split_paths, config.split_ratios))
        self._image_extension = config.image_extension

        self._files_list = []
        self._split_lists = {}

    def partition(self) -> None:
        """
        Partitions the files into train, test, and validation sets.
        """
        LOGGER.info("Partitioning files...")

        self._read_files_list()
        self._verify_integrity()
        self._delete_existing_data()

        self._partition_files()

    def _read_files_list(self) -> None:
        LOGGER.info("Reading files list.")

        self._files_list = set(
            [f.split(".")[0] for f in os.listdir(self._raw_dataset_path)]
        )
        shuffle(self._files_list)

    def _verify_integrity(self) -> None:
        LOGGER.info("Verifying integrity of files.")

        if len(self._files_list) == 0:
            raise ValueError(
                f"No files found in {os.getcwd()}/{self._raw_dataset_path}."
            )

        files_without_labels = []
        for filename in self._files_list:
            labels_path = os.path.join(self._raw_dataset_path, f"{filename}.txt")
            if not os.path.exists(labels_path):
                files_without_labels.append(filename)

        if files_without_labels:
            raise ValueError(f"Files without labels found: {files_without_labels}.")

    def _delete_existing_data(self) -> None:
        if not os.path.exists(self._dataset_path):
            return

        LOGGER.info("Deleting existing data.")
        shutil.rmtree(self._dataset_path)

    def _partition_files(self) -> None:
        LOGGER.info("Partitioning files")

        start_index = 0
        for split_name in self._split_paths:
            ratio = self._split_ratios[split_name]
            end_index = start_index + int(len(self._files_list) * ratio)

            for index, filename in enumerate(self._files_list[start_index:end_index]):
                image_path = os.path.join(
                    self._raw_dataset_path, f"{filename}.{self._image_extension}"
                )
                label_path = os.path.join(self._raw_dataset_path, f"{filename}.txt")
                target_name = f"{start_index + index:05d}"
                target_image_path = os.path.join(
                    self._dataset_path,
                    "images",
                    split_name,
                    f"{target_name}.{self._image_extension}",
                )
                target_label_path = os.path.join(
                    self._dataset_path, "labels", split_name, f"{target_name}.txt"
                )
                shutil.copyfile(image_path, target_image_path)
                shutil.copyfile(label_path, target_label_path)

            start_index = end_index
