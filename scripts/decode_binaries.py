"""
decode_binaries.py — Base64テキストをバイナリファイルに復元

PRマージ後にローカルで実行し、画像・DOCXを復元する。

Usage:
    python scripts/decode_binaries.py output/{slug}

復元先:
    元のパスに復元される（manifest.jsonに基づく）
    例: output/{slug}/images/cover.jpg
        output/{slug}/images/aplus_1.png
        output/{slug}/manuscript.docx
"""

import base64
import os
import sys
import json


def decode_file(b64_path: str, dst_path: str) -> int:
    """1ファイルをBase64デコードして復元"""
    with open(b64_path, 'r', encoding='utf-8') as f:
        encoded = f.read().strip()

    data = base64.b64decode(encoded)

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, 'wb') as f:
        f.write(data)

    return len(data)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/decode_binaries.py output/{slug}")
        sys.exit(1)

    output_dir = sys.argv[1]
    binaries_dir = os.path.join(output_dir, 'binaries')
    manifest_path = os.path.join(binaries_dir, 'manifest.json')

    if not os.path.isfile(manifest_path):
        print(f"ERROR: マニフェストが見つかりません: {manifest_path}")
        print("encode_binaries.py が実行されていない可能性があります。")
        sys.exit(1)

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    if not manifest:
        print("デコード対象のファイルがありません。")
        sys.exit(0)

    restored = 0
    for entry in manifest:
        rel_path = entry['relative_path']
        flat_name = rel_path.replace(os.sep, '_') + '.b64'
        b64_path = os.path.join(binaries_dir, flat_name)
        dst_path = os.path.join(output_dir, rel_path)

        if not os.path.isfile(b64_path):
            print(f"  SKIP: {flat_name} が見つかりません")
            continue

        size = decode_file(b64_path, dst_path)
        restored += 1
        print(f"  RESTORED: {rel_path} ({size:,} bytes)")

    print(f"\n完了: {restored}/{len(manifest)}ファイルを復元しました。")


if __name__ == '__main__':
    main()
