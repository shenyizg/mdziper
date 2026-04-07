"""Command-line interface for mdziper."""

import argparse
import sys

from . import __version__, compress


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mdziper",
        description="Compress Markdown to reduce word count while preserving content.",
    )
    parser.add_argument("input", nargs="?", help="Input Markdown file (default: stdin)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--extreme", action="store_true", help="Enable extreme compression mode"
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[], help="Rule names to skip (e.g., E01 S14)"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Print word count statistics to stderr"
    )
    parser.add_argument(
        "--list-rules", action="store_true", help="List all available rules and exit"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    if args.list_rules:
        from .rules import registry
        from .rules import math_rules as _  # noqa: F401
        from .rules import text_rules as __  # noqa: F401
        from .rules import global_rules as ___  # noqa: F401

        for rule in registry.list_rules():
            print(f"{rule.name:5s} [{rule.mode:8s}] [{rule.scope:6s}] {rule.description}")
        return

    # Read input
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    mode = "extreme" if args.extreme else "standard"
    exclude = set(args.exclude)

    result = compress(text, mode=mode, exclude=exclude)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.text)
    else:
        sys.stdout.write(result.text)

    if args.stats:
        saved = result.original_words - result.compressed_words
        pct = result.savings * 100
        print(
            f"\n[mdziper] {result.original_words} → {result.compressed_words} words "
            f"(saved {saved}, {pct:.1f}%)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
