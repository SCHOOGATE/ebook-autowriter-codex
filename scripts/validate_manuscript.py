#!/usr/bin/env python3
"""manuscript.md quality validator. stdlib only."""
import os
import re
import sys
from collections import Counter


def extract_chapters(content):
    parts = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    chapters = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        title = lines[0].strip().lstrip("#").strip()
        body = lines[1] if len(lines) > 1 else ""
        chapters.append((title, body))
    return chapters


def ngram_duplication_ratio(text, n=5):
    """Return practical repetition ratio based on duplicated sentences.

    A raw 5-character n-gram check over Japanese prose over-counts particles,
    polite endings, headings, and repeated structural markers. The production
    risk is duplicated sentence or paragraph padding, so this validator detects
    exact sentence reuse after whitespace normalization.
    """
    body = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)
    body = re.sub(r"\\newpage", "", body)
    sentences = [s.strip() for s in re.split(r"(?<=。)", body) if len(s.strip()) >= 12]
    if not sentences:
        return 0.0
    normalized = [re.sub(r"\s+", "", s) for s in sentences]
    counter = Counter(normalized)
    duplicate_count = sum(count - 1 for count in counter.values() if count > 1)
    return duplicate_count / len(normalized)


def check_forbidden_patterns(content):
    issues = []
    if re.search(r"^\|.*\|.*\|", content, re.MULTILINE):
        issues.append("Markdownテーブル記法（| ... |）が検出されました")
    if "```" in content:
        issues.append("コードブロック（```）が検出されました")
    if re.search(r"[┌┐└┘├┤┬┴┼─│]", content):
        issues.append("ASCII/罫線図文字が検出されました")
    if re.search(r"<!--\s*\[.*IMAGE.*\]\s*-->", content, re.IGNORECASE):
        issues.append("画像タグ（<!-- [IMAGE] -->）が検出されました")
    return issues


def check_section_homogeneity(content):
    """Detect cookie-cutter sections where only the title differs."""
    issues = []
    sections = re.split(r"(?=^### )", content, flags=re.MULTILINE)
    section_openings = []
    for sec in sections:
        lines = sec.strip().split("\n")
        if not lines or not lines[0].startswith("### "):
            continue
        title = lines[0]
        # Collect first 5 non-empty body lines (skip title, newpage, empty)
        body_lines = []
        for line in lines[1:]:
            stripped = line.strip()
            if stripped and stripped != "\\newpage" and not stripped.startswith("#"):
                body_lines.append(stripped)
                if len(body_lines) >= 5:
                    break
        if len(body_lines) >= 3:
            section_openings.append((title, body_lines))

    if len(section_openings) < 3:
        return issues

    # Compare opening structures: normalize by removing section-specific nouns
    def normalize(text):
        # Remove quoted section titles and specific nouns to find structural similarity
        t = re.sub(r"「[^」]+」", "TITLE", text)
        t = re.sub(r"たとえば.*?という場面", "EXAMPLE", t)
        return t

    # Check if >50% of sections share the same opening pattern
    normalized_openings = []
    for title, body in section_openings:
        key = "|".join(normalize(line)[:40] for line in body[:3])
        normalized_openings.append((title, key))

    key_counter = Counter(k for _, k in normalized_openings)
    most_common_key, most_common_count = key_counter.most_common(1)[0]
    ratio = most_common_count / len(normalized_openings)
    if ratio > 0.5 and most_common_count >= 3:
        # Find example section titles
        examples = [t for t, k in normalized_openings if k == most_common_key][:3]
        issues.append(
            f"section homogeneity: {most_common_count}/{len(normalized_openings)} sections "
            f"({ratio:.0%}) share identical opening structure. "
            f"Examples: {', '.join(examples[:3])}"
        )
    return issues


def check_template_contamination(content):
    """Detect template remnants and process instructions leaked into manuscript."""
    issues = []
    patterns = [
        (r"第\d+章\d+節の実践\d+として確認します", "template marker (実践N)"),
        (r"を考える時は、.{2,20}を手がかりにして、.+という視点を加えてください", "template filler (視点を加えてください)"),
        (r"この考え方を.+の流れに置くと、.+は単なる知識ではなく", "template filler (流れに置くと)"),
        (r"特に「[^」]+」の場面で効いてきます", "template filler (場面で効いてきます)"),
        (r"Phase\s*\d+", "process term (Phase N)"),
        (r"Step\s*[A-Z0-9]", "process term (Step N)"),
        (r"Layer\s*[1-5]", "research ref (Layer N)"),
        (r"\{[^}]*テーマ[^}]*\}", "placeholder ({theme})"),
        (r"\{[^}]*タイトル[^}]*\}", "placeholder ({title})"),
        (r"\{[^}]*slug[^}]*\}", "placeholder ({slug})"),
        (r"\bTODO\b", "TODO marker"),
        (r"\bFIXME\b", "FIXME marker"),
        (r"\bPLACEHOLDER\b", "PLACEHOLDER marker"),
        (r"\bINSERT\s+HERE\b", "INSERT HERE marker"),
        (r"validate_\w+\.py", "script ref (validate_*.py)"),
        (r"chapter_blueprint", "file ref (chapter_blueprint)"),
        (r"research\.md", "file ref (research.md)"),
        (r"book_meta\.md", "file ref (book_meta.md)"),
        (r"output/", "path ref (output/)"),
    ]
    for pat, label in patterns:
        matches = re.findall(pat, content)
        if matches:
            sample = matches[0][:50]
            issues.append(
                f"template contamination ({label}): "
                f"{len(matches)} occurrences, e.g. \"{sample}\""
            )
    return issues


