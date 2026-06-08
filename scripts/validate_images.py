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


def get_image_dimensions(path):
    """Get image width and height from file header (stdlib only, no PIL)."""
    try:
        with open(path, 'rb') as f:
            header = f.read(32)
            # PNG
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                w = int.from_bytes(header[16:20], 'big')
                h = int.from_bytes(header[20:24], 'big')
                return w, h
            # JPEG
            if header[:2] == b'\xff\xd8':
                f.seek(0)
                data = f.read()
                i = 2
                while i < len(data) - 9:
                    if data[i] != 0xFF:
                        break
                    marker = data[i + 1]
                    if marker in (0xC0, 0xC1, 0xC2):
                        h = int.from_bytes(data[i+5:i+7], 'big')
                        w = int.from_bytes(data[i+7:i+9], 'big')
                        return w, h
                    seg_len = int.from_bytes(data[i+2:i+4], 'big')
                    i += 2 + seg_len
    except Exception:
        pass
    return None, None


def validate_cover(slug_dir):
    """Cover image validation with size and resolution check."""
    path = os.path.join(slug_dir, "images", "cover.jpg")
    if not os.path.exists(path):
        path = os.path.join(slug_dir, "images", "cover.png")
        if not os.path.exists(path):
            return "cover.jpg/png が存在しません"

    size = os.path.getsize(path)
    if size < MIN_COVER_SIZE:
        return f"cover画像のサイズが小さすぎます: {size:,}B / 最低{MIN_COVER_SIZE:,}B（ダミー画像の可能性）"

    w, h = get_image_dimensions(path)
    if w and h:
        print(f"  cover resolution: {w}x{h}")
        if w < 1000 or h < 1500:
            return f"cover解像度が低すぎます: {w}x{h} / 推奨1600x2560以上"

    return None


def validate_aplus(slug_dir):
    """A+ content images validation with size and resolution check."""
    issues = []
    for i in range(1, 5):
        path = os.path.join(slug_dir, "images", f"aplus_{i}.png")
        if not os.path.exists(path):
            issues.append(f"aplus_{i}.png が存在しません")
            continue
        size = os.path.getsize(path)
        if size < MIN_APLUS_SIZE:
            issues.append(f"aplus_{i}.png のサイズが小さすぎます: {size:,}B / 最低{MIN_APLUS_SIZE:,}B")
        w, h = get_image_dimensions(path)
        if w and h:
            print(f"  aplus_{i} resolution: {w}x{h}")
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
