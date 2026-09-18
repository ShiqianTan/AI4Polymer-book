import unittest

import _common  # noqa: F401
from ai4polymer_calc.topics.robust_ranking import calculate


class RobustRankingTests(unittest.TestCase):
    def test_equal_means_are_tied_under_mean_only(self):
        summary = calculate()["summary"]
        self.assertTrue(summary["mean_only_tie"])
        self.assertEqual(summary["mean_only_order"], ["C1", "C2"])

    def test_interval_criterion_prefers_narrow_candidate(self):
        summary = calculate()["summary"]
        self.assertEqual(summary["best_by_interval"], "C2")
        self.assertTrue(summary["ranking_flip"])

    def test_probability_in_window_orders_narrow_first(self):
        summary = calculate()["summary"]
        narrow = next(row for row in summary["candidates"] if row["candidate"] == "C2")
        wide = next(row for row in summary["candidates"] if row["candidate"] == "C1")
        self.assertGreater(narrow["probability_in_window"], wide["probability_in_window"])
        self.assertGreater(narrow["lower_bound"], wide["lower_bound"])

    def test_half_width_is_one_sigma(self):
        summary = calculate(means=(205.0,), half_widths=(1.0,), spec_low=204.0, spec_high=206.0)["summary"]
        self.assertAlmostEqual(summary["candidates"][0]["probability_in_window"], 0.6826894921370859, places=9)

    def test_rejects_bad_inputs(self):
        with self.assertRaises(ValueError):
            calculate(means=(1.0,), half_widths=(1.0, 2.0))
        with self.assertRaises(ValueError):
            calculate(spec_low=10.0, spec_high=5.0)


if __name__ == "__main__":
    unittest.main()
