#!/usr/bin/env python3
"""書籍メタ情報（book_meta.md）の検証スクリプト（stdlib only）"""
import sys
import os
import re


def validate(slug_dir):
    path = os.path.join(slug_dir, "book_meta.md")
    errors = []

    if not os.path.exists(path):
        print("FAIL: book_meta.md が存在しません")
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Title check (accepts Japanese or English labels, with or without bold markdown)
    title_match = re.search(r"(?:\*{0,2})(?:タイトル|[Tt]itle)(?:\*{0,2})[：:]\s*(.+)", content)
    if not title_match or len(title_match.group(1).strip()) < 3:
        errors.append("title missing or too short")

    # Subtitle check
    sub_match = re.search(r"(?:\*{0,2})(?:サブタイトル|[Ss]ubtitle)(?:\*{0,2})[：:]\s*(.+)", content)
    if not sub_match or len(sub_match.group(1).strip()) < 3:
        errors.append("subtitle missing or too short")

    # Author check
    author_match = re.search(r"(?:\*{0,2})(?:著者名|[Aa]uthor)(?:\*{0,2})[：:]\s*(.+)", content)
    if not author_match or len(author_match.group(1).strip()) < 1:
        errors.append("author missing")

    # 文字化け・不正バイト列検出
    # Shift-JIS mojibake patterns (e.g. 繧ｿ繧､繝医Ν)
    mojibake_pattern = re.compile(r"[繧繝繧ｧ繧ｩ繧ｫ繧ｭ繧ｯ繧ｱ繧ｳ繧ｵ繧ｷ繧ｹ繧ｻ繧ｿ]{2,}")
    mojibake_matches = mojibake_pattern.findall(content)
    if mojibake_matches:
        errors.append(
            f"mojibake (garbled text) detected: {len(mojibake_matches)} occurrences, "
            f"e.g. \"{mojibake_matches[0][:30]}\""
        )
    # Zero-width / invisible characters
    invisible = re.findall(r"[\u200c\u200b\u200d\ufeff]", content)
    if invisible:
        errors.append(f"invisible characters detected: {len(invisible)} occurrences")
    # Tags block (U+E0000-U+E01FF)
    tags = re.findall(r"[\U000E0000-\U000E01FF]", content)
    if tags:
        errors.append(f"Unicode Tags block characters detected: {len(tags)} occurrences")

    if errors:
        print("FAIL: book_meta.md 検証エラー")
        for e in errors:
            print(f"  - {e}")
        return 1

    title = title_match.group(1).strip() if title_match else "?"
    author = author_match.group(1).strip() if author_match else "?"
    print(f"PASS: book_meta.md (タイトル: {title}, 著者: {author})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_meta.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
