"""Model-independent prompts, results, and inference ports."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .images import AlphaMatte, ImageDocument, ProbabilityMask, Trimap


class PointKind(Enum):
    """Whether an interactive point asks to preserve or remove an area."""

    POSITIVE = "positive"
    NEGATIVE = "negative"


@dataclass(frozen=True, slots=True)
class PointPrompt:
    """A point at integer pixel coordinate ``(x, y)``."""

    x: int
    y: int
    kind: PointKind

    def __post_init__(self) -> None:
        if type(self.x) is not int or type(self.y) is not int:
            raise TypeError("point coordinates must have int dtype")
        if type(self.kind) is not PointKind:
            raise TypeError("point kind must be a PointKind")


@dataclass(frozen=True, slots=True)
class BoxPrompt:
    """Half-open box ``[left, right) × [top, bottom)`` in pixel coordinates."""

    left: int
    top: int
    right: int
    bottom: int

    def __post_init__(self) -> None:
        coordinates = (self.left, self.top, self.right, self.bottom)
        if any(type(value) is not int for value in coordinates):
            raise TypeError("box coordinates must have int dtype")
        if self.left < 0 or self.top < 0:
            raise ValueError("box origin must not be negative")
        if self.right <= self.left or self.bottom <= self.top:
            raise ValueError("box must have positive width and height")


@dataclass(frozen=True, slots=True)
class SubjectPrompt:
    """Validated point and box prompts associated with one image size."""

    image_size: tuple[int, int]
    points: tuple[PointPrompt, ...] = ()
    boxes: tuple[BoxPrompt, ...] = ()

    def __post_init__(self) -> None:
        if (
            type(self.image_size) is not tuple
            or len(self.image_size) != 2
            or any(type(value) is not int for value in self.image_size)
        ):
            raise TypeError("prompt image_size must be a (width, height) int tuple")
        width, height = self.image_size
        if width <= 0 or height <= 0:
            raise ValueError("prompt image size must be positive")
        if type(self.points) is not tuple or any(
            type(point) is not PointPrompt for point in self.points
        ):
            raise TypeError("points must be a tuple of PointPrompt values")
        if type(self.boxes) is not tuple or any(type(box) is not BoxPrompt for box in self.boxes):
            raise TypeError("boxes must be a tuple of BoxPrompt values")
        if not self.points and not self.boxes:
            raise ValueError("subject prompt must contain at least one point or box")
        if len(self.boxes) > 1:
            raise ValueError("subject prompt accepts at most one box")
        for point in self.points:
            if not 0 <= point.x < width or not 0 <= point.y < height:
                raise ValueError("point is outside the associated image")
        for box in self.boxes:
            if box.right > width or box.bottom > height:
                raise ValueError("box is outside the associated image")

    def validate_for(self, image: ImageDocument) -> None:
        """Reject use of this prompt with a differently sized image."""

        if self.image_size != image.size:
            raise ValueError("subject prompt size does not match input image")


@dataclass(frozen=True, slots=True)
class ModelIdentity:
    """Stable source identity for a model-generated value."""

    name: str
    revision: str

    def __post_init__(self) -> None:
        if type(self.name) is not str or type(self.revision) is not str:
            raise TypeError("model name and revision must be strings")
        if not self.name.strip() or not self.revision.strip():
            raise ValueError("model name and revision must not be blank")


@dataclass(frozen=True, slots=True)
class SegmentationCandidate:
    """A probability mask tied to its source and original image size."""

    image_size: tuple[int, int]
    mask: ProbabilityMask
    source: ModelIdentity

    def __post_init__(self) -> None:
        if type(self.image_size) is not tuple or len(self.image_size) != 2:
            raise TypeError("candidate image_size must be a (width, height) tuple")
        if any(type(value) is not int for value in self.image_size):
            raise TypeError("candidate image_size values must have int dtype")
        if type(self.mask) is not ProbabilityMask:
            raise TypeError("candidate mask must be a ProbabilityMask")
        if type(self.source) is not ModelIdentity:
            raise TypeError("candidate source must be a ModelIdentity")
        if self.image_size != (self.mask.width, self.mask.height):
            raise ValueError("candidate mask size does not match image size")


class SegmentationModel(Protocol):
    """Port for automatic subject segmentation."""

    def segment(self, image: ImageDocument) -> SegmentationCandidate:
        """Generate a candidate for ``image``."""
        ...


class InteractiveSegmentationModel(Protocol):
    """Port for segmentation guided by validated user prompts."""

    def segment(self, image: ImageDocument, prompt: SubjectPrompt) -> SegmentationCandidate:
        """Generate a candidate using ``prompt``."""
        ...


class MattingModel(Protocol):
    """Port for producing continuous alpha from an image and trimap."""

    def matte(self, image: ImageDocument, trimap: Trimap) -> AlphaMatte:
        """Produce an alpha matte aligned with ``image``."""
        ...
