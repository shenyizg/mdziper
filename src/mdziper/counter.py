"""Word counting utilities."""


def count_words(text: str) -> int:
    """Count words as whitespace-delimited tokens (matching most review platforms)."""
    return len(text.split())
