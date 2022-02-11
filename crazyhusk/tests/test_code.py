# Third Party
import pytest

# CrazyHusk
from crazyhusk import code


@pytest.fixture(scope="function")
def null_code_template():
    yield code.CodeTemplate(None)

@pytest.fixture(scope="function")
def empty_code_template():
    yield code.CodeTemplate("")

@pytest.fixture(scope="function")
def basic_code_template():
    yield code.CodeTemplate("Basic", "%TEST_TOKEN%")

@pytest.fixture(scope="function")
def multiline_basic_code_template():
    yield code.CodeTemplate("MultilineBasic", "//%TEST_TOKEN%\n//%TEST_TOKEN%")

@pytest.fixture(scope="function")
def multiline_multitoken_code_template():
    yield code.CodeTemplate("MultilineMultitoken", r"//%TEST_TOKEN_1%\n//%TEST_TOKEN_2%")

@pytest.mark.parametrize(
    "code_template,name,template_string,tokens",
    [
        ("null_code_template", None, "", set()),
        ("empty_code_template", "", "", set()),
        ("basic_code_template", "Basic", "%TEST_TOKEN%", {"TEST_TOKEN"}),
        ("multiline_basic_code_template", "MultilineBasic", "//%TEST_TOKEN%\n//%TEST_TOKEN%", {"TEST_TOKEN"}),
        ("multiline_multitoken_code_template", "MultilineMultitoken", r"//%TEST_TOKEN_1%\n//%TEST_TOKEN_2%", set()),
    ]
)
def test_codetemplate_init(code_template, name, template_string, tokens, request):
    code_template = request.getfixturevalue(code_template)
    assert code_template.name == name
    assert code_template.template_string == template_string
    assert repr(code_template) == f"<CodeTemplate {code_template.name}>"
    assert type(code_template.tokens) is set
    assert code_template.tokens == tokens

@pytest.mark.parametrize(
    "code_template,tokens,raises,expected",
    [
        ("null_code_template", {}, None, ""),
        ("empty_code_template", {}, None, ""),
        ("basic_code_template", {}, code.CodeTemplateError, ""),
        ("basic_code_template", {'TEST_TOKEN':"test"}, None, "test"),
        ("multiline_basic_code_template", {'TEST_TOKEN':"test"}, None, "//test\n//test"),
        ("multiline_multitoken_code_template", {'TEST_TOKEN_1':"test1", 'TEST_TOKEN_2':"test2"}, None, r"//test1\n//test2"),
    ]
)
def test_codetemplate_make_instance(code_template, tokens, raises, expected, request):
    code_template = request.getfixturevalue(code_template)
    if raises is not None:
        with pytest.raises(raises):
            code_template.make_instance(**tokens)
    else:
        assert code_template.make_instance(**tokens) == expected
