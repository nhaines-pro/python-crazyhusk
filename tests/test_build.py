# Future Standard Library
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any, Iterable, Optional

# Third Party
import pytest

# CrazyHusk
from crazyhusk import build

if TYPE_CHECKING:
    # CrazyHusk
    from crazyhusk.engine import UnrealEngine


class MockBuildable(build.Buildable):
    def __init__(self) -> None:
        super().__init__()

    @property
    def engine(self) -> Optional[UnrealEngine]:
        return super().engine

    def get_build_command(
        self,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        platform: Optional[str] = None,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> Iterable[str]:
        return super().get_build_command(
            target, configuration, platform, *extra_switches, **extra_parameters
        )

    def is_buildable(self) -> bool:
        return super().is_buildable()


def test_buildable(monkeypatch: Any) -> None:
    with pytest.raises(TypeError):
        assert build.Buildable() is None

    mb = MockBuildable()
    with pytest.raises(NotImplementedError):
        assert mb.is_buildable() is None
    with pytest.raises(NotImplementedError):
        assert mb.engine is None
    with pytest.raises(NotImplementedError):
        assert mb.get_build_command() is None

    assert mb.is_valid_build_target("Game")
    assert not mb.is_valid_build_target(None)
    assert mb.is_valid_build_platform("Win32")
    assert not mb.is_valid_build_platform(None)
    assert mb.is_valid_build_configuration("Development")
    assert not mb.is_valid_build_configuration(None)
    assert mb.default_build_target() == "Editor"
    assert mb.default_build_configuration() == "Development"

    assert isinstance(mb.default_local_platform(), str)

    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert mb.default_local_platform() == "Win64"
    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert mb.default_local_platform() == "Linux"
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    assert mb.default_local_platform() == "Mac"
    monkeypatch.setattr("platform.system", lambda: "Invalid")
    with pytest.raises(NotImplementedError):
        assert mb.default_local_platform() is None


def test_unreal_build() -> None:
    mb = MockBuildable()
    b = build.UnrealBuild(mb)
    assert b is not None
    assert b.target is not None
    assert b.configuration is not None
    assert b.platform is not None

    b = build.UnrealBuild(mb, target="Game")
    assert b.target is not None
    b.target = None
    assert b.target is not None

    b = build.UnrealBuild(mb, configuration="Debug")
    assert b.configuration is not None
    b.configuration = None
    assert b.configuration is not None

    b = build.UnrealBuild(mb, build_platform="Linux")
    assert b.platform is not None
    b.platform = None
    assert b.platform is not None
