# eBook AutoWriter for Codex v3.2

電子書籍（25,000字・5章構成）を対話型でリサーチ → 執筆 → メタデータ → 表紙 → A+画像 → 申請データまで一括生成。
**要所でユーザー確認を挟み、承認後に自動進行する。**

## 言語

- 日本語で応答する
- プロンプト・技術用語は英語OK

## 起動方法

ユーザーが「スタート」と入力したら、以下の質問を順番に行う:

```
電子書籍の制作を開始します。以下を教えてください。

1. テーマ（必須）: どんな内容の本ですか？
2. 著者名（必須）: Kindle出版時の著者名
3. 参考資料（任意）: URL、ファイル、テキストなど
```

回答を受け取ったら、Phase 1 から自動開始する。

## 最重要ルール

```
1. 「ファイルが存在する」≠「完了」。内容の品質チェックが必須
2. 各Phaseの末尾で python scripts/validate_*.py を必ず実行する
3. 検証NGなら該当Phaseを再実行する（最大2回リトライ）
4. DOCX変換はpython-docxで行う（setup.shで事前インストール済み。pandocは不可）
5. 画像はファイルサイズ50KB以上を必須とする（ダミー禁止）
6. 原稿の同一文反復は禁止（n-gram重複率15%未満を厳守）
7. 原稿はHTML形式で出力する（Markdown原稿とは別にHTMLも生成）
8. 不可視文字を絶対に混入させない（ZWNJ U+200C、Tags U+E0000〜U+E01FF 等）
9. Markdownでは1文（句点「。」まで）= 1段落とする（Kindle読みやすさのため）
10. PR作成前に必ず python scripts/encode_binaries.py を実行する（バイナリPR制限回避）
11. 表紙画像はJPG形式で出力する（KDP申請可能＋ファイルサイズ削減）
```

## リトライ時の絶対ルール

```
■ 原稿（manuscript.md / manuscript.html）のリトライ:
  - 不合格の章を特定し、その章を「全文削除してから新しく書き直す」
  - 既存テキストの末尾に追記（append）は絶対禁止
  - 書き直す際は、前の版と異なる具体例・表現・構成を使う
  - リトライ後も n-gram重複率が15%以上なら、原稿全体を1から再生成する

■ メタデータ（listing.txt / kindle_application.txt）のリトライ:
  - listing.txt の紹介文は最低3,000字（不足時は内容を深掘りして加筆）
  - kindle_application.txt の書籍説明文は最低2,500字（PASONA各節を充実させる）
  - 文字数不足で再生成する場合も、同じ文の繰り返しで水増ししない

■ コミット分離ルール:
  - Phase 3〜5 完了時: テキストファイルのみコミット（manuscript/listing/kindle_app等）
  - Phase 6 完了時: cover.jpg + cover_prompt.txt のみコミット
  - Phase 7 完了時: aplus_1〜4.png のみコミット
  - Phase 8 完了時: completion_report.json をコミット
```

## 全体フロー（対話型・7チェックポイント）

```
「スタート」
  ↓ テーマ・著者名・参考資料を質問
Phase 1: 入力受付
  ↓
Phase 2: 5層ディープリサーチ → validate_research.py
  ↓
★確認1: タイトル10案提案 → ユーザーがタイトル・サブタイトルを確定
★確認2: 構成（目次）提示 → ユーザーが承認
  ↓ 承認後、一気に自動生成 ↓
Phase 3: 原稿執筆 25,000字（HTML + Markdown）→ validate_manuscript.py
Phase 4: 出版メタデータ生成 → validate_listing.py
Phase 5: Kindle申請データ生成 → validate_kindle_app.py
  ↓ ここで一旦停止 ↓
★確認3: 表紙プロンプト確認（入稿前）
  ↓ 承認後 ↓
Phase 6: 表紙画像生成（gpt-image-2）→ validate_images.py cover
  ↓
★確認4: 表紙画像の確認
  ↓ 承認後 ↓
★確認5: A+コンテンツ4枚のプロンプト確認
  ↓ 承認後 ↓
Phase 7: A+画像4枚生成（gpt-image-2）→ validate_images.py aplus
  ↓
★確認6: A+画像4枚の確認
  ↓ 承認後 ↓
Phase 8: 統合検証 → validate_all.py
  ↓
★確認7: 最終出力の確認・完了報告
```

