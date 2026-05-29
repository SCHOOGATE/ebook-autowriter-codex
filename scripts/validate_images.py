#!/usr/bin/env python3
"""画像ファイルの品質検証スクリプト（stdlib only）
- ファイル存在チェック
- 最小ファイルサイズチェック（ダミー画像排除）
"""
import sys
import os


# 最小ファイルサイズ（バイト）
MIN_COVER_SIZE = 50 * 1024    # 50KB
MIN_APLUS_SIZE = 30 * 1024    # 30KB


def validate_cover(slug_dir):
    """表紙画像の検証"""
    path = os.path.join(slug_dir, "images", "cover.jpg")
    if not os.path.exists(path):
        # .pngもチェック
        path = os.path.join(slug_dir, "images", "cover.png")
        if not os.path.exists(path):
            return "cover.jpg/png が存在しません"

    size = os.path.getsize(path)
    if size < MIN_COVER_SIZE:
        return f"cover画像のサイズが小さすぎます: {size:,}B / 最低{MIN_COVER_SIZE:,}B（ダミー画像の可能性）"

    return None


def validate_aplus(slug_dir):
    """A+コンテンツ画像4枚の検証"""
    issues = []
    for i in range(1, 5):
        path = os.path.join(slug_dir, "images", f"aplus_{i}.png")
        if not os.path.exists(path):
            issues.append(f"aplus_{i}.png が存在しません")
            continue
        size = os.path.getsize(path)
        if size < MIN_APLUS_SIZE:
            issues.append(f"aplus_{i}.png のサイズが小さすぎます: {size:,}B / 最低{MIN_APLUS_SIZE:,}B")
    return issues


def validate(slug_dir, mode="all"):
    errors = []

    if mode in ("all", "cover"):
        cover_err = validate_cover(slug_dir)
        if cover_err:
            errors.append(cover_err)

    if mode in ("all", "aplus"):
        aplus_errs = validate_aplus(slug_dir)
        errors.extend(aplus_errs)

    if errors:
        print(f"FAIL: 画像検証エラー ({mode})")
        for e in errors:
            print(f"  - {e}")
        return 1

    # サイズ情報を表示
    cover_path = os.path.join(slug_dir, "images", "cover.jpg")
    if not os.path.exists(cover_path):
        cover_path = os.path.join(slug_dir, "images", "cover.png")
    if os.path.exists(cover_path):
        print(f"  cover: {os.path.getsize(cover_path):,}B")
    for i in range(1, 5):
        ap = os.path.join(slug_dir, "images", f"aplus_{i}.png")
        if os.path.exists(ap):
            print(f"  aplus_{i}: {os.path.getsize(ap):,}B")

    print(f"PASS: 画像検証OK ({mode})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_images.py <output/slug_dir> [all|cover|aplus]")
        sys.exit(1)
    mode = sys.argv[2] if len(sys.argv) > 2 else "all"
    sys.exit(validate(sys.argv[1], mode))