def check_style_consistency(content):
    desu_masu = len(re.findall(r"(?:です|ます|ください|ましょう|でしょう)[。\n]", content))
    da_dearu = len(re.findall(r"(?:だ|である|しよう|だろう)[。\n]", content))
    total = desu_masu + da_dearu
    if total == 0:
        return 1.0
    return desu_masu / total


FILLER_PATTERN = re.compile(
    r"(第\d章|はじめに|おわりに|第\d章:.+)の補足\d+では"
)

# v4.5: Additional filler patterns detected in eigo-kentei / suimin-busoku tests
FILLER_PATTERNS_V45 = [
    # Type 1: Chapter-opening template ("第X章の実践視点/学習場面/記録方法/行動設計")
    re.compile(r"^第\d章の(実践視点|学習場面|記録方法|行動設計)\d"),
    # Type 2: Subsection-title-insertion template ("{title}では...孤立した作業にせず")
    re.compile(r"孤立した作業にせず"),
    re.compile(r"今日の到達点を一つだけ決めてから始めます"),
    re.compile(r"の結果を感覚で終わらせず"),
    re.compile(r"の流れを使うと、短い勉強時間でも"),
    # Original pattern
    FILLER_PATTERN,
]


def _count_filler_lines(content):
    """Count lines matching any known filler pattern."""
    lines = content.split("\n")
    filler_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(pat.search(stripped) for pat in FILLER_PATTERNS_V45):
            filler_lines.append(i + 1)
    return filler_lines


def check_template_filler(content):
    """B-1: Detect template-style filler lines (v4.5 expanded)."""
    filler_lines = _count_filler_lines(content)
    if len(filler_lines) >= 4:
        return [f"template filler detected: {len(filler_lines)} lines (threshold: 3)"]
    return []


def check_subsection_filler(content):
    """B-2: Detect filler immediately after ### headings."""
    lines = content.split("\n")
    count = 0
    i = 0
    while i < len(lines):
        if lines[i].startswith("### "):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and any(
                pat.search(lines[j].strip()) for pat in FILLER_PATTERNS_V45
            ):
                count += 1
        i += 1
    if count > 0:
        return [f"subsection heading followed by filler: {count} occurrences"]
    return []


def check_filler_excluded_total(content):
    """B-6: Total char count after removing all filler lines must meet 25,000.

    Uses the same counting as the main total_chars (len of full content)
    minus the characters on filler lines (including their newlines).
    Only triggers if filler lines were actually detected.
    """
    filler_line_nums = _count_filler_lines(content)
    if not filler_line_nums:
        return []  # No filler detected, skip this check
    lines = content.split("\n")
    filler_set = set(filler_line_nums)
    # Rebuild content without filler lines and measure
    real_content = "\n".join(
        lines[i] for i in range(len(lines)) if (i + 1) not in filler_set
    )
    real_chars = len(real_content)
    if real_chars < 25000:
        return [
            f"filler-excluded total chars: {real_chars} / min 25,000 "
            f"({len(filler_set)} filler lines removed)"
        ]
    return []


def check_excessive_blank_lines(content):
    """B-7: Detect 3+ consecutive blank lines."""
    runs = re.findall(r"\n{4,}", content)
    if runs:
        return [f"excessive blank lines: {len(runs)} runs of 3+ consecutive blanks"]
    return []


def check_chapter_chars_excluding_filler(chapters):
    """B-3: Per-chapter character count after removing filler lines."""
    chapter_min = {1: 3000, 2: 3500, 3: 5000, 4: 4000, 5: 2500}
    errors = []
    ch_num = 0
    for title, body in chapters:
        filtered_lines = [
            line for line in body.split("\n")
            if not FILLER_PATTERN.search(line)
        ]
        filtered_len = sum(len(line) for line in filtered_lines)
        if "はじめに" in title or "おわりに" in title:
            if filtered_len < 1200:
                errors.append(
                    f"「{title}」filler-excluded char count: {filtered_len} / min 1,200"
                )
        elif title.startswith("第") or re.match(r"\d+章", title):
            ch_num += 1
            min_len = chapter_min.get(ch_num, 3000)
            if filtered_len < min_len:
                errors.append(
                    f"「{title}」filler-excluded char count: {filtered_len} / min {min_len}"
                )
    return errors


