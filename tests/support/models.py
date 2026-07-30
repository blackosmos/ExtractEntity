"""Test doubles for the model ports; never imported by production code."""

from dataclasses import dataclass, field

from extract_entity.domain import (
    AlphaMatte,
    ImageDocument,
    SegmentationCandidate,
    SubjectPrompt,
    Trimap,
)


def _image_calls() -> list[ImageDocument]:
    return []


def _interactive_calls() -> list[tuple[ImageDocument, SubjectPrompt]]:
    return []


def _matting_calls() -> list[tuple[ImageDocument, Trimap]]:
    return []


@dataclass(slots=True)
class SegmentationSpy:
    result: SegmentationCandidate | None = None
    error: Exception | None = None
    _calls: list[ImageDocument] = field(default_factory=_image_calls, init=False)

    @property
    def calls(self) -> tuple[ImageDocument, ...]:
        return tuple(self._calls)

    def segment(self, image: ImageDocument) -> SegmentationCandidate:
        self._calls.append(image)
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise RuntimeError("segmentation spy has no configured result")
        if self.result.image_size != image.size:
            raise ValueError("segmentation result size does not match input image")
        return self.result


@dataclass(slots=True)
class InteractiveSegmentationSpy:
    result: SegmentationCandidate | None = None
    error: Exception | None = None
    _calls: list[tuple[ImageDocument, SubjectPrompt]] = field(
        default_factory=_interactive_calls, init=False
    )

    @property
    def calls(self) -> tuple[tuple[ImageDocument, SubjectPrompt], ...]:
        return tuple(self._calls)

    def segment(self, image: ImageDocument, prompt: SubjectPrompt) -> SegmentationCandidate:
        self._calls.append((image, prompt))
        prompt.validate_for(image)
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise RuntimeError("interactive segmentation spy has no configured result")
        if self.result.image_size != image.size:
            raise ValueError("segmentation result size does not match input image")
        return self.result


@dataclass(slots=True)
class MattingSpy:
    result: AlphaMatte | None = None
    error: Exception | None = None
    _calls: list[tuple[ImageDocument, Trimap]] = field(default_factory=_matting_calls, init=False)

    @property
    def calls(self) -> tuple[tuple[ImageDocument, Trimap], ...]:
        return tuple(self._calls)

    def matte(self, image: ImageDocument, trimap: Trimap) -> AlphaMatte:
        self._calls.append((image, trimap))
        if (trimap.width, trimap.height) != image.size:
            raise ValueError("trimap size does not match input image")
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise RuntimeError("matting spy has no configured result")
        if (self.result.width, self.result.height) != image.size:
            raise ValueError("matting result size does not match input image")
        return self.result
