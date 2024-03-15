# pylint: skip-file


def assert_within_tolerance(actual, expected, tolerance):
    assert (
        abs(actual - expected) < tolerance
    ), f"Expected {expected}, got {actual}; tolerance: {tolerance}"
