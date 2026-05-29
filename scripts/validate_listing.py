#!/usr/bin/env python3
"""出版メタデータ（listing.txt）の品質検証スクリプト（stdlib only）"""
import sys
import os
import re


def validate(slug_dir):
    path = os.path.join(slug_dir, "listing.txt")
    errors = []

    if not os.path.exists(path):
        print("FAIL: listing.txt が存在しません")
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    char_count = len(content)
    if char_count < 3000:
        errors.append(f"総文字数不足: {char_count} / 最低3,000字")

    # タイトル提案チェック（3案）
    title_proposals = re.findall(r"【提案\d", content)
    if len(title_proposals) < 3:
        errors.append(f"タイトル提案数不足: {len(title_proposals)} / 最低3案")

    # キーワード行チェック（7行）
    kw_section = re.search(r"キーワード.*?(?=------|\Z)", content, re.DOTALL)
    if kw_section:
        kw_text = kw_section.group()
        kw_lines = [l for l in kw_text.split("\n") if l.strip() and not l.startswith("-") and "キーワード" not in l and "----" not in l and "50文字" not in l]
        if len(kw_lines) < 7:
            errors.append(f"キーワード行数不足: {len(kw_lines)} / 最低7行")
    else:
        errors.append("キーワードセクションが見つかりません")

    # 著者名チェック
    if "著者" not in content:
        errors.append("著者名セクションが見つかりません")

    # フリガナチェック
    if "カタカナ" not in content and "ローマ字" not in content:
        errors.append("フリガナセクションが見つかりません")

    # 紹介文チェック
    intro_match = re.search(r"紹介文.*?(?=======|\Z)", content, re.DOTALL)
    if intro_match:
        intro_text = intro_match.group()
        intro_chars = len(intro_text)
        if intro_chars < 3000:
            errors.append(f"紹介文の文字数不足: {intro_chars} / 最低3,000字")
    else:
        errors.append("紹介文セクションが見つかりません")

    if errors:
        print("FAIL: listing.txt 検証エラー")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: listing.txt ({char_count}字)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_listing.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
