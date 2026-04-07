"""Compression rules for TEXT segments (Markdown prose, tables, links, etc.)."""

import re

from . import registry

# ============================================================
# Standard mode rules — rendered output is identical
# ============================================================


@registry.register("S01", "standard", "text", "Strip trailing whitespace per line")
def strip_trailing_whitespace(text: str) -> str:
    # Preserve two trailing spaces + newline (Markdown hard line break)
    # Only strip trailing whitespace that is NOT exactly two spaces before \n
    def _strip_line(m):
        trailing = m.group(0)
        # If the trailing whitespace is exactly "  \n" (hard break), preserve it
        if trailing == "  \n":
            return trailing
        # Otherwise strip all trailing whitespace (keep the newline if present)
        if trailing.endswith("\n"):
            return "\n"
        return ""

    return re.sub(r"[^\S\n]+\n|[^\S\n]+$", _strip_line, text, flags=re.MULTILINE)


@registry.register("S03", "standard", "text", "Remove spaces inside table cells")
def compress_table_cells(text: str) -> str:
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # Table row: remove spaces around cell content
            # Split by |, strip each cell, rejoin
            parts = stripped.split("|")
            # parts[0] and parts[-1] are empty strings from leading/trailing |
            compressed = "|".join(p.strip() for p in parts)
            result.append(compressed)
        else:
            result.append(line)
    return "\n".join(result)


@registry.register("S04", "standard", "text", "Remove spaces in table separator rows")
def compress_table_separators(text: str) -> str:
    # Matches separator rows like | --- | :---: | ---: |
    return re.sub(
        r"^\|[\s\-:|\s]+\|$",
        lambda m: re.sub(r"\s+", "", m.group()),
        text,
        flags=re.MULTILINE,
    )


@registry.register("S10", "standard", "text", "Remove extra spaces after > in blockquotes")
def compress_blockquotes(text: str) -> str:
    return re.sub(r"^(>+)\s+", r"\1", text, flags=re.MULTILINE)


@registry.register("S11", "standard", "text", "Remove spaces in link syntax")
def compress_links(text: str) -> str:
    # [  text  ](  url  ) -> [text](url)
    # But preserve spaces in title: [text](url "title with spaces")
    def _compress_link(m):
        full = m.group(0)
        # Handle image or link
        prefix = "!" if full.startswith("!") else ""
        text_part = m.group(1).strip()
        url_part = m.group(2).strip()
        return f"{prefix}[{text_part}]({url_part})"

    text = re.sub(
        r"!?\[\s*([^\]]*?)\s*\]\(\s*([^)]*?)\s*\)",
        _compress_link,
        text,
    )
    return text


# ============================================================
# Extreme mode rules — aggressive compression
#
# IMPORTANT: All rules here use ` +` (horizontal space only),
# never `\s+`, to avoid collapsing newlines. Collapsing lines
# breaks tables, lists, and other block-level Markdown elements.
# ============================================================


@registry.register("E04", "extreme", "text", "Remove space after commas in prose")
def compress_comma_spaces(text: str) -> str:
    return re.sub(r", +", ",", text)


@registry.register("E05", "extreme", "text", "Remove space after semicolons")
def compress_semicolon_spaces(text: str) -> str:
    return re.sub(r"; +", ";", text)


@registry.register("E06", "extreme", "text", "Remove space after colons (non-URL)")
def compress_colon_spaces(text: str) -> str:
    # Don't touch http:// or https://
    return re.sub(r"(?<!http)(?<!https): +", ":", text)


@registry.register("E07", "extreme", "text", "Remove space before opening parens")
def compress_before_parens(text: str) -> str:
    return re.sub(r" +\(", "(", text)


@registry.register("E08", "extreme", "text", "Remove space after closing parens")
def compress_after_parens(text: str) -> str:
    return re.sub(r"\) +", ")", text)


@registry.register("E09", "extreme", "text", "Remove spaces around dashes")
def compress_dashes(text: str) -> str:
    return re.sub(r" *-- *", "--", text)


@registry.register("E10", "extreme", "text", "Remove spaces around slashes")
def compress_slashes(text: str) -> str:
    return re.sub(r" */ *", "/", text)


@registry.register("E12", "extreme", "text", "Remove space between sentences")
def compress_sentence_spaces(text: str) -> str:
    # "sentence. Next" -> "sentence.Next"
    # Require a letter before the period to avoid matching list markers like "1. Item"
    return re.sub(r"(?<=[a-zA-Z])\. +(?=[A-Z])", ".", text)


@registry.register("E13", "extreme", "text", "Remove spaces in nested blockquotes")
def compress_nested_blockquotes(text: str) -> str:
    return re.sub(r"^(>) *(>)", r"\1\2", text, flags=re.MULTILINE)


@registry.register("E14", "extreme", "text", "Replace spaces in table cells with hyphens")
def hyphenate_table_cells(text: str) -> str:
    """Replace spaces within table cell content with hyphens.

    E.g.: |Base A|89.1| -> |Base-A|89.1|
    Does not touch separator rows (|---|).
    """
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            result.append(line)
            continue
        # Skip separator rows like |---|:---:|
        if re.match(r"^\|[\s\-:|]+\|$", stripped):
            result.append(line)
            continue
        # Replace spaces within each cell content
        parts = stripped.split("|")
        # parts[0] and parts[-1] are empty strings from leading/trailing |
        compressed = []
        for p in parts:
            cell = p.strip()
            if cell:
                cell = cell.replace(" ", "-")
            compressed.append(cell)
        result.append("|".join(compressed))
    return "\n".join(result)


@registry.register("E15", "extreme", "text", "Remove space after numbered prefix in headings")
def compress_heading_numbers(text: str) -> str:
    """Remove space after 'N.' in headings: '## 1. Setup' -> '## 1.Setup'."""
    return re.sub(r"^(#{1,6} +\d+\.) +", r"\1", text, flags=re.MULTILINE)


@registry.register("E16", "extreme", "text", "Replace spaces in heading content with underscores")
def underscore_heading_content(text: str) -> str:
    """Replace spaces in heading text with underscores.

    '## Experimental Setup' -> '## Experimental_Setup'
    Preserves the '# ' prefix required for rendering.
    """

    def _replace(m):
        prefix = m.group(1)  # e.g., "## "
        content = m.group(2)
        content = content.replace(" ", "_")
        return prefix + content

    return re.sub(r"^(#{1,6} +)(.+)$", _replace, text, flags=re.MULTILINE)


@registry.register("E17", "extreme", "text", "Replace spaces in Reviewer references with hyphens")
def hyphenate_reviewer_refs(text: str) -> str:
    """'Reviewer 1' -> 'Reviewer-1', 'Reviewer A' -> 'Reviewer-A', etc."""
    return re.sub(r"(?i)(reviewer) +(\S+)", r"\1-\2", text)
