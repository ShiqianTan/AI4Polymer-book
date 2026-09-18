import unittest

import _common  # noqa: F401
from ai4polymer_calc.topics.closed_loop import calculate


class ClosedLoopTests(unittest.TestCase):
    def test_random_search_is_geometric_expectation(self):
        for hit_fraction in (1.0, 0.5, 0.1, 0.001):
            summary = calculate(top_fraction=hit_fraction)["summary"]
            self.assertAlmostEqual(summary["random_experiments_expected"], 1.0 / hit_fraction, places=9)
            self.assertAlmostEqual(summary["expected_failures_before_success"],
                                   (1.0 - hit_fraction) / hit_fraction, places=9)

    def test_geometric_series_matches_closed_form(self):
        hit_fraction = 0.01
        series = sum(step * (1 - hit_fraction) ** (step - 1) * hit_fraction for step in range(1, 200000))
        self.assertAlmostEqual(series, 1.0 / hit_fraction, places=2)

    def test_bo_and_calendar_days(self):
        summary = calculate(space_size=1_000_000, top_fraction=0.001, bo_speedup=5.0,
                            experiments_per_day=50)["summary"]
        self.assertAlmostEqual(summary["bo_experiments_expected"], 1000.0 / 5.0)
        self.assertAlmostEqual(summary["calendar_days"], 200.0 / 50.0)
        self.assertAlmostEqual(summary["random_calendar_days"], 1000.0 / 50.0)
        self.assertEqual(summary["speedup_vs_random"], 5.0)

    def test_expected_hits_in_space(self):
        summary = calculate(space_size=1_000_000, top_fraction=0.001)["summary"]
        self.assertAlmostEqual(summary["expected_hits_in_space"], 1000.0)

    def test_rejects_invalid_fraction(self):
        for bad in (0.0, 1.5, -0.1):
            with self.assertRaises(ValueError):
                calculate(top_fraction=bad)


if __name__ == "__main__":
    unittest.main()
