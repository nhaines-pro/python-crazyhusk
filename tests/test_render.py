# Standard Library
from typing import Any, Dict, Optional, Tuple, Type

# Third Party
import pytest

# CrazyHusk
from crazyhusk import render


@pytest.mark.parametrize(
    "MovieSceneCaptureType,raises",
    [
        (None, render.UnrealRenderError),
        (123, render.UnrealRenderError),
        ("", render.UnrealRenderError),
        ("/Game", render.UnrealRenderError),
        ("/Engine", render.UnrealRenderError),
        ("/Script", None),
    ],
)
def test_valid_movie_capture_type(
    MovieSceneCaptureType: Any, raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert (
                render.valid_movie_capture_type(
                    MovieSceneCaptureType=MovieSceneCaptureType
                )
                is None
            )
    else:
        assert (
            render.valid_movie_capture_type(MovieSceneCaptureType=MovieSceneCaptureType)
            is None
        )


@pytest.mark.parametrize(
    "LevelSequence,raises",
    [
        (None, render.UnrealRenderError),
        (123, render.UnrealRenderError),
        ("", render.UnrealRenderError),
        ("/Game", None),
    ],
)
def test_valid_level_sequence(
    LevelSequence: Any, raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert render.valid_level_sequence(LevelSequence=LevelSequence) is None
    else:
        assert render.valid_level_sequence(LevelSequence=LevelSequence) is None


def test_valid_default_params_null() -> None:
    assert render.valid_default_params() is None


@pytest.mark.parametrize(
    "Shot,raises",
    [
        (123, render.UnrealRenderError),
    ],
)
def test_valid_default_params_shot(
    Shot: Any, raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert (
                render.valid_default_params(
                    MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                    Shot=Shot,
                )
                is None
            )
    else:
        assert (
            render.valid_default_params(
                MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                Shot=Shot,
            )
            is None
        )


@pytest.mark.parametrize(
    "MovieFormat,raises",
    [
        (123, render.UnrealRenderError),
        ("", render.UnrealRenderError),
        ("abc", render.UnrealRenderError),
        (None, None),
        ("JPG", None),
        ("BMP", None),
        ("PNG", None),
        ("Video", None),
        ("CustomRenderPasses", None),
    ],
)
def test_valid_default_params_movie_format(
    MovieFormat: Any, raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert (
                render.valid_default_params(
                    MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                    MovieFormat=MovieFormat,
                )
                is None
            )
    else:
        assert (
            render.valid_default_params(
                MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                MovieFormat=MovieFormat,
            )
            is None
        )


@pytest.mark.parametrize(
    "MovieName,raises",
    [
        (123, render.UnrealRenderError),
        (None, None),
        ("", None),
        ("test_movie", None),
    ],
)
def test_valid_default_params_movie_name(
    MovieName: Any, raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert (
                render.valid_default_params(
                    MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                    MovieName=MovieName,
                )
                is None
            )
    else:
        assert (
            render.valid_default_params(
                MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                MovieName=MovieName,
            )
            is None
        )


@pytest.mark.parametrize(
    "CustomRenderPasses,switches,params,raises",
    [
        (None, (), {}, None),
        (123, (), {}, render.UnrealRenderError),
        (123, (), {"MovieFormat": "CustomRenderPasses"}, render.UnrealRenderError),
        ("AmbientOcclusion", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("BaseColor", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("CustomDepth", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("CustomDepthWorldUnits", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("CustomStencil", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("FinalImage", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("MaterialAO", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("Metallic", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("Opacity", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("PostTonemapHDRColor", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("Roughness", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("SceneDepth", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("SceneDepthWorldUnits", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("SeparateTranslucencyA", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("SeparateTranslucencyRGB", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("ShadingModel", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("Specular", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("SubsurfaceColor", (), {"MovieFormat": "CustomRenderPasses"}, None),
        ("WorldNormal", (), {"MovieFormat": "CustomRenderPasses"}, None),
        (
            "WorldNormal",
            (),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": None},
            None,
        ),
        (
            "WorldNormal",
            (),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": 123},
            render.UnrealRenderError,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": 123},
            render.UnrealRenderError,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": "HCGM_Rec709"},
            None,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": "HCGM_P3DCI"},
            None,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": "HCGM_Rec2020"},
            None,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": "HCGM_ACES"},
            None,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": "HCGM_ACEScg"},
            None,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "CaptureGamut": "HCGM_MAX"},
            None,
        ),
        (
            "WorldNormal",
            (),
            {"MovieFormat": "CustomRenderPasses", "HDRCompressionQuality": None},
            None,
        ),
        (
            "WorldNormal",
            (),
            {"MovieFormat": "CustomRenderPasses", "HDRCompressionQuality": 123},
            render.UnrealRenderError,
        ),
        (
            "WorldNormal",
            ("CaptureFramesInHDR",),
            {"MovieFormat": "CustomRenderPasses", "HDRCompressionQuality": 123},
            None,
        ),
    ],
)
def test_valid_default_params_custom_render_passes(
    CustomRenderPasses: Any,
    switches: Tuple[str],
    params: Dict[str, str],
    raises: Optional[Type[BaseException]],
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert (
                render.valid_default_params(
                    *switches,
                    MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                    CustomRenderPasses=CustomRenderPasses,
                    **params
                )
                is None
            )
    else:
        assert (
            render.valid_default_params(
                *switches,
                MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
                CustomRenderPasses=CustomRenderPasses,
                **params
            )
            is None
        )
