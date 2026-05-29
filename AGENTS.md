# eBook AutoWriter for Codex v2.0

電子書籍（25,000字・5章構成）をリサーチ → 執筆 → メタデータ → 表紙 → A+画像 → 申請データまで一括生成。
**全Phase末に検証スクリプトを実行し、不合格なら再実行する。**

## 言語

- 日本語で応答する
- プロンプト・技術用語は英語OK

## 最重要ルール（前回失敗からの教訓）

```
1. 「ファイルが存在する」≠「完了」。内容の品質チェックが必須
2. 各Phaseの末尾で python scripts/validate_*.py を必ず実行する
3. 検証NGなら該当Phaseを再実行する（最大2回リトライ）
4. DOCX変換はCodexの責務ではない（pandoc/python-docx不要）
5. 画像はファイルサイズ50KB以上を必須とする（ダミー禁止）
6. 原稿の同一文反復は禁止（n-gram重複率15%未満を厳守）
```

## 全体フロー（9フェーズ）

```
Phase 1  → 参考資料の受け取り
Phase 2  → 5層ディープリサーチ        → validate_research.py
Phase 2.5 → タイトル10案 & 基本情報確定（★唯一のユーザー確認）→ validate_meta.py
Phase 3  → 構成設計（目次）
Phase 4  → 原稿執筆 25,000字          → validate_manuscript.py
Phase 5  → 出版メタデータ生成         → validate_listing.py
Phase 6  → 表紙プロンプト + 画像生成  → validate_images.py cover
Phase 7  → A+コンテンツ画像4枚生成    → validate_images.py aplus
Phase 8  → Kindle申請データ出力       → validate_kindle_app.py
Phase 9  → 統合検証                   → validate_all.py
```

**旧Phase 5（DOCX変換）は削除。** Codexの成果物はMarkdown + 画像 + メタデータ。DOCX変換はローカル環境で実行する。

## 自動進行ルール

Phase 2.5（タイトル確定）のみユーザー確認。他はすべて自動進行。
ただし **各Phase末の検証スクリプトがNGの場合、そのPhaseを再実行してからでないと次に進まない。**

## 成果物一覧

```
output/{slug}/
├── manuscript.md             # Markdown原稿（25,000字以上）
├── research.md               # リサーチ結果（3,000字以上・URL15件以上）
├── book_meta.md              # 確定メタ情報（タイトル・著者）
├── listing.txt               # 出版メタデータ（3,000字以上）
├── cover_prompt.txt          # 表紙プロンプト（YAML）
├── kindle_application.txt    # Kindle申請データ（2,000字以上）
├── completion_report.json    # 統合検証レポート
└── images/
    ├── cover.jpg             # 表紙画像（>50KB）
    ├── aplus_1.png           # A+ 問題提起（>30KB）
    ├── aplus_2.png           # A+ 煽り・共感（>30KB）
    ├── aplus_3.png           # A+ 解決策（>30KB）
    └── aplus_4.png           # A+ CTA（>30KB）
```

**注意: manuscript.docx はCodexでは生成しない。ローカルでpandoc変換する。**

---

## Phase 1: 参考資料の受け取り

ユーザーからテーマと参考資料を受け取る。

受け取れる形式:
- ファイル（PDF、テキスト、Markdown、DOCX）
- URL（Web検索で内容取得）
- テキスト（直接貼り付け）
- 複数資料の組み合わせ

受け取ったら即座にPhase 2へ進む。

---

## Phase 2: 5層ディープリサーチ

参考資料からテーマ・キーワードを抽出し、以下の5層リサーチを実行する。

### Layer 1: YouTube専門家の知見
- 「{テーマ} やり方 解説」「{テーマ} プロ 実践」「{テーマ} 2026 最新」等で検索
- 再生回数が多い動画・専門チャンネルを**5〜10本**特定
- 各動画について: タイトル、チャンネル名、要点、独自ノウハウ、具体的手法を記載
- **動画ページのURLを必ず記録する**

### Layer 2: note専門家の記事
- 「{テーマ} site:note.com」で検索
- 上位**5〜10記事**の内容を取得
- 著者の専門性、独自フレームワーク、具体的数値、読者反応を記載
- **記事URLを必ず記録する**

