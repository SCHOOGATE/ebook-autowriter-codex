#!/bin/bash
# Codex Cloud Environment Setup
# このスクリプトはタスク実行前に自動実行される（インターネットアクセスあり）

set -e

# DOCX変換・画像処理に必要なパッケージ
pip install python-docx Pillow

echo "Setup complete: python-docx, Pillow installed"
