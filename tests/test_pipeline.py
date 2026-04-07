"""Integration tests for the compression pipeline."""

import os

from mdziper import compress


def test_standard_mode_basic():
    text = "| a | b |\n| --- | --- |\n| 1 | 2 |\n"
    result = compress(text, mode="standard")
    assert "|a|b|" in result.text
    assert result.compressed_words <= result.original_words


def test_standard_mode_math():
    text = "The value $a + b = c$ is here.\n"
    result = compress(text, mode="standard")
    assert "$a+b=c$" in result.text


def test_extreme_mode_preserves_headings():
    text = "# Introduction\n\nSome text.\n"
    result = compress(text, mode="extreme")
    # Headings must keep their space to render correctly
    assert "# Introduction" in result.text


def test_extreme_mode_preserves_lists():
    text = "1. First item\n2. Second item\n"
    result = compress(text, mode="extreme")
    # List markers must keep their space to render correctly
    assert "1. First" in result.text


def test_extreme_mode_commas():
    text = "word, another, more\n"
    result = compress(text, mode="extreme")
    assert "word,another,more" in result.text


def test_code_blocks_protected():
    text = "Before\n\n```\na + b = c\n```\n\nAfter\n"
    result = compress(text, mode="extreme")
    assert "a + b = c" in result.text  # spaces preserved in code


def test_inline_code_protected():
    text = "Use `a + b` here.\n"
    result = compress(text, mode="extreme")
    assert "`a + b`" in result.text


def test_word_count_decreases():
    text = "| hello | world |\n| --- | --- |\n| a | b |\n"
    result = compress(text, mode="standard")
    assert result.compressed_words < result.original_words


def test_savings_percentage():
    text = "# Hello World\n\n1. First item, with detail\n"
    result = compress(text, mode="extreme")
    assert 0 <= result.savings <= 1


def test_exclude_rules():
    text = "word, another\n"
    result = compress(text, mode="extreme", exclude={"E04"})
    # E04 (comma spaces) is excluded, so comma space should remain
    assert "word, another" in result.text


def test_sample_rebuttal():
    fixture = os.path.join(os.path.dirname(__file__), "fixtures", "sample_rebuttal.md")
    with open(fixture, encoding="utf-8") as f:
        text = f.read()
    result = compress(text, mode="standard")
    assert result.compressed_words < result.original_words
    # Code/structure preserved
    assert "94.2" in result.text

    extreme = compress(text, mode="extreme")
    assert extreme.compressed_words <= result.compressed_words


def test_empty_input():
    result = compress("")
    assert result.text == ""
    assert result.original_words == 0


def test_frontmatter_preserved():
    text = "---\ntitle: Test\n---\n\n# Hello World\n"
    result = compress(text, mode="extreme")
    assert "---\ntitle: Test\n---" in result.text
