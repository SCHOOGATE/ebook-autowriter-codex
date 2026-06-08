# eBook AutoWriter for Codex v4.0

電子書籍（25,000字・5章構成）を対話型でリサーチ → 執筆 → メタデータ → 表紙 → A+画像 → 申請データまで一括生成。
**画像はすべてChatGPT Images 2.0をChrome DevTools経由で生成する（APIクレジット不要）。**
**要所でユーザー確認を挟み、承認後に自動進行する。**

## 言語

- 日本語で応答する
- プロンプト・技術用語は英語OK

## 起動方法

ユーザーが「**{テーマ}の電子書籍を制作**」と入力して起動する。
（例: 「AI副業の電子書籍を制作」「猫のアロマケアの電子書籍を制作」）

テーマは起動プロンプトから自動抽出し、残りの情報を質問する:

```
テーマ「{抽出したテーマ}」で電子書籍の制作を開始します。

以下を教えてください。
1. 著者名（必須）: Kindle出版時の著者名
2. 参考資料（任意）: URL、ファイル、テキストなど
```

回答を受け取ったら、Phase 1 から自動開始する。

※ Codex Cloudではこの起動プロンプトがタスク名になるため、テーマを含めて起動すること。

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
10. バイナリファイル(.png/.jpg/.docx)は絶対に直接コミットしない（validate_images.pyが自動Base64化する）
11. 表紙画像はJPG形式で出力する（KDP申請可能＋ファイルサイズ削減）
12. validate_images.py実行後にbinaries/ディレクトリをコミットに含める
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

