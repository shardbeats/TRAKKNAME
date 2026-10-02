import sqlite3
import unittest

from app.database.repositories import history as h
from app.database.schema import create_schema
from app.database.seed import seed_database
from app.utils.text import normalize_title


class TestHistory(unittest.TestCase):
    def test_save_retrieve_delete_normalization(self):
        c = sqlite3.connect(":memory:")
        c.row_factory = sqlite3.Row
        create_schema(c)
        seed_database(c)
        h.save_history(c, "Midnight Pressure", 1, "en", ["Future"], "Adj + Noun")
        rows = h.list_history(c)
        self.assertEqual(len(rows), 1)
        self.assertEqual(normalize_title("MIDNIGHT  PRESSURE"), "midnight pressure")
        recent = h.recent_titles(c, 10)
        self.assertIn("midnight pressure", recent)
        h.delete_history(c, rows[0]["id"])
        self.assertEqual(len(h.list_history(c)), 0)


if __name__ == "__main__":
    unittest.main()