## チェックポイントのルール

- ★マークのタイミングでは**必ずユーザーに確認を求めて停止する**
- ユーザーが「OK」「進めて」等で承認したら次へ進む
- ユーザーが修正指示を出したら修正してから再確認
- ★マーク以外のPhaseは確認なしで自動進行する

## 成果物一覧

```
output/{slug}/
├── manuscript.md             # Markdown原稿（25,000字以上）
├── manuscript.html           # HTML原稿（DOCX変換用）
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

---

## Phase 1: 入力受付

ユーザーからテーマ・著者名・参考資料を受け取る。

受け取れる参考資料の形式:
- ファイル（PDF、テキスト、Markdown、DOCX）
- URL（Web検索で内容取得）
- テキスト（直接貼り付け）
- 複数資料の組み合わせ
- なし（テーマのみでもOK）

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

## ★確認1: タイトル・サブタイトル確定

リサーチ完了後、**ユーザーに確認を求めて停止する。**

### 提示する内容

1. リサーチ結果のサマリー（各Layer の要点を3行程度ずつ）
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
   - タイトル + サブタイトル（番号選択 or 改変 or 新規）

### 確定後の処理

確定情報を `output/{slug}/book_meta.md` に保存:

```markdown
# 書籍メタ情報

- **タイトル**: {確定タイトル}
- **サブタイトル**: {確定サブタイトル}
- **著者名**: {確定著者名}
- **想定読者**: {...}
- **確定日**: YYYY-MM-DD
```

```bash
python scripts/validate_meta.py output/{slug}
```

**ユーザーが確定するまで次に進まない。**

---

## ★確認2: 構成（目次）確認

タイトル確定後、目次を設計してユーザーに提示する。

### 提示する目次

```
書籍タイトル: {確定タイトル}
想定読者: {テーマから推定}
読者のゴール: {この本を読んで何ができるようになるか}

はじめに（1,200〜1,500字）
  - この本の目的 / 読者への約束 / 本書の使い方

第1章: {章タイトル}（4,000〜5,000字）
  1.1 {節タイトル}
  1.2 {節タイトル}
  1.3 {節タイトル}
  1.4 {節タイトル}
  1.5 {節タイトル}

第2章〜第5章: 同上の形式（各5節）

おわりに（1,200〜1,500字）
```

### 構成ルール
- 章の順序: 基礎 → 応用 → 実践
- 各章は独立して読んでも価値がある
- 章をまたいで内容が行き来しない
- 読者が「次に何をすればいいか」がわかる
- 各章に最低5節（### 見出し）を設ける

**ユーザーが「OK」と承認したら、Phase 3〜5 を一気に自動実行する。**

---

## Phase 3: 原稿執筆（25,000字・HTML + Markdown）

**構成が承認されたら、Phase 3〜5 は確認なしで一気に自動実行する。**

### 出力形式

原稿は**2つの形式**で出力する:

1. `manuscript.md` — Markdown形式（検証・変換用）
2. `manuscript.html` — HTML形式（最終成果物）

### HTML出力の仕様（Kindle申請可能な品質）

**このHTMLはそのままKindle Direct Publishing（KDP）に申請できるレベルで作り込む。**
文字装飾（太字・強調）、改ページタグ、目次リンク、段落スタイルをすべて含める。

```html
<!DOCTYPE html>
<html lang="ja" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="UTF-8" />
<title>{書籍タイトル}</title>
<style type="text/css">
  /* === Kindle対応 基本スタイル === */
  body {
    font-family: serif;
    line-height: 1.8;
    margin: 0;
    padding: 0;
  }

  /* === 書籍タイトル === */
  h1 {
    font-size: 2em;
    text-align: center;
    margin: 3em 0 1em;
    font-weight: bold;
  }

  /* === 章タイトル（H2）= 改ページ + 装飾 === */
  h2 {
    font-size: 1.5em;
    font-weight: bold;
    border-bottom: 2px solid #333;
    padding-bottom: 0.3em;
    margin-top: 2em;
    margin-bottom: 1em;
    page-break-before: always;
  }

  /* === 節タイトル（H3）= 改ページ + 装飾 === */
  h3 {
    font-size: 1.2em;
    font-weight: bold;
    margin-top: 2em;
    margin-bottom: 0.8em;
    page-break-before: always;
  }

  /* === 小見出し（H4） === */
  h4 {
    font-size: 1.1em;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
  }

  /* === 本文段落 === */
  p {
    margin: 0.8em 0;
    text-indent: 1em;
  }

  /* === 強調・太字 === */
  strong, b { font-weight: bold; }
  em, i { font-style: italic; }

  /* === 箇条書き === */
  ul, ol {
    margin: 1em 0;
    padding-left: 2em;
  }
  li { margin: 0.3em 0; }

  /* === 補足ボックス（ポイント・注意） === */
  .note {
    background: #f5f5f5;
    border-left: 4px solid #333;
    padding: 1em;
    margin: 1.5em 0;
  }
  .point {
    background: #fff8e1;
    border-left: 4px solid #f9a825;
    padding: 1em;
    margin: 1.5em 0;
  }

  /* === 目次 === */
  .toc { margin: 2em 0; }
  .toc a { text-decoration: none; color: #1a0dab; }
  .toc li { margin: 0.5em 0; list-style: none; }

  /* === 改ページ === */
  .page-break { page-break-before: always; }

  /* === 区切り線 === */
  hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 2em 0;
  }
