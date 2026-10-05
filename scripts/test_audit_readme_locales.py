#!/usr/bin/env python3
"""Regression checks for the README localization structure audit."""

import re
import unittest

from audit_readme_locales import (
    BOLD_COUNT, FACT, HTML_ALT, ISO_DATE, ROOT, SOURCE, body, check, check_document,
    fenced_blocks, landing_facts, outside_fences, sync_stats_facts,
)


class ReadmeLocaleAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.chinese_document = (ROOT / "i18n" / "zh" / "README.md").read_text(encoding="utf-8")
        cls.chinese = body(cls.chinese_document)

    def assert_reports(self, changed, expected):
        errors = check(self.source, changed, "zh")
        self.assertTrue(any(expected in item for item in errors), errors)

    def test_current_chinese_structure(self):
        self.assertEqual(check(self.source, self.chinese, "zh"), [])
        self.assertEqual(check_document(self.source, self.chinese_document, "zh"), [])

    def test_fence_closes_only_with_matching_character_and_length(self):
        text = "before\n````text\n```\n~~~\n```` trailing\n````\nafter"
        self.assertEqual(outside_fences(text), "before\nafter")
        self.assertEqual(fenced_blocks(text), ["````text\n```\n~~~\n```` trailing\n````"])

    def test_tilde_fence_ignores_backticks_and_short_closers(self):
        text = "before\n~~~~text\n```\n~~~\n~~~~\nafter"
        self.assertEqual(outside_fences(text), "before\nafter")
        self.assertEqual(fenced_blocks(text), ["~~~~text\n```\n~~~\n~~~~"])

    def test_canonical_english_link_is_required(self):
        changed = self.chinese_document.replace('href="../../README.md"', 'href="README.md"', 1)
        errors = check_document(self.source, changed, "zh")
        self.assertTrue(any("canonical English link" in item for item in errors), errors)

    def test_rtl_locale_note_is_removed_before_comparison(self):
        text = '<p align="center" dir="rtl"><sub>Localized note</sub></p>\n' + self.chinese
        self.assertEqual(body(text), self.chinese)

    def test_missing_relative_prefix(self):
        changed = self.chinese.replace('src="../../assets/banner.svg"', 'src="assets/banner.svg"', 1)
        self.assert_reports(changed, "lacks ../../ prefix")

    def test_missing_anchor(self):
        changed = self.chinese.replace('id="contents"', 'id="missing-contents"', 1)
        self.assert_reports(changed, "HTML IDs differ")

    def test_figure_identifier_is_not_transliterated(self):
        changed = self.chinese.replace("<sub>FIG_001 · A</sub>", "<sub>FIG_001 · А</sub>", 1)
        self.assert_reports(changed, "figure identifiers differ")

    def test_changed_lesson_link(self):
        changed = self.chinese.replace(
            "../../phases/00-setup-and-tooling/01-dev-environment/",
            "../../phases/00-setup-and-tooling/01-dev-environment-missing/",
            1,
        )
        self.assert_reports(changed, "lesson link destinations differ")

    def test_changed_code_block(self):
        changed = self.chinese.replace(
            "git clone https://github.com/rohitg00/ai-engineering-from-scratch.git",
            "git clone https://github.com/example/broken.git",
            1,
        )
        self.assert_reports(changed, "code block")

    def test_translated_directory_tree_description_is_allowed(self):
        changed = re.sub(r"(├── code/\s{2,})[^\n]+", r"\1可运行实现（校验）", self.chinese, count=1)
        self.assertEqual(check(self.source, changed, "zh"), [])

    def test_directory_tree_path_is_preserved(self):
        changed = self.chinese.replace("├── code/", "├── other/", 1)
        self.assert_reports(changed, "directory tree paths changed")

    def test_changed_stats_date(self):
        _, stats = landing_facts(self.chinese)
        date = ISO_DATE.search(stats).group()
        changed = self.chinese.replace(date, "1900-01-01", 1)
        self.assert_reports(changed, "stats numeric facts differ")

    def test_stats_sync_preserves_translated_copy(self):
        _, stats = landing_facts(self.chinese)
        reader_count = BOLD_COUNT.findall(stats)[0]
        date = ISO_DATE.search(stats).group()
        changed = self.chinese.replace(f"<b>{reader_count}</b>", "<b>1,000</b>", 1)
        changed = changed.replace(date, "1900-01-01", 1)
        self.assertEqual(sync_stats_facts(self.source, changed), self.chinese)

    def test_reader_and_page_view_roles_are_not_swapped(self):
        _, stats = landing_facts(self.chinese)
        readers, views = BOLD_COUNT.findall(stats)
        changed = self.chinese.replace(f"<b>{readers}</b>", "<b>TEMP</b>", 1)
        changed = changed.replace(f"<b>{views}</b>", f"<b>{readers}</b>", 1)
        changed = changed.replace("<b>TEMP</b>", f"<b>{views}</b>", 1)
        self.assert_reports(changed, "reader and page-view counts differ")

    def test_changed_hero_count(self):
        line = next(line for line in self.chinese.splitlines() if line.startswith("> ") and FACT.search(line))
        original = FACT.search(line).group()
        altered = line.replace(original, str(int(original.replace(",", "")) + 1), 1)
        changed = self.chinese.replace(line, altered, 1)
        self.assert_reports(changed, "hero numeric facts differ")

    def test_extra_table_cell(self):
        changed = self.chinese.replace("|---|---|---|", "|---|---|---|---|", 1)
        self.assert_reports(changed, "table row or cell counts differ")

    def test_accidental_list_marker(self):
        changed = self.chinese.replace("不确定从哪里开始？", "- 不确定从哪里开始？", 1)
        self.assert_reports(changed, "Markdown list item counts differ")

    def test_untranslated_english_paragraph(self):
        line = next(
            line for line in outside_fences(self.source).splitlines()
            if len(line) > 80 and len(line.split()) > 10 and not line.lstrip().startswith(("|", "<", ">", "-", "*"))
        )
        self.assert_reports(self.chinese + "\n" + line + "\n", "long English prose remains untranslated")

    def test_untranslated_image_description(self):
        description = next(
            match.group(1) for match in HTML_ALT.finditer(self.source)
            if len(match.group(1)) > 70 and len(match.group(1).split()) > 8
        )
        self.assert_reports(self.chinese + "\n<p>" + description + "</p>\n", "long English prose remains untranslated")

    def test_critical_inline_path_is_preserved(self):
        changed = self.chinese.replace("catalog.json", "catalog.txt")
        self.assert_reports(changed, "inline code formatting missing")

    def test_inline_code_markers_are_preserved(self):
        changed = self.chinese.replace("`start-learning`", "start-learning")
        self.assert_reports(changed, "inline code formatting missing")

    def test_course_route_range_is_preserved(self):
        changed = self.chinese.replace("第 47–54 课", "第 47 课", 1)
        self.assert_reports(changed, "course range 47")


if __name__ == "__main__":
    unittest.main()
