from cameratokeyboard.core.detected_objects import DetectedFingersAndThumbs
from cameratokeyboard.interfaces import ICalibrationStrategy
from cameratokeyboard.types import Finger, Fingers


class CalibrationStrategy(ICalibrationStrategy):
    """
    Base class for calibration strategies.
    """

    def __init__(self, history_size: int) -> None:
        self.history_size = history_size
        self._historical_coordinates = []
        self._cache = {}

    @property
    def is_calibrated(self) -> bool:
        return bool(self._cache)

    @property
    def calibration_progress(self) -> float:
        if self._cache:
            return 1.0
        return min(len(self._historical_coordinates) / self.history_size, 1.0)

    def append(self, fingers_and_thumbs: DetectedFingersAndThumbs) -> None:
        if (
            len(fingers_and_thumbs.thumb_coordinates) < 2
            or len(fingers_and_thumbs.finger_coordinates) < 8
        ):
            return

        self._historical_coordinates.append(fingers_and_thumbs)
        self._historical_coordinates = self._historical_coordinates[
            -self.history_size :
        ]
        self._cache = {}

        if len(self._historical_coordinates) >= self.history_size:
            self._calculate_calibration_values()
            self._historical_coordinates = []

    def get_calibration_for(self, finger: Finger) -> float:
        """
        Retrieves the calibration value for the specified finger.

        Args:
            finger (Finger): The finger for which to retrieve the calibration value.

        Returns:
            float: The calibration value for the specified finger.
        """
        return self._cache_get(finger)

    def _cache_get(self, finger: Finger) -> float:
        if not self._cache and len(self._historical_coordinates) >= self.history_size:
            self._calculate_calibration_values()

        # TODO: To be silent or not to be? That is the question.
        return self._cache.get(finger, 0)


class AdjacentNeighborCalibrationStrategy(CalibrationStrategy):
    """
    Calculates a calibration value for each finger based on the distance to an
    specific adjacent neighbor finger.
    """

    _adjacent_neighbors_for_calibration_map = {
        Fingers.LEFT_PINKY: Fingers.LEFT_RING,
        Fingers.LEFT_RING: Fingers.LEFT_MIDDLE,
        Fingers.LEFT_MIDDLE: Fingers.LEFT_INDEX,
        Fingers.LEFT_INDEX: Fingers.LEFT_MIDDLE,
        Fingers.LEFT_THUMB: Fingers.LEFT_INDEX,
        Fingers.RIGHT_THUMB: Fingers.RIGHT_INDEX,
        Fingers.RIGHT_INDEX: Fingers.RIGHT_MIDDLE,
        Fingers.RIGHT_MIDDLE: Fingers.RIGHT_INDEX,
        Fingers.RIGHT_RING: Fingers.RIGHT_MIDDLE,
        Fingers.RIGHT_PINKY: Fingers.RIGHT_RING,
    }

    def calculate_calibration_value(
        self, fingers_and_thumbs: DetectedFingersAndThumbs, finger: Finger
    ) -> float:
        finger_coordinates = fingers_and_thumbs[finger]
        neighbor = self._adjacent_neighbors_for_calibration_map.get(finger)
        neighbor_coordinates = fingers_and_thumbs[neighbor]

        if not finger_coordinates or not neighbor_coordinates:
            return None

        return finger_coordinates.y - neighbor_coordinates.y

    def _calculate_calibration_values(self) -> None:
        if not self._historical_coordinates:
            return

        distance_sums = {finger: [] for finger in Fingers.values()}

        for fingers_and_thumbs in self._historical_coordinates:
            for finger in Fingers.values():
                calibration_value = self.calculate_calibration_value(
                    fingers_and_thumbs, finger
                )
                if calibration_value is not None:
                    distance_sums[finger].append(calibration_value)

        for finger, distances in distance_sums.items():
            self._cache[finger] = sum(distances) / len(distances)


class HandbaselineCalibrationStrategy(CalibrationStrategy):
    """
    DEPRECATED:
    For the calculation, first a baseline or a reference point for the whole hand is
    calculated on the Y axis. Then the average distance from the baseline for each
    finger is calculated and stored as a calibration value. This value is then used to
    calculate the distance from the baseline for each finger in the future and detemines
    if the finger is down or not.
    """

    def calculate_calibration_value(
        self, fingers_and_thumbs: DetectedFingersAndThumbs, finger: Finger
    ) -> float:
        baseline = self._get_baseline_for(fingers_and_thumbs)

        finger_coordinates = fingers_and_thumbs[finger]

        if not finger_coordinates:
            return None

        return finger_coordinates.y - baseline

    @classmethod
    def _get_baseline_for(
        cls, fingers_and_thumbs: DetectedFingersAndThumbs, finger: Finger = None
    ) -> float:
        """
        Calculates a baseline value for the given fingers and thumbs using their
        average Y positions.

        Args:
            fingers_and_thumbs (FingersAndThumbs): An object containing the coordinates
            of fingers and thumbs.
            finger (Finger, optional): If provided, this finger and its immediate
            neighbors will be excluded from the calculation.


        Returns:
            float: The calculated baseline value.

        """
        excluded_fingers = []
        if finger:
            excluded_fingers = [
                x
                for x in [
                    Fingers.by_index(finger.index - 1),
                    finger,
                    Fingers.by_index(finger.index + 1),
                ]
                if x
            ]
        y_positions = [
            f.y
            for f in fingers_and_thumbs.finger_coordinates
            if f and f not in excluded_fingers
        ]
        y_positions += [
            t.y
            for t in fingers_and_thumbs.thumb_coordinates
            if t and t not in excluded_fingers
        ]
        return sum(y_positions) / len(y_positions)

    def _calculate_calibration_values(self) -> None:
        if not self._historical_coordinates:
            return

        distance_sums = {finger: [] for finger in Fingers.values()}

        for fingers_and_thumbs in self._historical_coordinates:
            for finger in Fingers.values():
                calibration_value = self.calculate_calibration_value(
                    fingers_and_thumbs, finger
                )

                if calibration_value is not None:
                    distance_sums[finger].append(calibration_value)

        for finger, distances in distance_sums.items():
            self._cache[finger] = sum(distances) / len(distances)