</style>
</head>
<body>

<!-- ========== タイトルページ ========== -->
<div class="page-break" style="text-align: center; margin-top: 30%;">
  <h1>{書籍タイトル}</h1>
  <p style="font-size: 1.2em; text-indent: 0;">{サブタイトル}</p>
  <br /><br />
  <p style="text-indent: 0;">{著者名}</p>
</div>

<!-- ========== 目次 ========== -->
<div class="page-break">
  <h2>目次</h2>
  <ul class="toc">
    <li><a href="#intro">はじめに</a></li>
    <li><a href="#ch1">第1章: {章タイトル}</a></li>
    <li><a href="#ch2">第2章: {章タイトル}</a></li>
    <li><a href="#ch3">第3章: {章タイトル}</a></li>
    <li><a href="#ch4">第4章: {章タイトル}</a></li>
    <li><a href="#ch5">第5章: {章タイトル}</a></li>
    <li><a href="#outro">おわりに</a></li>
  </ul>
</div>

<!-- ========== はじめに ========== -->
<h2 id="intro">はじめに</h2>
<p>本文を<strong>太字</strong>や<em>強調</em>で装飾しながら執筆する。</p>
<p>重要なポイントは以下のように表現する:</p>
<div class="point">
  <p style="text-indent: 0;"><strong>ポイント:</strong> ここに重要な内容を記載します。</p>
</div>

<!-- ========== 第1章 ========== -->
<h2 id="ch1">第1章: {章タイトル}</h2>
<h3>1.1 {節タイトル}</h3>
<p>本文...</p>

<h3>1.2 {節タイトル}</h3>
<p>本文...</p>

<!-- 以下同様に第2章〜第5章、おわりに -->

<!-- ========== おわりに ========== -->
<h2 id="outro">おわりに</h2>
<p>本文...</p>

</body>
</html>
```

### HTML装飾ルール（Kindle申請品質）

1. **改ページ**: 章（H2）と節（H3）に `page-break-before: always` を適用済み
2. **太字**: 重要な用語・キーワードは `<strong>` で囲む（各段落に1〜2箇所）
3. **強調**: 補足的な強調は `<em>` を使用
4. **ポイントボックス**: 各章に1〜2箇所、`<div class="point">` で重要ポイントを囲む
5. **補足ボックス**: 注意事項は `<div class="note">` で囲む
6. **目次リンク**: 各章のIDに `<a href="#ch1">` でジャンプ可能にする
7. **タイトルページ**: 書籍タイトル・サブタイトル・著者名を中央配置
8. **箇条書き**: `<ul>/<ol>` で構造化
9. **段落インデント**: `text-indent: 1em` で日本語書籍の体裁
10. **句点で改行しない**: HTML版では句点改行は行わない（DOCX版のみの処理）

### 執筆ルール（厳守）

- **総文字数: 25,000字以上**（25,000字未満は不合格）
- 1章あたり: 4,000〜5,000字（3,500字未満は不合格）
- はじめに/おわりに: 各1,200〜1,500字（1,000字未満は不合格）
- 文体: **です・ます調で統一**（80%以上）
  - NG: 「〜だ」「〜である」「〜しよう」「〜だろう」
  - OK: 「〜です」「〜になります」「〜してみましょう」「〜してください」
- 段落: 3〜4文ごとに改行
- 具体例: 各章に最低2つの具体例・事例
- **表（テーブル）禁止**: 比較情報は箇条書きで表現
- **コードブロック禁止**: コマンドは通常テキストとして記述
- **ASCII図禁止**: 罫線文字は使わない
- **ユーザー名禁止**: 「読者の皆さん」等の一般表現を使用
- **著者情報禁止**: 原稿本文に著者名・プロフィールを入れない

### 句点改行ルール（Kindle品質のため必須）

**Markdownでは1文=1段落にする。** 句点「。」のたびに改行し、空行を入れる。

```
NG（1段落に複数文を詰め込む）:
AI副業を学ぶ前に確認してください。使える時間は週に何時間あるのか。初期費用はいくらまでなら出せるのか。

