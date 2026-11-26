import unittest
from monitor import number, parse, aggregate
class TestMonitor(unittest.TestCase):
    def test_number(self):
        self.assertEqual(number("63,405 bilhões"),63405000000)
        self.assertEqual(number("2,93 milhões"),2930000)
    def test_parse(self):
        p="ctl00_ContentPlaceHolder1_lbl"
        values={"ValorNFeAutorizada":"63,405 bilhões","DataNFeAutorizada":"26/11/2026","ValorEmissores":"2,93 milhões","DataEmissores":"22/11/2026"}
        html="".join(f'<span id="{p}{k}">{v}</span>' for k,v in values.items())
        self.assertEqual(parse(html)["emissores"]["data"],"2026-11-22")
    def test_missing(self):
        self.assertIsNone(aggregate([{"data":"2026-11-26","variacao":None}],"daily")[0]["variacao"])
