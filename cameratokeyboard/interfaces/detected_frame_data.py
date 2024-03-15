from abc import ABC, abstractmethod
from typing import List

from cameratokeyboard.types import FrameState, Point, RawImage


class IDetectedFrameData(ABC):
    """
    Represents a detected frame from a camera feed.

    Args:
        detection_results (ultralytics.engine.results.Results): The detection results for
            the frame.
        markers_min_confidence (float): The minimum confidence threshold for marker detection.
        fingers_min_confidence (float): The minimum confidence threshold for finger detection.
        thumbs_min_confidence (float): The minimum confidence threshold for thumb detection.
        sensitivity (float, optional): The sensitivity of the finger down detection.
            Defaults to 0.5.
    """

    @property
    @abstractmethod
    def current_frame(self) -> RawImage:
        """
        Returns the current frame.

        Returns:
            RawImage: The current frame.
        """

    @property
    @abstractmethod
    def state(self) -> FrameState:
        """
        Returns the state of the detected frame.

        Returns:
            str: The state of the detected frame. Values:
                - "initializing": No detection results yet.
                - "valid": All markers, fingers and thumbs are detected.
                - "missing_markers": One or more markers are missing.
                - "missing_fingers": One or more fingers are missing.
                - "missing_thumbs": One or more thumbs are missing.
        """

    @property
    @abstractmethod
    def marker_coordinates(self) -> List[Point]:
        """
        Returns the coordinates of all markers in the detected frame.

        If no markers are found, an empty list is returned.

        Returns:
            A list of Point objects representing the coordinates of the markers.
        """

    @property
    @abstractmethod
    def finger_coordinates(self) -> List[Point]:
        """
        Returns the coordinates of the fingers excluding thumbs.

        Returns:
            A list of Point objects representing the coordinates of the fingers.
        """

    @property
    @abstractmethod
    def thumb_coordinates(self) -> List[Point]:
        """
        Returns the coordinates of the thumbs detected in the frame.

        Returns:
            A list of Point objects representing the coordinates of the thumbs.
        """

    @property
    @abstractmethod
    def down_finger_coordinates(self) -> List[Point]:
        """
        Returns the coordinates of the fingers that are currently down.

        Returns:
            A list of Point objects representing the coordinates of the down fingers.
        """

    @property
    @abstractmethod
    def requires_calibration(self) -> bool:
        """
        Checks if calibration needs to be done or not.

        Returns:
            bool: True if calibration is required, False otherwise.
        """

    @property
    @abstractmethod
    def is_calibration_in_progress(self) -> bool:
        """
        Checks if calibration is currently in progress or not.

        Returns:
            bool: True if calibrating, False otherwise.
        """

    @property
    @abstractmethod
    def calibration_progress(self) -> float:
        """
        Returns the progress of the finger calibration.

        Returns:
            float: The calibration progress as a value between 0 and 1.
        """

    @property
    @abstractmethod
    def camera_angle(self) -> float:
        """
        Returns the Euler angle of the camera.
        """

    @abstractmethod
    def start_calibration(self, on_calibration_complete: callable) -> None:
        """
        Starts the calibration process.

        Args:
            callback (callable): A callback function to be called when the calibration
                is complete.
        """
