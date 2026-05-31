"""
encode_binaries.py — バイナリファイルをBase64テキストに変換

Codex PRにバイナリファイルを含められないため、
Base64エンコードしたテキストファイルとしてPRに含める。

Usage:
    python scripts/encode_binaries.py output/{slug}

エンコード後、元のバイナリファイルは自動削除される（Codex PR制限回避のため）。
ユーザーはPRマージ後に decode_binaries.py で復元する。

出力:
    output/{slug}/binaries/
        cover.jpg.b64
        aplus_1.png.b64
        aplus_2.png.b64
        aplus_3.png.b64
        aplus_4.png.b64
        manuscript.docx.b64  (存在する場合)
        manifest.json        (復元用マッピング)
"""

import base64
import os
import sys
import json


BINARY_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.docx', '.pdf', '.gif', '.webp', '.bmp'}


def encode_file(src_path: str, dst_path: str) -> dict:
    """1ファイルをBase64エンコードして保存"""
    with open(src_path, 'rb') as f:
        data = f.read()

    encoded = base64.b64encode(data).decode('ascii')

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(encoded)

    return {
        'original': os.path.basename(src_path),
        'encoded': os.path.basename(dst_path),
        'original_size': len(data),
        'encoded_size': len(encoded),
    }


def find_binaries(output_dir: str) -> list:
    """output_dir内のバイナリファイルを再帰的に検索"""
    binaries = []
    for root, dirs, files in os.walk(output_dir):
        # binaries/ ディレクトリ自体はスキップ
        if 'binaries' in root:
            continue
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in BINARY_EXTENSIONS:
                binaries.append(os.path.join(root, fname))
    return binaries


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/encode_binaries.py output/{slug}")
        sys.exit(1)

    output_dir = sys.argv[1]
    if not os.path.isdir(output_dir):
        print(f"ERROR: ディレクトリが見つかりません: {output_dir}")
        sys.exit(1)

    binaries_dir = os.path.join(output_dir, 'binaries')
    os.makedirs(binaries_dir, exist_ok=True)

    binaries = find_binaries(output_dir)
    if not binaries:
        print("バイナリファイルが見つかりませんでした。")
        sys.exit(0)

    manifest = []
    for src_path in binaries:
        # 元のパスからoutput_dir相対パスを取得
        rel_path = os.path.relpath(src_path, output_dir)
        # フラットに保存（サブディレクトリ構造を _ で置換）
        flat_name = rel_path.replace(os.sep, '_') + '.b64'
        dst_path = os.path.join(binaries_dir, flat_name)

        info = encode_file(src_path, dst_path)
        info['relative_path'] = rel_path
        manifest.append(info)
        print(f"  ENCODED: {rel_path} -> binaries/{flat_name} ({info['original_size']:,} bytes)")

    # マニフェスト保存（デコード時に使用）
    manifest_path = os.path.join(binaries_dir, 'manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 元のバイナリファイルを削除（Codex PRがバイナリを検出しないようにする）
    deleted = 0
    for src_path in binaries:
        try:
            os.remove(src_path)
            deleted += 1
            print(f"  DELETED: {os.path.relpath(src_path, output_dir)}")
        except OSError as e:
            print(f"  WARNING: 削除失敗 {src_path}: {e}")

    # 空になったディレクトリも削除
    for root, dirs, files in os.walk(output_dir, topdown=False):
        if 'binaries' in root:
            continue
        if not files and not dirs and root != output_dir:
            try:
                os.rmdir(root)
            except OSError:
                pass

    print(f"\n完了: {len(manifest)}ファイルをエンコード、{deleted}ファイルの元バイナリを削除しました。")
    print(f"マニフェスト: {manifest_path}")
    print(f"\n※ PRマージ後に python scripts/decode_binaries.py output/{{slug}} で復元してください。")


if __name__ == '__main__':
    main()
