from typing import List

import ultralytics

from cameratokeyboard.config import Config
from cameratokeyboard.core.calibration import AdjacentNeighborCalibrationStrategy
from cameratokeyboard.core.detected_objects import (
    DetectedFingersAndThumbs,
    DetectedMarkers,
)
from cameratokeyboard.core.finger_down_detector import FingerDownDetector
from cameratokeyboard.core.keyboard_layouts import KeyboardLayout
from cameratokeyboard.core.math import finger_to_keyboard_fractional_coordinates
from cameratokeyboard.interfaces import IDetectedFrameData
from cameratokeyboard.types import Fingers, FrameState, Point, RawImage


class DetectedFrame(
    IDetectedFrameData
):  # pylint: disable=missing-class-docstring, too-many-instance-attributes
    def __init__(
        self, detection_results: ultralytics.engine.results.Results, config: Config
    ):
        self._detection_results = detection_results
        self._markers_min_confidence = config.markers_min_confidence
        self._fingers_min_confidence = config.fingers_min_confidence
        self._thumbs_min_confidence = config.thumbs_min_confidence

        self.calibration_strategy = AdjacentNeighborCalibrationStrategy(
            history_size=100  # TODO: history_size->CONFIG
        )
        self._down_detector = FingerDownDetector(
            self.calibration_strategy, sensitivity=config.key_down_sensitivity
        )

        self._keyboard_layout = KeyboardLayout(layout=config.keyboard_layout)
        self._is_calibrating = False
        self._on_calibration_complete = None

        self._markers = None
        self._fingers_and_thumbs = None
        self._down_fingers = []
        self._down_keys = []

        # When a finger goes down on a key, it is locked to that key until it goes up.
        # Because sometimes even different keys are detected just because of the noise
        # and the jitter of the detection results.
        self._locked_keys = {}

        self._state = FrameState.INITIALIZING
        self.update(detection_results)

    @property
    def current_frame(self) -> RawImage:
        return self.frame

    @property
    def markers(self) -> DetectedMarkers:
        """
        Returns the detected markers in the frame.

        Returns:
            Markers: The detected markers.
        """
        return self._markers

    @property
    def marker_coordinates(self) -> List[Point]:
        if not self._markers:
            return []

        return self._markers.all_marker_coordinates

    @property
    def finger_coordinates(self) -> List[Point]:
        return self._fingers_and_thumbs.finger_coordinates

    @property
    def thumb_coordinates(self) -> List[Point]:
        return self._fingers_and_thumbs.thumb_coordinates

    @property
    def down_finger_coordinates(self) -> List[Point]:
        return [coordinates for _, coordinates in self._down_fingers]

    @property
    def down_keys(self) -> List[str]:
        """
        Returns the keys that are currently down.

        Returns:
            A list of strings representing the keys that are currently down.
        """
        return self._down_keys

    @property
    def state(self):
        return self._state

    @property
    def requires_calibration(self) -> bool:
        return not self.calibration_strategy.is_calibrated

    @property
    def is_calibration_in_progress(self) -> bool:
        return self._is_calibrating

    @property
    def calibration_progress(self) -> float:
        return self.calibration_strategy.calibration_progress

    def update(self, detection_results: ultralytics.engine.results.Results):
        """
        Updates the detected frame with new detection results.

        Args:
            detection_results (ultralytics.engine.results.Results): The new detection results.

        Returns:
            None
        """
        self._detection_results = detection_results
        self.frame = detection_results.orig_img
        self._calculate_coordinates()
        self._set_state()
        self._handle_calibration()

        self._detect_down_fingers()
        self._map_down_fingers_to_keys()

    def start_calibration(self, on_calibration_complete: callable):
        self._is_calibrating = True
        self._on_calibration_complete = on_calibration_complete

    def _handle_calibration(self):
        if self.is_calibration_in_progress and self._state == FrameState.VALID:
            self.calibration_strategy.append(self._fingers_and_thumbs)

            if self.calibration_strategy.is_calibrated:
                self._is_calibrating = False

                if self._on_calibration_complete and callable(
                    self._on_calibration_complete
                ):
                    self._on_calibration_complete()

    def _calculate_coordinates(self):
        classes = [int(i) for i in self._detection_results.boxes.cls]
        confidences = [float(i) for i in self._detection_results.boxes.conf]
        boxes = [[float(y) for y in x] for x in self._detection_results.boxes.xywh]

        # TODO: fix the hardcoded class values
        marker_boxes = [
            boxes[i]
            for i, c in enumerate(classes)
            if c == 2 and confidences[i] > self._markers_min_confidence
        ]
        finger_boxes = [
            boxes[i]
            for i, c in enumerate(classes)
            if c == 0 and confidences[i] > self._fingers_min_confidence
        ]
        thumb_boxes = [
            boxes[i]
            for i, c in enumerate(classes)
            if c == 1 and confidences[i] > self._thumbs_min_confidence
        ]

        self._update_markers(marker_boxes)
        self._update_fingers_and_thumbs(finger_boxes, thumb_boxes)

    def _update_markers(self, marker_boxes: List[List[float]]):
        if not self._markers:
            self._markers = DetectedMarkers(marker_boxes)
        else:
            self._markers.update(marker_boxes)

    def _update_fingers_and_thumbs(
        self, finger_boxes: List[List[float]], thumb_boxes: List[List[float]]
    ):
        if not self._fingers_and_thumbs:
            self._fingers_and_thumbs = DetectedFingersAndThumbs(
                finger_boxes, thumb_boxes
            )
        else:
            self._fingers_and_thumbs.update(finger_boxes, thumb_boxes)

    def _set_state(self):
        if not self._markers or len(self._markers.all_marker_coordinates) != 4:
            self._state = FrameState.MISSING_MARKERS
            return

        if (
            not self._fingers_and_thumbs
            or len(self._fingers_and_thumbs.finger_coordinates) != 8
        ):
            self._state = FrameState.MISSING_FINGERS
            return

        if len(self._fingers_and_thumbs.thumb_coordinates) != 2:
            self._state = FrameState.MISSING_THUMBS
            return

        self._state = FrameState.VALID

    def _detect_down_fingers(self):
        if self.requires_calibration:
            return

        self._down_fingers = []

        for finger in Fingers.values():
            if self._down_detector.is_finger_down(self._fingers_and_thumbs, finger):
                self._down_fingers.append((finger, self._fingers_and_thumbs[finger]))

        if len(self._down_fingers) > 4:
            self._down_fingers = []

    def _map_down_fingers_to_keys(self):
        # TODO: The placement of this logic feels really wrong, it should be in another
        # module.
        self._down_keys = []

        for finger, coordinates in self._down_fingers:
            if finger in self._locked_keys:
                self._down_keys.append(self._locked_keys[finger])
                continue

            if finger in [Fingers.LEFT_THUMB, Fingers.RIGHT_THUMB]:
                self._down_keys.append(" ")
                self._locked_keys[finger] = " "
                continue

            relative_to_keyboard_x, relative_to_keyboard_y = (
                finger_to_keyboard_fractional_coordinates(self.markers, coordinates)
            )
            key = self._keyboard_layout.convert_coordinates_to_key(
                relative_x=relative_to_keyboard_x, relative_y=relative_to_keyboard_y
            )

            # TODO: Implement modifier keys
            if self._keyboard_layout.is_modifier_key(key):
                continue

            mapped_key = self._keyboard_layout.get_key_value(key)
            self._down_keys.append(mapped_key)
            self._locked_keys[finger] = mapped_key

        self._locked_keys = {
            finger: key
            for finger, key in self._locked_keys.items()
            if finger in [x for x, _ in self._down_fingers]
        }