OK（1文=1段落）:
AI副業を学ぶ前に確認してください。

使える時間は週に何時間あるのか。

初期費用はいくらまでなら出せるのか。
```

この形式にすることで、Kindle端末で読みやすい行間が確保される。

### 不可視文字の混入禁止

**テキスト内にゼロ幅非結合子（U+200C）、Tags（U+E0000〜U+E01FF）、その他の不可視制御文字を絶対に入れない。**
これらが混入するとKindle変換時に「??」として表示される重大な品質問題を引き起こす。

原稿完成後に以下のクリーニングスクリプトを実行すること:

```bash
python scripts/clean_invisible.py output/{slug}
```

### 同一文反復の絶対禁止

**前回の失敗: 見た目は25,000字だが同じ文章の繰り返しだった。**

以下を厳守:
- 同じ文を2回以上使わない
- 同じ段落パターンを繰り返さない
- 各節で異なる具体例・データ・視点を提供する
- validate_manuscript.py の n-gram重複チェック（15%未満）をパスすること

### Markdown版の改ページ・整形ルール

- 各章（`##`）の直前に `\newpage`
- 各節（`###`）の直前に `\newpage`
- はじめに・おわりにの直前にも `\newpage`
- 見出しの前後に空行1行
- 段落間に空行1行

### 見出しレベル（Markdown / HTML共通）

- H1: 書籍タイトル（冒頭1回のみ）
- H2: 章タイトル（はじめに、第1章〜第5章、おわりに）
- H3: 節タイトル（1.1, 1.2, ...）
- H4: 小見出し（必要に応じて）

### 章ごとの文字数確認

各章を書き終えたら、その章の文字数を数え、3,500字未満なら加筆する。

### Phase 3 完了時の検証（必須）

```bash
python scripts/validate_manuscript.py output/{slug}
```

**検証基準:**
- 総字数 >= 25,000
- 各章 >= 3,500字 / はじめに・おわりに >= 1,000字
- n-gram重複率 < 15%
- 禁止パターン（テーブル・コードブロック・ASCII図）なし
- です/ます調 80%以上

**NGの場合:** 「リトライ時の絶対ルール」に従い、不合格の章を全文削除してから新しく書き直す。既存テキストへのappend禁止。

---

## Phase 4: 出版メタデータ生成

**確認なしで自動実行（Phase 3 から連続）**

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

#### 著者名

```
{メインKW}（{テーマ1}×{テーマ2}）活用研究室
```

#### キーワード（7行 × 各50文字以内）

- タイトルに含まれるKWは除外
- 各行内は半角スペース区切り

#### フリガナ

タイトル・副タイトル・著者名のカタカナ・ローマ字を生成。

#### 紹介文（3,000〜4,000文字厳守）

- emoji禁止、装飾記号禁止、HTMLタグ禁止
- プレーンテキストのみ
- 目次を含める（SEO対策）
- **3,000字未満の場合は必ず加筆して3,000字以上にすること**

### Phase 4 完了時の検証（必須）

```bash
python scripts/validate_listing.py output/{slug}
```

---

## Phase 5: Kindle申請データ出力

**確認なしで自動実行（Phase 4 から連続）**

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

### Phase 5 完了時の検証（必須）

```bash
python scripts/validate_kindle_app.py output/{slug}
```

**Phase 3〜5 完了後、ユーザーに報告して★確認3 へ進む。**

