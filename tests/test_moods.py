import json
import random
import sqlite3
import unittest

from tests.helpers import memdb
from app.database.repositories import moods as moods_repo
from app.database.repositories import words as words_repo
from app.database.schema import migrate_database
from app.database.seed import seed_moods
from app.generator.engine import generate_title




class TestMoods(unittest.TestCase):
    def test_seed_has_20_moods(self):
        c = memdb()
        rows = moods_repo.list_moods(c, only_enabled=True)
        self.assertEqual(len(rows), 20)
        names = {r["name"] for r in rows}
        for expected in ("Dark", "Sad", "Aggressive", "Bouncy", "Mysterious", "Gritty"):
            self.assertIn(expected, names)

    def test_seed_moods_idempotent(self):
        c = memdb()
        seed_moods(c)
        seed_moods(c)
        self.assertEqual(len(moods_repo.list_moods(c)), 20)

    def test_mood_boosts_vibe_words(self):
        c = memdb()
        grow = c.execute("SELECT id FROM genres WHERE name='Trap'").fetchone()
        dark = moods_repo.mood_ids_for_names(c, ["Dark"])
        boost = moods_repo.mood_word_weights(c, dark)
        self.assertTrue(boost)
        plain = {w: eff for w, _, _, eff in words_repo.pool_words(
            c, "en", "noun", grow["id"], [], 0.7, 0.2, 0.1, {"noun"}, None)}
        boosted = {w: eff for w, _, _, eff in words_repo.pool_words(
            c, "en", "noun", grow["id"], [], 0.7, 0.2, 0.1, {"noun"}, None, boost, 1.0)}
        linked = [w for w in boosted if w in {r["word"] for r in
                  c.execute("SELECT w.word FROM words w JOIN word_moods wm ON wm.word_id=w.id WHERE wm.mood_id=?", (dark[0],))}]
        self.assertTrue(linked)
        for w in linked[:10]:
            self.assertGreater(boosted[w], plain[w])

    def test_generate_with_mood(self):
        c = memdb()
        r = generate_title(c, "Trap", "en", 1, rng=random.Random(5), save=True, moods=["Dark"])
        self.assertEqual(r.moods, ["Dark"])
        row = c.execute("SELECT moods_json FROM generation_history ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(json.loads(row["moods_json"]), ["Dark"])

    def test_unknown_mood_ignored(self):
        c = memdb()
        r = generate_title(c, "Trap", "en", 1, rng=random.Random(5), save=False, moods=["Nope"])
        self.assertEqual(r.moods, [])

    def test_migrate_old_db(self):
        c = sqlite3.connect(":memory:")
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys = ON;")
        c.executescript("CREATE TABLE genres(id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
                        "CREATE TABLE generation_history(id INTEGER PRIMARY KEY, title TEXT, created_at TEXT);")
        migrate_database(c)  # must not raise; adds moods tables + column
        cols = {r["name"] for r in c.execute("PRAGMA table_info(generation_history)")}
        self.assertIn("moods_json", cols)
        seed_moods(c)
        self.assertEqual(len(moods_repo.list_moods(c)), 20)


if __name__ == "__main__":
    unittest.main()
