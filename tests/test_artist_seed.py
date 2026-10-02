import unittest

from tests.helpers import memdb
from app.database.seed import ensure_artists




class TestArtistSeed(unittest.TestCase):
    def test_wave2_present(self):
        c = memdb()
        names = {r["name"] for r in c.execute("SELECT name FROM artists")}
        for expected in ("Yeat", "Doechii", "Leon Thomas", "Asake", "Tyla",
                         "Cash Cobain", "Roc Marciano", "Black Coffee", "4batz",
                         "Young Miko", "Charli XCX", "JPEGMAFIA"):
            self.assertIn(expected, names)

    def test_every_genre_has_artists(self):
        c = memdb()
        rows = c.execute(
            "SELECT g.name, COUNT(*) n FROM artist_genres ag "
            "JOIN genres g ON g.id=ag.genre_id GROUP BY g.name").fetchall()
        self.assertEqual(len(rows), 20)
        for r in rows:
            self.assertGreaterEqual(r["n"], 3, r["name"])

    def test_ensure_artists_preserves_user_weights(self):
        c = memdb()
        aid = c.execute("SELECT id FROM artists WHERE name='Future'").fetchone()["id"]
        gid = c.execute("SELECT id FROM genres WHERE name='Trap'").fetchone()["id"]
        c.execute("UPDATE artist_genres SET weight=1.0 WHERE artist_id=? AND genre_id=?", (aid, gid))
        c.execute("DELETE FROM artists WHERE name='Yeat'")
        added = ensure_artists(c)
        self.assertGreaterEqual(added, 1)
        w = c.execute("SELECT weight FROM artist_genres WHERE artist_id=? AND genre_id=?", (aid, gid)).fetchone()["weight"]
        self.assertEqual(w, 1.0)  # user edit untouched
        self.assertIsNotNone(c.execute("SELECT id FROM artists WHERE name='Yeat'").fetchone())
        self.assertEqual(ensure_artists(c), 0)  # idempotent


if __name__ == "__main__":
    unittest.main()
