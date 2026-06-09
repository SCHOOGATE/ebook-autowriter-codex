#!/usr/bin/env python3
"""Kindle申請データ（kindle_application.txt）の品質検証スクリプト（stdlib only）"""
import sys
import os
import re


def validate(slug_dir):
    path = os.path.join(slug_dir, "kindle_application.txt")
    errors = []

    if not os.path.exists(path):
        print("FAIL: kindle_application.txt が存在しません")
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    char_count = len(content)
    if char_count < 2000:
        errors.append(f"総文字数不足: {char_count} / 最低2,000字")

    # タイトル3表記チェック（漢字・カタカナ・ローマ字）
    for label in ["漢字", "カタカナ", "ローマ字"]:
        if label not in content:
            errors.append(f"タイトル表記「{label}」が見つかりません")

    # 書籍説明文チェック（PASONA / 3,000〜4,000字）
    # v4.5: Handle both formats (with/without separator lines)
    # Format A: "4. 書籍説明文...\n------\ncontent\n------\n5."
    desc_match = re.search(
        r"(?:4\.\s*書籍説明文|書籍説明文)[^\n]*\n-{5,}\n(.*?)(?=\n-{5,}|\Z)",
        content, re.DOTALL
    )
    if not desc_match:
        # Format B: "4. 書籍説明文\n<p>content</p>\n\n5."
        desc_match = re.search(
            r"(?:4\.\s*書籍説明文|書籍説明文)[^\n]*\n(.*?)(?=\n\d+\.\s|\Z)",
            content, re.DOTALL
        )
    if desc_match:
        desc_text = desc_match.group(1) if desc_match.lastindex else desc_match.group()
        # HTMLタグを除去して文字数カウント
        plain_text = re.sub(r"<[^>]+>", "", desc_text)
        desc_chars = len(plain_text.strip())
        if desc_chars < 2500:
            errors.append(f"書籍説明文の文字数不足: {desc_chars} / 最低2,500字")
        # 段落反復検出
        sentences = [s.strip() for s in re.split(r"[。\n]", plain_text) if len(s.strip()) >= 20]
        if sentences:
            from collections import Counter
            sent_counts = Counter(sentences)
            repeated = {s: c for s, c in sent_counts.items() if c >= 3}
            if repeated:
                sample = list(repeated.keys())[0][:60]
                total_repeats = sum(c - 1 for c in repeated.values())
                errors.append(
                    f"書籍説明文に段落反復 {total_repeats} 箇所 "
                    f"(同一文3回以上): \"{sample}...\""
                )
    else:
        errors.append("書籍説明文セクションが見つかりません")

    # カテゴリチェック（5件）— v4.5: Handle both formats
    cat_match = re.search(
        r"(?:5\.\s*カテゴリ|カテゴリ)[^\n]*\n-{5,}\n(.*?)(?=\n-{5,}|\n\d+\.\s*キーワード|\Z)",
        content, re.DOTALL
    )
    if not cat_match:
        cat_match = re.search(
            r"(?:5\.\s*カテゴリ|カテゴリ)[^\n]*\n(.*?)(?=\n\d+\.\s*キーワード|\Z)",
            content, re.DOTALL
        )
    if cat_match:
        cat_text = cat_match.group(1) if cat_match.lastindex else cat_match.group()
        cat_lines = re.findall(r"^\s*\d+\.", cat_text, re.MULTILINE)
        if len(cat_lines) < 5:
            errors.append(f"カテゴリ数不足: {len(cat_lines)} / 最低5件")
    else:
        errors.append("カテゴリセクションが見つかりません")

    # キーワードチェック（7マス・合計40個以上）
    kw_match = re.search(r"(?:6\.\s*キーワード|キーワード.*?40).*?(?=======|\Z)", content, re.DOTALL)
    if kw_match:
        kw_text = kw_match.group()
        # スペース区切りのキーワードをカウント
        kw_words = []
        for line in kw_text.split("\n"):
            line = line.strip()
            if line and not line.startswith("-") and "キーワード" not in line and "---" not in line and "50文字" not in line and not re.match(r"^\d+\.$", line):
                words = line.split()
                kw_words.extend([w for w in words if len(w) > 1])
        if len(kw_words) < 30:
            errors.append(f"キーワード総数不足: {len(kw_words)} / 最低30個")
    else:
        errors.append("キーワードセクションが見つかりません")

    if errors:
        print("FAIL: kindle_application.txt 検証エラー")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: kindle_application.txt ({char_count}字)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_kindle_app.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
