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

    # タイトルチェック
    title_match = re.search(r"タイトル[：:]\s*(.+)", content)
    if not title_match or len(title_match.group(1).strip()) < 3:
        errors.append("タイトルが未設定または短すぎます")

    # サブタイトルチェック
    sub_match = re.search(r"サブタイトル[：:]\s*(.+)", content)
    if not sub_match or len(sub_match.group(1).strip()) < 3:
        errors.append("サブタイトルが未設定または短すぎます")

    # 著者名チェック
    author_match = re.search(r"著者名[：:]\s*(.+)", content)
    if not author_match or len(author_match.group(1).strip()) < 1:
        errors.append("著者名が未設定です（空欄不可）")

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
