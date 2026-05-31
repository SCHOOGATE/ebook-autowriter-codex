#!/usr/bin/env python3
"""画像ファイルの品質検証 + Base64エンコード + 元ファイル削除

validate → PASS → encode_binaries自動実行 → 元バイナリ削除
これによりPR作成時にバイナリが存在しない状態を保証する。
"""
import sys
import os
import importlib.util


# 最小ファイルサイズ（バイト）
MIN_COVER_SIZE = 50 * 1024    # 50KB
MIN_APLUS_SIZE = 30 * 1024    # 30KB


def validate_cover(slug_dir):
    """表紙画像の検証"""
    path = os.path.join(slug_dir, "images", "cover.jpg")
    if not os.path.exists(path):
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


def run_encode(slug_dir):
    """encode_binaries.pyのencode_and_cleanup関数を呼び出す"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    encode_path = os.path.join(script_dir, "encode_binaries.py")

    if not os.path.exists(encode_path):
        print("  WARNING: encode_binaries.py が見つかりません。エンコードをスキップします。")
        return

    spec = importlib.util.spec_from_file_location("encode_binaries", encode_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.encode_and_cleanup(slug_dir)


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

    # サイズ情報を表示（エンコード前に記録）
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

    # ✅ PASS後に自動Base64エンコード＋元ファイル削除
    print(f"\n--- Base64エンコード開始 ---")
    run_encode(slug_dir)

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_images.py <output/slug_dir> [all|cover|aplus]")
        sys.exit(1)
    mode = sys.argv[2] if len(sys.argv) > 2 else "all"
    sys.exit(validate(sys.argv[1], mode))
