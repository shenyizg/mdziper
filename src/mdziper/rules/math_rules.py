"""Compression rules for LaTeX math segments.

All rules here are standard-mode safe: LaTeX rendering ignores whitespace,
so removing spaces in math never changes the rendered output.
"""

import re

from . import registry

# --- Helpers ---

_TEXT_CMD_RE = re.compile(r"\\text\w*\{[^}]*\}")


def _protect_text_commands(math: str) -> tuple:
    """Replace \\text{...} with placeholders to protect their spaces."""
    placeholders = {}
    counter = [0]

    def _replace(m):
        key = f"\x00TEXT{counter[0]}\x00"
        placeholders[key] = m.group()
        counter[0] += 1
        return key

    protected = _TEXT_CMD_RE.sub(_replace, math)
    return protected, placeholders


def _restore_text_commands(math: str, placeholders: dict) -> str:
    for key, value in placeholders.items():
        math = math.replace(key, value)
    return math


# --- Rules ---


@registry.register("S05", "standard", "math", "Remove spaces around operators in LaTeX")
def remove_operator_spaces(text: str) -> str:
    text, ph = _protect_text_commands(text)
    # Spaces around =, +, -, <, >, \leq, \geq, \neq, \approx, etc.
    text = re.sub(r"\s*([+\-=<>])\s*", r"\1", text)
    # Spaces around named operators like \leq, \geq, \neq, \approx, \sim, \times, \cdot
    text = re.sub(r"\s*(\\(?:leq|geq|neq|approx|sim|times|cdot|pm|mp|cap|cup|in|notin|subset|supset|to|rightarrow|leftarrow|Rightarrow|Leftarrow))\s*", r"\1", text)
    return _restore_text_commands(text, ph)


@registry.register("S06", "standard", "math", "Remove spaces after LaTeX commands before non-letter")
def remove_command_spaces(text: str) -> str:
    text, ph = _protect_text_commands(text)
    # \alpha + -> \alpha+ (space before non-letter is safe to remove)
    text = re.sub(r"(\\[a-zA-Z]+)\s+(?=[^a-zA-Z])", r"\1", text)
    return _restore_text_commands(text, ph)


@registry.register("S07", "standard", "math", "Replace command-space-letter with command{}letter")
def command_brace_letter(text: str) -> str:
    text, ph = _protect_text_commands(text)
    # \alpha x -> \alpha{}x (merges two words into one token)
    text = re.sub(r"(\\[a-zA-Z]+)\s+(?=[a-zA-Z])", r"\1{}", text)
    return _restore_text_commands(text, ph)


@registry.register("S08", "standard", "math", "Remove spaces after commas in LaTeX")
def remove_comma_spaces(text: str) -> str:
    text, ph = _protect_text_commands(text)
    text = re.sub(r",\s+", ",", text)
    return _restore_text_commands(text, ph)


@registry.register("S09", "standard", "math", "Remove spaces inside LaTeX braces")
def remove_brace_spaces(text: str) -> str:
    text, ph = _protect_text_commands(text)
    text = re.sub(r"\{\s+", "{", text)
    text = re.sub(r"\s+\}", "}", text)
    return _restore_text_commands(text, ph)


@registry.register("S16", "standard", "math", "Remove spaces around pipe in LaTeX")
def remove_pipe_spaces(text: str) -> str:
    text, ph = _protect_text_commands(text)
    text = re.sub(r"\s*(\\?\|)\s*", r"\1", text)
    return _restore_text_commands(text, ph)
