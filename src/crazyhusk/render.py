"""Render utilities for crazyhusk Unreal Engine object wrappers."""


class UnrealRenderError(Exception):
    """Custom exception representing errors encountered with rendering."""


def valid_movie_capture_type(*switches: str, **params: str) -> None:
    """Determine whether the render's MovieSceneCaptureType is valid or raise UnrealRenderError."""
    MovieSceneCaptureType = params.get("MovieSceneCaptureType")
    if MovieSceneCaptureType is None:
        raise UnrealRenderError(
            "MovieSceneCaptureType is required and must not be None."
        )
    if not isinstance(MovieSceneCaptureType, str):
        raise UnrealRenderError(
            f"MovieSceneCaptureType must be stringlike, got: {MovieSceneCaptureType!r}"
        )
    if not MovieSceneCaptureType.startswith("/Script"):
        raise UnrealRenderError(
            f"MovieSceneCaptureType must be declared as a /Script object path, got: {MovieSceneCaptureType}"
        )


def valid_level_sequence(*switches: str, **params: str) -> None:
    """Determine whether the render's LevelSequence is valid or raise UnrealRenderError."""
    LevelSequence = params.get("LevelSequence")
    if LevelSequence is None:
        raise UnrealRenderError("LevelSequence is required and must not be None.")
    if not isinstance(LevelSequence, str):
        raise UnrealRenderError(
            f"LevelSequence must be stringlike, got: {LevelSequence!r}"
        )
    if not LevelSequence.startswith("/Game"):
        raise UnrealRenderError(
            f"LevelSequence must be declared as a /Game object path, got: {LevelSequence}"
        )


def valid_default_params(*switches: str, **params: str) -> None:
    """Determine whether the default MovieSceneCaptureType is valid for the provided parameters or raise UnrealRenderError."""
    if (
        params.get("MovieSceneCaptureType")
        == "/Script/MovieSceneCapture.AutomatedLevelSequenceCapture"
    ):
        Shot = params.get("Shot")
        if Shot is not None and not isinstance(Shot, str):
            raise UnrealRenderError(f"Shot must be stringlike, got: {Shot!r}")

        MovieFormat = params.get("MovieFormat")
        if MovieFormat is not None:
            if not isinstance(MovieFormat, str):
                raise UnrealRenderError(
                    f"MovieFormat must be stringlike, got: {MovieFormat!r}"
                )
            if MovieFormat.lower() not in {
                "jpg",
                "bmp",
                "png",
                "video",
                "customrenderpasses",
            }:
                raise UnrealRenderError(f"Invalid MovieFormat: {MovieFormat}")

        MovieName = params.get("MovieName")
        if MovieName is not None:
            if not isinstance(MovieName, str):
                raise UnrealRenderError(
                    f"MovieName must be stringlike, got: {MovieName!r}"
                )

        CustomRenderPasses = params.get("CustomRenderPasses")
        if CustomRenderPasses is not None:
            if MovieFormat != "CustomRenderPasses":
                raise UnrealRenderError(
                    "CustomRenderPasses parameter requires -MovieFormat=CustomRenderPasses to be set."
                )
            if CustomRenderPasses not in {
                "AmbientOcclusion",
                "BaseColor",
                "CustomDepth",
                "CustomDepthWorldUnits",
                "CustomStencil",
                "FinalImage",
                "MaterialAO",
                "Metallic",
                "Opacity",
                "PostTonemapHDRColor",
                "Roughness",
                "SceneColor",
                "SceneDepth",
                "SceneDepthWorldUnits",
                "SeparateTranslucencyA",
                "SeparateTranslucencyRGB",
                "ShadingModel",
                "Specular",
                "SubsurfaceColor",
                "WorldNormal",
            }:
                raise UnrealRenderError(
                    f"-CustomRenderPasses={CustomRenderPasses} is not a valid target name."
                )

            CaptureGamut = params.get("CaptureGamut")
            if CaptureGamut is not None:
                if "CaptureFramesInHDR" not in switches:
                    raise UnrealRenderError(
                        f"CaptureGamut requires -CaptureFramesInHDR to be set."
                    )
                if CaptureGamut not in {
                    "HCGM_Rec709",
                    "HCGM_P3DCI",
                    "HCGM_Rec2020",
                    "HCGM_ACES",
                    "HCGM_ACEScg",
                    "HCGM_MAX",
                }:
                    raise UnrealRenderError(
                        f"-CaptureGamut={CaptureGamut} is not a valid gamut name."
                    )

            HDRCompressionQuality = params.get("HDRCompressionQuality")
            if HDRCompressionQuality is not None:
                if "CaptureFramesInHDR" not in switches:
                    raise UnrealRenderError(
                        f"HDRCompressionQuality requires -CaptureFramesInHDR to be set."
                    )
