"""Split Markdown source into typed segments for selective compression."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List


class SegmentType(Enum):
    TEXT = "text"
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    DISPLAY_MATH = "display_math"
    INLINE_MATH = "inline_math"
    FRONTMATTER = "frontmatter"
    HTML_BLOCK = "html_block"


@dataclass
class Segment:
    type: SegmentType
    content: str


# Order matters: longer/greedier patterns first.
# Each pattern is a named group so we can identify what matched.
_SEGMENT_RE = re.compile(
    r"(?P<code_block>^```[^\S\n]*[^\n]*\n[\s\S]*?^```[^\S\n]*$)"  # fenced code
    r"|(?P<html_block><(?:pre|code|script|style)\b[^>]*>[\s\S]*?</(?:pre|code|script|style)>)"
    r"|(?P<inline_code>``[^`]+``|`[^`\n]+`)"  # inline code (double or single backtick)
    r"|(?P<display_math>\$\$[\s\S]*?\$\$)"  # display math
    r"|(?P<inline_math>(?<!\$)\$(?!\$)(?!\s)(?:[^\$\n\\]|\\.)+(?<!\s)\$(?!\$))",  # inline math
    re.MULTILINE,
)

_FRONTMATTER_RE = re.compile(r"\A---\n[\s\S]*?\n---\n?")


def segment(text: str) -> List[Segment]:
    """Split markdown text into typed segments.

    Protected segments (code, math, frontmatter, HTML) are identified so that
    compression rules can skip them. Everything else is TEXT.
    """
    segments: List[Segment] = []

    # Handle YAML frontmatter at the very start
    fm_match = _FRONTMATTER_RE.match(text)
    start_offset = 0
    if fm_match:
        segments.append(Segment(SegmentType.FRONTMATTER, fm_match.group()))
        start_offset = fm_match.end()

    remaining = text[start_offset:]
    pos = 0

    for m in _SEGMENT_RE.finditer(remaining):
        # Add any TEXT before this match
        if m.start() > pos:
            segments.append(Segment(SegmentType.TEXT, remaining[pos : m.start()]))

        # Determine segment type from which group matched
        if m.group("code_block") is not None:
            seg_type = SegmentType.CODE_BLOCK
        elif m.group("html_block") is not None:
            seg_type = SegmentType.HTML_BLOCK
        elif m.group("inline_code") is not None:
            seg_type = SegmentType.INLINE_CODE
        elif m.group("display_math") is not None:
            seg_type = SegmentType.DISPLAY_MATH
        elif m.group("inline_math") is not None:
            seg_type = SegmentType.INLINE_MATH
        else:
            seg_type = SegmentType.TEXT

        segments.append(Segment(seg_type, m.group()))
        pos = m.end()

    # Trailing text
    if pos < len(remaining):
        segments.append(Segment(SegmentType.TEXT, remaining[pos:]))

    return segments


def reassemble(segments: List[Segment]) -> str:
    """Join segments back into a single string."""
    return "".join(seg.content for seg in segments)
