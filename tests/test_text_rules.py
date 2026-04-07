"""Tests for text compression rules."""

from mdziper.rules.text_rules import (
    compress_after_parens,
    compress_before_parens,
    compress_blockquotes,
    compress_colon_spaces,
    compress_comma_spaces,
    compress_dashes,
    compress_heading_numbers,
    compress_links,
    compress_sentence_spaces,
    compress_slashes,
    compress_table_cells,
    compress_table_separators,
    hyphenate_reviewer_refs,
    hyphenate_table_cells,
    strip_trailing_whitespace,
    underscore_heading_content,
)


# --- Standard rules ---


def test_strip_trailing_whitespace():
    assert strip_trailing_whitespace("hello   \nworld  ") == "hello\nworld"


def test_strip_trailing_whitespace_preserves_hard_break():
    # Two trailing spaces + newline is a Markdown hard line break
    assert strip_trailing_whitespace("line1  \nline2\n") == "line1  \nline2\n"


def test_strip_trailing_whitespace_excess_spaces():
    # More than two trailing spaces should be stripped to just two
    assert strip_trailing_whitespace("line1     \nline2\n") == "line1\nline2\n"


def test_compress_table_cells():
    line = "| hello | world | test |"
    assert compress_table_cells(line) == "|hello|world|test|"


def test_compress_table_cells_preserves_non_table():
    line = "This is not a table"
    assert compress_table_cells(line) == line


def test_compress_table_separators():
    line = "| --- | :---: | ---: |"
    result = compress_table_separators(line)
    assert " " not in result
    assert "|" in result


def test_compress_blockquotes():
    assert compress_blockquotes(">  text") == ">text"
    assert compress_blockquotes("> text") == ">text"


def test_compress_links():
    assert compress_links("[ text ]( url )") == "[text](url)"
    assert compress_links("![  alt  ](  img.png  )") == "![alt](img.png)"


# --- Extreme rules ---


def test_compress_comma_spaces():
    assert compress_comma_spaces("word, another, more") == "word,another,more"


def test_compress_colon_spaces():
    assert compress_colon_spaces("Note: text") == "Note:text"
    # Should not touch URLs
    assert "https://" in compress_colon_spaces("Visit https://example.com")


def test_compress_before_parens():
    assert compress_before_parens("word (detail)") == "word(detail)"


def test_compress_after_parens():
    assert compress_after_parens("(detail) word") == "(detail)word"


def test_compress_dashes():
    assert compress_dashes("word -- word") == "word--word"


def test_compress_slashes():
    assert compress_slashes("and / or") == "and/or"


def test_compress_sentence_spaces():
    assert compress_sentence_spaces("End. Start") == "End.Start"
    # Lowercase after period should be untouched
    assert compress_sentence_spaces("e.g. this") == "e.g. this"


def test_compress_comma_preserves_newlines():
    text = "a,\nb"
    assert compress_comma_spaces(text) == "a,\nb"


# --- Table cell hyphenation (extreme) ---


def test_hyphenate_table_cells():
    text = "|Base A|89.1|86.3|5.1s|"
    assert hyphenate_table_cells(text) == "|Base-A|89.1|86.3|5.1s|"


def test_hyphenate_table_cells_multi_word():
    text = "|F1 Score|Our Method|"
    assert hyphenate_table_cells(text) == "|F1-Score|Our-Method|"


def test_hyphenate_table_cells_skips_separator():
    text = "|---|:---:|---:|"
    assert hyphenate_table_cells(text) == "|---|:---:|---:|"


def test_hyphenate_table_cells_preserves_non_table():
    text = "This is not a table"
    assert hyphenate_table_cells(text) == text


# --- Heading number compression (extreme) ---


def test_compress_heading_numbers():
    assert compress_heading_numbers("## 1. Setup") == "## 1.Setup"
    assert compress_heading_numbers("### 2. Results") == "### 2.Results"


def test_compress_heading_numbers_no_heading():
    # Regular text with "1. " should NOT be affected (no # prefix)
    assert compress_heading_numbers("1. First item") == "1. First item"


# --- Heading content underscores (extreme) ---


def test_underscore_heading_content():
    assert underscore_heading_content("## Experimental Setup") == "## Experimental_Setup"
    assert underscore_heading_content("# Hello World") == "# Hello_World"


def test_underscore_heading_preserves_prefix():
    # The "# " must remain for rendering
    result = underscore_heading_content("# Title")
    assert result.startswith("# ")


# --- Reviewer hyphenation (extreme) ---


def test_hyphenate_reviewer_refs():
    assert hyphenate_reviewer_refs("Reviewer 1") == "Reviewer-1"
    assert hyphenate_reviewer_refs("Reviewer A") == "Reviewer-A"
    assert hyphenate_reviewer_refs("reviewer u78b") == "reviewer-u78b"


def test_hyphenate_reviewer_in_context():
    text = "We thank Reviewer 1 for their comments."
    result = hyphenate_reviewer_refs(text)
    assert "Reviewer-1" in result


# --- Newline preservation (extreme rules must not collapse lines) ---


def test_colon_preserves_newlines():
    text = "baselines:\n\n|Method|Accuracy|"
    assert "\n\n" in compress_colon_spaces(text)


def test_sentence_preserves_newlines():
    text = "End.\nStart of next line"
    assert "\n" in compress_sentence_spaces(text)
