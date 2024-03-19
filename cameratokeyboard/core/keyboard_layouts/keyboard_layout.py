# pylint: disable=too-many-arguments

import os
import pathlib

import yaml


KEY_MAPS = {
    "backtick": "`",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "zero": "0",
    "minus": "-",
    "equal": "=",
    "backspace": "\b",
    "tab": "\t",
    "left_bracket": "[",
    "right_bracket": "]",
    "backslash": "\\",
    "semicolon": ";",
    "quote": "'",
    "enter": "\n",
    "comma": ",",
    "period": ".",
    "slash": "/",
    "space": " ",
}

MODIFIER_KEYS = [
    "left_shift",
    "right_shift",
    "left_ctrl",
    "right_ctrl",
    "left_alt",
    "right_alt",
    "left_win",
    "right_win",
    "menu",
    "caps_lock",
]


class Key:
    """
    Represents a key on the keyboard layout.
    """

    def __init__(
        self, name: str, x: float, y: float, width: float, height: float
    ) -> None:
        self.name = name
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def contains(self, x: float, y: float) -> bool:
        """
        Checks if the given coordinates are within the key.

        Args:
            x (float): The X coordinate.
            y (float): The Y coordinate.

        Returns:
            bool: True if the coordinates are within the key, False otherwise.
        """
        return (
            self._x <= x <= self._x + self._width
            and self._y <= y <= self._y + self._height
        )


class KeyboardLayout:
    """
    Represents a keyboard layout.

    Args:
        layout (str, optional): The name of the layout. Defaults to "qwerty".

    Attributes:
        keyboard_distance_from_markers (float): The distance from the markers to the
            keyboard layout. Used to calculate relative coordinates to the keyboard rather
            than the markers.

    Methods:
        convert_coordinates_to_key: Converts the given coordinates to a key on the keyboard layout.
    """

    def __init__(self, layout: str = "qwerty") -> None:
        self._layout_name = layout
        self._layout = None
        self._flat_layout = None

        self._load_layout()
        self._calculate_key_coordinates()

    @property
    def real_world_dimensions(self) -> tuple:
        """
        The real world dimensions (width, height) of the keyboard in millimeters.
        """
        return (
            None
            if not self._layout
            else tuple(self._layout["real_world_dimensions_mm"])
        )

    def convert_coordinates_to_key(self, relative_x: float, relative_y: float) -> str:
        """
        Converts the given coordinates to a key on the keyboard layout.

        Args:
            relative_x (float): An X coordinate (0.0 - 1.0) relative to the bottom markers
            relative_y (float): A Y coordinate (0.0 - 1.0) relative to the top markers

        Returns:
            str: The key on the keyboard layout.
        """

        for key in self._flat_layout:
            if key.contains(relative_x, relative_y):
                return key.name

        return ""

    def get_key_value(self, key: str) -> str:
        """
        Retrieves the corresponding value for the given key from the KEY_MAPS dictionary.

        If the key is not found in the dictionary, the key itself is returned.

        Args:
            key (str): The key to retrieve the value for. For a list of key names see qwerty.yaml.

        Returns:
            str: The corresponding value for the given key, or the key itself if not found.
        """
        return KEY_MAPS.get(key, key)

    def is_modifier_key(self, key: str) -> bool:
        """
        Checks if the given key is a modifier key.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key is a modifier key, False otherwise.
        """
        return key in MODIFIER_KEYS

    def _load_layout(self) -> None:
        current_file_path = pathlib.Path(__file__).parent
        layout_path = os.path.join(current_file_path, f"{self._layout_name}.yaml")

        with open(layout_path, "r", encoding="utf-8") as f:
            self._layout = yaml.safe_load(f)

    def _calculate_key_coordinates(self) -> None:
        self._flat_layout = []

        for row, keys in self._layout["keys"].items():
            row_index = int(row.split("_")[-1]) - 1

            x = 0.0
            for key in keys:
                if x >= 1.0:
                    raise ValueError(
                        f"Invalid layout: X position exceeds row width for {key['name']}."
                    )

                y = row_index * self._layout["key_height"]

                if y >= 1.0:
                    raise ValueError(
                        f"Invalid layout: Y position exceeds layout height for {key['name']}."
                    )

                self._flat_layout.append(
                    Key(
                        key["name"],
                        x,
                        y,
                        key["width"],
                        self._layout["key_height"],
                    )
                )

                x += key["width"]
