import unittest
from provider_authorized import number, period
class AuthorizationTest(unittest.TestCase):
    def test_counts(self):
        for value in ("3.420.345.714","3,420,345,714","3420345714"):
            self.assertEqual(number(value),3420345714)
        self.assertEqual(number("0"),0)
        for value in ("","null","1.2"):
            with self.assertRaises(ValueError): number(value)
    def test_period(self):
        self.assertEqual(period({"Month of Mês":"janeiro","Year of Mês":"2026"}),"2026-01-01")
