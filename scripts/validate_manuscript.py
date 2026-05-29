#!/usr/bin/env python3
"""原稿（manuscript.md）の品質検証スクリプト（stdlib only）
- 総字数・章別字数チェック
- n-gram重複検知（同一文反復防止）
- 禁止パターン検出
- です/ます調の一貫性チェック
"""
import sys
import os
import re
from collections import Counter


def extract_chapters(content):
    """## 見出しで章を分割し、(章名, 本文) のリストを返す"""
    parts = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    chapters = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        title = lines[0].strip().lstrip("#").strip()
        body = lines[1] if len(lines) > 1 else ""
        chapters.append((title, body))
    return chapters


def ngram_duplication_ratio(text, n=5):
    """n文字のn-gramを抽出し、重複率を計算（0.0〜1.0）"""
    # 空白・改行を正規化
    clean = re.sub(r"\s+", "", text)
    if len(clean) < n:
        return 0.0
    ngrams = [clean[i:i+n] for i in range(len(clean) - n + 1)]
    if not ngrams:
        return 0.0
    counter = Counter(ngrams)
    total = len(ngrams)
    unique = len(counter)
    if total == 0:
        return 0.0
    duplication = 1.0 - (unique / total)
    return duplication


def check_forbidden_patterns(content):
    """禁止パターンの検出"""
    issues = []
    # Markdownテーブル
    if re.search(r"^\|.*\|.*\|", content, re.MULTILINE):
        issues.append("Markdownテーブル記法（| ... |）が検出されました")
    # コードブロック
    if "```" in content:
        issues.append("コードブロック（```）が検出されました")
    # ASCII罫線図
    if re.search(r"[┌─┐│└─┘├┤┬┴┼]", content):
        issues.append("ASCII罫線文字が検出されました")
    # 画像タグ
    if re.search(r"<!--\s*\[.*IMAGE.*\]\s*-->", content, re.IGNORECASE):
        issues.append("画像タグ（<!-- [IMAGE] -->）が検出されました")
    return issues


def check_style_consistency(content):
    """です/ます調の一貫性チェック"""
    desu_masu = len(re.findall(r"(?:です|ます|ください|ましょう|でしょう)[。\n]", content))
    da_dearu = len(re.findall(r"(?:だ|である|しよう|だろう)[。\n]", content))
    total = desu_masu + da_dearu
    if total == 0:
        return 1.0  # 判定不能は合格扱い
    return desu_masu / total


def validate(slug_dir):
    path = os.path.join(slug_dir, "manuscript.md")
    errors = []

    if not os.path.exists(path):
        print("FAIL: manuscript.md が存在しません")
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # 総字数チェック
    total_chars = len(content)
    if total_chars < 25000:
        errors.append(f"総字数不足: {total_chars} / 最低25,000字")

    # 章分割チェック
    chapters = extract_chapters(content)
    if len(chapters) < 7:  # はじめに + 5章 + おわりに
        errors.append(f"章数不足: {len(chapters)} / 最低7セクション（はじめに+5章+おわりに）")

    # 章別字数チェック
    for title, body in chapters:
        body_len = len(body)
        if "はじめに" in title or "おわりに" in title:
            if body_len < 1000:
                errors.append(f"「{title}」字数不足: {body_len} / 最低1,000字")
        elif title.startswith("第") or re.match(r"\d+章", title):
            if body_len < 3500:
                errors.append(f"「{title}」字数不足: {body_len} / 最低3,500字")

    # n-gram重複チェック
    dup_ratio = ngram_duplication_ratio(content, n=5)
    if dup_ratio > 0.15:
        errors.append(f"n-gram重複率が高すぎます: {dup_ratio:.1%} / 上限15%")

    # 禁止パターンチェック
    forbidden = check_forbidden_patterns(content)
    errors.extend(forbidden)

    # です/ます調チェック
    style_ratio = check_style_consistency(content)
    if style_ratio < 0.80:
        errors.append(f"です/ます調の一貫性不足: {style_ratio:.0%} / 最低80%")

    if errors:
        print("FAIL: manuscript.md 検証エラー")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: manuscript.md ({total_chars}字, {len(chapters)}セクション, 重複率{dup_ratio:.1%})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_manuscript.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
