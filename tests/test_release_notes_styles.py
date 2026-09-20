from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "src" / "index.tsx"


class ReleaseNotesStyleTests(unittest.TestCase):
    def test_release_note_styles_are_scoped_to_the_plugin_container(self):
        source = SOURCE.read_text(encoding="utf-8")

        self.assertIn(".bazzite-buddy-release-notes * {", source)
        self.assertNotIn("\n                  * {", source)
        self.assertIn('className="bazzite-buddy-release-notes"', source)


if __name__ == "__main__":
    unittest.main()
