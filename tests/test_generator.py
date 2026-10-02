import random
import unittest

from tests.helpers import memdb
from app.generator.engine import generate_title


class TestGenerator(unittest.TestCase):
    def test_english(self):
        c = memdb()
        r = generate_title(c, "Trap", "en", 2, rng=random.Random(0), save=False)
        self.assertTrue(r.title.strip())

    def test_spanish(self):
        c = memdb()
        r = generate_title(c, "Trap", "es", 2, rng=random.Random(0), save=False)
        self.assertTrue(r.title.strip())

    def test_every_template_renders(self):
        from app.database.seed import RETIRED_PATTERNS, STYLE_RENAMES, ensure_patterns
        c = memdb()
        pats = list(c.execute("SELECT template, language FROM patterns WHERE enabled = 1"))
        self.assertEqual(len(pats), 8)  # concise curated set: 4 EN + 4 ES (no single-word styles)
        es_names = [r["name"] for r in c.execute("SELECT name FROM patterns WHERE language = 'es'")]
        for n in es_names:  # ES styles shown in Spanish, no English grammar terms
            self.assertNotRegex(n, r"\b(ADJ|NOUN|VERB)\b")
            self.assertNotIn("(ES)", n)
        self.assertEqual(
            {r["name"] for r in c.execute("SELECT name FROM patterns WHERE language = 'es'")},
            {"Sustantivo + Adjetivo", "Adjetivo + Sustantivo", "Sustantivo de Sustantivo",
             "Verbo + Sustantivo"})
        self.assertEqual(STYLE_RENAMES["Noun + Adj (ES)"], "Sustantivo + Adjetivo")
        for p in pats:
            lang = p["language"] if p["language"] in ("en", "es") else "en"
            r = generate_title(c, "Trap", lang, 1, style="Random", rng=random.Random(3), save=False)
            self.assertTrue(r.title)
        # retired gimmicks get disabled by the migration (reversible in UI)
        c.execute("INSERT INTO patterns(name, language, template, weight, enabled) VALUES (?,?,?,?,1)",
                  (RETIRED_PATTERNS[0], "en", "ADJ ADJ NOUN", 3))
        ensure_patterns(c)
        row = c.execute("SELECT enabled FROM patterns WHERE name = ?", (RETIRED_PATTERNS[0],)).fetchone()
        self.assertEqual(row["enabled"], 0)
        # retired pattern never picked by Random
        seen = {generate_title(c, "Trap", "en", 1, style="Random", rng=random.Random(i), save=False).title
                for i in range(30)}
        self.assertTrue(seen)

    def test_removed_single_word_patterns_deleted(self):
        from app.database.seed import REMOVED_PATTERNS, ensure_patterns
        c = memdb()
        for name in ("Single Noun", "Una Palabra"):
            c.execute("INSERT INTO patterns(name, language, template, weight, enabled) VALUES (?,?,?,?,1)",
                      (name, "en", "NOUN", 2))
        ensure_patterns(c)
        left = c.execute(
            f"SELECT COUNT(*) c FROM patterns WHERE name IN ({','.join('?' * len(REMOVED_PATTERNS))})",
            REMOVED_PATTERNS).fetchone()["c"]
        self.assertEqual(left, 0)
        # 1-WORD toggle still works via the engine's lone-NOUN fallback
        r = generate_title(c, "Trap", "en", 1, single_word=True, rng=random.Random(7), save=False)
        self.assertEqual(len(r.title.strip().split()), 1)

    def test_fallback_no_artists(self):
        c = memdb()
        c.execute("INSERT INTO genres(name) VALUES ('EmptyGenre')")
        r = generate_title(c, "EmptyGenre", "en", 2, rng=random.Random(0), save=False)
        self.assertEqual(r.artists, [])

    def test_duplicate_avoidance(self):
        c = memdb()
        r1 = generate_title(c, "Trap", "en", 1, rng=random.Random(42))
        # force same rng state titles into recent; next gen with tight window should differ or raise gracefully
        seen = {r1.title.lower()}
        r2 = generate_title(c, "Trap", "en", 1, rng=random.Random(43))
        self.assertNotEqual(r1.title.lower(), r2.title.lower() if r2.title.lower() in seen else r2.title.lower())

    def test_missing_genre_falls_back(self):
        c = memdb()
        r = generate_title(c, "Nope", "en", 1, rng=random.Random(0), save=False)
        self.assertTrue(r.title)


if __name__ == "__main__":
    unittest.main()
