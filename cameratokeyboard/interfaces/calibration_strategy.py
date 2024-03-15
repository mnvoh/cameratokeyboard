from abc import ABC, abstractmethod

from cameratokeyboard.types import Finger
from cameratokeyboard.core.detected_objects import DetectedFingersAndThumbs


class ICalibrationStrategy(ABC):
    """
    Strategy that detemines how calibration should be done.
    """

    @abstractmethod
    def __init__(self, history_size: int) -> None:
        """
        Initialize the Calibration object.

        Args:
            history_size (int): The size of the history to keep track of for the calibration.

        Returns:
            None
        """

    @property
    @abstractmethod
    def is_calibrated(self) -> bool:
        """
        Determines whether calibration has already been done or not.
        """

    @property
    @abstractmethod
    def calibration_progress(self) -> float:
        """
        Calibration progress as a float value between 0.0 and 1.0 while
        the operation is in progress.
        """

    @abstractmethod
    def append(self, fingers_and_thumbs: DetectedFingersAndThumbs) -> None:
        """
        Appends the given `FingersAndThumbs` object to the historical coordinates list.

        Args:
            fingers_and_thumbs (FingersAndThumbs): The object containing thumb and finger
            coordinates.

        Returns:
            None
        """

    @abstractmethod
    def get_calibration_for(self, finger: Finger) -> float:
        """
        Retrieves the calibration value for the specified finger.

        Args:
            finger (Finger): The finger for which to retrieve the calibration value.

        Returns:
            float: The calibration value for the specified finger.
        """

    @abstractmethod
    def calculate_calibration_value(
        self, fingers_and_thumbs: DetectedFingersAndThumbs, finger: Finger
    ) -> float:
        """
        Calculates the calibration value for one finger. This will be used both while
        calibrating and while trying to determine if a finger is down by comparing
        the calibration time and detection time values.
        """
