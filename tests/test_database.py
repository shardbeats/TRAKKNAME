import sqlite3
import unittest

from app.database.schema import create_schema
from app.database.seed import seed_database


class TestDB(unittest.TestCase):
    def test_schema_and_seed_counts(self):
        c = sqlite3.connect(":memory:")
        c.row_factory = sqlite3.Row
        create_schema(c)
        seed_database(c)
        n_words = c.execute("SELECT COUNT(*) c FROM words").fetchone()["c"]
        self.assertGreaterEqual(n_words, 900)
        n_en_v = c.execute("SELECT COUNT(*) c FROM words WHERE language='en' AND part_of_speech='verb'").fetchone()["c"]
        n_en_a = c.execute("SELECT COUNT(*) c FROM words WHERE language='en' AND part_of_speech='adjective'").fetchone()["c"]
        n_en_n = c.execute("SELECT COUNT(*) c FROM words WHERE language='en' AND part_of_speech='noun'").fetchone()["c"]
        self.assertGreaterEqual(n_en_v, 100)
        self.assertGreaterEqual(n_en_a, 150)
        self.assertGreaterEqual(n_en_n, 200)
        # cascade
        gid = c.execute("SELECT id FROM genres WHERE name='Trap'").fetchone()["id"]
        self.assertTrue(gid)

    def test_cascade_delete_genre(self):
        c = sqlite3.connect(":memory:")
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys = ON;")
        create_schema(c)
        seed_database(c)
        gid = c.execute("SELECT id FROM genres WHERE name='Trap'").fetchone()["id"]
        before = c.execute("SELECT COUNT(*) c FROM artist_genres WHERE genre_id=?", (gid,)).fetchone()["c"]
        self.assertGreater(before, 0)
        c.execute("DELETE FROM genres WHERE id=?", (gid,))
        after = c.execute("SELECT COUNT(*) c FROM artist_genres WHERE genre_id=?", (gid,)).fetchone()["c"]
        self.assertEqual(after, 0)


if __name__ == "__main__":
    unittest.main()
