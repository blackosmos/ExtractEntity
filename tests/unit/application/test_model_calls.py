from dataclasses import dataclass, field

import pytest

from extract_entity.application import (
    run_interactive_segmentation,
    run_matting,
    run_segmentation,
)
from extract_entity.domain import (
    AlphaMatte,
    ImageDocument,
    ModelIdentity,
    PointKind,
    PointPrompt,
    ProbabilityMask,
    SegmentationCandidate,
    SubjectPrompt,
    Trimap,
)
from tests.support.models import (
    InteractiveSegmentationSpy,
    MattingSpy,
    SegmentationSpy,
)


def image(width: int = 2, height: int = 1) -> ImageDocument:
    return ImageDocument(width, height, bytes(width * height * 3))


def candidate(width: int = 2, height: int = 1) -> SegmentationCandidate:
    return SegmentationCandidate(
        (width, height),
        ProbabilityMask(width, height, (0.5,) * (width * height)),
        ModelIdentity("fake", "v1"),
    )


def image_calls() -> list[ImageDocument]:
    return []


def interactive_calls() -> list[tuple[ImageDocument, SubjectPrompt]]:
    return []


def matting_calls() -> list[tuple[ImageDocument, Trimap]]:
    return []


@dataclass
class UntrustedSegmentationAdapter:
    output: object
    calls: list[ImageDocument] = field(default_factory=image_calls)

    def segment(self, source: ImageDocument) -> object:
        self.calls.append(source)
        return self.output


@dataclass
class UntrustedInteractiveAdapter:
    output: object
    calls: list[tuple[ImageDocument, SubjectPrompt]] = field(default_factory=interactive_calls)

    def segment(self, source: ImageDocument, prompt: SubjectPrompt) -> object:
        self.calls.append((source, prompt))
        return self.output


@dataclass
class UntrustedMattingAdapter:
    output: object
    calls: list[tuple[ImageDocument, Trimap]] = field(default_factory=matting_calls)

    def matte(self, source: ImageDocument, trimap: Trimap) -> object:
        self.calls.append((source, trimap))
        return self.output


def test_automatic_boundary_preserves_valid_candidate_and_records_call() -> None:
    source = image()
    expected = candidate()
    model = SegmentationSpy(expected)

    assert run_segmentation(model, source) is expected
    assert model.calls == (source,)


def test_automatic_boundary_rejects_bad_input_before_model_call() -> None:
    model = SegmentationSpy(candidate())
    with pytest.raises(TypeError, match="ImageDocument"):
        run_segmentation(model, object())  # type: ignore[arg-type]
    assert model.calls == ()


@pytest.mark.parametrize("output", [None, object(), ProbabilityMask(2, 1, (0.0, 1.0))])
def test_automatic_boundary_rejects_wrong_result_type(output: object) -> None:
    model = UntrustedSegmentationAdapter(output)
    with pytest.raises(TypeError, match="SegmentationCandidate"):
        run_segmentation(model, image())  # type: ignore[arg-type]
    assert len(model.calls) == 1


@pytest.mark.parametrize("size", [(1, 1), (2, 2), (1, 2)])
def test_automatic_boundary_rejects_wrong_or_transposed_result_size(
    size: tuple[int, int],
) -> None:
    model = UntrustedSegmentationAdapter(candidate(*size))
    with pytest.raises(ValueError, match="candidate size"):
        run_segmentation(model, image())  # type: ignore[arg-type]
    assert len(model.calls) == 1


def test_automatic_boundary_propagates_model_exception_unchanged() -> None:
    failure = RuntimeError("model failed")
    model = SegmentationSpy(error=failure)
    with pytest.raises(RuntimeError) as caught:
        run_segmentation(model, image())
    assert caught.value is failure
    assert len(model.calls) == 1


def test_interactive_boundary_preserves_result_and_records_call() -> None:
    source = image()
    prompt = SubjectPrompt(source.size, points=(PointPrompt(1, 0, PointKind.POSITIVE),))
    expected = candidate()
    model = InteractiveSegmentationSpy(expected)

    assert run_interactive_segmentation(model, source, prompt) is expected
    assert model.calls == ((source, prompt),)


