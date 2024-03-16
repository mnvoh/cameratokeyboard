import logging
import os

import ultralytics

from cameratokeyboard.config import Config
from cameratokeyboard.core.detected_frame import DetectedFrame

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model.pt")


class Detector:
    """
    Class for detecting fingers in a frame.

    Args:
        config(Config): The application configuration.
    """

    def __init__(self, config: Config) -> None:
        logging.getLogger("ultralytics").setLevel(logging.ERROR)

        self._config = config
        self._model = ultralytics.YOLO(MODEL_PATH)
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
