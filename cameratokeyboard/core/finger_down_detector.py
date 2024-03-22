from cameratokeyboard.core.detected_objects import DetectedFingersAndThumbs
from cameratokeyboard.types import Finger, Fingers
from cameratokeyboard.interfaces import ICalibrationStrategy


class FingerDownDetector:
    """
    Detects whether a finger is down or not based on the given finger coordinates and the
    calibration values.
    """

    def __init__(self, calibration: ICalibrationStrategy, sensitivity: float) -> None:
        self._calibration = calibration
        self._sensitivity = sensitivity

    def is_finger_down(
        self, fingers_and_thumbs: DetectedFingersAndThumbs, finger: Finger
    ) -> bool:
        """
        Determines if a finger is considered to be down based on the given finger
        coordinates and calibration values.

        Args:
            fingers_and_thumbs (FingersAndThumbs): The fingers and thumbs coordinates.
            finger (Finger): The finger to check.

        Returns:
            bool: True if the finger is considered to be down, False otherwise.
        """
        coordinates = fingers_and_thumbs[finger]
        if not coordinates:
            return False

        velocity_y = coordinates.velocity_y(window=3)
        if velocity_y > 5.0:  # TODO: Unhardcode this value
            return False

        calibration_value = self._calibration.get_calibration_for(finger)
        current_value = self._calibration.calculate_calibration_value(
            fingers_and_thumbs, finger
        )

        if current_value is None or calibration_value is None:
            return False

        delta = current_value - calibration_value

        threshold = (
            fingers_and_thumbs.average_finger_height * 2 * (1 - self._sensitivity)
        )
        other_coordinates = [
            fingers_and_thumbs[f] for f in Fingers.values() if f != finger
        ]
        lower_than_all_other = all(
            c.y < coordinates.y for c in other_coordinates if c is not None
        )

        return lower_than_all_other and delta > threshold
