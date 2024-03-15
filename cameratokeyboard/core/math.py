import math
from typing import Tuple

import cv2
import numpy as np

from cameratokeyboard.types import EulerAngle, Point


def calculate_euler_angles_from_markers(
    top_left: Point,
    top_right: Point,
    bottom_right: Point,
    bottom_left: Point,
    image_size: tuple,
) -> EulerAngle:
    """
    Calculates the euler angles of the camera using the marker coordinates.
    """
    if not all([top_left, top_right, bottom_right, bottom_left]):
        return EulerAngle(yaw=0, pitch=0, roll=0)

    optical_center_y = image_size[1] / 2

    dx = top_right.x - top_left.x
    dy = top_right.y - top_left.y
    yaw = np.arctan2(dy, dx)

    d = np.sqrt(dx**2 + dy**2)
    dy = top_left.y - optical_center_y
    pitch = np.arctan2(dy, d)

    return EulerAngle(yaw=np.degrees(yaw), pitch=np.degrees(pitch), roll=0)


def calculate_box_width_without_perspective_distortion(box, reference_box_pos):
    """
    Calculates the size of the box without perspective distortion.

    Args:
        box (Tuple[float]): The bounding box coordinates. (center_x, center_y, width, height)
        reference_box (Tuple[float]): The bounding box of another object below or above to
            calculate distortion angles.
    """
    if not box or not reference_box_pos:
        raise ValueError("Invalid box or reference_box_pos")

    tangent = abs(box[0] - reference_box_pos[0]) / abs(box[1] - reference_box_pos[1])
    angle = math.atan(tangent)
    angle = max(0.0, min(math.pi / 2, angle))

    return box[2] / (1 + angle * 1.5)


def finger_to_keyboard_fractional_coordinates(
    markers,
    finger_coordinates,
    x_offset: float = 0.0,
    y_offset: float = 0.0,
) -> Tuple[float, float]:
    """
    Converts the given finger coordinates to fractional coordinates relative to the
    edges of the keyboard.

    Args:
        markers (Markers): The 4 marker coordinates.
        finger_coordinates (Point): The finger coordinates. Bottom left, top left and
            bottom right markers are required.
        x_offset (float, optional): An offset to add to the x-coordinate. It most
            likely will be the fractional distance from the center of the markers to
            the edge of the keyboard.
        y_offset (float, optional): An offset to add to the y-coordinate to
            improve accuracy. Defaults to 0.0. A ball-park of the value is anywhere
            between 0.0 and 0.15.

    Returns:
        Tuple[float, float]: The finger coordinates on the keyboard layout relative to
            its edges (0.0 to 1.0).

    Raises:
        ValueError: If finger_coodinates is None or there aren't 4 marker_coordinates.
    """
    if not finger_coordinates:
        raise ValueError("Invalid finger coordinates.")

    if (
        not markers.bottom_left_marker
        or not markers.top_left_marker
        or not markers.bottom_right_marker
    ):
        raise ValueError("Missing required markers")

    perspective_boundry = np.float32(
        [
            markers.bottom_left_marker.xy,
            markers.top_left_marker.xy,
            markers.bottom_right_marker.xy,
            markers.top_right_marker.xy,
        ]
    )
    target_boundry = np.float32(
        [
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1],
        ]
    )
    matrix = cv2.getPerspectiveTransform(perspective_boundry, target_boundry)
    transformed = np.dot(matrix, [*finger_coordinates.xy, 1])
    transformed /= transformed[2]

    return transformed[0] + x_offset, transformed[1] + y_offset
