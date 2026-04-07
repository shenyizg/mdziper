"""Tests for the Markdown segmenter."""

from mdziper.segmenter import SegmentType, reassemble, segment


def test_plain_text():
    text = "Hello world"
    segs = segment(text)
    assert len(segs) == 1
    assert segs[0].type == SegmentType.TEXT
    assert segs[0].content == text


def test_inline_code():
    text = "Use `print()` here"
    segs = segment(text)
    types = [s.type for s in segs]
    assert SegmentType.INLINE_CODE in types
    code_seg = [s for s in segs if s.type == SegmentType.INLINE_CODE][0]
    assert code_seg.content == "`print()`"


def test_double_backtick_code():
    text = "Use ``code with `backtick` inside`` here"
    segs = segment(text)
    types = [s.type for s in segs]
    assert SegmentType.INLINE_CODE in types


def test_fenced_code_block():
    text = "Before\n\n```python\nx = 1 + 2\n```\n\nAfter"
    segs = segment(text)
    types = [s.type for s in segs]
    assert SegmentType.CODE_BLOCK in types
    code_seg = [s for s in segs if s.type == SegmentType.CODE_BLOCK][0]
    assert "x = 1 + 2" in code_seg.content


def test_inline_math():
    text = "The value $a + b = c$ is computed"
    segs = segment(text)
    types = [s.type for s in segs]
    assert SegmentType.INLINE_MATH in types
    math_seg = [s for s in segs if s.type == SegmentType.INLINE_MATH][0]
    assert math_seg.content == "$a + b = c$"


def test_display_math():
    text = "Below:\n$$\nE = mc^2\n$$\nAbove"
    segs = segment(text)
    types = [s.type for s in segs]
    assert SegmentType.DISPLAY_MATH in types


def test_dollar_sign_not_math():
    """$5 and $10 should not be treated as math."""
    text = "The cost is $5 per item"
    segs = segment(text)
    # $5 has a space after $ — our regex requires no leading space in math
    # So this should all be TEXT
    math_segs = [s for s in segs if s.type == SegmentType.INLINE_MATH]
    assert len(math_segs) == 0


def test_frontmatter():
    text = "---\ntitle: Test\n---\n\n# Hello"
    segs = segment(text)
    assert segs[0].type == SegmentType.FRONTMATTER
    assert "title: Test" in segs[0].content


def test_reassemble_roundtrip():
    text = "Hello `code` and $math$ here\n\n```\nblock\n```\n\nEnd"
    segs = segment(text)
    assert reassemble(segs) == text


def test_mixed_segments_order():
    text = "Text `code` more $x+1$ end"
    segs = segment(text)
    assert segs[0].type == SegmentType.TEXT
    assert segs[1].type == SegmentType.INLINE_CODE
    assert segs[2].type == SegmentType.TEXT
    assert segs[3].type == SegmentType.INLINE_MATH
    assert segs[4].type == SegmentType.TEXT