■ コミットルール（バイナリは絶対にコミットしない）:
  - Phase 3〜5 完了時: テキストファイルのみコミット（manuscript/listing/kindle_app等）
  - Phase 6 完了時: cover_prompt.txt + binaries/*.b64 をコミット（表紙画像）
  - Phase 7 完了時: binaries/*.b64 をコミット（A+画像）
  - *.png *.jpg *.jpeg *.docx は直接コミット禁止（validate_images.pyが自動で削除する）
```

## 全体フロー（対話型・7チェックポイント）

```
「{テーマ}の電子書籍を制作」
  ↓ テーマ自動抽出 → 著者名・参考資料を質問
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
Phase 6: 表紙画像生成（ChatGPT Images 2.0 DevTools経由）→ validate_images.py cover → コミット
  ↓
★確認4: 表紙画像の確認（manifest.jsonのサイズ情報を参照）
  ↓ 承認後 ↓
★確認5: A+コンテンツ4枚のプロンプト確認
  ↓ 承認後 ↓
Phase 7: A+画像4枚生成（ChatGPT Images 2.0 DevTools経由）→ validate_images.py aplus → コミット
  ↓
★確認6: A+画像4枚の確認（manifest.jsonのサイズ情報を参照）
  ↓ 承認後 ↓
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

起動プロンプト「{テーマ}の電子書籍を制作」からテーマを自動抽出済み。
ユーザーから著者名・参考資料を受け取る。

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
3. カラーパレットを自動選択（4色+背景色）
4. **5ブロックYAMLプロンプト**を生成して**ユーザーに提示**

### スタイル自動選択（5種類）

| スタイル | 適用ジャンル | 特徴 |
|---------|------------|------|
| **A: テキストインパクト型** | ビジネス/自己啓発/話し方/時間術 | 大きく太い文字が主役。イラスト最小限。高コントラスト配色。タイトルの視認性最優先 |
| **B: イラスト＋テキスト型** | 健康/暮らし/料理/ダイエット/エッセイ | フラットイラストが中央。柔らかいパステル系配色。文字はイラストの上下に配置 |
| **C: マンガ・アニメ型** | エンタメ/物語/AI活用/テック入門 | キャラクターイラスト中心。動きのある構図。遊び心のあるフォント |
| **D: プレミアム型** | 投資/金融/経営戦略/専門書 | ダーク背景（ネイビー/ブラック）。写実的な質感。洗練されたフォント。高級感 |
| **E: ハイブリッド型** | 副業/ハウツー/○○入門 | イラスト＋テキストリボン。バランスの取れた配置。入門書らしい親しみやすさ |

### カラーパレット（4色+背景色）

| ジャンル | メイン | サブ | アクセント | 背景 |
|---------|--------|------|-----------|------|
| ビジネス/自己啓発 | #2C3E50 ネイビー | #E8C547 マスタード | #C0392B レッド | #FFFFFF ホワイト |
| 健康/ダイエット/自然療法 | #6B8E7F セージ | #D4B896 ベージュ | #C97B63 テラコッタ | #F5F1EA クリーム |
| 投資/マネー/副業 | #1ABC9C エメラルド | #F39C12 オレンジ | #34495E ダーク | #ECF0F1 ライト |
| AI/テック | #3498DB ブルー | #9B59B6 パープル | #F39C12 オレンジ | #ECF0F1 ライトグレー |
| 女性向け/エッセイ | #D4A5A5 ローズ | #F4E5C2 アイボリー | #B6852C ゴールド | #FAF6F1 シェル |
| 心理学/コミュニケーション | #0D1B2A ダークネイビー | #E8872A オレンジ | #D4AF37 ゴールド | #1B2838 ダーク |

### 表紙プロンプトのYAML形式（5ブロック — cover-master-ss準拠）

プロンプトは以下の5ブロックYAML形式で生成する。**各ブロックは具体的かつ詳細に記述すること。曖昧・汎用的な指示は禁止。**

```yaml
subject: |
  A {style_keyword} book cover for a Japanese {genre} guide.
  Central motif: {テーマの核心を視覚化する具体的なモチーフ。抽象的な説明ではなく、
  「疲れた表情のビジネスマンが朝日を浴びて目覚める瞬間」のように具体的なシーンを描写する}.
  Target reader: {「30代の営業職で初めて部下を持った人」のように具体的なペルソナ}.
  The cover should immediately communicate: {この本を手に取る理由を1文で}.

layout: |
  Vertical 2:3 ratio Kindle cover (1600x2560px, 300DPI, print-ready).
  3-section composition with clear visual hierarchy:
  - Top band ({top_pct}%): {メインカラー} background. Main title in bold Japanese sans-serif,
    centered horizontally. Title font size must dominate this area.
  - Middle area ({mid_pct}%): {背景色} background with central motif illustration.
    {モチーフの具体的な配置: 「中央にやや左寄りで人物、右側にアイコン群を放射状に配置」等}.
    Breathing space around the motif (余白を十分に確保).
  - Bottom band ({bot_pct}%): {サブカラー} background with subtitle in smaller text.
  - {アクセントカラー} thin divider strips (2-3px) between sections for visual separation.
  - Z-pattern eye flow: title → motif → subtitle の順で自然に視線が流れる構成.
  DO NOT include any author name, writer name, or 著者 text anywhere on the cover.
  DO NOT include ISBN, barcode, price, or publisher logo.

typography: |
  Main title 「{確定タイトル}」
    — Size: occupies 60-70% of top band width
    — Weight: Extra Bold / Black
    — Font: Japanese sans-serif (Noto Sans JP Black equivalent)
    — Color: {タイトル色: スタイルAなら白または黒、Dならゴールド等}
    — Shadow: subtle drop shadow for depth (opacity 20%, offset 2px)
  Subtitle 「{確定サブタイトル}」
    — Size: 40-50% of bottom band width
    — Weight: Medium / Regular
    — Font: Japanese sans-serif
    — Color: {サブタイトル色}
  CRITICAL: All Japanese text MUST be rendered in actual Japanese characters.
  DO NOT translate, romanize, or use placeholder text.
  Japanese text must be crisp, clean, and perfectly legible at thumbnail size.

visuals: |
  Color palette (strict):
    Main: {メイン} — used for title background or primary elements
    Sub: {サブ} — used for subtitle area and secondary elements
    Accent: {アクセント} — used for dividers, highlights, key visual accents
    Background: {背景} — used for middle area and breathing space
  Central motif details:
    {スタイル別の具体的なビジュアル指示:
    - スタイルA: 太い文字が主役。背景は単色またはシンプルなグラデーション。
      アイコンは最小限（1-2個）で文字の引き立て役に徹する。
    - スタイルB: フラットイラスト（線なし塗り）で温かみのあるシーン。
      パステル調の柔らかい色合い。人物やオブジェクトは丸みを帯びたデザイン。
    - スタイルC: アニメ/マンガ調のキャラクターイラスト。
      動きのある構図（斜め配置、飛び出し効果）。吹き出しや効果線も可。
    - スタイルD: ダーク背景に金属質感またはガラス質感のモチーフ。
      写実的な光の反射、グラデーション、立体感。高級時計の広告のような洗練さ。
    - スタイルE: イラスト＋テキストバナーの組み合わせ。
      リボン状のテキスト帯、角丸の情報カード、親しみやすいアイコン群。}
  Lighting: {「右上からの柔らかい自然光」「左下からのスポットライト」等の具体的な光源指示}
  Texture: {「マット仕上げ」「光沢感」「紙のようなテクスチャ」等}
  Clean composition, soft shadows for subtle depth and premium feel.
  No watermarks, no logos, no ISBN, no decorative borders.

style: |
  Professional Japanese Kindle book cover design.
  Quality level: Amazon Kindle ベストセラーTOP10に並ぶ商業品質.
  Mood: {ジャンル固有のムード3-4語: 例「信頼感, 洗練された, 知的, 温かみ」}.
  Must look polished and premium when displayed as a small thumbnail (120x180px).
  High resolution 4K, print-ready, 1600x2560px, 300DPI.
  Use the ChatGPT Images 2.0 (4o) model. Do NOT use DALL-E.
```

### 表紙プロンプト品質チェックリスト（生成前に必ず確認）

生成するYAMLプロンプトが以下を満たしているか確認してから★確認3で提示する:

- [ ] subject: 具体的なシーン/モチーフが描写されている（「professional design」のような曖昧な指示ではない）
- [ ] layout: 3セクションの比率とモチーフの配置が明示されている
- [ ] typography: タイトル・サブタイトルが実際の日本語で記述されている
- [ ] typography: フォントサイズ・ウェイト・色・影が指定されている
- [ ] visuals: 4色のHEXコードが明記されている
- [ ] visuals: スタイル別のビジュアル指示が具体的（スタイルA〜Eのどれか）
- [ ] visuals: 光源・質感の指示がある
- [ ] style: ムードキーワードが3語以上ある
- [ ] 著者名・ISBN・ロゴ・バーコードの除外指示がある

### ユーザーに提示する内容

```
【表紙プロンプト確認】

スタイル: {選択スタイル名}（{スタイルの特徴1文}）
カラー: {メイン} / {サブ} / {アクセント} / {背景}

プロンプト（5ブロックYAML）:
---
{上記YAML形式で生成したプロンプト全文}
---

出力サイズ: 1600×2560px（2:3比率）/ 300DPI / JPG形式
このプロンプトで表紙を生成してよろしいですか？
修正があればお知らせください。
```

**ユーザーが承認したら Phase 6 へ。修正指示があればプロンプトを修正して再提示。**

承認後、`cover_prompt.txt` にYAML形式で保存。

---

## Phase 6: 表紙画像生成（ChatGPT Images 2.0 DevTools経由）

**★確認3 で承認されたプロンプトで画像を生成する。**
生成手順は後述「ChatGPT Images 2.0 生成プロトコル」に従う。

生成した画像を `output/{slug}/images/cover.jpg` に保存。

**画像形式ルール:**
- 表紙は必ず **JPG形式** で保存（PNGで生成された場合はJPGに変換）
- KDP申請にそのまま使える形式にする
- 画像ファイルは直接コミットしない（validate_images.pyが自動Base64化＋削除する）

### Phase 6 完了時の検証（必須）

```bash
python scripts/validate_images.py output/{slug} cover
```

**検証基準:** cover.jpg/png が存在し、ファイルサイズが50KB以上

---

## ★確認4: 表紙画像の確認

生成された表紙画像をユーザーに提示する。
※ validate_images.py実行後は元画像が削除済み。manifest.jsonのサイズ情報と、Phase 6実行中にチャットに表示された画像プレビューで確認する。

```
表紙画像が生成されました。確認してください。

Base64: output/{slug}/binaries/images_cover.jpg.b64
元ファイルサイズ: {manifest.jsonのoriginal_size}KB

問題なければ「OK」、再生成する場合は修正指示をお知らせください。
```

**ユーザーが承認したら ★確認5 へ。再生成指示があれば Phase 6 を再実行（encode_binaries.pyが自動で上書きする）。**

---

## ★確認5: A+コンテンツプロンプト確認

A+コンテンツ画像4枚のプロンプトを**ユーザーに提示して承認を得る。**
A+画像は表紙と同じカラーパレットを使用し、ブランドの統一感を出す。

### A+画像の品質ルール

- サイズ: **970×600px**（Amazon A+コンテンツ標準）
- PASONA法則に沿った4枚構成（問題提起→煽り・共感→解決策→CTA）
- 表紙と同じカラーパレットを使用し、**4枚を通してブランドの統一感を出す**
- **各画像に日本語キャッチコピーを大きく配置する**（テキストなしの風景写真は禁止）
- 各画像は独立してもストーリーが伝わるビジュアル
- ラベル文字（「問題提起」等の構成名）は画像内に入れない
- **4枚をスクロールしたとき、色のトーンがProblem(暗)→Agitation(赤/警告)→Solution(明)→CTA(活力)とグラデーション変化するように設計する**

### A+キャッチコピー生成ルール

各画像のキャッチコピーは以下の基準で生成する:
- **8〜15文字**（一目で読める長さ）
- 読者の感情を動かす言葉を選ぶ
- 4枚でストーリーが完結する（問題→危機→解決→行動）
- テーマと書籍タイトルに直結する具体的な表現

### 各画像の5ブロックYAMLプロンプト

**プロンプト品質の絶対ルール:**
- scene/layout/visuals は「具体的なシーン・人物・オブジェクト」で描写すること
- 「professional」「high quality」のような**曖昧な形容詞だけの指示は禁止**
- 必ず「誰が」「どこで」「何をしている」「どんな表情で」を含めること

#### aplus_1.png（問題提起 — Problem）

```yaml
subject: |
  Amazon A+ content banner showing a reader's pain point.
  Concrete scene: {テーマ固有の悩みを具体的なシーンで描写。
  例（睡眠本）: 「深夜2時、暗い寝室でスマホの青白い光に照らされた疲れた表情の30代男性。
  ベッドに横たわりながら目が冴えて眠れない。枕元に散らかった書類とコーヒーカップ」
  例（営業本）: 「会議室で顧客に提案中、沈黙が続き額に汗をかく若手営業マン。
  テーブルの向こうで腕を組む厳しい表情のクライアント」}
  Japanese headline: 「{8-15文字のキャッチコピー}」

layout: |
  Wide landscape banner 970x600px.
  Split composition:
  - Left 55%: 上記のシーンをリアルに描写（人物の表情が見える距離感）
  - Right 45%: ダーク半透明オーバーレイ（opacity 70%）の上に日本語キャッチコピー
  - キャッチコピーは右エリアの中央に配置、上下に十分な余白
  - 画像全体の下端: {メインカラー}の細いライン（3px）でブランド統一

typography: |
  Headline 「{キャッチコピー}」
    — Size: 右エリア幅の70%を占める大きさ
    — Weight: Extra Bold
    — Font: Japanese sans-serif
    — Color: #FFFFFF (white)
    — Shadow: 2px drop shadow, rgba(0,0,0,0.5)
  Sub-text 「{補足1行: 問題の具体的な数字や状況}」
    — Size: Headlineの40%
    — Weight: Regular
    — Color: {アクセントカラー}
  All Japanese text MUST be rendered in actual Japanese characters, crisp and legible.

visuals: |
  Color palette: Problem tone (暗く重い)
    Primary: {メインカラー} darkened 30%
    Secondary: {サブカラー} desaturated
    Background: #1a1a2e to #16213e gradient
    Accent: {アクセントカラー} for sub-text only
  Lighting: 画面左上からの弱い間接光。人物の顔に影。全体的にローキー。
  Texture: わずかなフィルムグレイン（映画的な質感）
  Emotion: 「あ、これ自分のことだ」と読者が感じるリアルさ
  NO composition labels (no text like "問題提起"), NO watermarks, NO logos.

style: |
  Cinematic advertising banner. Photorealistic illustration style.
  Reference mood: Netflix映画のキービジュアルのような映画的構図と光.
  Mood: 切実感, 共感, リアルさ, 静かな緊張.
  High resolution 4K, 970x600px.
  Use the ChatGPT Images 2.0 (4o) model. Do NOT use DALL-E.
```

#### aplus_2.png（煽り・共感 — Agitation）

```yaml
subject: |
  Amazon A+ content banner amplifying the reader's urgency.
  Concrete scene: {問題を放置した結果の深刻な状況を描写。
  例（睡眠本）: 「重要な会議中に居眠りしそうになる疲労困憊のビジネスマン。
  周囲の同僚の冷たい視線。PCに映るグラフは右肩下がり」
  例（営業本）: 「空っぽのオフィスで一人残業。デスクにはゼロの営業成績表。
  窓の外は暗く、同期が笑顔で退社していく後ろ姿」}
  Japanese headline: 「{危機感を煽る8-15文字キャッチコピー}」

layout: |
  Wide landscape banner 970x600px.
  Full-bleed dramatic composition:
  - 全面にシーンを配置（人物は画面の1/3以上を占める）
  - 中央やや上に日本語ヘッドラインを重ねる
  - ヘッドライン背景: 横幅100%の半透明ダークバンド（height 120px, opacity 80%）
  - 対角線構図またはダッチアングル（視覚的な不安定さを演出）
  - 下端: {アクセントカラー}の細いライン（3px）

typography: |
  Headline 「{キャッチコピー}」
    — Size: バンド幅の60%を占める
    — Weight: Extra Bold
    — Font: Japanese sans-serif
    — Color: {アクセントカラー} or #FFFFFF
    — Letter-spacing: slightly wide for emphasis
  All Japanese text in actual Japanese characters, perfectly legible.

visuals: |
  Color palette: Agitation tone (赤みがかった警告色)
    Primary: {アクセントカラー} at 80% saturation
    Secondary: {メインカラー} darkened 40%
    Background: deep navy to black gradient
    Warning: subtle red/orange tint in shadows
  Lighting: 強いコントラスト。ハイライトとシャドウの差を極端に。
  右上から強い単一光源（スポットライト的）。
  Texture: ハイコントラスト、ドラマチック
  Emotion: 「このままではまずい」という切迫感
  NO composition labels, NO watermarks.

style: |
  High-impact advertising banner. Dramatic cinematic style.
  Reference mood: 映画予告編の最もテンションが上がるカットのような緊張感.
  Mood: 危機感, 焦燥, 緊張, 訴求力.
  High resolution 4K, 970x600px.
  Use the ChatGPT Images 2.0 (4o) model. Do NOT use DALL-E.
```

#### aplus_3.png（解決策 — Solution）

```yaml
subject: |
  Amazon A+ content banner showing the transformation after applying the book's solution.
  Concrete scene: {本書の解決策を実践した後の明るい変化を描写。
  例（睡眠本）: 「朝日が差し込む明るい寝室で、すっきりと目覚めた笑顔の30代男性。
  窓の外は青空。ベッドは整えられ、サイドテーブルに本とコップの水」
  例（営業本）: 「笑顔で握手を交わす営業マンとクライアント。
  テーブルには契約書。窓から明るい光が差し込む。自信に満ちた表情」}
  Japanese headline: 「{解決策を示す8-15文字キャッチコピー}」

layout: |
  Wide landscape banner 970x600px.
  Bright, open composition:
  - Left 35%: クリーンな{背景色}エリアに日本語ヘッドラインを配置
  - Right 65%: 明るく希望に満ちたシーン（人物の笑顔が見える）
  - 右上方向への対角線構図（上昇・成長を暗示）
  - 下端: {メインカラー}の細いライン（3px）

typography: |
  Headline 「{キャッチコピー}」
    — Size: 左エリアの中央に大きく
    — Weight: Bold
    — Font: Japanese sans-serif
    — Color: {メインカラー}
  Sub-text 「{本書のベネフィットを1行で}」
    — Size: Headlineの35%
    — Weight: Regular
    — Color: {サブカラー}
  All Japanese text in actual Japanese characters, crisp and clean.

visuals: |
  Color palette: Solution tone (明るく温かい)
    Primary: {メインカラー} at full brightness
    Secondary: {サブカラー} lightened 20%
    Background: {背景色} or white
    Highlight: {アクセントカラー} for subtle accents only
  Lighting: 右上からの温かい朝日のような自然光。全体的にハイキー。
  ソフトシャドウ、柔らかいハイライト。
  Texture: クリーンで爽やか。マット仕上げ。
  Emotion: 「こうなれるなら読みたい」という希望と期待
  NO composition labels, NO watermarks.

style: |
  Aspirational advertising banner. Clean modern style with warmth.
  Reference mood: Apple製品広告のようなクリーンさ + 人物の温かみ.
  Mood: 希望, 爽快感, 達成感, 自信.
  High resolution 4K, 970x600px.
  Use the ChatGPT Images 2.0 (4o) model. Do NOT use DALL-E.
```

#### aplus_4.png（CTA — Call to Action）

```yaml
subject: |
  Amazon A+ content banner with strong call-to-action.
  Concrete scene: {本書そのものを魅力的に見せる。
  「木目のデスクの上に表紙が見えるKindle端末。横にコーヒーとノート。
  画面には本書の表紙デザイン（実際の色合い・構成を再現）。
  背景はソフトボケの温かい光」}
  Japanese headline: 「{行動を促す8-15文字キャッチコピー}」
  Japanese CTA: 「今すぐ読み始める」

layout: |
  Wide landscape banner 970x600px.
  Product-hero composition:
  - Center: 本書のモックアップ（表紙デザインの色合いとスタイルを再現した書籍/Kindle）
    — 画面の40%を占める存在感
    — やや傾けて立体感を出す（15度程度の角度）
  - 上部: 日本語ヘッドラインキャッチコピー
  - 下部: CTAテキスト「今すぐ読み始める」を{アクセントカラー}のボタン風デザインで配置
    — 角丸矩形の背景 + 白文字、またはアンダーライン付き
  - 背景: ソフトボケのグラデーション（表紙カラーパレットから）

typography: |
  Headline 「{キャッチコピー}」
    — Size: 画面幅の50%
    — Weight: Bold
    — Font: Japanese sans-serif
    — Color: {メインカラー}
  CTA 「今すぐ読み始める」
    — Size: Headlineの50%
    — Weight: Bold
    — Color: #FFFFFF on {アクセントカラー} button background
    — Button: 角丸矩形 (border-radius 8px), padding 12px 32px
  All Japanese text in actual Japanese characters.

visuals: |
  Color palette: CTA tone (活力・行動)
    Primary: {アクセントカラー} at full saturation (CTAボタン)
    Secondary: {メインカラー} (ヘッドライン)
    Background: {背景色} to white soft gradient
    Glow: 書籍モックアップの周囲にソフトグロー（{アクセントカラー} at 20% opacity）
  Lighting: 正面やや上からの均一な光。商品撮影スタジオのような照明。
  書籍モックアップにスポットライト効果。
  Texture: ポリッシュドでプレミアム。ガラスのような反射。
  Emotion: 「今すぐクリックしたい」という行動意欲
  NO composition labels, NO watermarks.

style: |
  Premium product hero banner. E-commerce conversion-optimized.
  Reference mood: Apple Store製品ページ or Amazon商品ヒーローバナー.
  Mood: 期待感, 行動意欲, プレミアム感, ワクワク.
  High resolution 4K, 970x600px.
  Use the ChatGPT Images 2.0 (4o) model. Do NOT use DALL-E.
```

### A+プロンプト品質チェックリスト（生成前に必ず確認）

- [ ] 4枚すべてのsubjectに「具体的な人物・場所・状況・表情」が描写されている
- [ ] 4枚の色トーンがProblem(暗)→Agitation(赤/警告)→Solution(明)→CTA(活力)のグラデーションになっている
- [ ] 全画像にtypographyブロックで日本語キャッチコピー（8-15文字）が指定されている
- [ ] キャッチコピー4つでPASONAストーリーが完結している
- [ ] 各visuals に具体的な光源・質感・感情の指示がある
- [ ] 表紙と同じカラーパレット（4色HEXコード）が使用されている
- [ ] 「professional」「high quality」のような曖昧な指示だけで終わっていない

### ユーザーに提示する内容

```
【A+コンテンツ画像プロンプト確認】（4枚 / 各970×600px）
カラーパレット: 表紙と統一（{メイン} / {サブ} / {アクセント} / {背景}）

■ aplus_1.png（問題提起）
  キャッチコピー: "{生成したコピー}"
  → {YAMLプロンプト全文}

■ aplus_2.png（煽り・共感）
  キャッチコピー: "{生成したコピー}"
  → {YAMLプロンプト全文}

■ aplus_3.png（解決策）
  キャッチコピー: "{生成したコピー}"
  → {YAMLプロンプト全文}

■ aplus_4.png（CTA）
  キャッチコピー: "{生成したコピー}"
  → {YAMLプロンプト全文}

これらのプロンプトで画像を生成してよろしいですか？
```

**ユーザーが承認したら Phase 7 へ。**

---

## Phase 7: A+画像4枚生成（ChatGPT Images 2.0 DevTools経由）

**★確認5 で承認されたプロンプトで画像を生成する。**
生成手順は後述「ChatGPT Images 2.0 生成プロトコル」に従う。

### Phase 7 完了時の検証（必須）

```bash
python scripts/validate_images.py output/{slug} aplus
```

**検証基準:** aplus_1〜4.png がすべて存在し、各30KB以上

---

## ★確認6: A+画像4枚の確認

生成されたA+画像4枚をユーザーに提示する。
※ validate_images.py実行後は元画像が削除済み。manifest.jsonのサイズ情報と、Phase 7実行中にチャットに表示された画像プレビューで確認する。

```
A+コンテンツ画像4枚が生成されました。確認してください。
（manifest.jsonのoriginal_sizeを参照）

1. aplus_1.png（問題提起）— {N}KB
2. aplus_2.png（煽り・共感）— {N}KB
3. aplus_3.png（解決策）— {N}KB
4. aplus_4.png（CTA）— {N}KB

問題なければ「OK」、再生成する場合は番号と修正指示をお知らせください。
```

**ユーザーが承認したら ★確認7 へ。再生成指示があれば該当画像のみ Phase 7 を再実行（encode_binaries.pyが自動で上書きする）。**

---

## 画像のBase64エンコードについて（自動処理・手動操作不要）

`validate_images.py` が画像検証PASSと同時に以下を自動実行する:
1. 全バイナリをBase64エンコード → `output/{slug}/binaries/*.b64` に保存
2. `manifest.json`（復元用マッピング）を生成/追記
3. **元のバイナリファイルを自動削除**

Phase 6/7 で `validate_images.py` を実行すれば、追加の手順は不要。
エージェントが `encode_binaries.py` を手動で呼ぶ必要はない。

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
3. research.md — リサーチ結果
4. book_meta.md — 確定メタ情報
5. listing.txt — 出版メタデータ
6. cover_prompt.txt — 表紙プロンプト
7. kindle_application.txt — Kindle申請データ
8. binaries/*.b64 — 表紙画像・A+画像（Base64エンコード済み）
9. binaries/manifest.json — 復元用マッピング

※ PRマージ後、ローカルで以下を実行して画像を復元してください:
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
- **pandoc は使用しない**
- **検証スクリプトはPython標準ライブラリのみで動作する**
- **表紙画像はJPG形式で出力する（PNG生成時はJPGに変換）**
- **バイナリファイル（.png .jpg .jpeg .docx）を直接 git add / git commit してはならない**
- **validate_images.py が自動でBase64化＋元ファイル削除する。手動エンコードは不要**
- **PR作成時にワークスペースにバイナリが残っていないことを確認する**
- **画像内の日本語テキストはChatGPT Images 2.0のプロンプトに含めて描画する（Pillow/PILでのテキスト描画は禁止。Codex環境に日本語フォントがない）**
- **全画像（表紙・A+）はHTML/CSS/SVGで描画しない。必ずChatGPT Images 2.0（ブラウザ版 chatgpt.com）でChrome DevTools MCP経由で生成する**
- **DALL-E 3での生成は禁止。生成前後でモデルがChatGPT Images 2.0 (4o)であることを必ず確認する**
- **imagegen skill / gpt-image-2 API での画像生成は絶対に禁止。品質が低いため使用不可。すべての画像はChrome DevTools MCP経由のChatGPT Images 2.0で生成すること**

---

## ChatGPT Images 2.0 生成プロトコル（DevTools経由）

Phase 6（表紙）・Phase 7（A+）の全画像生成で共通のプロトコルを使用する。
Codex CLI環境ではChrome DevTools MCPが `mcp__chrome-devtools__*` として利用可能。

### 前提条件

- `~/.codex/config.toml` に `[mcp_servers.chrome-devtools]` が設定済み
- Chromeが起動中で、ChatGPTにログイン済み

### DevTools MCP 接続失敗時の対処（必須）

```
Phase 6 または Phase 7 の開始前に、必ず DevTools MCP の接続を確認する。
接続失敗時は imagegen skill や gpt-image-2 API にフォールバックしてはならない。
以下の手順で自動リカバリーを行う。

Step A: mcp__chrome-devtools__list_pages() を実行
  → 成功 → 通常の生成フローへ進む
  → 失敗（connection closed / MCP startup failed）→ Step B へ

Step B: ユーザーに案内メッセージを表示して待機
  「Chrome（書籍制作用）がデバッグモードで起動していません。
   デスクトップの「Chrome（書籍制作用）」をダブルクリックして起動し、
   ChatGPTにログインしてください。
   準備ができたら「OK」と入力してください。」

Step C: ユーザーが「OK」と回答したら、再度接続を試行
  mcp__chrome-devtools__list_pages()
  → 成功 → 通常の生成フローへ進む
  → 失敗 → Step B に戻る（最大3回リトライ）

Step D: 3回リトライしても失敗
  「Chrome DevTools への接続に失敗しました。
   以下を確認してください:
   1. Chrome を一度すべて閉じて「Chrome（書籍制作用）」で再起動
   2. ChatGPT にログイン済みであること
   準備ができたら「OK」と入力してください。」
  → Step C に戻る
```

**絶対禁止:** DevTools MCP 接続失敗時に imagegen skill / gpt-image-2 API / DALL-E で代替生成すること

### 4ブロックプロンプト構造（全画像共通）

すべての画像プロンプトは以下の4ブロック形式で記述する:

```
* Subject: (画像の主題・内容。日本語テキストを含む場合はここに記載)
* Layout: (配置・構造・階層・接続関係の指示)
* Visuals: (色・アイコン・フォント・装飾の指示。カラースキームを明示)
* Style: (全体のスタイル・品質。末尾に必ず「Use the ChatGPT Images 2.0 (4o) model. Do NOT use DALL-E.」を付加)
```

### 生成フロー（Step 1-8）

```
Step 1: 接続確認
  │  mcp__chrome-devtools__list_pages()
  │  → エラー時: mcp__chrome-devtools__new_page(url="https://chatgpt.com") で復帰
  ▼
Step 2: ChatGPT Images 2.0 を新しいタブで開く
  │  mcp__chrome-devtools__new_page(url="https://chatgpt.com/g/g-2fkFE8rbu-dall-e")
  │  sleep 5（ページ読み込み待ち）
  ▼
Step 2.5: モデル確認（DALL-Eフォールバック防止）
  │  mcp__chrome-devtools__take_screenshot()
  │  → ページ上部のモデル表示を確認
  │  → 「4o」以外: モデル選択UIで「4o」を選択し直す
  ▼
Step 3: プロンプト入力
  │  mcp__chrome-devtools__take_snapshot()
  │  → プロンプト入力欄の uid を特定
  │  mcp__chrome-devtools__fill(uid, value=プロンプト)
  ▼
Step 4: 送信
  │  mcp__chrome-devtools__take_snapshot()
  │  → 送信ボタンの uid を特定
  │  mcp__chrome-devtools__click(uid)
  ▼
Step 5: 生成待ち（ポーリング方式）
  │  sleep 30（初回待機）
  │  → mcp__chrome-devtools__take_screenshot() で完了確認
  │  → 未完了: sleep 15 → 再確認（最大4回）
  ▼
Step 6: モデル結果確認
  │  DALL-E生成の兆候チェック
  │  → 検知: close_page → 新タブで再生成
  ▼
Step 7: 画像保存
  │  方式A: ダウンロードボタンclick → ~/Downloads から移動
  │    sleep 3 → LATEST=$(ls -t ~/Downloads/*.png | head -1)
  │    mv "$LATEST" "output/{slug}/images/{filename}.png"
  │  方式B: evaluate_script で img src 取得 → curl で保存
  │  方式C: canvas → base64 → デコード保存
  ▼
Step 8: 次の画像 or 完了
  │  並列モード: new_page で別タブを開き Step 3 から並列
  │  逐次モード: 同じタブで Step 3 から繰り返し
  │  完了: close_page で不要タブを閉じる
```

### 複数枚生成時の注意事項

- 8タブ以上の同時生成はレートリミットの恐れ（6/2セッションで確認済み）
- 各タブは独立したChatGPTセッション（会話が混ざらない）
- 生成失敗時は該当タブを close_page → new_page で再生成

---

# PR作成ルール（厳守）

## Base64方式によるバイナリファイルのPR対応

Codex WebのPRはバイナリファイルを直接含められない。
validate_images.py が各Phase完了時に自動でBase64テキスト化し、元バイナリを削除する。

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

Phase 6/7の各完了時に、validate_images.pyが自動でBase64化+元ファイル削除を行う。
コミット時はテキスト+Base64ファイルのみがステージングされる。

```bash
# binaries/ディレクトリをコミットに含める（.b64 + manifest.json）
git add output/{slug}/binaries/

# バイナリが含まれていないことを確認（.gitignoreで除外済みだが念のため）
git diff --cached --name-only | grep -E '\.(docx|png|jpg|jpeg|pdf)$' && echo "ERROR: バイナリが含まれています" || echo "OK"
```

### ユーザーへの復元案内
PRの説明欄に以下を必ず記載する:

```
## 画像・DOCXの復元方法
PRマージ後、以下を実行してください:
python scripts/decode_binaries.py output/{slug}
```
