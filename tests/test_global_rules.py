"""Tests for global compression rules."""

from mdziper.rules.global_rules import (
    collapse_blank_lines,
    compress_references,
    deduplicate_links,
    strip_trailing_blanks,
)


def test_collapse_blank_lines():
    text = "a\n\n\n\nb\n\n\nc"
    assert collapse_blank_lines(text) == "a\n\nb\n\nc"


def test_strip_trailing_blanks():
    assert strip_trailing_blanks("text\n\n\n") == "text\n"
    assert strip_trailing_blanks("text") == "text"


def test_deduplicate_links():
    text = (
        "See [A](https://example.com) and [B](https://example.com) "
        "plus [C](https://other.com)"
    )
    result = deduplicate_links(text)
    # Repeated URL should become reference-style
    assert "[A][1]" in result
    assert "[B][1]" in result
    # Single-use URL stays inline
    assert "[C](https://other.com)" in result
    # Reference definition at end
    assert "[1]: https://example.com" in result


def test_deduplicate_links_no_repeats():
    text = "[A](url1) [B](url2)"
    assert deduplicate_links(text) == text


def test_compress_references():
    text = '[1]: Smith et al., "Deep Learning for X", NeurIPS 2023'
    result = compress_references(text)
    assert result == "[1]:Smith_et_al.,Deep_Learning_for_X,NeurIPS_2023"


def test_compress_references_no_quotes():
    text = "[2]: Jones et al., Better Y with Z, ICML 2024"
    result = compress_references(text)
    assert result == "[2]:Jones_et_al.,Better_Y_with_Z,ICML_2024"


def test_compress_references_url_unchanged():
    """URL reference definitions should also get spaces replaced."""
    text = "[1]: https://example.com/path"
    result = compress_references(text)
    assert result == "[1]:https://example.com/path"
