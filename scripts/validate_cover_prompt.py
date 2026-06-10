#!/usr/bin/env python3
"""Cover prompt quality validator (v4.7 — 3-pattern support). stdlib only."""
import sys
import os
import re


def _read_meta(slug_dir):
    """Read book_meta.md and return (author, title) or (None, None)."""
    meta_path = os.path.join(slug_dir, "book_meta.md")
    author = None
    title = None
    if not os.path.exists(meta_path):
        return author, title
    with open(meta_path, encoding="utf-8") as mf:
        meta_content = mf.read()
    for line in meta_content.split("\n"):
        m = re.match(r"(?:\*\*)?著者名(?:\*\*)?[：:]\s*(.+)", line)
        if m:
            author = m.group(1).strip().strip("*").strip()
        m = re.match(r"(?:\*\*)?タイトル(?:\*\*)?[：:]\s*(.+)", line)
        if m:
            title = m.group(1).strip().strip("*").strip()
    return author, title


def _detect_format(content):
    """Detect prompt format: 'yaml' (pattern A), 'step' (pattern B), 'free' (pattern C)."""
    if re.search(r"processing_steps:", content):
        return "step"
    yaml_blocks = ["subject", "layout", "typography", "visuals", "style"]
    yaml_count = sum(
        1 for b in yaml_blocks
        if re.search(rf"(?:^|\n)\*?\s*{b}\s*[:\|]", content, re.IGNORECASE)
    )
    if yaml_count >= 3:
        return "yaml"
    return "free"


def _validate_one(content, label, author, title):
    """Validate a single cover prompt. Returns list of error strings."""
    errors = []
    fmt = _detect_format(content)

    if fmt == "yaml":
        required_blocks = {
            "subject": r"(?:^|\n)\*?\s*(?:subject|Subject)\s*[:\|]",
            "layout": r"(?:^|\n)\*?\s*(?:layout|Layout)\s*[:\|]",
            "typography": r"(?:^|\n)\*?\s*(?:typography|Typography)\s*[:\|]",
            "visuals": r"(?:^|\n)\*?\s*(?:visuals|Visuals)\s*[:\|]",
            "style": r"(?:^|\n)\*?\s*(?:style|Style)\s*[:\|]",
        }
        for block_name, pattern in required_blocks.items():
            if not re.search(pattern, content):
                errors.append(f"[{label}] missing block: {block_name}")

    elif fmt == "step":
        for i in range(1, 6):
            if not re.search(rf"step:\s*{i}", content):
                errors.append(f"[{label}] missing step: {i}")
        if not re.search(r"generation_output", content):
            errors.append(f"[{label}] missing generation_output section")

    # Common checks for all formats
    if author and author not in content:
        errors.append(f"[{label}] author name \"{author}\" not found")
    if title and title not in content:
        errors.append(f"[{label}] title \"{title}\" not found")

    # Model instruction check
    has_model = any(
        kw in content
        for kw in ["GPT-5.5", "gpt-5.5", "ChatGPT Images 2.0", "4o"]
    )
    if not has_model:
        errors.append(f"[{label}] missing model instruction (GPT-5.5)")

    # Minimum length
    if len(content) < 300:
        errors.append(f"[{label}] prompt too short: {len(content)} chars (min 300)")

    return errors, fmt


def validate(slug_dir):
    author, title = _read_meta(slug_dir)

    # v4.7: Support 3-pattern files (cover_prompt_a/b/c.txt)
    # Also support legacy single file (cover_prompt.txt)
    pattern_files = {
        "A": os.path.join(slug_dir, "cover_prompt_a.txt"),
        "B": os.path.join(slug_dir, "cover_prompt_b.txt"),
        "C": os.path.join(slug_dir, "cover_prompt_c.txt"),
    }
    legacy_file = os.path.join(slug_dir, "cover_prompt.txt")

    has_patterns = any(os.path.exists(f) for f in pattern_files.values())
    has_legacy = os.path.exists(legacy_file)

    if not has_patterns and not has_legacy:
        print("FAIL: no cover prompt files found")
        print("  Expected: cover_prompt_a.txt / cover_prompt_b.txt / cover_prompt_c.txt")
        print("  Or legacy: cover_prompt.txt")
        return 1

    all_errors = []
    results = []

    if has_patterns:
        for label, path in pattern_files.items():
            if not os.path.exists(path):
                all_errors.append(f"[Pattern {label}] file missing: {os.path.basename(path)}")
                continue
            with open(path, encoding="utf-8") as f:
                content = f.read()
            errs, fmt = _validate_one(content, f"Pattern {label}", author, title)
            all_errors.extend(errs)
            results.append((label, len(content), fmt))
    else:
        # Legacy single file
        with open(legacy_file, encoding="utf-8") as f:
            content = f.read()
        errs, fmt = _validate_one(content, "cover_prompt", author, title)
        all_errors.extend(errs)
        results.append(("single", len(content), fmt))

    if all_errors:
        print("FAIL: cover prompt validation errors")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    for label, chars, fmt in results:
        print(f"PASS: Pattern {label} ({chars} chars, format={fmt})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_cover_prompt.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