def test_interactive_boundary_rejects_prompt_before_model_call() -> None:
    source = image()
    model = InteractiveSegmentationSpy(candidate())
    wrong_size = SubjectPrompt((1, 1), points=(PointPrompt(0, 0, PointKind.POSITIVE),))
    with pytest.raises(ValueError, match="prompt size"):
        run_interactive_segmentation(model, source, wrong_size)
    assert model.calls == ()


def test_interactive_boundary_rejects_bad_image_before_model_call() -> None:
    source = image()
    model = InteractiveSegmentationSpy(candidate())
    prompt = SubjectPrompt((2, 1), points=(PointPrompt(0, 0, PointKind.POSITIVE),))
    with pytest.raises(TypeError, match="ImageDocument"):
        run_interactive_segmentation(model, object(), prompt)  # type: ignore[arg-type]
    assert model.calls == ()
    with pytest.raises(TypeError, match="SubjectPrompt"):
        run_interactive_segmentation(model, source, object())  # type: ignore[arg-type]
    assert model.calls == ()


def test_interactive_boundary_rejects_wrong_result_type_and_size() -> None:
    source = image()
    prompt = SubjectPrompt(source.size, points=(PointPrompt(0, 0, PointKind.NEGATIVE),))
    wrong_type = UntrustedInteractiveAdapter(object())
    with pytest.raises(TypeError, match="SegmentationCandidate"):
        run_interactive_segmentation(wrong_type, source, prompt)  # type: ignore[arg-type]
    assert len(wrong_type.calls) == 1
    wrong_size = UntrustedInteractiveAdapter(candidate(1, 1))
    with pytest.raises(ValueError, match="candidate size"):
        run_interactive_segmentation(wrong_size, source, prompt)  # type: ignore[arg-type]
    assert len(wrong_size.calls) == 1


def test_interactive_boundary_propagates_model_exception_unchanged() -> None:
    source = image()
    prompt = SubjectPrompt(source.size, points=(PointPrompt(0, 0, PointKind.POSITIVE),))
    failure = LookupError("interactive failed")
    model = InteractiveSegmentationSpy(error=failure)
    with pytest.raises(LookupError) as caught:
        run_interactive_segmentation(model, source, prompt)
    assert caught.value is failure
    assert len(model.calls) == 1


def test_matting_boundary_preserves_valid_alpha_and_records_call() -> None:
    source = image()
    trimap = Trimap(2, 1, b"\x00\xff")
    expected = AlphaMatte(2, 1, (0.0, 1.0))
    model = MattingSpy(expected)

    assert run_matting(model, source, trimap) is expected
    assert model.calls == ((source, trimap),)


def test_matting_boundary_rejects_inputs_before_model_call() -> None:
    source = image()
    model = MattingSpy(AlphaMatte(2, 1, (0.0, 1.0)))
    with pytest.raises(TypeError, match="ImageDocument"):
        run_matting(model, object(), Trimap(2, 1, b"\x00\xff"))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Trimap"):
        run_matting(model, source, object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="trimap size"):
        run_matting(model, source, Trimap(1, 2, b"\x00\xff"))
    assert model.calls == ()


@pytest.mark.parametrize("output", [None, object(), candidate()])
def test_matting_boundary_rejects_wrong_result_type(output: object) -> None:
    model = UntrustedMattingAdapter(output)
    with pytest.raises(TypeError, match="AlphaMatte"):
        run_matting(model, image(), Trimap(2, 1, b"\x00\xff"))  # type: ignore[arg-type]
    assert len(model.calls) == 1


@pytest.mark.parametrize("size", [(1, 1), (2, 2), (1, 2)])
def test_matting_boundary_rejects_wrong_or_transposed_result_size(
    size: tuple[int, int],
) -> None:
    width, height = size
    model = UntrustedMattingAdapter(AlphaMatte(width, height, (1.0,) * (width * height)))
    with pytest.raises(ValueError, match="alpha matte size"):
        run_matting(model, image(), Trimap(2, 1, b"\x00\xff"))  # type: ignore[arg-type]
    assert len(model.calls) == 1


def test_matting_boundary_propagates_model_exception_unchanged() -> None:
    failure = ArithmeticError("matting failed")
    model = MattingSpy(error=failure)
    with pytest.raises(ArithmeticError) as caught:
        run_matting(model, image(), Trimap(2, 1, b"\x00\xff"))
    assert caught.value is failure
    assert len(model.calls) == 1
