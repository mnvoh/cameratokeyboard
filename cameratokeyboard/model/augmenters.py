from abc import ABC, abstractmethod
from typing import Tuple, Union

from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import numpy as np


class ImageAugmenter(ABC):
    """
    Abstract base class for image augmenters.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def apply(self, image: np.ndarray, bounding_boxes: str) -> Tuple[np.ndarray, str]:
        """
        Apply image augmentation to the input image and bounding boxes.

        Args:
            image (np.ndarray): The input image.
            bounding_boxes (str): The bounding boxes in string format.

        Returns:
            Tuple[np.ndarray, str]: The augmented image and the serialized bounding boxes.
        """
        bbs = self.parse_bounding_boxes(bounding_boxes, image.shape)
        aug_image, aug_bounding_boxes = self.augmenter(image=image, bounding_boxes=bbs)

        return aug_image, self.__class__.serialize_bounding_boxes(aug_bounding_boxes)

    def parse_bounding_boxes(
        self, bounding_boxes: str, image_shape: Tuple[int, int]
    ) -> BoundingBoxesOnImage:
        """
        Parse the bounding boxes from the string format to BoundingBoxesOnImage object.

        Args:
            bounding_boxes (str): The bounding boxes in string format.
            image_shape (Tuple[int, int]): The shape of the input image.

        Returns:
            BoundingBoxesOnImage: The parsed bounding boxes.
        """
        if not bounding_boxes:
            return None

        parsed_bounding_boxes = []

        for bounding_box_str in bounding_boxes.split("\n"):
            if len(bounding_box_str.split(" ")) != 5:
                continue
            label, x_center, y_center, width, height = bounding_box_str.split(" ")

            parsed_bounding_boxes.append(
                BoundingBox(
                    x1=(float(x_center) - float(width) / 2) * image_shape[1],
                    y1=(float(y_center) - float(height) / 2) * image_shape[0],
                    x2=(float(x_center) + float(width) / 2) * image_shape[1],
                    y2=(float(y_center) + float(height) / 2) * image_shape[0],
                    label=label,
                )
            )

        return BoundingBoxesOnImage(parsed_bounding_boxes, shape=image_shape)

    @classmethod
    def serialize_bounding_boxes(cls, bounding_boxes: BoundingBoxesOnImage) -> str:
        """
        Serialize the bounding boxes from BoundingBoxesOnImage object to string format.

        Args:
            bounding_boxes (BoundingBoxesOnImage): The bounding boxes.

        Returns:
            str: The serialized bounding boxes.
        """
        if not bounding_boxes:
            return None

        bbs = []

        for box in bounding_boxes.bounding_boxes:
            x_center = box.center_x / bounding_boxes.shape[1]
            y_center = box.center_y / bounding_boxes.shape[0]
            width = box.width / bounding_boxes.shape[1]
            height = box.height / bounding_boxes.shape[0]

            bbs.append(
                f"{box.label} {x_center:0.6f} {y_center:0.6f} {width:0.6f} {height:0.6f}"
            )

        return "\n".join(bbs)


class ScaleAugmenter(ImageAugmenter):
    """
    A class representing a scale augmenter.

    This augmenter applies scaling transformations to images.

    Args:
        min_scale (float): The minimum scale factor to apply.
        max_scale (float): The maximum scale factor to apply.
    """

    def __init__(self, min_scale: float, max_scale: float):
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.augmenter = iaa.Affine(
            scale={"x": (min_scale, max_scale), "y": (min_scale, max_scale)}
        )

    def __repr__(self) -> str:
        return f"ScaleAugmenter({self.min_scale}, {self.max_scale})"


class RotationAugmenter(ImageAugmenter):
    """
    A class representing a rotation augmenter for images.

    Attributes:
        min_angle (float): The minimum angle of rotation.
        max_angle (float): The maximum angle of rotation.
        augmenter (iaa.Affine): The image augmentation object.

    """

    def __init__(self, min_angle: float, max_angle: float):
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.augmenter = iaa.Affine(rotate=(min_angle, max_angle))

    def __repr__(self) -> str:
        return f"RotationAugmenter({self.min_angle}, {self.max_angle})"


class VerticalFlipAugmenter(ImageAugmenter):
    """
    A class representing a vertical flip augmenter.

    This augmenter flips images vertically.

    Attributes:
        augmenter (imgaug.augmenters.Flipud): The vertical flip augmenter.

    """

    def __init__(self):
        self.augmenter = iaa.Flipud(True)

    def __repr__(self) -> str:
        return "VerticalFlipAugmenter()"


class HorizontalFlipAugmenter(ImageAugmenter):
    """
    Augmenter that performs horizontal flipping on images.
    """

    def __init__(self):
        self.augmenter = iaa.Fliplr(True)

    def __repr__(self) -> str:
        return "HorizontalFlipAugmenter()"


class BlurAugmenter(ImageAugmenter):
    """
    A class representing a blur augmenter that applies Gaussian blur to an image.

    Args:
        min_sigma (float): The minimum standard deviation for the Gaussian blur.
        max_sigma (float): The maximum standard deviation for the Gaussian blur.
    """

    def __init__(self, min_sigma: float, max_sigma: float):
        self.min_sigma = min_sigma
        self.max_sigma = max_sigma
        self.augmenter = None

    def apply(
        self, image: np.ndarray, bounding_boxes: str
    ) -> Tuple[Union[np.ndarray, str]]:
        """
        Applies Gaussian blur to the input image.

        Args:
            image (np.ndarray): The input image to be augmented.
            bounding_boxes (str): The bounding boxes associated with the image.

        Returns:
            Tuple[Union[np.ndarray, str]]: A tuple containing the augmented image and the
                bounding boxes.
        """
        sigma = np.random.uniform(self.min_sigma, self.max_sigma)
        self.augmenter = iaa.GaussianBlur(sigma=sigma)
        return super().apply(image, bounding_boxes)

    def __repr__(self) -> str:
        return f"BlurAugmenter({self.min_sigma}, {self.max_sigma})"


class ShearAugmenter(ImageAugmenter):
    """
    A class representing a shear augmenter for image data.

    Attributes:
        min_shear (float): The minimum shear value to apply.
        max_shear (float): The maximum shear value to apply.
        augmenter (iaa.ShearX): The shear augmentation object.
    """

    def __init__(self, min_shear: float, max_shear: float):
        self.min_shear = min_shear
        self.max_shear = max_shear
        self.augmenter = iaa.ShearX((min_shear, max_shear))

    def __repr__(self) -> str:
        return f"ShearAugmenter({self.min_shear}, {self.max_shear})"


class PerspectiveAugmenter(ImageAugmenter):
    """
    A class representing a perspective augmenter for image data.

    This augmenter applies perspective transformations to images.

    Args:
        min_scale (float): The minimum scale factor for the perspective transformation.
        max_scale (float): The maximum scale factor for the perspective transformation.
    """

    def __init__(self, min_scale: float, max_scale: float):
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.augmenter = iaa.PerspectiveTransform(scale=(min_scale, max_scale))

    def __repr__(self) -> str:
        return f"PerspectiveAugmenter({self.min_scale}, {self.max_scale})"
