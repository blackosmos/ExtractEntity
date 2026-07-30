import pytest

from extract_entity.application import TrimapThresholds, extract_image
from extract_entity.domain import (
    AlphaMatte,
    ImageDocument,
    ModelIdentity,
    ProbabilityMask,
    SegmentationCandidate,
    Trimap,
    TrimapValue,
)
from tests.support.models import MattingSpy, SegmentationSpy


def make_image() -> ImageDocument:
    return ImageDocument(width=3, height=2, pixels=bytes(range(18)))


def make_candidate() -> SegmentationCandidate:
    return SegmentationCandidate(
        image_size=(3, 2),
        mask=ProbabilityMask(width=3, height=2, values=(0.0, 0.2, 0.5, 0.8, 1.0, 0.3)),
        source=ModelIdentity(name="fake", revision="test"),
    )


def test_extract_image_runs_each_stage_once_and_preserves_result_identity() -> None:
    image = make_image()
    candidate = make_candidate()
    alpha = AlphaMatte(width=3, height=2, values=(0.0, 0.1, 0.5, 0.9, 1.0, 0.4))
    segmenter = SegmentationSpy(result=candidate)
    matter = MattingSpy(result=alpha)

    result = extract_image(
        image,
        segmenter,
        matter,
        TrimapThresholds(background=0.2, foreground=0.8),
    )

    assert len(segmenter.calls) == 1
    assert segmenter.calls[0] is image
    assert len(matter.calls) == 1
    matte_image, trimap = matter.calls[0]
    assert matte_image is image
    assert trimap == Trimap(
        width=3,
        height=2,
        values=bytes(
            (
                TrimapValue.BACKGROUND,
                TrimapValue.BACKGROUND,
                TrimapValue.UNKNOWN,
                TrimapValue.FOREGROUND,
                TrimapValue.FOREGROUND,
                TrimapValue.UNKNOWN,
            )
        ),
    )
    assert result.image is image
    assert result.alpha is alpha


class InvalidSegmentationModel:
    def segment(self, image: ImageDocument) -> object:
        return object()


class InvalidMattingModel:
    def matte(self, image: ImageDocument, trimap: Trimap) -> object:
        return object()


class RawSegmentationModel:
    def __init__(self, result: SegmentationCandidate) -> None:
        self.result = result

    def segment(self, image: ImageDocument) -> SegmentationCandidate:
        return self.result


class RawMattingModel:
    def __init__(self, result: AlphaMatte) -> None:
        self.result = result

    def matte(self, image: ImageDocument, trimap: Trimap) -> AlphaMatte:
        return self.result


def test_extract_image_propagates_segmentation_error_by_identity() -> None:
    error = RuntimeError("segmentation failed")
    matter = MattingSpy()
    with pytest.raises(RuntimeError) as caught:
        extract_image(make_image(), SegmentationSpy(error=error), matter)
    assert caught.value is error
    assert matter.calls == ()


def test_extract_image_propagates_matting_error_by_identity() -> None:
    error = KeyError("matting")
    with pytest.raises(KeyError) as caught:
        extract_image(
            make_image(), SegmentationSpy(result=make_candidate()), MattingSpy(error=error)
        )
    assert caught.value is error


def test_invalid_segmentation_output_stops_before_matting() -> None:
    matter = MattingSpy()
    with pytest.raises(TypeError, match="SegmentationCandidate"):
        extract_image(make_image(), InvalidSegmentationModel(), matter)  # type: ignore[arg-type]
    assert matter.calls == ()


def test_invalid_threshold_configuration_stops_before_models() -> None:
    segmenter = SegmentationSpy(result=make_candidate())
    matter = MattingSpy()
    with pytest.raises(TypeError, match="TrimapThresholds"):
        extract_image(
            make_image(),
            segmenter,
            matter,
            thresholds=object(),  # type: ignore[arg-type]
        )
    assert segmenter.calls == ()
    assert matter.calls == ()


def test_invalid_matting_output_is_rejected() -> None:
    with pytest.raises(TypeError, match="AlphaMatte"):
        extract_image(
            make_image(),
            SegmentationSpy(result=make_candidate()),
            InvalidMattingModel(),  # type: ignore[arg-type]
        )


def test_spatially_misaligned_segmentation_is_rejected_before_matting() -> None:
    candidate = SegmentationCandidate(
        image_size=(2, 2),
        mask=ProbabilityMask(width=2, height=2, values=(0.0, 0.5, 0.5, 1.0)),
        source=ModelIdentity(name="fake", revision="test"),
    )
    matter = MattingSpy()
    with pytest.raises(ValueError, match="candidate size"):
        extract_image(make_image(), RawSegmentationModel(candidate), matter)
    assert matter.calls == ()


def test_spatially_misaligned_alpha_is_rejected() -> None:
    alpha = AlphaMatte(width=2, height=2, values=(0.0, 0.5, 0.5, 1.0))
    with pytest.raises(ValueError, match="alpha matte size"):
        extract_image(
            make_image(),
            SegmentationSpy(result=make_candidate()),
            RawMattingModel(alpha),
        )


def test_extract_image_calls_segmentation_before_matting() -> None:
    events: list[str] = []
    candidate = make_candidate()
    alpha = AlphaMatte(width=3, height=2, values=(0.5,) * 6)

    class OrderedSegmentationModel:
        def segment(self, image: ImageDocument) -> SegmentationCandidate:
            events.append("segmentation")
            return candidate

    class OrderedMattingModel:
        def matte(self, image: ImageDocument, trimap: Trimap) -> AlphaMatte:
            events.append("matting")
            return alpha

    extract_image(make_image(), OrderedSegmentationModel(), OrderedMattingModel())
    assert events == ["segmentation", "matting"]
