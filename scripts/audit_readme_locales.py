#!/usr/bin/env python3
"""Check that localized READMEs preserve the English README's structure.

This intentionally checks facts and navigation, not translation fluency.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "README.md"
LANGS = ("es", "fr", "pt", "de", "it", "zh", "ja", "ko", "hi", "ar", "ru", "tr")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
MD_LINK = re.compile(r"\]\(([^)]+)\)")
HTML_TARGET = re.compile(r'\b(?:href|srcset|src)="([^"]+)"')
HTML_TEXT = re.compile(r">([^<>]+)<")
HTML_ALT = re.compile(r'\balt="([^"]+)"')
HTML_ID = re.compile(r'\bid="([^"]+)"')
FIGURE_SUB = re.compile(r"<sub>(FIG_\d{3}\s*·\s*[A-Z])</sub>")
INLINE_CODE = re.compile(r"`([^`\n]+)`")
LESSON_ROW = re.compile(r"^\|\s*\d{2}\s*\|\s*\[[^\]]+\]\((?:\.\./\.\./)?(phases/[^)]+)\)", re.M)
FACT = re.compile(r"(?<!\d)\d+(?:,\d{3})*(?:-\d{2})*(?:\.\d+)?")
STATS_BLOCK = re.compile(r"(<!-- STATS:START[^\n]*-->)(.*?)(<!-- STATS:END -->)", re.S)
BOLD_COUNT = re.compile(r"(?<=<b>)\d[\d,]*(?=</b>)")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def body(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if lines and re.match(r"^<p\b[^>]*><sub>", lines[0]):
        lines = lines[1:]
    return "".join(lines)


def unlocalize_target(target: str) -> str:
    if target.startswith("../../"):
        return target[6:]
    return target


def link_targets(text: str) -> Counter[str]:
    return Counter(unlocalize_target(t) for t in MD_LINK.findall(text) + HTML_TARGET.findall(text))


def fence_step(line: str, opener: str | None) -> tuple[bool, str | None]:
    match = FENCE.match(line)
    if match is None:
        return False, opener
    run, rest = match.groups()
    if opener is None:
        if run[0] == "`" and "`" in rest:
            return False, None
        return True, run
    if run[0] == opener[0] and len(run) >= len(opener) and not rest.strip():
        return True, None
    return False, opener


def outside_fences(text: str) -> str:
    lines = []
    opener = None
    for line in text.splitlines():
        fence, opener = fence_step(line, opener)
        if not fence and opener is None:
            lines.append(line)
    return "\n".join(lines)


def local_link_errors(text: str, lang: str) -> list[str]:
    errors = []
    base = ROOT / "i18n" / lang
    visible = outside_fences(text)
    for target in MD_LINK.findall(visible) + HTML_TARGET.findall(visible):
        if target.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        path = target.split("#", 1)[0].split("?", 1)[0]
        if not path:
            continue
        if not path.startswith("../../"):
            errors.append(f"repo-relative target lacks ../../ prefix: {target}")
            continue
        if not (base / path).exists():
            errors.append(f"repo-relative target does not exist: {target}")
    return list(dict.fromkeys(errors))


def fenced_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    opener = None
    for line in text.splitlines():
        fence, new_opener = fence_step(line, opener)
        if opener is None:
            if fence:
                current = [line]
        else:
            current.append(line)
            if fence:
                blocks.append("\n".join(current))
                current = []
        opener = new_opener
    if opener is not None:
        raise ValueError("unclosed fenced code block")
    return blocks


def mermaid_topology(block: str) -> str:
    return re.sub(r'"[^"]*"', '""', block)


def tree_topology(block: str) -> str:
    return re.sub(
        r"((?:code/|en\.md|outputs/|prompts/|skills/))\s{2,}[^\n]*",
        r"\1",
        block,
    )


def table_cells(text: str) -> list[int]:
    counts = []
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            counts.append(len(re.findall(r"(?<!\\)\|", line)))
    return counts


def list_item_counts(text: str) -> tuple[int, int]:
    visible = outside_fences(text)
    unordered = len(re.findall(r"^\s*[-*+]\s+", visible, re.M))
    ordered = len(re.findall(r"^\s*\d+\.\s+", visible, re.M))
    return unordered, ordered


def untranslated_long_lines(source: str, locale: str) -> list[str]:
    visible_source = outside_fences(source)
    visible_locale = outside_fences(locale)
    prose = [
        line for line in visible_source.splitlines()
        if len(line) > 80 and len(line.split()) > 10
        and not line.lstrip().startswith(("|", "<", ">", "-", "*"))
    ]
    html = [
        match.group(1).strip() for pattern in (HTML_TEXT, HTML_ALT)
        for match in pattern.finditer(visible_source)
        if len(match.group(1)) > 70 and len(match.group(1).split()) > 8
        and "\n-" not in match.group(1)
    ]
    return [value for value in prose + html if value in visible_locale]


def protected_inline_tokens(text: str) -> set[str]:
    return {
        token for token in INLINE_CODE.findall(text)
        if not re.fullmatch(r"\d+ lessons", token)
        and not token.startswith(" comment listing non-stdlib deps")
    }


def landing_facts(text: str) -> tuple[str, str]:
    before_stats, _, rest = text.partition("<!-- STATS:START")
    stats, _, _ = rest.partition("<!-- STATS:END -->")
    hero = "\n".join(line for line in before_stats.splitlines() if line.startswith(">"))
    return hero, stats


def route_contexts(text: str, path: str) -> list[str]:
    return [
        text[max(0, match.start() - 240):match.start() + len(path) + 240]
        for match in re.finditer(re.escape(path), text)
    ]


def sync_stats_facts(source: str, locale: str) -> str:
    source_match = STATS_BLOCK.search(source)
    locale_match = STATS_BLOCK.search(locale)
    if source_match is None or locale_match is None:
        raise ValueError("README stats block is missing")
    source_stats = source_match.group(2)
    locale_stats = locale_match.group(2)
    source_counts = BOLD_COUNT.findall(source_stats)
    locale_counts = BOLD_COUNT.findall(locale_stats)
    if len(source_counts) != 2 or len(locale_counts) != 2:
        raise ValueError("README stats reader/page-view counts are missing")
    source_date = ISO_DATE.findall(source_stats)
    locale_date = ISO_DATE.findall(locale_stats)
    if len(source_date) != 1 or len(locale_date) != 1:
        raise ValueError("README stats date is missing")
    replacements = iter(source_counts)
    translated_stats = BOLD_COUNT.sub(lambda _: next(replacements), locale_stats)
    translated_stats = ISO_DATE.sub(source_date[0], translated_stats, count=1)
    return locale[:locale_match.start(2)] + translated_stats + locale[locale_match.end(2):]


def check(source: str, locale: str, lang: str) -> list[str]:
    errors: list[str] = []
    language_bar = set(re.findall(r'href="i18n/([a-z]{2})/README\.md"', source))
    if not set(LANGS).issubset(language_bar):
        errors.append("root README language bar is missing complete locales")
    if link_targets(source) != link_targets(locale):
        missing = link_targets(source) - link_targets(locale)
        extra = link_targets(locale) - link_targets(source)
        errors.append(f"links differ: missing={sum(missing.values())}, extra={sum(extra.values())}")
    identical_prose = untranslated_long_lines(source, locale)
    if identical_prose:
        errors.append(f"long English prose remains untranslated: {len(identical_prose)} line(s)")
    localized_inline = set(INLINE_CODE.findall(locale))
    missing_tokens = sorted(token for token in protected_inline_tokens(source) if token not in localized_inline)
    if missing_tokens:
        errors.append(f"inline code formatting missing: {len(missing_tokens)} token(s), e.g. {missing_tokens[:5]}")
    if table_cells(source) != table_cells(locale):
        errors.append("table row or cell counts differ")
    if list_item_counts(source) != list_item_counts(locale):
        errors.append("Markdown list item counts differ")
    if Counter(HTML_ID.findall(source)) != Counter(HTML_ID.findall(locale)):
        errors.append("explicit HTML IDs differ")
    if Counter(FIGURE_SUB.findall(source)) != Counter(FIGURE_SUB.findall(locale)):
        errors.append("figure identifiers differ")
    errors.extend(local_link_errors(locale, lang))
    source_lesson_rows = LESSON_ROW.findall(source)
    locale_lesson_rows = LESSON_ROW.findall(locale)
    if not source_lesson_rows:
        errors.append("English README has no linked lesson rows")
    if len(locale_lesson_rows) != len(source_lesson_rows):
        errors.append("lesson row count differs")
    if Counter(source_lesson_rows) != Counter(locale_lesson_rows):
        errors.append("lesson link destinations differ")
    for path in (
        "learning-paths/model-context-protocol.json",
        "learning-paths/agent-skills.json",
        "learning-paths/using-coding-agents.json",
        "learning-paths/shaping-the-build.json",
    ):
        source_context = " ".join(
            source[max(0, match.start() - 180):match.start()]
            for match in re.finditer(re.escape(path), source)
        )
        ranges = set(re.findall(r"(?<!\d)(\d{2})\s*[-–—]\s*(\d{2})(?!\d)", source_context))
        contexts = route_contexts(locale, path)
        for first, last in ranges:
            marker = rf"(?<!\d){first}(?!\d)[^\d]{{0,24}}(?<!\d){last}(?!\d)"
            if not any(re.search(marker, context) for context in contexts):
                errors.append(f"course range {first}–{last} missing near {path}")
    source_hero, source_stats = landing_facts(source)
    hero, stats = landing_facts(locale)
    if Counter(FACT.findall(source_hero)) != Counter(FACT.findall(hero)):
        errors.append("hero numeric facts differ")
    if Counter(FACT.findall(source_stats)) != Counter(FACT.findall(stats)):
        errors.append("stats numeric facts differ")
    if BOLD_COUNT.findall(source_stats) != BOLD_COUNT.findall(stats):
        errors.append("reader and page-view counts differ")
    if re.search(r'\b(?:alt|title)"', locale):
        errors.append("malformed HTML alt/title attribute")

    try:
        original_fences = fenced_blocks(source)
        translated_fences = fenced_blocks(locale)
    except ValueError as exc:
        errors.append(str(exc))
        original_fences, translated_fences = [], []
    if len(original_fences) != len(translated_fences):
        errors.append("fenced code block count differs")
    else:
        for index, (original, translated) in enumerate(zip(original_fences, translated_fences)):
            if original.startswith("```mermaid"):
                if mermaid_topology(original) != mermaid_topology(translated):
                    errors.append(f"Mermaid topology changed in block {index}")
            elif original.startswith("```text") and "├──" in original:
                if tree_topology(original) != tree_topology(translated):
                    errors.append(f"directory tree paths changed in block {index}")
            elif original != translated:
                errors.append(f"code block {index} changed")

    if lang != "zh" and "Read in your language:" in locale:
        errors.append("language navigation heading remains English")
    if lang == "zh" and "选择 README 语言" not in locale:
        errors.append("Chinese language navigation missing")
    return errors


def check_document(source: str, document: str, lang: str) -> list[str]:
    first_line = document.splitlines()[0] if document else ""
    errors = []
    if not re.match(r"^<p\b[^>]*><sub>", first_line):
        errors.append("localized README has no language note")
    if 'href="../../README.md"' not in first_line:
        errors.append("language note has no canonical English link")
    return errors + check(source, body(document), lang)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=LANGS)
    args = parser.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
    failed = False
    for lang in ((args.lang,) if args.lang else LANGS):
        path = ROOT / "i18n" / lang / "README.md"
        if not path.is_file():
            print(f"{lang}: missing {path.relative_to(ROOT)}")
            failed = True
            continue
        document = path.read_text(encoding="utf-8")
        errors = check_document(source, document, lang)
        if errors:
            failed = True
            print(f"{lang}: FAIL")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"{lang}: structure and facts preserved")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
