#!/usr/bin/env python3
"""統合検証スクリプト: 全Phase検証を順次実行し、completion_report.json を出力

画像はBase64エンコード後に元ファイルが削除されるため、
images検証はbinaries/manifest.jsonの存在と.b64ファイルの整合性で判定する。
"""
import sys
import os
import json
import importlib.util
from datetime import datetime


VALIDATORS = [
    ("research",     "validate_research.py"),
    ("meta",         "validate_meta.py"),
    ("manuscript",   "validate_manuscript.py"),
    ("listing",      "validate_listing.py"),
    ("kindle_app",   "validate_kindle_app.py"),
]


def load_validator(script_name):
    """同じディレクトリの検証スクリプトを動的にインポート"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    spec = importlib.util.spec_from_file_location(script_name.replace(".py", ""), script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validate_binaries(slug_dir):
    """Base64エンコード済み画像の検証（manifest.json + .b64ファイルの存在確認）"""
    binaries_dir = os.path.join(slug_dir, 'binaries')
    manifest_path = os.path.join(binaries_dir, 'manifest.json')

    if not os.path.isfile(manifest_path):
        print("FAIL: binaries/manifest.json が存在しません")
        return 1

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    if not manifest:
        print("FAIL: manifest.json が空です")
        return 1

    # 必須ファイルチェック
    required = {'images/cover.jpg', 'images/cover.png'}
    found_paths = {e['relative_path'] for e in manifest}
    has_cover = bool(required & found_paths)
    if not has_cover:
        print("FAIL: 表紙画像(cover.jpg/png)がmanifestに含まれていません")
        return 1

    aplus_count = sum(1 for p in found_paths if 'aplus_' in p)
    if aplus_count < 4:
        print(f"FAIL: A+画像が不足しています: {aplus_count}/4")
        return 1

    # .b64ファイルの存在確認
    errors = []
    for entry in manifest:
        rel_path = entry['relative_path']
        flat_name = rel_path.replace('/', '_') + '.b64'
        b64_path = os.path.join(binaries_dir, flat_name)
        if not os.path.isfile(b64_path):
            errors.append(f"  - {flat_name} が見つかりません")

    if errors:
        print("FAIL: Base64ファイルが不足しています")
        for e in errors:
            print(e)
        return 1

    print(f"PASS: binaries ({len(manifest)}ファイル, manifest.json整合OK)")
    return 0


def validate_all(slug_dir):
    results = {}
    all_pass = True

    print("=" * 60)
    print(f"eBook AutoWriter 統合検証")
    print(f"対象: {slug_dir}")
    print(f"実行日時: {datetime.now().isoformat()}")
    print("=" * 60)

    for name, script in VALIDATORS:
        print(f"\n--- {name} ({script}) ---")
        try:
            mod = load_validator(script)
            ret = mod.validate(slug_dir)
            results[name] = "PASS" if ret == 0 else "FAIL"
            if ret != 0:
                all_pass = False
        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = f"ERROR: {str(e)}"
            all_pass = False

    # Base64画像の検証（元画像は削除済みのためmanifest+.b64で検証）
    print(f"\n--- binaries (Base64画像検証) ---")
    ret = validate_binaries(slug_dir)
    results["binaries"] = "PASS" if ret == 0 else "FAIL"
    if ret != 0:
        all_pass = False

    # completion_report.json を出力
    report = {
        "timestamp": datetime.now().isoformat(),
        "slug_dir": slug_dir,
        "overall": "PASS" if all_pass else "FAIL",
        "results": results,
    }
    report_path = os.path.join(slug_dir, "completion_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"総合結果: {'PASS' if all_pass else 'FAIL'}")
    print(f"レポート: {report_path}")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_all.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate_all(sys.argv[1]))