### Layer 3: SNS/ショート動画トレンド
- Instagram、TikTokのバズキーワード・切り口を調査
- インフルエンサーの推しポイント、Z世代に響く表現を抽出
- **バズワード3つ以上**を明記

### Layer 4: 市場・競合・書籍分析
- Amazon上位書籍**3冊以上**の目次構成・レビュー分析
- 星1-2レビューから読者の不満・期待を抽出
- 競合にない切り口・空白地帯を特定
- **書籍名とURLを必ず記録する**

### Layer 5: 読者の悩み・ニーズ
- Yahoo知恵袋、Q&Aサイトで**10件以上**の悩みを収集
- 初心者がぶつかる壁、「こういう本があれば」という要望を抽出
- **各悩みの出典URLを記録する**

### research.md の必須構造

`templates/research_template.md` を参照し、以下の構造で出力すること:

```markdown
# リサーチ結果: {テーマ}
作成日: YYYY-MM-DD

## 参考資料の要約
{受け取った資料のポイント整理}

## Layer 1: YouTube専門家の知見
### 調査した動画（5本以上）
1. [{動画タイトル}]({URL})
   - チャンネル: {名前}
   - 要点: {具体的内容}
   - 独自ノウハウ: {手法}
2. ...（最低5本）

### 専門家間の主張の違い
{整理}

## Layer 2: note専門家の記事
### 主要記事（5記事以上）
1. [{記事タイトル}]({URL})
   - 著者: {名前}
   - 要点: {具体的内容}
2. ...（最低5記事）

### 共通知見
{まとめ}

## Layer 3: SNS/ショート動画トレンド
### バズキーワード（3つ以上）
- {キーワード1}
- {キーワード2}
- {キーワード3}

### トレンドの切り口
- {切り口}

## Layer 4: 競合書籍分析（3冊以上）
### 主要競合
1. [{書名}]({URL})
   - 強み: {内容}
   - 弱み（低評価レビューから）: {内容}
2. ...（最低3冊）

### 差別化チャンス（空白地帯）
- {ポイント}

## Layer 5: 読者の悩み・ニーズ（10件以上）
### よくある悩み
1. {悩み} — 出典: {URL}
2. ...（最低10件）

### 読者が求めるもの
1. {ニーズ}

## 品質基準チェック
- YouTube: {N}本 ✅/❌
- note: {N}記事 ✅/❌
- SNSバズワード: {N}語 ✅/❌
- 競合書籍: {N}冊 ✅/❌
- 読者の声: {N}件 ✅/❌
```

### Phase 2 完了時の検証（必須）

```bash
python scripts/validate_research.py output/{slug}
```

**検証基準:**
- research.md が3,000字以上
- 5層すべての見出しが存在
- 参考URL 15件以上
- 品質基準チェックセクションが存在

**NGの場合:** 不足しているLayerのリサーチを追加実行し、research.mdを更新してから再検証。

---

## Phase 2.5: タイトル提案 & 基本情報確定（★唯一のユーザー確認ポイント）

### このフェーズだけはユーザー確認を行う

1. リサーチ結果から「次が読みたくなる」書籍構成案を1つ提案
2. 売れるタイトル/サブタイトル案を**10個**生成（以下の型を必ず混ぜる）

| # | 型 | 例 |
|---|---|---|
| 1 | ベネフィット直球型 | 「3日で身につく〇〇」 |
| 2 | 数字提示型 | 「7つの〇〇ルール」 |
| 3 | 問いかけ型 | 「なぜ〇〇は××なのか？」 |
| 4 | 否定・常識破り型 | 「〇〇をやめなさい」 |
| 5 | ターゲット限定型 | 「初心者のための〇〇入門」 |
| 6 | ストーリー型 | 「ゼロから〇〇になった話」 |
| 7 | 比較・選択型 | 「AとBどっちがいい？」 |
| 8 | 完全ガイド型 | 「〇〇完全攻略ガイド」 |
| 9 | 時短・効率型 | 「最短で〇〇する方法」 |
| 10 | 権威・最新型 | 「2026年最新版 〇〇のすべて」 |

3. ユーザーに確定してもらう:
   - タイトル + サブタイトル（10案から選択 or 改変 or 新規）
   - 著者名（必須・空欄不可）

