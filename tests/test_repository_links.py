import tempfile
from pathlib import Path
import unittest

from scripts.check_repository import broken_links


class RepositoryLinksTest(unittest.TestCase):
    def test_hidden_html_comments_do_not_create_links_or_definitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "README.md"
            page.write_text('<!-- [hidden](missing.md)\n[hidden-ref]: absent.md\n-->\n'
                            '[hidden-ref] [visible](real-missing.md)\n')
            errors = broken_links(root, [page])
            self.assertEqual(len(errors), 1)
            self.assertIn("real-missing.md", errors[0])

    def test_literal_links_in_inline_code_and_fences_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "README.md"
            page.write_text('`[inline](missing.md)`\n'
                            '``[inline with ` character](missing.md)``\n'
                            '~~~md\n[tilde](missing.md)\n~~~\n'
                            '````md\n```\n[nested](missing.md)\n```\n````\n'
                            '[real](absent.md)\n')
            errors = broken_links(root, [page])
            self.assertEqual(len(errors), 1)
            self.assertIn("absent.md", errors[0])

    def test_code_markers_inside_a_paragraph_do_not_hide_real_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "README.md"
            page.write_text('Text ~~~ followed by [real](missing.md)\n')
            self.assertEqual(len(broken_links(root, [page])), 1)

    def test_backslash_escaped_links_remain_literal_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "README.md"
            page.write_text(r"\[literal](missing.md) \![image](missing.png) [real](absent.md)")
            errors = broken_links(root, [page])
            self.assertEqual(len(errors), 1)
            self.assertIn("absent.md", errors[0])
    def test_empty_links_and_angle_destinations_with_spaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a b.md").write_text("# Guide")
            page = root / "README.md"
            page.write_text('[self]() [blank](  ) [guide](<a b.md> "Title")')
            self.assertEqual(broken_links(root, [page]), [])

    def test_first_reference_definition_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "README.md"
            page.write_text("[first][Guide] and [second][Other]\n"
                            "[Guide]: missing.md\n[guide]: README.md\n"
                            "[Other]: README.md\n[OTHER]: unused.md\n")
            self.assertEqual(broken_links(root, [page]), ["README.md: broken local link missing.md"])

    def test_reference_links_are_checked_when_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guide.md").write_text("# Guide")
            page = root / "README.md"
            page.write_text('[ok][Guide] [missing][lost] ![image][photo] [collapsed][]\n'
                            '[guide]: guide.md "Title"\n[lost]: absent.md\n'
                            '[photo]: missing.png\n[collapsed]: missing.md\n'
                            '[unused]: unused.md\n')
            errors = broken_links(root, [page])
            self.assertEqual(len(errors), 3)
            for target in ("absent.md", "missing.png", "missing.md"):
                self.assertTrue(any(target in error for error in errors))

    def test_missing_and_escaping_links_fail_but_urls_and_anchors_are_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "README.md"
            (root / "guide.md").write_text("# Guide")
            page.write_text("[ok](guide.md#section) [url](https://example.com) "
                            "[anchor](#here) [missing](absent.md) [escape](../outside.md)")
            errors = broken_links(root, [page])
            self.assertEqual(len(errors), 2)
            self.assertTrue(any("absent.md" in error for error in errors))
            self.assertTrue(any("outside.md" in error for error in errors))

    def test_nested_links_spaces_and_code_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "a b.md").write_text("# Guide")
            page = root / "docs" / "guide.md"
            page.write_text("[root](/a%20b.md) [relative](../a%20b.md)\n"
                            "```md\n[example](missing.md)\n```\n")
            self.assertEqual(broken_links(root, [page]), [])


if __name__ == "__main__":
    unittest.main()
