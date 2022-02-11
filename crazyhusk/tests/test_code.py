# Third Party
import pytest

# CrazyHusk
from crazyhusk import code


@pytest.fixture(scope="function")
def empty_code_template():
    yield code.CodeTemplate("")


def test_codetemplate_init(empty_code_template):
    with pytest.raises(TypeError):
        code.CodeTemplate()

    assert empty_code_template.name == ""
    assert empty_code_template.template_string == ""
    assert repr(empty_code_template) == "<CodeTemplate >"
    assert type(empty_code_template.tokens) is set
    assert empty_code_template.tokens == set()
