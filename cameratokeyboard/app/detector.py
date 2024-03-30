import logging

import ultralytics

from cameratokeyboard.config import Config
from cameratokeyboard.core.detected_frame import DetectedFrame
from cameratokeyboard.model.model_downloader import ModelDownloader


class Detector:
    """
    Class for detecting fingers in a frame.

    Args:
        config(Config): The application configuration.
    """

    def __init__(self, config: Config) -> None:
        logging.getLogger("ultralytics").setLevel(logging.ERROR)
        model_path = ModelDownloader(config).local_path_to_latest_model

        self._config = config
        self._model = ultralytics.YOLO(model_path)
        self._device = config.processing_device
        self._iou = config.iou
        self._detected_frame = None

    def detect(self, frame):
        """
        Detects objects in the given frame.

        Args:
            frame: The frame to detect objects in.

        Returns:
            DetectedFrame: An object representing the detected objects in the frame.
        """
        try:
            device = int(self._device)
        except ValueError:
            device = self._device

        results = self._model(frame, device, iou=self._iou)[0]

        if not self._detected_frame:
            self._detected_frame = DetectedFrame(results, config=self._config)
        else:
            self._detected_frame.update(results)

        return self._detected_frame
