# Third Party
import pytest

# CrazyHusk
from crazyhusk import code


def test_codetemplate_init():
    with pytest.raises(TypeError):
        code.CodeTemplate()

    empty_template = code.CodeTemplate("empty")
    assert empty_template.name == "empty"
    assert empty_template.template_string == ""
    assert repr(empty_template) == "<CodeTemplate empty>"
    assert type(empty_template.tokens) is set
    assert empty_template.tokens == set()
