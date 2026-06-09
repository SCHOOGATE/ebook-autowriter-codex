# eBook AutoWriter for Codex

Codex CLI で **Kindle電子書籍（25,000字・5章構成）** を対話型で一括生成するワークフロー。

テーマを入力するだけで、リサーチ → 執筆 → メタデータ → 表紙 → A+画像 → Kindle申請データまで自動生成します。

> **初めての方は [導入手順書（docs/setup-guide.md）](docs/setup-guide.md) を参照してください。**
> アカウント作成からKindle出版までの全手順をステップバイステップで解説しています。

---

## 成果物（8点セット）

| # | ファイル | 内容 |
|---|---------|------|
| 1 | `manuscript.md` | Markdown原稿（25,000字以上） |
| 2 | `manuscript.html` | HTML原稿（DOCX変換用） |
| 3 | `research.md` | 5層ディープリサーチ結果（URL15件以上） |
| 4 | `listing.txt` | 出版メタデータ（タイトル・KW・紹介文） |
| 5 | `cover_prompt.txt` | 表紙プロンプト（YAML） |
| 6 | `kindle_application.txt` | Kindle申請データ |
| 7 | `images/cover.png` | 表紙画像（1600×2560px） |
| 8 | `images/aplus_1〜4.png` | A+コンテンツ画像4枚（970×600px） |

全成果物は `output/{テーマslug}/` に出力されます。

---

## 前提条件

| 項目 | 詳細 |
|------|------|
| **OpenAI** | Plus プラン以上（$20/月〜）。**Codex CLI で `--model gpt-5.5` を指定して使用** |
| **GitHub** | アカウント作成済み（リポジトリ接続に必要） |
| **Python** | 3.8 以上 |
| **pandoc** | DOCX変換に使用（ローカル後処理） |
| **python-docx** | DOCX改ページ挿入に使用（ローカル後処理） |
| **Pillow** | A+画像リサイズに使用（ローカル後処理） |

---

## セットアップ手順

### Step 1: OpenAI Plus 以上の契約

ChatGPT Plus（$20/月）以上の契約が必要です。Codex CLI のログインに使用します。

### Step 2: セットアップ

詳細な手順は [導入手順書（docs/setup-guide.md）](docs/setup-guide.md) を参照してください。
Node.js → Git → Python → Codex CLI → Chrome設定 → リポジトリダウンロード の順で進めます。

### Step 3: ローカル環境の準備

```bash
# pandoc のインストール
# Windows: https://pandoc.org/installing.html からインストーラーをダウンロード
# Mac: brew install pandoc

# Python パッケージのインストール
pip install python-docx Pillow
```

---

## 使い方

### Codex での対話フロー

1. Codex CLI で **`--model gpt-5.5`** を指定して起動（例: `codex --model gpt-5.5 --dangerously-bypass-approvals-and-sandbox "AGENTS.mdの指示に従って「AI副業の電子書籍を制作」を開始してください。"`）
2. 著者名・参考資料（任意）を回答
3. 以下の7つのチェックポイント（★）で確認を求められます

```
「{テーマ}の電子書籍を制作」入力
  ↓
Phase 1: 著者名・参考資料の入力
Phase 2: 5層ディープリサーチ（自動）
  ↓
★確認1: タイトル10案 → 選択・確定
★確認2: 構成（目次）の承認
  ↓ 承認後、自動で一気に生成 ↓
Phase 3: 原稿執筆（25,000字以上）
Phase 4: 出版メタデータ生成
Phase 5: Kindle申請データ生成
  ↓
★確認3: 表紙プロンプトの確認
  ↓
Phase 6: 表紙画像生成
★確認4: 表紙画像の確認
  ↓
★確認5: A+コンテンツ4枚のプロンプト確認
Phase 7: A+画像4枚生成
★確認6: A+画像の確認
  ↓
Phase 8: 統合検証（全品質ゲート自動実行）
★確認7: 最終確認・完了
```

各★で「OK」「進めて」と回答すれば次に進みます。修正指示も可能です。

### ローカル後処理（Codex完了後）

Codex での生成が完了したら、ローカルで以下を実行します。

```bash
# 1. 最新の出力を取得
git pull

# 2. 不可視文字の除去（必須）
python scripts/clean_invisible.py output/{slug}/

# 3. DOCX変換
pandoc output/{slug}/manuscript.html -o output/{slug}/manuscript.docx

# 4. DOCX後処理（章ごとの改ページ挿入）
python scripts/docx_postprocess.py output/{slug}/manuscript.docx

# 5. A+画像リサイズ（970x600px）
python scripts/resize_aplus.py output/{slug}/images/

# 6. 品質検証（任意・確認用）
python scripts/validate_all.py output/{slug}/
```

`{slug}` はテーマから自動生成されるフォルダ名です（例: `ai-side-hustle`）。

---

## フォルダ構成