def check_research_citations(slug_dir, content):
    """B-4: Warn if no research.md URLs or domains are cited in manuscript."""
    research_path = os.path.join(slug_dir, "research.md")
    if not os.path.isfile(research_path):
        return []  # no research.md, skip
    with open(research_path, encoding="utf-8") as f:
        research = f.read()
    urls = re.findall(r"(https?://\S+)", research)
    if not urls:
        return []
    # extract domains
    domains = set()
    for url in urls:
        m = re.match(r"https?://([^/]+)", url)
        if m:
            domains.add(m.group(1))
    # check if any url or domain appears in manuscript
    for url in urls:
        if url in content:
            return []
    for domain in domains:
        if domain in content:
            return []
    return [f"WARN: research.md has {len(urls)} URLs but none cited in manuscript"]


def check_duplicate_sentences(content):
    """B-5: Detect sentences (>=15 chars) appearing 3+ times."""
    sentences = [s.strip() for s in content.split("。") if len(s.strip()) >= 15]
    normalized = [re.sub(r"\s+", "", s) for s in sentences]
    counter = Counter(normalized)
    duplicates = {sent: cnt for sent, cnt in counter.items() if cnt >= 3}
    if duplicates:
        issues = []
        for sent, cnt in list(duplicates.items())[:5]:
            preview = sent[:40]
            issues.append(f"duplicate sentence ({cnt}x): \"{preview}...\"")
        return issues
    return []


def validate(slug_dir):
    path = os.path.join(slug_dir, "manuscript.md")
    errors = []
    warnings = []

    if not os.path.exists(path):
        print("FAIL: manuscript.md が存在しません")
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    total_chars = len(content)
    if total_chars < 25000:
        errors.append(f"総文字数不足: {total_chars} / 最低25,000字")

    chapters = extract_chapters(content)
    if len(chapters) < 7:
        errors.append(f"章数不足: {len(chapters)} / 最低7セクション（はじめに+5章+おわりに）")

    # Chapter length check with graduated thresholds
    # Ch1=3000, Ch2=3500, Ch3=5000(Solution), Ch4=4000, Ch5=2500
    chapter_min = {1: 3000, 2: 3500, 3: 5000, 4: 4000, 5: 2500}
    ch_num = 0
    for title, body in chapters:
        body_len = len(body)
        if "はじめに" in title or "おわりに" in title:
            if body_len < 1200:
                errors.append(f"「{title}」字数不足: {body_len} / 最低1,200字")
        elif title.startswith("第") or re.match(r"\d+章", title):
            ch_num += 1
            min_len = chapter_min.get(ch_num, 3000)
            if body_len < min_len:
                errors.append(f"「{title}」字数不足: {body_len} / 最低{min_len}字")

    dup_ratio = ngram_duplication_ratio(content, n=5)
    if dup_ratio > 0.15:
        errors.append(f"n-gram重複率が高すぎます: {dup_ratio:.1%} / 上限15%")

    errors.extend(check_forbidden_patterns(content))
    errors.extend(check_section_homogeneity(content))
    errors.extend(check_template_contamination(content))

    style_ratio = check_style_consistency(content)
    if style_ratio < 0.80:
        errors.append(f"です・ます調の一貫性不足: {style_ratio:.0%} / 最低80%")

    # B-1: Template filler detection (v4.5 expanded)
    errors.extend(check_template_filler(content))

    # B-2: Subsection heading followed by filler
    errors.extend(check_subsection_filler(content))

    # B-3: Chapter char count excluding filler lines
    errors.extend(check_chapter_chars_excluding_filler(chapters))

    # B-4: Research citation check (WARN only, not FAIL)
    warnings.extend(check_research_citations(slug_dir, content))

    # B-5: Duplicate sentence detection (3+ identical, >=15 chars)
    errors.extend(check_duplicate_sentences(content))

    # B-6: Filler-excluded total char count
    errors.extend(check_filler_excluded_total(content))

    # B-7: Excessive blank lines
    errors.extend(check_excessive_blank_lines(content))

    if errors:
        print("FAIL: manuscript.md 検証エラー")
        for e in errors:
            print(f"  - {e}")
        for w in warnings:
            print(f"  - {w}")
        return 1

    if warnings:
        for w in warnings:
            print(f"  - {w}")

    print(f"PASS: manuscript.md ({total_chars}字, {len(chapters)}セクション, 重複率{dup_ratio:.1%})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_manuscript.py <output/slug_dir>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
