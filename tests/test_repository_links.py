import tempfile
from pathlib import Path
import unittest

from scripts.check_repository import broken_links


class RepositoryLinksTest(unittest.TestCase):
    def test_empty_links_and_angle_destinations_with_spaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a b.md").write_text("# Guide")
            page = root / "README.md"
            page.write_text('[self]() [blank](  ) [guide](<a b.md> "Title")')
            self.assertEqual(broken_links(root, [page]), [])

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
