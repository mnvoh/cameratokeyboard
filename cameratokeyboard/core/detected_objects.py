from typing import List


from cameratokeyboard.core.math import (
    calculate_box_width_without_perspective_distortion,
)
from cameratokeyboard.types import Point, Finger, Fingers


class DetectedMarkers:  # pylint: disable=too-many-instance-attributes
    """
    Represents the coordinates of the detected markers.
    NOTE: This class assumes that the yaw and roll angles of the camera are as close
          to 0 as possible. Check out `assets/keyboard.jpg` and the marker placements
          to better understand the calculations.
    """

    def __init__(self, boxes: List[List[float]]):
        self._bl = None
        self._tl = None
        self._tr = None
        self._br = None

        self._bl_width = None
        self._bl_height = None
        self._tl_width = None
        self._tl_height = None
        self._tr_width = None
        self._tr_height = None
        self._br_width = None
        self._br_height = None

        self.update(boxes)

    def __repr__(self) -> str:
        return f"Markers(tl={self._tl}, bl={self._bl}, tr={self._tr}, br={self._br})"

    @property
    def bottom_left_marker(self) -> Point:
        """
        The coordinates of the bottom left marker.
        """
        if self._bl is None or self._bl_width is None:
            return None

        return Point(self._bl.x - self._bl_width / 2, self._bl.y - self._bl_height / 2)

    @property
    def top_left_marker(self) -> Point:
        """
        The coordinates of the top left marker.
        """
        if self._tl is None or self._tl_width is None:
            return None

        return Point(self._tl.x - self._tl_width / 2, self._tl.y + self._tl_height / 2)

    @property
    def top_right_marker(self) -> Point:
        """
        The coordinates of the top right marker.
        """
        if self._tr is None or self._tr_width is None:
            return None

        return Point(self._tr.x + self._tr_width / 2, self._tr.y + self._tr_height / 2)

    @property
    def bottom_right_marker(self) -> Point:
        """
        The coordinates of the bottom right marker.
        """
        if self._br is None or self._br_width is None:
            return None

        return Point(self._br.x + self._br_width / 2, self._br.y - self._br_height / 2)

    @property
    def all_marker_coordinates(self) -> List[Point]:
        """
        All 4 coordinates of the markers. Can contain None values if the markers are missing.
        """
        return [
            self.bottom_left_marker,
            self.top_left_marker,
            self.top_right_marker,
            self.bottom_right_marker,
        ]

    @property
    def any_markers_missing(self) -> bool:
        """
        Returns True if any of the markers are missing, False otherwise.
        """
        return len([m for m in self.all_marker_coordinates if m is not None]) < 4

    @property
    def all_markers_present(self) -> bool:
        """
        Returns True if all markers are present, False otherwise.
        """
        return not self.any_markers_missing

    def update(self, boxes: List[List[float]]):
        """
        Updates the coordinates of the markers.

        Args:
            boxes (List[List[float]]): A list of bounding box coordinates for the
                detected objects.

        Returns:
            None
        """
        self.raw_boxes = sorted(boxes, key=lambda box: box[0])
        self._identify_markers()

    def _identify_markers(self) -> None:
        if not self.raw_boxes or len(self.raw_boxes) < 4:
            return

        # The boxes are already sorted by x and the assumption is that yaw is 0.

        boxes = self.raw_boxes
        self._bl = self._bl.update(*boxes[0][:2]) if self._bl else Point(*boxes[0][:2])
        self._tl = self._tl.update(*boxes[1][:2]) if self._tl else Point(*boxes[1][:2])
        self._tr = self._tr.update(*boxes[2][:2]) if self._tr else Point(*boxes[2][:2])
        self._br = self._br.update(*boxes[3][:2]) if self._br else Point(*boxes[3][:2])

        self._bl_width = calculate_box_width_without_perspective_distortion(
            boxes[0], self._tl.xy
        )
        self._bl_height = boxes[0][3] * 0.7
        self._tl_width = calculate_box_width_without_perspective_distortion(
            boxes[1], self._bl.xy
        )
        self._tl_height = boxes[1][3] * 0.7
        self._tr_width = calculate_box_width_without_perspective_distortion(
            boxes[2], self._br.xy
        )
        self._tr_height = boxes[2][3] * 0.7
        self._br_width = calculate_box_width_without_perspective_distortion(
            boxes[3], self._tr.xy
        )
        self._br_height = boxes[3][3] * 0.7


