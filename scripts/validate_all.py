#!/usr/bin/env python3
"""統合検証スクリプト: 全Phase検証を順次実行し、completion_report.json を出力"""
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
    ("images",       "validate_images.py"),
]


def load_validator(script_name):
    """同じディレクトリの検証スクリプトを動的にインポート"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    spec = importlib.util.spec_from_file_location(script_name.replace(".py", ""), script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
