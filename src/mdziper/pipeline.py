"""Main compression pipeline: segment → apply rules → reassemble."""

from dataclasses import dataclass
from typing import Optional, Set

from .counter import count_words
from .rules import registry
from .segmenter import SegmentType, reassemble, segment


@dataclass
class CompressResult:
    text: str
    original_words: int
    compressed_words: int

    @property
    def savings(self) -> float:
        if self.original_words == 0:
            return 0.0
        return (self.original_words - self.compressed_words) / self.original_words


# Map segment types to rule scopes
_SCOPE_MAP = {
    SegmentType.TEXT: "text",
    SegmentType.INLINE_MATH: "math",
    SegmentType.DISPLAY_MATH: "math",
}

# These segment types are never modified
_PROTECTED = {
    SegmentType.CODE_BLOCK,
    SegmentType.INLINE_CODE,
    SegmentType.FRONTMATTER,
    SegmentType.HTML_BLOCK,
}


def compress(
    text: str,
    mode: str = "standard",
    exclude: Optional[Set[str]] = None,
) -> CompressResult:
    """Compress Markdown text to reduce word count.

    Args:
        text: Markdown source text.
        mode: "standard" (rendering-safe) or "extreme" (aggressive).
        exclude: Set of rule names to skip (e.g., {"E01", "S14"}).

    Returns:
        CompressResult with compressed text and word count stats.
    """
    # Ensure rules are loaded
    from .rules import math_rules as _  # noqa: F401
    from .rules import text_rules as __  # noqa: F401
    from .rules import global_rules as ___  # noqa: F401

    original_words = count_words(text)

    # 1. Segment the document
    segments = segment(text)

    # 2. Apply scoped rules to each segment
    for scope in ("text", "math"):
        rules = registry.get_rules(mode=mode, scope=scope, exclude=exclude)
        for i, seg in enumerate(segments):
            if seg.type in _PROTECTED:
                continue
            seg_scope = _SCOPE_MAP.get(seg.type)
            if seg_scope == scope:
                content = seg.content
                for rule in rules:
                    content = rule.fn(content)
                segments[i] = type(seg)(seg.type, content)

    # 3. Reassemble
    result = reassemble(segments)

    # 4. Apply global rules
    global_rules = registry.get_rules(mode=mode, scope="global", exclude=exclude)
    for rule in global_rules:
        result = rule.fn(result)

    compressed_words = count_words(result)

    return CompressResult(
        text=result,
        original_words=original_words,
        compressed_words=compressed_words,
    )
