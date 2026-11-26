import unittest
from provider_nfce import parse_csv
class TestProvider(unittest.TestCase):
    def test_series(self):
        raw = "Ano de Mês,Mês de Mês,Mês,Máx. Mês,Soma de Emissores  (CNPJ)\n2026,setembro,01/09/2026,01/09/2026,2.668.491\n".encode()
        self.assertEqual(parse_csv(raw)["2026-09-01"]["valor"], 2668491)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            parse_csv(b"<html>error</html>")
