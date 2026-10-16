"""Build the static web app for GitHub Pages.

Usage:
    python web/build.py [OUT_DIR]    # default: _site/

Copies web/index.html and bundles src/mdziper into mdziper.zip, which the page
loads into Pyodide, so the browser runs exactly the same code as the CLI.
"""

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "web" / "index.html", out / "index.html")
    shutil.copy2(ROOT / "tests" / "fixtures" / "sample_rebuttal.md", out / "sample.md")

    src = ROOT / "src"
    with zipfile.ZipFile(out / "mdziper.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted((src / "mdziper").rglob("*.py")):
            zf.write(path, path.relative_to(src).as_posix())


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
    build(out)
    print(f"Built web app in {out}")
