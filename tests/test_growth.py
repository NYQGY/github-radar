import datetime as dt
import sys
import pathlib
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from collect import growth

class GrowthTests(unittest.TestCase):
    def test_no_baseline_is_not_zero(self):
        self.assertIsNone(growth({}, dt.date(2026,11,6), 'x', 100))
    def test_exact_seven_days_and_negative(self):
        self.assertEqual(growth({'2026-10-30': {'x': 110}}, dt.date(2026,11,6), 'x', 100), -10)
    def test_wrong_day_not_used(self):
        self.assertIsNone(growth({'2026-10-29': {'x': 1}}, dt.date(2026,11,6), 'x', 100))
