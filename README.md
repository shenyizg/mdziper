# mdziper

Compress Markdown source text to reduce word count while preserving content. Designed for academic peer review rebuttals with strict word limits.

## Install

```bash
pip install mdziper
```

## Usage

### Python API

```python
from mdziper import compress

text = open("rebuttal.md").read()

# Standard mode: rendered output is pixel-perfect identical
result = compress(text, mode="standard")

# Extreme mode: aggressive compression, may alter formatting
result = compress(text, mode="extreme")

print(result.text)
print(f"{result.original_words} → {result.compressed_words} words ({result.savings:.0%} saved)")
```

### CLI

```bash
# Standard compression
mdziper input.md -o output.md

# Extreme compression with stats
mdziper input.md --extreme --stats

# Pipe from stdin
cat input.md | mdziper --extreme > output.md

# Skip specific rules
mdziper input.md --extreme --exclude E04 E16

# List all rules
mdziper --list-rules
```

## Compression Modes

### Standard Mode

Removes whitespace that doesn't affect Markdown rendering:

- Trailing whitespace on lines
- Extra blank lines
- Spaces inside table cells: `| cell |` → `|cell|`
- Spaces in LaTeX math: `$a + b = c$` → `$a+b=c$`
- Spaces in LaTeX braces: `$\frac{ a }{ b }$` → `$\frac{a}{b}$`
- Redundant spaces in link syntax
- Repeated inline links → reference-style links

### Extreme Mode

All standard optimizations plus aggressive space removal. Markdown structure (headings, lists, code blocks, tables) is preserved — only cosmetic spaces are removed.

**Punctuation spacing:**

- `word, word` → `word,word`
- `Note: text` → `Note:text`
- `word; word` → `word;word`
- `sentence. Next` → `sentence.Next`
- `word (detail)` → `word(detail)`
- `and / or` → `and/or`
- `word -- word` → `word--word`

**Headings:**

- Numbered prefix: `## 1. Setup` → `## 1.Setup`
- Content underscores: `## Experimental Setup` → `## Experimental_Setup`

**Tables:**

- Cell content hyphens: `|Base A|` → `|Base-A|`

**References:**

- `[1]: Smith et al., "Deep Learning for X", NeurIPS 2023` → `[1]:Smith_et_al.,Deep_Learning_for_X,NeurIPS_2023`

**Common phrases:**

- `Reviewer 1` → `Reviewer-1`, `Reviewer A` → `Reviewer-A`

> **Note**: Extreme mode produces minor visual differences but does not break Markdown rendering. Headings, lists, tables, and code blocks all render correctly.

## How It Works

1. **Segment**: Split input into protected regions (code blocks, inline code) and compressible regions (text, math)
2. **Compress**: Apply mode-specific rules to each segment type
3. **Reassemble**: Join segments and apply global optimizations

Code blocks and inline code are never modified.

## License

MIT
