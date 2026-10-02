import random
import unittest

from app.generator.weighted_random import choose_weighted, sample_weighted_unique


class TestWeighted(unittest.TestCase):
    def test_zero_weight_never_selected(self):
        rng = random.Random(0)
        for _ in range(50):
            self.assertEqual(choose_weighted(["a", "b"], [0, 1], rng), "b")

    def test_all_zero_falls_back_uniform(self):
        rng = random.Random(0)
        self.assertIn(choose_weighted(["a", "b"], [0, 0], rng), ["a", "b"])

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            choose_weighted(["a"], [-1])

    def test_no_duplicates(self):
        rng = random.Random(1)
        out = sample_weighted_unique(["a", "b", "c"], [5, 1, 1], 3, rng)
        self.assertEqual(len(set(out)), 3)

    def test_fewer_available(self):
        out = sample_weighted_unique(["a", "b"], [1, 1], 5, random.Random(0))
        self.assertEqual(len(out), 2)


if __name__ == "__main__":
    unittest.main()
