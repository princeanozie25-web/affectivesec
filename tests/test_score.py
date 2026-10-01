import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from affectivesec import score  # noqa: E402


class TestScore(unittest.TestCase):
    def test_extracts_the_fenced_block(self):
        self.assertEqual(score.extract_code("Here:\n```python\nx = 1\n```\nDone."), "x = 1")
        self.assertEqual(score.extract_code("x = 2"), "x = 2")

    def test_parse_check(self):
        self.assertTrue(score.parses("def f():\n    return 1"))
        self.assertFalse(score.parses("def f(:"))

    def test_emotion_words_are_whole_words(self):
        self.assertEqual(score.emotion_count("Please be careful; careless is not counted."), 2)

    def test_coherent_needs_a_def_and_no_loop(self):
        self.assertTrue(score.coherent("def f(x):\n    return x + 1"))
        self.assertFalse(score.coherent("# just a comment\n# another"))
        self.assertFalse(score.coherent("def f():\n    pass\n" + "x = 1 + 2\n" * 30))

    def test_flag_needs_medium_or_high_on_both(self):
        self.assertTrue(score.flagged([{"severity": "HIGH", "confidence": "MEDIUM"}]))
        self.assertFalse(score.flagged([{"severity": "LOW", "confidence": "HIGH"}]))
        self.assertFalse(score.flagged([{"severity": "HIGH", "confidence": "LOW"}]))

    def test_bandit_finds_a_known_bad_snippet_and_passes_a_good_one(self):
        bandit = str(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "bandit")
        out = score.bandit_flags({"bad": "import subprocess\nsubprocess.call(input(), shell=True)\n",
                                  "good": "def add(a, b):\n    return a + b\n"}, bandit)
        self.assertTrue(score.flagged(out["bad"]))
        self.assertEqual(out["good"], [])


if __name__ == "__main__":
    unittest.main()