報告メッセージ:
```
原稿・メタデータ・申請データの生成が完了しました。

- manuscript.md: {N}字
- manuscript.html: 生成済み
- listing.txt: 生成済み
- kindle_application.txt: 生成済み

次に表紙画像を制作します。プロンプトを確認してください。
```

---

## ★確認3: 表紙プロンプト確認（入稿前）

表紙画像を生成する前に、**プロンプトをユーザーに提示して承認を得る。**

### 手順

1. manuscript.md からジャンル・テーマを自動抽出
2. スタイルを自動選択（A〜E）
3. カラーパレットを自動選択
4. プロンプトを生成して**ユーザーに提示**

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

### ユーザーに提示する内容

```
【表紙プロンプト確認】

スタイル: {選択スタイル名}
カラー: {メイン} / {アクセント} / {ハイライト}

プロンプト:
---
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
---

このプロンプトで表紙を生成してよろしいですか？
修正があればお知らせください。
```

**ユーザーが承認したら Phase 6 へ。修正指示があればプロンプトを修正して再提示。**

承認後、`cover_prompt.txt` に保存。

---

## Phase 6: 表紙画像生成（gpt-image-2）

**★確認3 で承認されたプロンプトで画像を生成する。**

生成した画像を `output/{slug}/images/cover.jpg` に保存。

**画像形式ルール:**
- 表紙は必ず **JPG形式** で保存（PNGで生成された場合はJPGに変換）
- KDP申請にそのまま使える形式にする
- 画像生成後、テキストファイルとは **別のコミット** で保存する

### Phase 6 完了時の検証（必須）

```bash
python scripts/validate_images.py output/{slug} cover
```

**検証基準:** cover.jpg/png が存在し、ファイルサイズが50KB以上

---

## ★確認4: 表紙画像の確認

生成された表紙画像をユーザーに提示する。

```
表紙画像が生成されました。確認してください。

ファイル: output/{slug}/images/cover.jpg
サイズ: {W}x{H}px, {N}KB

問題なければ「OK」、再生成する場合は修正指示をお知らせください。
```

**ユーザーが承認したら ★確認5 へ。再生成指示があれば Phase 6 を再実行。**

---

## ★確認5: A+コンテンツプロンプト確認

A+コンテンツ画像4枚のプロンプトを**ユーザーに提示して承認を得る。**

### 提示する内容

```
【A+コンテンツ画像プロンプト確認】（4枚 / 各970×600px）

■ aplus_1.png（問題提起）
{プロンプト全文}

■ aplus_2.png（煽り・共感）
{プロンプト全文}

■ aplus_3.png（解決策）
{プロンプト全文}

■ aplus_4.png（CTA）
{プロンプト全文}

これらのプロンプトで画像を生成してよろしいですか？
```

### 各画像のプロンプト生成ルール

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

**ユーザーが承認したら Phase 7 へ。**

---

## Phase 7: A+画像4枚生成（gpt-image-2）

**★確認5 で承認されたプロンプトで画像を生成する。**

### Phase 7 完了時の検証（必須）

```bash
python scripts/validate_images.py output/{slug} aplus
```

**検証基準:** aplus_1〜4.png がすべて存在し、各30KB以上

---

## ★確認6: A+画像4枚の確認

生成されたA+画像4枚をユーザーに提示する。

```
A+コンテンツ画像4枚が生成されました。確認してください。

1. aplus_1.png（問題提起）— {N}KB
2. aplus_2.png（煽り・共感）— {N}KB
3. aplus_3.png（解決策）— {N}KB
4. aplus_4.png（CTA）— {N}KB

問題なければ「OK」、再生成する場合は番号と修正指示をお知らせください。
```

**ユーザーが承認したら Phase 8 へ。**

---

## Phase 8: 統合検証

```bash
python scripts/validate_all.py output/{slug}
```

このスクリプトは:
1. 全検証スクリプトを順次実行
2. 各Phaseの合否を判定
3. `completion_report.json` を出力

---

## Phase 9: DOCX変換（setup.shでpython-docx インストール済み）

manuscript.md をもとに python-docx で DOCX ファイルを生成する。

```python
# scripts/md_to_docx.py で変換（python-docx使用）
python scripts/md_to_docx.py output/{slug}/manuscript.md output/{slug}/manuscript.docx
```

変換後、後処理スクリプトを実行:
```bash
python scripts/docx_postprocess.py output/{slug}/manuscript.docx
```

---

## Phase 10: バイナリファイルのBase64エンコード（PR対応・必須）

