"""Tests for math compression rules."""

from mdziper.rules.math_rules import (
    command_brace_letter,
    remove_brace_spaces,
    remove_comma_spaces,
    remove_command_spaces,
    remove_operator_spaces,
    remove_pipe_spaces,
)


def test_remove_operator_spaces():
    assert remove_operator_spaces("a + b = c") == "a+b=c"
    assert remove_operator_spaces("x - y > 0") == "x-y>0"


def test_remove_operator_spaces_named():
    # remove_operator_spaces removes spaces around \leq but doesn't add {}
    # (that's command_brace_letter's job)
    assert remove_operator_spaces(r"a \leq b") == r"a\leqb"
    result = remove_operator_spaces(r"x \leq 1")
    assert r"\leq" in result


def test_remove_command_spaces_before_nonletter():
    assert remove_command_spaces(r"\alpha + x") == r"\alpha+ x"


def test_command_brace_letter():
    assert command_brace_letter(r"\alpha x") == r"\alpha{}x"
    assert command_brace_letter(r"\beta y") == r"\beta{}y"


def test_remove_comma_spaces():
    assert remove_comma_spaces("f(x, y, z)") == "f(x,y,z)"


def test_remove_brace_spaces():
    assert remove_brace_spaces(r"\frac{ a }{ b }") == r"\frac{a}{b}"


def test_remove_pipe_spaces():
    assert remove_pipe_spaces(r"a \| b") == r"a\|b"


def test_preserve_text_command():
    """Spaces inside \\text{} must be preserved."""
    result = remove_operator_spaces(r"\text{hello world} + x")
    assert "hello world" in result


def test_full_math_pipeline():
    """Test applying all math rules in sequence."""
    text = r"\frac{ 1 }{ N } \sum_{i=1}^{N} \ell(f(x_i), y_i)"
    text = remove_brace_spaces(text)
    text = remove_comma_spaces(text)
    text = remove_operator_spaces(text)
    text = remove_command_spaces(text)
    text = command_brace_letter(text)
    # Should have significantly fewer spaces
    assert text.count(" ") < 5
