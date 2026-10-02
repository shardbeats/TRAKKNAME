import unittest

from app.generator.grammar import agree_adjective


class TestGrammar(unittest.TestCase):
    def test_masculine_kept(self):
        self.assertEqual(agree_adjective("oscuro", "masculine", "singular"), "oscuro")

    def test_feminine_o_to_a(self):
        self.assertEqual(agree_adjective("oscuro", "feminine", "singular"), "oscura")

    def test_no_gender_no_change(self):
        self.assertEqual(agree_adjective("neón", None, None), "neón")


if __name__ == "__main__":
    unittest.main()
