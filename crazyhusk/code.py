"""Wrapper objects for Unreal code templates."""
# Standard Library
import copy
import re


class CodeTemplateError(Exception):
    """Custom exception representing errors encountered with CodeTemplate."""


class CodeTemplate(object):
    TOKEN_RE = re.compile(r".*\%([A-Z_]+)\%.*")

    def __init__(self, name, template_string=""):
        self.name = name
        self.template_string = template_string

    def __repr__(self):
        """Python interpreter representation of CodeTemplate."""
        return f"<CodeTemplate {self.name}>"

    @property
    def tokens(self):
        return {
            token
            for match in CodeTemplate.TOKEN_RE.finditer(self.template_string)
            for token in match.groups()
        }

    def make_instance(self, **tokens):
        missing = self.tokens - set(tokens.keys())
        if len(missing):
            raise CodeTemplateError(
                f"Cannot instantiate template: {self.name} - missing required tokens: {missing}"
            )

        result = copy.copy(self.template_string)
        for token, value in tokens.items():
            result = re.sub(f"\%{token}\%", value, result)

        return result
