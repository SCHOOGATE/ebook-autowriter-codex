#!/usr/bin/env python3
"""Cover prompt (cover_prompt.txt) quality validator. stdlib only."""
import sys
import os
import re


def validate(slug_dir):
    path = os.path.join(slug_dir, "cover_prompt.txt")
    errors = []

    if not os.path.exists(path):
        print("FAIL: cover_prompt.txt does not exist")
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # 5-block YAML check (subject, layout, typography, visuals, style)
    required_blocks = {
        "subject": r"(?:^|\n)\*?\s*(?:subject|Subject)\s*[:\|]",
        "layout": r"(?:^|\n)\*?\s*(?:layout|Layout)\s*[:\|]",
        "typography": r"(?:^|\n)\*?\s*(?:typography|Typography)\s*[:\|]",
        "visuals": r"(?:^|\n)\*?\s*(?:visuals|Visuals)\s*[:\|]",
        "style": r"(?:^|\n)\*?\s*(?:style|Style)\s*[:\|]",
    }
    for block_name, pattern in required_blocks.items():
        if not re.search(pattern, content):
            errors.append(f"missing block: {block_name} (5-block YAML required)")

    # Author name check (must be present in typography or layout)
    meta_path = os.path.join(slug_dir, "book_meta.md")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as mf:
            meta_content = mf.read()
        for line in meta_content.split("\n"):
            m = re.match(r"(?:\*\*)?著者名(?:\*\*)?[：:]\s*(.+)", line)
            if m:
                author = m.group(1).strip().strip("*").strip()
                if author and author not in content:
                    errors.append(
                        f"author name \"{author}\" not found in cover prompt"
                    )
                break

    # Japanese title check
    title_match = None
    if os.path.exists(meta_path):
        for line in meta_content.split("\n"):
            m = re.match(r"(?:\*\*)?タイトル(?:\*\*)?[：:]\s*(.+)", line)
            if m:
                title_match = m.group(1).strip().strip("*").strip()
                break
    if title_match and title_match not in content:
        errors.append(f"title \"{title_match}\" not found in cover prompt")

    # ChatGPT Images 2.0 instruction check
    if "ChatGPT Images 2.0" not in content and "4o" not in content:
        errors.append("missing model instruction (ChatGPT Images 2.0 / 4o)")

    # Minimum length check
    if len(content) < 500:
        errors.append(f"prompt too short: {len(content)} chars (min 500)")

    if errors:
        print("FAIL: cover_prompt.txt validation errors")
        for e in errors:
            print(f"  - {e}")
        return 1

    block_count = sum(1 for p in required_blocks.values() if re.search(p, content))
    print(f"PASS: cover_prompt.txt ({len(content)} chars, {block_count}/5 blocks)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_cover_prompt.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
