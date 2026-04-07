"""mdziper — Markdown word count compressor.

Usage:
    from mdziper import compress

    result = compress(markdown_text, mode="standard")
    print(result.text)
    print(f"Saved {result.savings:.0%} words")
"""

from .pipeline import CompressResult, compress

__all__ = ["compress", "CompressResult"]
__version__ = "0.1.0"