4. 確定情報を `output/{slug}/book_meta.md` に保存:

```markdown
# 書籍メタ情報（Phase 2.5 で確定）

- **タイトル**: {確定タイトル}
- **サブタイトル**: {確定サブタイトル}
- **著者名**: {確定著者名}
- **想定読者**: {...}
- **確定日**: YYYY-MM-DD
```

### Phase 2.5 完了時の検証（必須）

```bash
python scripts/validate_meta.py output/{slug}
```

**確定するまで次のPhaseに進まない。確定後は自動進行を再開。**

---

## Phase 3: 構成設計

`book_meta.md` が確定済みであることを確認し、目次を詳細化する。

### 目次テンプレート

```
書籍タイトル: {確定タイトル}
想定読者: {テーマから推定}
読者のゴール: {この本を読んで何ができるようになるか}

はじめに（1,200〜1,500字）
  - この本の目的 / 読者への約束 / 本書の使い方

第1章: {章タイトル}（4,000〜5,000字）
  1.1〜1.5 各節

第2章〜第5章: 同上の形式

おわりに（1,200〜1,500字）
```

### 構成ルール
- 章の順序: 基礎 → 応用 → 実践
- 各章は独立して読んでも価値がある
- 章をまたいで内容が行き来しない
- 読者が「次に何をすればいいか」がわかる
- 各章に最低5節（### 見出し）を設ける

確認なしでPhase 4へ進む。

---

## Phase 4: 原稿執筆（25,000字）

### 執筆ルール（厳守）

- **総文字数: 25,000字以上**（25,000字未満は不合格）
- 1章あたり: 4,000〜5,000字（3,500字未満は不合格）
- はじめに/おわりに: 各1,200〜1,500字（1,000字未満は不合格）
- 文体: **です・ます調で統一**（80%以上）
  - NG: 「〜だ」「〜である」「〜しよう」「〜だろう」
  - OK: 「〜です」「〜になります」「〜してみましょう」「〜してください」
- 段落: 3〜4文ごとに改行
- 具体例: 各章に最低2つの具体例・事例
- **画像タグ禁止**: `<!-- [IMAGE] -->` 等は一切使用しない
- **表（テーブル）禁止**: 比較情報は箇条書きで表現
- **コードブロック禁止**: コマンドは通常テキストとして記述
- **ASCII図禁止**: 罫線文字（┌─┐│└─┘等）は使わない
- **ユーザー名禁止**: 「読者の皆さん」等の一般表現を使用
- **著者情報禁止**: 原稿本文に著者名・プロフィールを入れない

### 同一文反復の絶対禁止

**前回の失敗: 見た目は25,000字だが同じ文章の繰り返しだった。**

以下を厳守:
- 同じ文を2回以上使わない
- 同じ段落パターンを繰り返さない
- 各節で異なる具体例・データ・視点を提供する
- validate_manuscript.py の n-gram重複チェック（15%未満）をパスすること

### 改ページ・整形ルール

- 各章（`##`）の直前に `\newpage`
- 各節（`###`）の直前に `\newpage`
- はじめに・おわりにの直前にも `\newpage`
- 見出しの前後に空行1行
- 段落間に空行1行
- 箇条書きの前後に空行1行

### 見出しレベル

- `#`: 書籍タイトル（冒頭1回のみ）
- `##`: 章タイトル（はじめに、第1章〜第5章、おわりに）
- `###`: 節タイトル（1.1, 1.2, ...）
- `####`: 小見出し（必要に応じて）

### 章ごとの文字数確認

各章を書き終えたら、その章の文字数を数え、3,500字未満なら加筆する。
全章完成後、`output/{slug}/manuscript.md` に保存。

### Phase 4 完了時の検証（必須）

```bash
python scripts/validate_manuscript.py output/{slug}
```

**検証基準:**
- 総字数 >= 25,000
- 各章 >= 3,500字 / はじめに・おわりに >= 1,000字
- n-gram重複率 < 15%
- 禁止パターン（テーブル・コードブロック・ASCII図・画像タグ）なし
- です/ます調 80%以上

**NGの場合:** 不合格の章を特定し、その章のみ再執筆してmanuscript.mdを更新、再検証。

