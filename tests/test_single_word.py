import random
import unittest

from tests.helpers import memdb
from app.generator.engine import generate_title




class TestSingleWord(unittest.TestCase):
    def test_english_single_token(self):
        c = memdb()
        for i in range(10):
            r = generate_title(c, "Trap", "en", 1, rng=random.Random(i), save=False, single_word=True)
            self.assertEqual(len(r.title.split()), 1, r.title)

    def test_spanish_single_token(self):
        c = memdb()
        for i in range(10):
            r = generate_title(c, "Trap", "es", 1, rng=random.Random(100 + i), save=False, single_word=True)
            self.assertEqual(len(r.title.split()), 1, r.title)

    def test_multiword_unaffected(self):
        c = memdb()
        r = generate_title(c, "Trap", "en", 1, rng=random.Random(7), save=False, single_word=False)
        self.assertTrue(r.title.strip())

    def test_survives_deleted_patterns(self):
        c = memdb()
        c.execute("DELETE FROM patterns WHERE template = 'NOUN'")
        r = generate_title(c, "Trap", "en", 1, rng=random.Random(3), save=False, single_word=True)
        self.assertEqual(len(r.title.split()), 1, r.title)


if __name__ == "__main__":
    unittest.main()
