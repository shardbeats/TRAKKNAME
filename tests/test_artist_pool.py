import random
import sqlite3
import unittest

from tests.helpers import memdb
from app.database.schema import migrate_database
from app.database.seed import ensure_artist_meta
from app.generator.engine import generate_title, select_artists




def genre_id(conn, name):
    return conn.execute("SELECT id FROM genres WHERE name=?", (name,)).fetchone()["id"]


class TestArtistPool(unittest.TestCase):
    def test_spanish_pool_language(self):
        c = memdb()
        gid = genre_id(c, "Reggaeton")
        names = select_artists(c, gid, 5, random.Random(0), "es")
        self.assertTrue(names)
        for n in names:
            r = c.execute("SELECT language FROM artists WHERE name=?", (n,)).fetchone()
            self.assertEqual(r["language"], "es", n)

    def test_english_pool(self):
        c = memdb()
        gid = genre_id(c, "Reggaeton")
        names = select_artists(c, gid, 5, random.Random(0), "en")
        for n in names:
            r = c.execute("SELECT language FROM artists WHERE name=?", (n,)).fetchone()
            self.assertNotEqual(r["language"], "es", n)

    def test_legacy_latam_maps_to_spanish(self):
        c = memdb()
        gid = genre_id(c, "Reggaeton")
        a = select_artists(c, gid, 5, random.Random(0), "latam")
        b = select_artists(c, gid, 5, random.Random(0), "es")
        self.assertEqual(a, b)
        r = generate_title(c, "Reggaeton", "es", 2, rng=random.Random(3), save=True, artist_pool="latam")
        row = c.execute("SELECT artist_pool FROM generation_history ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(row["artist_pool"], "es")
        self.assertTrue(r.artists)

    def test_spanish_pool(self):
        c = memdb()
        gid = genre_id(c, "Latin Trap")
        names = select_artists(c, gid, 5, random.Random(1), "es")
        self.assertTrue(names)
        for n in names:
            r = c.execute("SELECT language FROM artists WHERE name=?", (n,)).fetchone()
            self.assertEqual(r["language"], "es", n)

    def test_empty_pool_graceful(self):
        c = memdb()
        gid = genre_id(c, "Phonk")
        self.assertEqual(select_artists(c, gid, 3, random.Random(0), "es"), [])
        r = generate_title(c, "Phonk", "en", 2, rng=random.Random(0), save=False, artist_pool="es")
        self.assertEqual(r.artists, [])
        self.assertTrue(r.title)

    def test_generate_spanish_reggaeton(self):
        c = memdb()
        r = generate_title(c, "Reggaeton", "es", 2, rng=random.Random(3), save=True, artist_pool="es")
        self.assertTrue(r.artists)
        row = c.execute("SELECT artist_pool FROM generation_history ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(row["artist_pool"], "es")

    def test_meta_backfill(self):
        c = memdb()
        c.execute("UPDATE artists SET region=NULL, language=NULL")
        n = ensure_artist_meta(c)
        self.assertGreater(n, 0)
        r = c.execute("SELECT region, language FROM artists WHERE name='Duki'").fetchone()
        self.assertEqual((r["region"], r["language"]), ("LATAM", "es"))
        r = c.execute("SELECT region, language FROM artists WHERE name='Bad Bunny'").fetchone()
        self.assertEqual((r["region"], r["language"]), ("Caribbean", "es"))
        # user edit preserved
        c.execute("UPDATE artists SET region='US' WHERE name='Duki'")
        ensure_artist_meta(c)
        r = c.execute("SELECT region FROM artists WHERE name='Duki'").fetchone()
        self.assertEqual(r["region"], "US")

    def test_migrate_adds_artist_columns(self):
        c = sqlite3.connect(":memory:")
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys = ON;")
        c.executescript("CREATE TABLE artists(id INTEGER PRIMARY KEY, name TEXT UNIQUE, enabled INTEGER DEFAULT 1);"
                        "CREATE TABLE generation_history(id INTEGER PRIMARY KEY, title TEXT, created_at TEXT);")
        migrate_database(c)
        acols = {r["name"] for r in c.execute("PRAGMA table_info(artists)")}
        self.assertIn("region", acols)
        self.assertIn("language", acols)
        hcols = {r["name"] for r in c.execute("PRAGMA table_info(generation_history)")}
        self.assertIn("artist_pool", hcols)

    def test_wave3_present(self):
        c = memdb()
        names = {r["name"] for r in c.execute("SELECT name FROM artists")}
        for expected in ("Duki", "Bizarrap", "Karol G", "Eladio Carrión", "Morad",
                         "Santa Fe Klan", "Snow Tha Product", "Nicki Nicole"):
            self.assertIn(expected, names)

    def test_wave5_fame(self):
        c = memdb()
        names = {r["name"] for r in c.execute("SELECT name FROM artists")}
        for expected in ("Eminem", "Beyoncé", "Taylor Swift", "Daddy Yankee",
                         "Sean Paul", "Skrillex", "Amy Winehouse", "Ivy Queen",
                         "A$AP Rocky", "Ice Spice", "Tomppabeats", "Hensonn",
                         "Lauryn Hill", "Outkast", "Bruno Mars", "Porta",
                         "La Mala Rodríguez"):
            self.assertIn(expected, names)
        total = c.execute("SELECT COUNT(*) c FROM artists").fetchone()["c"]
        self.assertGreaterEqual(total, 300)
        c = memdb()
        names = {r["name"] for r in c.execute("SELECT name FROM artists")}
        for expected in ("Nach", "Canserbero", "Vico C", "Tego Calderón",
                         "Trueno", "Ca7riel y Paco Amoroso", "Kali Uchis",
                         "Cimafunk", "Lomiiel", "C. Tangana"):
            self.assertIn(expected, names)
        gid = genre_id(c, "Boom Bap")
        got = select_artists(c, gid, 5, random.Random(0), "es")
        self.assertTrue(got, "Boom Bap es pool must not be empty")
        gid = genre_id(c, "Hip Hop")
        got = select_artists(c, gid, 5, random.Random(0), "es")
        self.assertTrue(got, "Hip Hop es pool must not be empty")


if __name__ == "__main__":
    unittest.main()
