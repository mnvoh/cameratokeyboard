# pylint: disable=missing-function-docstring

from cameratokeyboard.core.keyboard_layouts import KeyboardLayout

key_center_test_cases = {
    "backtick": (0.034, 0.1),
    "one": (0.101, 0.1),
    "two": (0.168, 0.1),
    "three": (0.235, 0.1),
    "four": (0.301, 0.1),
    "five": (0.369, 0.1),
    "six": (0.435, 0.1),
    "seven": (0.503, 0.1),
    "eight": (0.57, 0.1),
    "nine": (0.636, 0.1),
    "zero": (0.703, 0.1),
    "minus": (0.77, 0.1),
    "equal": (0.837, 0.1),
    "backspace": (0.938, 0.1),
    "tab": (0.051, 0.3),
    "q": (0.135, 0.3),
    "w": (0.202, 0.3),
    "e": (0.269, 0.3),
    "r": (0.336, 0.3),
    "t": (0.403, 0.3),
    "y": (0.47, 0.3),
    "u": (0.537, 0.3),
    "i": (0.604, 0.3),
    "o": (0.67, 0.3),
    "p": (0.737, 0.3),
    "left_bracket": (0.804, 0.3),
    "right_bracket": (0.871, 0.3),
    "backslash": (0.955, 0.3),
    "caps_lock": (0.059, 0.5),
    "a": (0.151, 0.5),
    "s": (0.218, 0.5),
    "d": (0.285, 0.5),
    "f": (0.353, 0.5),
    "g": (0.419, 0.5),
    "h": (0.487, 0.5),
    "j": (0.553, 0.5),
    "k": (0.62, 0.5),
    "l": (0.687, 0.5),
    "semicolon": (0.754, 0.5),
    "quote": (0.821, 0.5),
    "enter": (0.93, 0.5),
    "left_shift": (0.075, 0.7),
    "z": (0.184, 0.7),
    "x": (0.252, 0.7),
    "c": (0.319, 0.7),
    "v": (0.386, 0.7),
    "b": (0.453, 0.7),
    "n": (0.52, 0.7),
    "m": (0.587, 0.7),
    "comma": (0.654, 0.7),
    "period": (0.721, 0.7),
    "slash": (0.787, 0.7),
    "right_shift": (0.912, 0.7),
    "left_ctrl": (0.051, 0.9),
    "left_win": (0.143, 0.9),
    "left_alt": (0.226, 0.9),
    "space": (0.459, 0.9),
    "right_alt": (0.692, 0.9),
    "menu": (0.774, 0.9),
    "right_win": (0.857, 0.9),
    "right_ctrl": (0.949, 0.9),
}


def test_convert_coordinates_to_key():
    layout = KeyboardLayout()  # Create an instance of the KeyboardLayout class

    for expected, (x, y) in key_center_test_cases.items():
        actual = layout.convert_coordinates_to_key(x, y)

        assert actual == expected, f"Expected {expected}, got {actual}"


def test_get_key_value():
    layout = KeyboardLayout()

    key = "space"
    expected = " "
    actual = layout.get_key_value(key)
    assert actual == expected

    key = "a"
    expected = "a"
    actual = layout.get_key_value(key)
    assert actual == expected