---

## Phase 5: 出版メタデータ生成

### 手順

1. manuscript.md からテーマ・ターゲット・キーコンセプトを抽出
2. Web検索でキーワードリサーチ
3. メタデータを生成して `listing.txt` に出力

### 生成内容

`templates/listing_template.txt` を参照し、以下を含むこと:

#### タイトル・副タイトル（3案）

```
【提案N：コンセプト】
タイトル: {30文字以内、メインキーワード必須}
副タイトル: {関連キーワード×接続 + ベネフィット文}
```

最重要ルール: メインキーワードは**必ずタイトルに入れる**。
3案の方向性: 1=網羅性、2=好奇心、3=簡単さ・具体的成果

#### 著者名

```
{メインKW}（{テーマ1}×{テーマ2}）活用研究室
```

#### キーワード（7行 × 各50文字以内）

- タイトルに含まれるKWは除外
- 各行内は半角スペース区切り
- 行ごとにテーマを変える

#### フリガナ

タイトル・副タイトル・著者名のカタカナ・ローマ字を生成。

#### 紹介文（3,000〜4,000文字厳守）

- emoji禁止、装飾記号禁止、HTMLタグ禁止
- プレーンテキストのみ
- 目次を含める（SEO対策）
- **3,000字未満の場合は必ず加筆して3,000字以上にすること**

### Phase 5 完了時の検証（必須）

```bash
python scripts/validate_listing.py output/{slug}
```

**検証基準:**
- 総字数 >= 3,000
- タイトル提案 3案以上
- キーワード 7行以上
- 著者名・フリガナセクション存在
- 紹介文 3,000字以上

---

## Phase 6: 表紙プロンプト生成 + 画像生成

### 手順

1. manuscript.md からジャンル・テーマを自動抽出
2. スタイル自動選択（A〜E）
3. カラーパレット自動選択
4. YAMLプロンプトを `cover_prompt.txt` に出力
5. gpt-image-2 で表紙画像を生成

### スタイル自動選択

```
ビジネス/自己啓発/話し方/時間術 → A（テキストインパクト型）
料理/健康/ダイエット/生活改善 → B（イラスト＋テキスト型）
マンガ解説/AI活用/テック入門 → C（マンガ・アニメ型）
投資/金融/経営戦略/不動産 → D（ダーク・プレミアム型）
副業/ハウツー → E（ハイブリッド型）
```

### カラーパレット

| ジャンル | メイン | アクセント | ハイライト |
|---------|--------|----------|-----------|
| ビジネス | #FFFFFF | #1A1A2E | #E74C3C |
| 自己啓発 | #FFF3CD | #E74C3C | #FFD700 |
| 投資・マネー | #1B2A4A | #D4AF37 | #FFFFFF |
| 健康・ダイエット | #E8F5E9 | #FF6B6B | #2E7D32 |
| AI・テック | #1A73E8 | #FFD700 | #FF5252 |
| 副業・稼ぐ系 | #FFF9C4 | #1565C0 | #FF5722 |
| 心理学 | #0D1B2A | #E8872A | #D4AF37 |

### YAMLプロンプト設計原則

- フラット構造
- 色はHEX値+色名
- portrait 2:3 比率
- **著者名は絶対に入れない**

### gpt-image-2 による表紙画像生成

```
Professional Kindle book cover, portrait orientation 2:3 ratio (1600x2560px).
Title: "{確定タイトル}" in large bold Japanese text, centered upper area.
Subtitle: "{確定サブタイトル}" in smaller Japanese text below title.
Style: {選択スタイル}
Color palette: {メイン} / {アクセント} / {ハイライト}
Design:
- Z-pattern eye flow
- Title text clearly readable
- Professional modern Kindle cover
- High contrast between text and background
- DO NOT include any author name on the cover
- No watermarks, no logos
High resolution, 4K quality.
```

生成した画像を `output/{slug}/images/cover.jpg` に保存。

### Phase 6 完了時の検証（必須）

```bash
python scripts/validate_images.py output/{slug} cover
```

**検証基準:** cover.jpg/png が存在し、ファイルサイズが50KB以上

---

## Phase 7: A+コンテンツ画像4枚生成（gpt-image-2）