Codex PRはバイナリファイルを直接含められないため、
全バイナリ（画像・DOCX）をBase64テキストに変換してPRに含める。

```bash
python scripts/encode_binaries.py output/{slug}
```

このスクリプトは:
1. output/{slug}/ 内のバイナリファイル（.png .jpg .jpeg .docx）を検索
2. 各ファイルをBase64エンコードして `output/{slug}/binaries/` に `.b64` テキストとして保存
3. `manifest.json`（復元用マッピング）を生成
4. **元のバイナリファイルを自動削除する**（Codex PRのバイナリ検出を回避）

**重要: エンコード後にワークスペースにバイナリが残っていてはならない。**
スクリプトが自動削除するが、もし手動で画像を生成した場合も必ず削除すること。
`.b64` ファイルはテキストなのでPRに含めてもエラーにならない。

---

## ★確認7: 最終出力の確認・完了報告

統合検証の結果をユーザーに報告する。

```
電子書籍の制作が完了しました。

テーマ: {テーマ名}
著者: {著者名}
タイトル: {確定タイトル}

成果物一覧:
1. manuscript.md — Markdown原稿（{N}字）
2. manuscript.html — HTML原稿
3. manuscript.docx — Word原稿（python-docx変換済み）
4. research.md — リサーチ結果
5. book_meta.md — 確定メタ情報
6. listing.txt — 出版メタデータ
7. cover_prompt.txt — 表紙プロンプト
8. kindle_application.txt — Kindle申請データ
9. images/cover.jpg — 表紙画像
10. images/aplus_1〜4.png — A+コンテンツ画像
11. binaries/ — Base64エンコード済みバイナリ（PR用）

統合検証: {PASS/FAIL}
{各Phase の結果}

※ PRマージ後、ローカルで以下を実行して画像・DOCXを復元してください:
  python scripts/decode_binaries.py output/{slug}
```

---

## 制約事項

- 表（テーブル）を原稿内で使わない
- コードブロックを原稿内で使わない
- 著者情報を原稿本文に入れない
- 表紙に著者名を入れない
- ASCII罫線図を使わない
- **pip install はエージェントフェーズで実行しない（setup.shで事前インストール済み）**
- **pandoc は使用しない（python-docxで直接生成する）**
- **検証スクリプトはPython標準ライブラリ + setup.shでインストール済みパッケージのみで動作する**
- **表紙画像はJPG形式で出力する（PNG生成時はJPGに変換）**
- **PR作成前に必ず `python scripts/encode_binaries.py` を実行する（バイナリPR制限回避）**

---

# PR作成ルール（厳守）

## Base64方式によるバイナリファイルのPR対応

Codex WebのPRはバイナリファイルを直接含められない。
そのため Phase 10 で全バイナリをBase64テキスト化してからPRに含める。

### コミット対象
- `*.md` — 原稿Markdown、リサーチ結果、メタ情報
- `*.txt` — listing.txt、cover_prompt.txt、kindle_application.txt
- `*.html` — HTML原稿
- `*.json` — completion_report.json、manifest.json
- `*.b64` — Base64エンコード済みバイナリ（binaries/内）
- `*.py` — スクリプト（新規・修正時のみ）

### コミット除外（.gitignoreで自動除外）
- `*.docx` `*.png` `*.jpg` `*.jpeg` `*.pdf` — 生バイナリファイル
- これらは `.b64` 形式でPRに含まれるため、生ファイルは不要

### コミット手順

```bash
# 1. Phase 10 のBase64エンコードが完了していることを確認
ls output/{slug}/binaries/manifest.json

# 2. テキスト + Base64ファイルをステージング
git add output/{slug}/*.md output/{slug}/*.txt output/{slug}/*.html
git add output/{slug}/*.json
git add output/{slug}/binaries/

# 3. バイナリが含まれていないことを確認
git diff --cached --name-only | grep -E '\.(docx|png|jpg|jpeg|pdf)$' && echo "ERROR: バイナリが含まれています" || echo "OK"

# 4. コミット
git commit -m "Add {slug} complete outputs (text + base64 binaries)"
```

### ユーザーへの復元案内
PRの説明欄に以下を必ず記載する:

```
## 画像・DOCXの復元方法
PRマージ後、以下を実行してください:
python scripts/decode_binaries.py output/{slug}
```