```
ebook-autowriter-codex/
├── README.md                   ← このファイル
├── AGENTS.md                   ← Codex指示書（v4.5）
├── scripts/
│   ├── validate_all.py         ← 統合検証（全Phase一括）
│   ├── validate_research.py    ← リサーチ検証（URL15件・3,000字）
│   ├── validate_meta.py        ← メタ情報検証
│   ├── validate_manuscript.py  ← 原稿検証（25,000字・n-gram重複15%未満）
│   ├── validate_listing.py     ← メタデータ検証（3,000字）
│   ├── validate_kindle_app.py  ← 申請データ検証（PASONA・KW40個）
│   ├── validate_images.py      ← 画像検証（ファイルサイズ50KB以上）
│   ├── clean_invisible.py      ← 不可視文字除去
│   ├── docx_postprocess.py     ← DOCX改ページ挿入
│   └── resize_aplus.py         ← A+画像リサイズ
├── templates/
│   ├── research_template.md    ← リサーチ出力テンプレート
│   ├── listing_template.txt    ← 出版メタデータテンプレート
│   └── kindle_app_template.txt ← Kindle申請テンプレート
├── input/                      ← 参考資料の置き場（任意）
└── output/                     ← 生成物の出力先（自動作成）
    └── {slug}/                 ← テーマごとのフォルダ
```

---

## 品質ゲート

全スクリプトは **外部依存なし（Python標準ライブラリのみ）** で動作します。

| 検証項目 | スクリプト | 基準 |
|---------|-----------|------|
| リサーチ | `validate_research.py` | URL 15件以上、3,000字以上 |
| メタ情報 | `validate_meta.py` | タイトル・著者名の存在確認 |
| 原稿 | `validate_manuscript.py` | 25,000字以上、n-gram重複率15%未満 |
| メタデータ | `validate_listing.py` | 3,000字以上、必須項目完備 |
| 申請データ | `validate_kindle_app.py` | PASONA説明文、KW 40個以上 |
| 画像 | `validate_images.py` | ファイルサイズ 50KB以上（ダミー防止） |

Codex が各Phase完了時に自動実行します。ローカルでも `validate_all.py` で一括確認できます。

---

## トラブルシューティング

### 原稿に「??」や文字化けが表示される

**原因:** Codex が生成するテキストに不可視文字（ZWNJ U+200C、Tags U+E0000〜等）が混入することがあります。

**対処:**
```bash
python scripts/clean_invisible.py output/{slug}/
```
このスクリプトが対象の7ファイルから不可視文字を自動除去します。

### DOCX で太字（Bold）が消える

**原因:** 旧バージョンの後処理で句点分割を行うと、Word の run 構造が破壊されていました。

**対処:** v3.1 で解決済みです。原稿は Markdown 段階で「1文=1段落」ルールが適用されるため、DOCX 後処理では改ページ挿入のみ行います。

### DOCX で `\newpage` が □ で表示される

**原因:** Markdown の特殊文字がそのまま残っている場合に発生します。

**対処:** v3.1 で解決済みです。Markdown 段階で `\newpage` は除去され、`docx_postprocess.py` が H1/H2 見出し前に改ページを挿入します。

### 検証スクリプトが FAIL になる

**原因:** Codex の生成が不完全な場合（字数不足、URL不足など）。

**対処:** Codex は検証 NG 時に自動リトライします（最大2回）。それでも FAIL の場合は、該当 Phase を手動で再実行してください。

### Codex が途中で止まる

**対処:** コマンドプロンプトで「続けて」と入力しEnterを押すと、中断地点から再開します。★チェックポイントで止まっている場合は「OK」で進行します。

---

## Kindle 出版までの流れ

1. **Codex で生成** — 「{テーマ}の電子書籍を制作」→ 対話フローで8点セット完成
2. **ローカル後処理** — 不可視文字除去 → DOCX変換 → 改ページ挿入
3. **表紙の最終調整** — `cover_prompt.txt` を使って表紙画像を微調整（必要に応じて）
4. **KDP にログイン** — [kdp.amazon.co.jp](https://kdp.amazon.co.jp/)
5. **書籍情報の入力** — `kindle_application.txt` の内容をコピー＆ペースト
6. **原稿のアップロード** — `manuscript.docx` をアップロード
7. **表紙のアップロード** — `images/cover.png` をアップロード
8. **A+コンテンツの設定** — `images/aplus_1〜4.png` を A+コンテンツに登録
9. **プレビュー確認 → 出版**

---

## 動作確認テスト

初回セットアップ後、以下のテーマで動作確認を推奨します:

```
テーマ: 朝5分でできる瞑想入門
著者名: （ご自身の名前）
参考資料: なし
```

短時間で全フローを確認できるシンプルなテーマです。

---

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| v3.1 | 2026-05-30 | Kindle変換問題解決（不可視文字・Bold破壊・行間） |
| v3.0 | 2026-05-25 | 対話型7チェックポイント方式に刷新 |
| v2.0 | 2026-05-20 | 品質ゲート・検証スクリプト統合 |
| v1.0 | 2026-05-15 | 初版リリース |

---

## ライセンス

本リポジトリは AI出版ラボ のコミュニティメンバー向けに提供されています。
個人の電子書籍制作目的での利用は自由ですが、商用再配布・競合サービスへの転用は禁止です。
詳細は [LICENSE](LICENSE) を参照してください。
