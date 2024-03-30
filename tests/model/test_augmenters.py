# pylint: disable=missing-function-docstring
from unittest.mock import patch, MagicMock

import imgaug
import numpy as np

from cameratokeyboard.model.augmenters import (
    ImageAugmenter,
    ScaleAugmenter,
    RotationAugmenter,
    VerticalFlipAugmenter,
    HorizontalFlipAugmenter,
    BlurAugmenter,
    ShearAugmenter,
    PerspectiveAugmenter,
)


def test_scale_augmenter():
    assert issubclass(ScaleAugmenter, ImageAugmenter)
    augmenter = ScaleAugmenter(0.05, 1.0)
    assert isinstance(augmenter.augmenter, imgaug.augmenters.Affine)


def test_Rotation_augmenter():
    assert issubclass(RotationAugmenter, ImageAugmenter)
    augmenter = ScaleAugmenter(0.05, 1.0)
    assert isinstance(augmenter.augmenter, imgaug.augmenters.Affine)


def test_vertical_flip_augmenter():
    assert issubclass(VerticalFlipAugmenter, ImageAugmenter)
    augmenter = VerticalFlipAugmenter()
    assert isinstance(augmenter.augmenter, imgaug.augmenters.Flipud)


def test_horizontal_flip_augmenter():
    assert issubclass(HorizontalFlipAugmenter, ImageAugmenter)
    augmenter = HorizontalFlipAugmenter()
    assert isinstance(augmenter.augmenter, imgaug.augmenters.Fliplr)


@patch("cameratokeyboard.model.augmenters.iaa.GaussianBlur")
def test_blur_augmenter(guassian_blur_mock):
    guassian_blur_mock.return_value.return_value = (
        "image",
        MagicMock(
            bounding_boxes=[
                MagicMock(label="0", center_x=10, center_y=10, width=10, height=10)
            ],
            shape=(20, 20),
        ),
    )
    assert issubclass(BlurAugmenter, ImageAugmenter)
    augmenter = BlurAugmenter(0.5, 1)
    augmenter.apply(np.zeros((100, 100, 1)), MagicMock())

    assert guassian_blur_mock.return_value.called


def test_shear_augmenter():
    assert issubclass(ShearAugmenter, ImageAugmenter)
    augmenter = ShearAugmenter(1.0, 2.0)
    assert isinstance(augmenter.augmenter, imgaug.augmenters.ShearX)


def test_perspective_augmenter():
    assert issubclass(PerspectiveAugmenter, ImageAugmenter)
    augmenter = PerspectiveAugmenter(1.0, 2.0)
    assert isinstance(augmenter.augmenter, imgaug.augmenters.PerspectiveTransform)
