"""Wrapper objects for Unreal code templates."""

# Standard Library
import copy
import re
from typing import Set


class CodeTemplateError(Exception):
    """Custom exception representing errors encountered with CodeTemplate."""


class CodeTemplate(object):
    TOKEN_RE = re.compile(r"\%([A-Z_]+)\%", flags=re.MULTILINE)

    def __init__(self, name: str, template_string: str = "") -> None:
        self.name: str = name
        self.template_string: str = template_string

    def __repr__(self) -> str:
        """Python interpreter representation of CodeTemplate."""
        return f"<CodeTemplate {self.name}>"

    @property
    def tokens(self) -> Set[str]:
        return {
            token
            for match in CodeTemplate.TOKEN_RE.finditer(self.template_string)
            for token in match.groups()
        }

    def make_instance(self, **tokens: str) -> str:
        missing = self.tokens - set(tokens.keys())
        if len(missing):
            raise CodeTemplateError(
                f"Cannot instantiate template: {self.name} - missing required tokens: {missing}"
            )

        result = copy.copy(self.template_string)
        for token, value in tokens.items():
            result = re.sub(r"\%{}\%".format(token), value, result)

        return result
