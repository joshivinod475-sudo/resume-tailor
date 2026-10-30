import tempfile
import unittest
from pathlib import Path

import yaml
from docx import Document

from tailor import keywords
from tailor.claude import integrity_check
from tailor.models import Resume
from tailor.render import to_docx

RESUME = Resume.model_validate(yaml.safe_load(Path("resume.yaml").read_text(encoding="utf-8")))


class KeywordTest(unittest.TestCase):
    def test_finds_whole_words_only(self):
        self.assertEqual(keywords.job_keywords("We use SQL daily, not MySQLite"), ["sql"])

    def test_go_to_market_does_not_match_partial_terms(self):
        self.assertIn("go-to-market", keywords.job_keywords("Own our go-to-market motion"))

    def test_coverage(self):
        pct, matched, missing = keywords.coverage(RESUME, ["python", "kubernetes"])
        self.assertEqual((pct, matched, missing), (50, ["python"], ["kubernetes"]))


class IntegrityTest(unittest.TestCase):
    def test_unchanged_resume_passes(self):
        self.assertEqual(integrity_check(RESUME, RESUME.model_copy(deep=True)), [])

    def test_changed_job_title_is_caught(self):
        edited = RESUME.model_copy(deep=True)
        edited.experience[0].title = "Head of Growth"
        self.assertIn("job titles, companies or dates were changed", integrity_check(RESUME, edited))

    def test_invented_project_is_caught(self):
        edited = RESUME.model_copy(deep=True)
        edited.projects[0].name = "Made-up project"
        self.assertTrue(integrity_check(RESUME, edited))


class RenderTest(unittest.TestCase):
    def test_docx_contains_name_and_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = to_docx(RESUME, Path(tmp) / "r.docx")
            text = "\n".join(p.text for p in Document(path).paragraphs)
        for expected in ("Alex Morgan", "EXPERIENCE", "EDUCATION", "Brightline Digital"):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
