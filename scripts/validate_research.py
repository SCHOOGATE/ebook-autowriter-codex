#!/usr/bin/env python3
"""研究レポート（research.md）の品質検証スクリプト（stdlib only）"""
import sys
import os
import re


def validate(slug_dir):
    path = os.path.join(slug_dir, "research.md")
    errors = []

    if not os.path.exists(path):
        print("FAIL: research.md が存在しません")
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    char_count = len(content)
    if char_count < 3000:
        errors.append(f"文字数不足: {char_count} / 最低3,000字")

    # 5層見出しチェック
    required_layers = [
        r"##\s*.*Layer\s*1|##\s*.*YouTube",
        r"##\s*.*Layer\s*2|##\s*.*note",
        r"##\s*.*Layer\s*3|##\s*.*SNS|##\s*.*ショート",
        r"##\s*.*Layer\s*4|##\s*.*市場|##\s*.*競合|##\s*.*書籍",
        r"##\s*.*Layer\s*5|##\s*.*悩み|##\s*.*ニーズ",
    ]
    layer_names = ["Layer1(YouTube)", "Layer2(note)", "Layer3(SNS)", "Layer4(競合)", "Layer5(悩み)"]
    for i, pattern in enumerate(required_layers):
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"見出し未検出: {layer_names[i]}")

    # URL数チェック
    urls = re.findall(r"https?://[^\s\)]+", content)
    if len(urls) < 15:
        errors.append(f"参考URL不足: {len(urls)} / 最低15件")

    # 品質基準セクションチェック
    if "品質基準" not in content and "チェック" not in content:
        errors.append("品質基準チェックセクションが見つかりません")

    if errors:
        print("FAIL: research.md 検証エラー")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: research.md ({char_count}字, URL {len(urls)}件)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_research.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
