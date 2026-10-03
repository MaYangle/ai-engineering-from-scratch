#!/usr/bin/env python3
"""Translate every reader-visible README phrase while preserving executable text.

This is the static reader's full-document source. The GitHub README translations
on main remain the hand-edited landing copies. GitHub Actions publishes this
generated document to the translations branch, one language at a time.
"""

import argparse
import hashlib
import re
from pathlib import Path

from build_readme_i18n import README, english_source, spans
from readme_translations import TRANSLATIONS
from translate_lessons import NLLB_CODES, _nllb_pipe, _nllb_sentence

FENCE = re.compile(r"^\s*(```|~~~)")
HTML_COMMENT = re.compile(r"<!--.*?-->")
PROTECT = re.compile(
    r"(<code\b[^>]*>.*?</code>|`+[^`\n]*`+|<[^>]+>|&(?:[A-Za-z][A-Za-z0-9]+|#[0-9]+|#x[0-9A-Fa-f]+);|"
    r"!?\]\([^)]*\)|https?://[^\s<>)]+|"
    r"(?<![\w/])[A-Za-z0-9_.-]+\.(?:md|py|js|ts|rs|jl|json|ipynb|html|yaml|yml))", re.IGNORECASE
)
MARKUP = re.compile(r"(\||\*\*|__|~~|\[|\]|(?<!\w)[*_](?!\w))")
LEADING_MARKER = re.compile(r"^(\s*(?:#{1,6}\s+|>\s*|[-*+]\s+|\d+\.\s+)+)")
ENGLISH = re.compile(r"[A-Za-z]{2,}")
INLINE_CODE = re.compile(r"`+[^`\n]*`+")
LINK_TARGET = re.compile(r"\]\(([^)]*)\)")
HTML_TARGET = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']")
ACCESSIBLE_TEXT = re.compile(r'\b(alt|title)=(\")([^\"]*)(\")', re.IGNORECASE)


def split_protected(value):
    """Return (is_protected, text) parts without exposing paths to the model."""
    out = []
    start = 0
    for match in PROTECT.finditer(value):
        if match.start() > start:
            out.append((False, value[start:match.start()]))
        out.append((True, match.group()))
        start = match.end()
    if start < len(value):
        out.append((False, value[start:]))
    return out


def translate_phrase(value, table, translate):
    if not ENGLISH.search(value):
        return value
    lead = re.match(r"^\s*", value).group()
    tail = re.search(r"\s*$", value).group()
    core = value[len(lead):len(value) - len(tail) if tail else len(value)]
    if not core or not ENGLISH.search(core):
        return value
    if core in table:
        translated = table[core]
    else:
        translated = translate(core).replace("\r", " ").replace("\n", " ").strip()
        if not translated:
            # NLLB occasionally returns an empty string for a mixed acronym /
            # product-name title. Keep the source phrase for editorial review
            # rather than discarding the rest of a long translation job.
            print(f"needs manual translation: {core!r}", flush=True)
            translated = core
        # A translated pipe would create another Markdown table cell.
        translated = translated.replace("|", r"\|")
    return lead + translated + tail


def translate_visible(line, table, translate):
    if not line.strip() or HTML_COMMENT.fullmatch(line.strip()):
        return line
    match = LEADING_MARKER.match(line)
    marker = match.group() if match else ""
    body = line[len(marker):]
    result = [marker]
    for protected, part in split_protected(body):
        if protected:
            if part.lower().startswith("<img "):
                part = ACCESSIBLE_TEXT.sub(
                    lambda match: match.group(1) + match.group(2)
                    + translate_phrase(match.group(3), table, translate) + match.group(4),
                    part,
                )
            result.append(part)
            continue
        for fragment in MARKUP.split(part):
            if fragment in ("|", "**", "__", "~~", "[", "]", "*", "_"):
                result.append(fragment)
            else:
                result.append(translate_phrase(fragment, table, translate))
    return "".join(result)


def structure(md):
    """Parts whose exact spelling must survive translation."""
    fences = []
    in_fence = False
    fenced = []
    for line in md.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            fenced.append(line)
        elif in_fence:
            fenced.append(line)
    fences = "\n".join(fenced)
    return {
        "fences": fences,
        "inline_code": INLINE_CODE.findall(md),
        "links": LINK_TARGET.findall(md),
        "html_targets": HTML_TARGET.findall(md),
        "tables": sum(1 for line in md.split("\n") if line.lstrip().startswith("|")),
    }


def translate_readme(source, lang, translate):
    table = TRANSLATIONS[lang]
    source_lines = source.split("\n")
    manual = [sp for sp in spans(source) if sp["key"] in table]
    manual_lines = {index for sp in manual for index in range(sp["start"], sp["end"])}
    out = []
    in_fence = False
    in_navigation = False
    for index, line in enumerate(source_lines):
        if line.strip() == "<!-- README-LANGUAGES:START -->":
            in_navigation = True
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
        elif in_fence or in_navigation or index in manual_lines:
            out.append(line)
        else:
            out.append(translate_visible(line, table, translate))
        if line.strip() == "<!-- README-LANGUAGES:END -->":
            in_navigation = False
    for sp in sorted(manual, key=lambda item: item["start"], reverse=True):
        out[sp["start"]:sp["end"]] = [sp["prefix"] + row for row in table[sp["key"]].split("\n")]
    translated = "\n".join(out)
    if structure(source) != structure(translated):
        raise ValueError("translation changed code, links, images, or table structure")
    return translated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True, choices=sorted(TRANSLATIONS))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = english_source(README.read_text(encoding="utf-8"))
    target = NLLB_CODES.get(args.lang)
    if not target:
        parser.error(f"no NLLB language code for {args.lang}")
    pipe = _nllb_pipe(target)
    cache = {}

    def translate(value):
        if value not in cache:
            cache[value] = _nllb_sentence(pipe, value)
        return cache[value]

    translated = translate_readme(source, args.lang, translate)
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        f"<!-- README-TRANSLATION-SOURCE:{digest} -->\n" + translated,
        encoding="utf-8",
    )
    print(f"{args.lang}: translated {len(cache)} distinct phrases into {args.output}")


if __name__ == "__main__":
    main()