サイズ: 970×600px（横長）、形式: PNG、枚数: 4枚

### 各画像の役割と生成指示

#### aplus_1.png（問題提起）
```
Wide landscape banner 970x600px. {テーマに関連する読者の悩みや問題状況を視覚化}.
Dark muted tones suggesting difficulty. Emotional relatable scene.
Professional advertising banner, modern illustration, no composition labels, no watermarks, 4K.
NO text labels like "問題提起" inside the image.
```

#### aplus_2.png（煽り・共感）
```
Wide landscape banner 970x600px. {問題が深刻化した状況、読者への共感}.
Dramatic contrast, intense colors amplifying urgency.
Professional banner, strong emotional impact, no composition labels, 4K.
```

#### aplus_3.png（解決策）
```
Wide landscape banner 970x600px. {本書の解決策、変化後の明るい状況}.
Bright optimistic colors, vivid fresh hopeful tones.
Professional banner, aspirational mood, no composition labels, 4K.
```

#### aplus_4.png（CTA）
```
Wide landscape banner 970x600px. {本書を手に取る行動を促すビジュアル}.
Energetic accent colors. Book cover or reading device featured.
Professional banner, call-to-action focused, no composition labels, 4K.
```

### Phase 7 完了時の検証（必須）

```bash
python scripts/validate_images.py output/{slug} aplus
```

**検証基準:** aplus_1〜4.png がすべて存在し、各30KB以上

---

## Phase 8: Kindle申請データ出力

### 生成内容

`templates/kindle_app_template.txt` を参照し、以下を含むこと:

1. タイトル・サブタイトル・著者名（漢字・カタカナ・ローマ字の3表記）
2. 書籍説明文（PASONA法則 / HTML / 3,000〜4,000字厳守）
3. カテゴリー5つ（各カテゴリー横に1位書籍の総合ランキング順位を併記）
4. キーワード30個以上（7マス × 各50文字以内）

### PASONA法則

P: 問題 → A: 煽り・親近感 → S: 解決策 → O: 提案 → N: 絞り込み → A: 行動

- HTML形式（`<p>`, `<strong>` タグ使用）
- PASONA項目名は本文に出さない
- **3,000字未満は必ず加筆して3,000字以上にすること**

### カテゴリー

- Web検索でAmazon Kindleカテゴリーを調査
- 1位書籍の総合ランキングが5,000位以上のジャンルを優先
- 必ず5つ提案

出力先: `output/{slug}/kindle_application.txt`

### Phase 8 完了時の検証（必須）

```bash
python scripts/validate_kindle_app.py output/{slug}
```

**検証基準:**
- 総字数 >= 2,000
- タイトル3表記（漢字・カタカナ・ローマ字）
- 書籍説明文 >= 2,500字
- カテゴリー 5件
- キーワード 30個以上

---

## Phase 9: 統合検証

すべてのPhaseが完了したら、統合検証を実行する。

```bash
python scripts/validate_all.py output/{slug}
```

このスクリプトは:
1. 全検証スクリプトを順次実行
2. 各Phaseの合否を判定
3. `completion_report.json` を出力
4. 総合結果（PASS/FAIL）を表示

**全Phaseが PASS の場合のみ、完了報告を行う。**

### 完了時の報告

```
電子書籍の制作が完了しました。

成果物一覧:
1. manuscript.md — 原稿Markdown（{N}字）
2. research.md — リサーチ結果
3. book_meta.md — 確定メタ情報
4. listing.txt — 出版メタデータ
5. cover_prompt.txt — 表紙プロンプト
6. kindle_application.txt — Kindle申請データ
7. images/cover.jpg — 表紙画像
8. images/aplus_1〜4.png — A+コンテンツ画像

※ manuscript.docx はローカル環境で pandoc 変換してください。
```

---

## 制約事項

- Markdown表（テーブル）を原稿内で使わない
- コードブロックを原稿内で使わない
- 著者情報を原稿本文に入れない
- 表紙に著者名を入れない
- 画像タグを原稿に入れない
- ASCII罫線図を使わない
- **pip install は実行しない（Codexサンドボックスでは不可）**
- **pandoc は使用しない（Codexサンドボックスでは不可）**
- **検証スクリプトはPython標準ライブラリのみで動作する**
