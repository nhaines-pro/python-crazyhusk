"""Monkeypatching for module-level issues, such as mocking winreg"""

# Future Standard Library
from __future__ import annotations

# Standard Library
import sys
from typing import Any, Optional, Type

# Third Party
from typing_extensions import final


@final
class HKEYType:
    def __bool__(self) -> bool:
        ...

    def __int__(self) -> int:
        ...

    def __enter__(self) -> HKEYType:
        ...

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[Type[BaseException]],
        exc_tb: Optional[Type[BaseException]],
    ) -> bool | None:
        ...

    def Close(self) -> None:
        ...

    def Detach(self) -> int:
        ...


def OpenKey(key: Any, sub_key: str, reserved: int = 0, access: int = 0) -> HKEYType:
    raise OSError()


def OpenKeyEx(key: Any, sub_key: str, reserved: int = 0, access: int = 0) -> HKEYType:
    raise OSError()


def QueryValueEx(__key: Any, __name: str) -> tuple[Any, int]:
    raise OSError()


module = type(sys)("winreg")
module.OpenKey = OpenKey
module.OpenKeyEx = OpenKeyEx
module.QueryValueEx = QueryValueEx
module.HKEY_CURRENT_USER = 1
module.HKEY_LOCAL_MACHINE = 1
sys.modules["winreg"] = module
