import pytest

from extract_entity.domain import (
    AlphaMatte,
    BoxPrompt,
    ImageDocument,
    InteractiveSegmentationModel,
    MattingModel,
    ModelIdentity,
    PointKind,
    PointPrompt,
    ProbabilityMask,
    SegmentationCandidate,
    SegmentationModel,
    SubjectPrompt,
    Trimap,
)
from tests.support.models import (
    InteractiveSegmentationSpy,
    MattingSpy,
    SegmentationSpy,
)


def image(width: int = 2, height: int = 2) -> ImageDocument:
    return ImageDocument(width, height, bytes(width * height * 3))


def candidate(width: int = 2, height: int = 2) -> SegmentationCandidate:
    return SegmentationCandidate(
        (width, height),
        ProbabilityMask(width, height, (0.5,) * (width * height)),
        ModelIdentity("fake-segmenter", "test-v1"),
    )


def test_points_use_xy_coordinates_and_explicit_kind() -> None:
    prompt = SubjectPrompt(
        (3, 2),
        points=(PointPrompt(2, 1, PointKind.POSITIVE), PointPrompt(0, 0, PointKind.NEGATIVE)),
    )
    assert prompt.points[0].x == 2
    assert prompt.points[0].y == 1


@pytest.mark.parametrize("coordinates", [(-1, 0), (0, -1), (3, 0), (0, 2)])
def test_subject_prompt_rejects_out_of_bounds_points(coordinates: tuple[int, int]) -> None:
    with pytest.raises(ValueError, match="outside"):
        SubjectPrompt((3, 2), points=(PointPrompt(*coordinates, PointKind.POSITIVE),))


def test_point_rejects_wrong_coordinate_and_kind_types() -> None:
    with pytest.raises(TypeError, match="int dtype"):
        PointPrompt(True, 0, PointKind.POSITIVE)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="PointKind"):
        PointPrompt(0, 0, "positive")  # type: ignore[arg-type]


def test_box_is_half_open_and_can_reach_image_edges() -> None:
    box = BoxPrompt(0, 0, 3, 2)
    assert SubjectPrompt((3, 2), boxes=(box,)).boxes == (box,)


@pytest.mark.parametrize("box", [BoxPrompt(0, 0, 4, 1), BoxPrompt(0, 0, 1, 3)])
def test_subject_prompt_rejects_out_of_bounds_boxes(box: BoxPrompt) -> None:
    with pytest.raises(ValueError, match="outside"):
        SubjectPrompt((3, 2), boxes=(box,))


@pytest.mark.parametrize("coordinates", [(1, 0, 1, 1), (1, 0, 0, 1), (0, 1, 1, 1)])
def test_box_rejects_empty_or_reversed_edges(coordinates: tuple[int, int, int, int]) -> None:
    with pytest.raises(ValueError, match="positive width and height"):
        BoxPrompt(*coordinates)


def test_box_rejects_negative_and_wrong_dtype_coordinates() -> None:
    with pytest.raises(ValueError, match="negative"):
        BoxPrompt(-1, 0, 1, 1)
    with pytest.raises(TypeError, match="int dtype"):
        BoxPrompt(0, 0, 1.0, 1)  # type: ignore[arg-type]


def test_subject_prompt_requires_content_and_valid_collections() -> None:
    with pytest.raises(ValueError, match="at least one"):
        SubjectPrompt((1, 1))
    with pytest.raises(TypeError, match="tuple of PointPrompt"):
        SubjectPrompt((1, 1), points=[PointPrompt(0, 0, PointKind.POSITIVE)])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="image_size"):
        SubjectPrompt([1, 1], points=(PointPrompt(0, 0, PointKind.POSITIVE),))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="at most one box"):
        SubjectPrompt((2, 2), boxes=(BoxPrompt(0, 0, 1, 1), BoxPrompt(1, 1, 2, 2)))


def test_subject_prompt_validates_its_associated_image() -> None:
    prompt = SubjectPrompt((1, 1), points=(PointPrompt(0, 0, PointKind.POSITIVE),))
    prompt.validate_for(image(1, 1))
    with pytest.raises(ValueError, match="prompt size"):
        prompt.validate_for(image(2, 1))


def test_model_identity_is_non_blank_and_typed() -> None:
    assert ModelIdentity("model", "revision").revision == "revision"
    with pytest.raises(ValueError, match="blank"):
        ModelIdentity(" ", "revision")
    with pytest.raises(TypeError, match="strings"):
        ModelIdentity("model", 1)  # type: ignore[arg-type]


def test_candidate_requires_mask_alignment_and_typed_source() -> None:
    assert candidate().image_size == (2, 2)
    with pytest.raises(ValueError, match="does not match"):
        SegmentationCandidate((1, 1), ProbabilityMask(2, 1, (0.0, 1.0)), ModelIdentity("m", "r"))
    with pytest.raises(TypeError, match="ProbabilityMask"):
        SegmentationCandidate((1, 1), object(), ModelIdentity("m", "r"))  # type: ignore[arg-type]


def test_spies_structurally_satisfy_model_ports_and_record_immutable_calls() -> None:
    source_image = image()
    subject_prompt = SubjectPrompt(
        source_image.size, points=(PointPrompt(0, 0, PointKind.POSITIVE),)
    )
    trimap = Trimap(2, 2, bytes((0, 128, 255, 255)))
    segmentation = SegmentationSpy(candidate())
    interactive = InteractiveSegmentationSpy(candidate())
    matting = MattingSpy(AlphaMatte(2, 2, (0.0, 0.5, 1.0, 1.0)))

    automatic_port: SegmentationModel = segmentation
    interactive_port: InteractiveSegmentationModel = interactive
    matting_port: MattingModel = matting
    assert automatic_port is segmentation
    assert interactive_port is interactive
    assert matting_port is matting
    assert segmentation.segment(source_image) is segmentation.result
    assert interactive.segment(source_image, subject_prompt) is interactive.result
    assert matting.matte(source_image, trimap) is matting.result
    assert segmentation.calls == (source_image,)
    assert interactive.calls == ((source_image, subject_prompt),)
    assert matting.calls == ((source_image, trimap),)


def test_spies_raise_configured_errors_after_recording_calls() -> None:
    source_image = image()
    failure = RuntimeError("expected failure")
    spy = SegmentationSpy(error=failure)
    with pytest.raises(RuntimeError, match="expected failure"):
        spy.segment(source_image)
    assert spy.calls == (source_image,)


def test_spies_reject_spatial_mismatches() -> None:
    source_image = image()
    with pytest.raises(ValueError, match="result size"):
        SegmentationSpy(candidate(1, 1)).segment(source_image)
    prompt = SubjectPrompt((1, 1), points=(PointPrompt(0, 0, PointKind.POSITIVE),))
    with pytest.raises(ValueError, match="prompt size"):
        InteractiveSegmentationSpy(candidate()).segment(source_image, prompt)
    with pytest.raises(ValueError, match="trimap size"):
        MattingSpy(AlphaMatte(2, 2, (1.0,) * 4)).matte(source_image, Trimap(1, 1, b"\x80"))
    with pytest.raises(ValueError, match="result size"):
        MattingSpy(AlphaMatte(1, 1, (1.0,))).matte(source_image, Trimap(2, 2, b"\x80" * 4))
