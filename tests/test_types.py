# pylint: disable=missing-function-docstring
import math

from cameratokeyboard.types import FrameState, Point, Finger, Fingers


def test_frame_state():
    assert FrameState.INITIALIZING.value == "initializing"
    assert FrameState.VALID.value == "valid"
    assert FrameState.MISSING_MARKERS.value == "missing_markers"
    assert FrameState.MISSING_FINGERS.value == "missing_fingers"
    assert FrameState.MISSING_THUMBS.value == "missing_thumbs"


def test_point_initialization():
    p = Point(3, 4)
    assert p.x == 3
    assert p.y == 4


def test_point_equality():
    p1 = Point(3, 4)
    p2 = Point(3, 4)
    assert p1 == p2


def test_point_distance():
    p1 = Point(1, 2)
    p2 = Point(4, 6)
    expected_distance = math.sqrt((4 - 1) ** 2 + (6 - 2) ** 2)
    assert p1.distance(p2) == expected_distance


def test_point_update():
    p = Point(1, 2)
    p.update(3, 4)
    assert p.x == 3
    assert p.y == 4


def test_point_velocity_y():
    p = Point(1, 2)
    p.update(1, 4)
    p.update(1, 6)
    p.update(1, 8)
    assert p.velocity_y(3) == (8 - 4) / 3


def test_fingers_values():
    fingers = Fingers.values()
    assert len(fingers) == 10
    assert all(isinstance(finger, Finger) for finger in fingers)


def test_fingers_by_index():
    assert Fingers.by_index(0) == Fingers.LEFT_PINKY
    assert Fingers.by_index(1) == Fingers.LEFT_RING
    assert Fingers.by_index(2) == Fingers.LEFT_MIDDLE
    assert Fingers.by_index(3) == Fingers.LEFT_INDEX
    assert Fingers.by_index(4) == Fingers.LEFT_THUMB
    assert Fingers.by_index(5) == Fingers.RIGHT_THUMB
    assert Fingers.by_index(6) == Fingers.RIGHT_INDEX
    assert Fingers.by_index(7) == Fingers.RIGHT_MIDDLE
    assert Fingers.by_index(8) == Fingers.RIGHT_RING
    assert Fingers.by_index(9) == Fingers.RIGHT_PINKY


def test_fingers_by_invalid_index():
    assert Fingers.by_index(10) is None
    assert Fingers.by_index(-1) is None
    assert Fingers.by_index(100) is None
