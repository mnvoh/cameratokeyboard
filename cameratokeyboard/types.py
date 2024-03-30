from collections import namedtuple
from enum import Enum
import math
from typing import List

import numpy as np

RawImage = np.ndarray


class FrameState(Enum):
    """
    The detection state of the frame, to indicate what objects have been detected.
    """

    INITIALIZING = "initializing"
    VALID = "valid"
    MISSING_MARKERS = "missing_markers"
    MISSING_FINGERS = "missing_fingers"
    MISSING_THUMBS = "missing_thumbs"


class Point:
    """
    A simple named tuple to represent a point in 2D space.
    """

    __slots__ = ["_x_history", "_y_history", "_window_length"]

    def __init__(self, x, y):
        self._x_history = [int(x)]
        self._y_history = [int(y)]
        self._window_length = 10

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def distance(self, other):
        """
        Calculates the distance between two points.
        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    @property
    def x(self):
        """
        The X coordinate.
        """
        return self._x_history[-1]

    @property
    def y(self):
        """
        The Y coordinate.
        """
        return self._y_history[-1]

    @x.setter
    def x(self, value):
        self._x_history[-1] = int(value)

    @y.setter
    def y(self, value):
        self._y_history[-1] = int(value)

    @property
    def xy(self):
        """
        Returns the coordinates as a list.
        """
        return (self.x, self.y)

    def update(self, x, y) -> "Point":
        """
        Updates the coordinates with x,y.
        """
        self._x_history.append(int(x))
        self._y_history.append(int(y))
        self._x_history = self._x_history[-self._window_length :]
        self._y_history = self._y_history[-self._window_length :]

        return self

    def pupdate(self, p: "Point") -> "Point":
        """
        Updates the coordinates with a Point
        """
        return self.update(p.x, p.y)

    def velocity_y(self, window: int) -> float:
        """
        Returns the velocity of the point in the last `window` frames.
        """
        if len(self._y_history) < window:
            return 0

        return (self._y_history[-1] - self._y_history[-window]) / window


Finger = namedtuple("Finger", ["index", "name"])


class Fingers:
    """
    Represents the fingers on both hands.
    """

    LEFT_PINKY = Finger(0, "left_pinky")
    LEFT_RING = Finger(1, "left_ring")
    LEFT_MIDDLE = Finger(2, "left_middle")
    LEFT_INDEX = Finger(3, "left_index")
    LEFT_THUMB = Finger(4, "left_thumb")
    RIGHT_THUMB = Finger(5, "right_thumb")
    RIGHT_INDEX = Finger(6, "right_index")
    RIGHT_MIDDLE = Finger(7, "right_middle")
    RIGHT_RING = Finger(8, "right_ring")
    RIGHT_PINKY = Finger(9, "right_pinky")

    @classmethod
    def values(cls) -> List[Finger]:
        """
        Returns a list of all fingers.
        """
        return [
            x
            for k, x in vars(cls).items()
            if k.startswith("LEFT_") or k.startswith("RIGHT_")
        ]

    @classmethod
    def by_index(cls, index) -> Finger:
        """
        Returns a finger by its index.
        """
        return next((x for x in cls.values() if x.index == index), None)


S3ContentsItem = namedtuple("S3ContentsItem", ["key", "last_modified"])
