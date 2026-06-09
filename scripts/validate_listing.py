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

    # キーワード行チェック（7行）— v4.5: count "キーワードN（50文字以内）" headers
    kw_headers = re.findall(r"^キーワード\d+（50文字以内）", content, re.MULTILINE)
    if kw_headers:
        if len(kw_headers) < 7:
            errors.append(f"キーワード行数不足: {len(kw_headers)} / 最低7行")
    else:
        # Fallback: find "キーワード（7つ）" section
        kw_section = re.search(r"キーワード（7つ）.*?(?=======|\Z)", content, re.DOTALL)
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

    # 著者名一貫性チェック（book_meta.md と一致するか）
    meta_path = os.path.join(slug_dir, "book_meta.md")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as mf:
            meta_content = mf.read()
        meta_author = None
        for line in meta_content.split("\n"):
            m = re.match(r"(?:\*\*)?著者名(?:\*\*)?[：:]\s*(.+)", line)
            if m:
                meta_author = m.group(1).strip().strip("*").strip()
                break
        if meta_author:
            # Check if the confirmed author name appears in listing.txt
            author_section = re.search(r"著者名\s*\n(.+?)(?:\n\n|\n---)", content, re.DOTALL)
            if author_section:
                listing_author = author_section.group(1).strip()
                if meta_author not in listing_author and listing_author not in meta_author:
                    errors.append(
                        f"著者名不一致: book_meta.md=\"{meta_author}\" vs "
                        f"listing.txt=\"{listing_author}\""
                    )

    # 紹介文タイプ選択チェック
    type_labels = ["タイプA", "タイプB", "タイプC", "タイプD", "おだやか共感", "成果アピール", "BtoB戦略", "技術入門"]
    has_type_label = any(label in content for label in type_labels)
    if not has_type_label:
        errors.append("紹介文のタイプ選択が明記されていません（タイプA〜Dのいずれかを記載）")

    # 紹介文チェック
    intro_match = re.search(r"紹介文.*?(?=======|\Z)", content, re.DOTALL)
    if intro_match:
        intro_text = intro_match.group()
        intro_chars = len(intro_text)
        if intro_chars < 3000:
            errors.append(f"紹介文の文字数不足: {intro_chars} / 最低3,000字")
        # 段落反復検出
        sentences = [s.strip() for s in re.split(r"[。\n]", intro_text) if len(s.strip()) >= 20]
        if sentences:
            from collections import Counter
            sent_counts = Counter(sentences)
            repeated = {s: c for s, c in sent_counts.items() if c >= 3}
            if repeated:
                sample = list(repeated.keys())[0][:60]
                total_repeats = sum(c - 1 for c in repeated.values())
                errors.append(
                    f"紹介文に段落反復 {total_repeats} 箇所 "
                    f"(同一文3回以上): \"{sample}...\""
                )
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
