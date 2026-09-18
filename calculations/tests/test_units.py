import math
import unittest

import _common  # noqa: F401
from ai4polymer_calc.units import ceil_div, fraction, log10_big_int, positive_int, positive_number


class PositiveIntTests(unittest.TestCase):
    def test_accepts_and_rejects(self):
        self.assertEqual(positive_int(3, "x"), 3)
        self.assertEqual(positive_int(0, "x", allow_zero=True), 0)
        for bad in (0, -1, True, 1.0, "3"):
            with self.assertRaises(ValueError):
                positive_int(bad, "x")

    def test_zero_only_with_flag(self):
        with self.assertRaises(ValueError):
            positive_int(0, "x")


class NumberTests(unittest.TestCase):
    def test_positive_number(self):
        self.assertEqual(positive_number(2.5, "x"), 2.5)
        for bad in (0, -1, float("inf"), float("nan"), True):
            with self.assertRaises(ValueError):
                positive_number(bad, "x")

    def test_fraction(self):
        self.assertEqual(fraction(0.5, "p"), 0.5)
        self.assertEqual(fraction(1.0, "p"), 1.0)
        for bad in (0, 1.5, -0.1, float("nan")):
            with self.assertRaises(ValueError):
                fraction(bad, "p")


class ArithmeticTests(unittest.TestCase):
    def test_ceil_div(self):
        self.assertEqual(ceil_div(10, 3), 4)
        self.assertEqual(ceil_div(9, 3), 3)
        self.assertEqual(ceil_div(0, 3), 0)

    def test_log10_big_int(self):
        self.assertAlmostEqual(log10_big_int(1000), 3.0)
        self.assertAlmostEqual(log10_big_int(10 ** 100), 100.0)
        self.assertAlmostEqual(log10_big_int(2 ** 100), 100 * math.log10(2), places=12)
        self.assertAlmostEqual(log10_big_int(10 ** 500), 500.0, places=9)


if __name__ == "__main__":
    unittest.main()
