"""
encode_binaries.py — バイナリファイルをBase64テキストに変換

Codex PRにバイナリファイルを含められないため、
Base64エンコードしたテキストファイルとしてPRに含める。

Usage:
    python scripts/encode_binaries.py output/{slug}

Phase 6/7のvalidate_images.py内から自動呼出しされる。
複数回呼ばれてもmanifest.jsonは追記モードで安全。
エンコード後、元のバイナリファイルは自動削除される。
ユーザーはPRマージ後に decode_binaries.py で復元する。
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

    raw = base64.b64encode(data).decode('ascii')
    # 76文字ごとに改行（MIME標準準拠）— Codex UI diff描画のフリーズ防止
    encoded = '\n'.join(raw[i:i+76] for i in range(0, len(raw), 76))
    file_content = encoded + '\n'

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    return {
        'original': os.path.basename(src_path),
        'encoded': os.path.basename(dst_path),
        'original_size': len(data),
        'encoded_size': len(file_content),
    }


def find_binaries(output_dir: str) -> list:
    """output_dir内のバイナリファイルを再帰的に検索"""
    binaries = []
    for root, dirs, files in os.walk(output_dir):
        if 'binaries' in root:
            continue
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in BINARY_EXTENSIONS:
                binaries.append(os.path.join(root, fname))
    return binaries


def load_existing_manifest(manifest_path: str) -> list:
    """既存のmanifest.jsonがあれば読み込む（追記モード対応）"""
    if os.path.isfile(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def encode_and_cleanup(output_dir: str) -> int:
    """メイン処理: エンコード→削除→manifest更新。戻り値はエンコードしたファイル数"""
    binaries_dir = os.path.join(output_dir, 'binaries')
    os.makedirs(binaries_dir, exist_ok=True)

    binaries = find_binaries(output_dir)
    if not binaries:
        print("  encode: バイナリファイルなし（スキップ）")
        return 0

    # 既存manifestを読み込み（Phase 6→7の追記対応）
    manifest_path = os.path.join(binaries_dir, 'manifest.json')
    manifest = load_existing_manifest(manifest_path)
    existing_paths = {e['relative_path'] for e in manifest}

    new_count = 0
    for src_path in binaries:
        # クロスプラットフォーム対応: パス区切りを常に '/' に統一
        rel_path = os.path.relpath(src_path, output_dir).replace(os.sep, '/')

        flat_name = rel_path.replace('/', '_') + '.b64'
        dst_path = os.path.join(binaries_dir, flat_name)

        # 既にエンコード済みの場合は上書き（ユーザーが再生成した場合の対応）
        if rel_path in existing_paths:
            manifest = [e for e in manifest if e['relative_path'] != rel_path]
            print(f"  OVERWRITE: {rel_path} の既存Base64を上書きします")

        info = encode_file(src_path, dst_path)
        info['relative_path'] = rel_path
        manifest.append(info)
        new_count += 1
        print(f"  ENCODED: {rel_path} -> binaries/{flat_name} ({info['original_size']:,} bytes)")

    # manifest保存（追記済み）
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 元のバイナリファイルを削除
    deleted = 0
    for src_path in binaries:
        try:
            os.remove(src_path)
            deleted += 1
            print(f"  DELETED: {os.path.relpath(src_path, output_dir)}")
        except OSError as e:
            print(f"  WARNING: 削除失敗 {src_path}: {e}")

    # 空ディレクトリ削除
    for root, dirs, files in os.walk(output_dir, topdown=False):
        if 'binaries' in root:
            continue
        if not files and not dirs and root != output_dir:
            try:
                os.rmdir(root)
            except OSError:
                pass

    print(f"  encode完了: {new_count}ファイルエンコード、{deleted}ファイル削除")
    return new_count


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/encode_binaries.py output/{slug}")
        sys.exit(1)

    output_dir = sys.argv[1]
    if not os.path.isdir(output_dir):
        print(f"ERROR: ディレクトリが見つかりません: {output_dir}")
        sys.exit(1)

    count = encode_and_cleanup(output_dir)
    if count > 0:
        print(f"\n※ PRマージ後に python scripts/decode_binaries.py output/{{slug}} で復元してください。")


if __name__ == '__main__':
    main()
