import unittest

from app.database.seed import ensure_no_placeholders
from tests.helpers import memdb


class TestPlaceholderCleanup(unittest.TestCase):
    def test_removes_digit_words(self):
        c = memdb()
        c.execute("INSERT INTO words(word, language, part_of_speech) VALUES ('verso999', 'es', 'adjective')")
        c.execute("INSERT INTO words(word, language, part_of_speech) VALUES ('sombra42', 'es', 'noun')")
        n = ensure_no_placeholders(c)
        self.assertEqual(n, 2)
        left = c.execute("SELECT COUNT(*) c FROM words WHERE word GLOB '*[0-9]*'").fetchone()["c"]
        self.assertEqual(left, 0)
        # legit words untouched
        self.assertGreater(c.execute("SELECT COUNT(*) c FROM words").fetchone()["c"], 900)

    def test_idempotent(self):
        c = memdb()
        self.assertEqual(ensure_no_placeholders(c), 0)


if __name__ == "__main__":
    unittest.main()