class DetectedFingersAndThumbs:
    """
    THIS CLASS WILL BE REPLACED SOON.

    Represents the coordinates of the detected fingers and thumbs.
    """

    def __init__(self, finger_boxes: List[List[float]], thumb_boxes: List[List[float]]):
        self._coordinates = {}
        self.update(finger_boxes, thumb_boxes)

    def __getitem__(self, key: Finger):
        return self._coordinates.get(key.name)

    def __setitem__(self, key: Finger, value: Point):
        self._coordinates[key.name] = value

    def update(self, finger_boxes: List[List[float]], thumb_boxes: List[List[float]]):
        """
        Updates the coordinates of the fingers and carries out the required calculations.

        Args:
            finger_boxes (List[List[float]]): A list of finger bounding boxes, where each
                box is represented as a list of four float values [x_min, y_min, x_max, y_max].
            thumb_boxes (List[List[float]]): A list of thumb bounding boxes, where each
                box is represented as a list of four float values [x_min, y_min, x_max, y_max].
        """
        self.raw_finger_boxes = sorted(finger_boxes, key=lambda box: box[0])
        self.raw_thumb_boxes = sorted(thumb_boxes, key=lambda box: box[0])
        self._identify_fingers()
        self._identify_thumbs()

    @property
    def finger_coordinates(self) -> List[Point]:
        """
        Returns the coordinates of the detected fingers (except thumbs).

        Returns:
            List[Point]: A list of Point objects representing the coordinates of the
                detected fingers.
        """
        retval = [
            x
            for x in [
                self[Fingers.LEFT_PINKY],
                self[Fingers.LEFT_RING],
                self[Fingers.LEFT_MIDDLE],
                self[Fingers.LEFT_INDEX],
                self[Fingers.RIGHT_INDEX],
                self[Fingers.RIGHT_MIDDLE],
                self[Fingers.RIGHT_RING],
                self[Fingers.RIGHT_PINKY],
            ]
            if x is not None
        ]
        return retval

    @property
    def thumb_coordinates(self) -> List[Point]:
        """
        Returns the coordinates of the detected thumbs.

        Returns:
            A list of Point objects representing the coordinates of the detected thumbs.
        """
        return [
            x
            for x in [self[Fingers.LEFT_THUMB], self[Fingers.RIGHT_THUMB]]
            if x is not None
        ]

    @property
    def average_finger_width(self) -> float:
        """
        The average width of the detected fingers
        """
        return sum(box[2] for box in self.raw_finger_boxes) / len(self.raw_finger_boxes)

    @property
    def average_finger_height(self) -> float:
        """
        The average height of the detected fingers
        """
        if len(self.raw_finger_boxes) == 0:
            return 0
        return sum(box[3] for box in self.raw_finger_boxes) / len(self.raw_finger_boxes)

    def _identify_fingers(self) -> None:
        for finger in Fingers.values():
            finger_index = finger.index if finger.index < 5 else finger.index - 2

            if len(self.raw_finger_boxes) <= finger_index:
                continue

            new_coordinates = Point(
                self.raw_finger_boxes[finger_index][0],
                self.raw_finger_boxes[finger_index][1]
                + self.raw_finger_boxes[finger_index][3] / 3,
            )

            current_coordinates = self[finger]
            self[finger] = (
                current_coordinates.pupdate(new_coordinates)
                if current_coordinates
                else new_coordinates
            )

    def _identify_thumbs(self) -> None:
        if len(self.raw_thumb_boxes) > 0:
            self[Fingers.LEFT_THUMB] = Point(
                self.raw_thumb_boxes[0][0],
                self.raw_thumb_boxes[0][1] + self.raw_thumb_boxes[0][3] / 2,
            )
            self[Fingers.RIGHT_THUMB] = (
                Point(
                    self.raw_thumb_boxes[1][0],
                    self.raw_thumb_boxes[1][1] + self.raw_thumb_boxes[1][3] / 2,
                )
                if len(self.raw_thumb_boxes) > 1
                else None
            )
