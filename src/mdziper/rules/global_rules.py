"""Global compression rules that operate on the full reassembled document."""

import re
from collections import Counter

from . import registry


@registry.register("S02", "standard", "global", "Collapse multiple blank lines to one")
def collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


@registry.register("S15", "standard", "global", "Remove trailing blank lines at end of file")
def strip_trailing_blanks(text: str) -> str:
    return text.rstrip("\n") + "\n" if text.endswith("\n") else text.rstrip("\n")


@registry.register("S14", "standard", "global", "Convert repeated inline links to reference-style")
def deduplicate_links(text: str) -> str:
    """Replace repeated inline links with reference-style links when it saves words."""
    inline_link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    matches = inline_link_re.findall(text)
    if not matches:
        return text

    # Count URL occurrences
    url_counts = Counter(url for _, url in matches)
    # Only convert URLs that appear 2+ times
    urls_to_convert = {url for url, count in url_counts.items() if count >= 2}
    if not urls_to_convert:
        return text

    # Assign short reference IDs
    ref_map = {}
    ref_id = 1
    for url in urls_to_convert:
        ref_map[url] = str(ref_id)
        ref_id += 1

    # Replace inline links with reference links
    def _replace(m):
        link_text, url = m.group(1), m.group(2)
        if url in ref_map:
            return f"[{link_text}][{ref_map[url]}]"
        return m.group(0)

    result = inline_link_re.sub(_replace, text)

    # Append reference definitions at the end
    ref_defs = "\n".join(f"[{rid}]: {url}" for url, rid in ref_map.items())
    result = result.rstrip("\n") + "\n\n" + ref_defs + "\n"

    return result


@registry.register("E11", "extreme", "global", "Compress reference definition lines")
def compress_references(text: str) -> str:
    """Compress reference definition lines by replacing spaces with underscores and removing quotes.

    E.g.: [1]: Smith et al., "Deep Learning for X", NeurIPS 2023
       -> [1]:Smith_et_al.,Deep_Learning_for_X,NeurIPS_2023
    """

    def _compress_ref_line(m):
        label = m.group(1)  # e.g., "1"
        content = m.group(2)  # everything after ]:
        # Remove quotes
        content = content.replace('"', "").replace("'", "")
        # Remove spaces after punctuation (, ; :) before replacing remaining with _
        content = re.sub(r"([,;:])\s+", r"\1", content)
        # Replace remaining spaces with underscores
        content = content.replace(" ", "_")
        return f"[{label}]:{content}"

    # Match reference definition lines: [label]: content
    text = re.sub(
        r"^\[([^\]]+)\]:\s*(.+)$",
        _compress_ref_line,
        text,
        flags=re.MULTILINE,
    )

    return text
