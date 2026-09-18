import math
import unittest

import _common  # noqa: F401
from ai4polymer_calc.topics.learning_curve import calculate


class LearningCurveTests(unittest.TestCase):
    def test_inverse_recovers_target(self):
        result = calculate(mae_inf=0.05, a=1.0, alpha=0.5, target_mae=0.2)
        summary = result["summary"]
        self.assertAlmostEqual(summary["required_n"], (1.0 / 0.15) ** 2, places=9)
        self.assertAlmostEqual(0.05 + 1.0 * summary["required_n"] ** -0.5, 0.2, places=9)

    def test_required_experiments_is_ceiling(self):
        summary = calculate(mae_inf=0.05, a=1.0, alpha=0.5, target_mae=0.2)["summary"]
        self.assertEqual(summary["required_n_experiments"], math.ceil(summary["required_n"]))
        self.assertEqual(summary["required_n_experiments"], 45)

    def test_marginal_data_to_stricter_target(self):
        summary = calculate(mae_inf=0.05, a=1.0, alpha=0.5, target_mae=0.2, strict_mae=0.1)["summary"]
        self.assertEqual(summary["strict_target_required_n_experiments"], 400)
        self.assertEqual(summary["marginal_experiments_to_strict_target"],
                         summary["strict_target_required_n_experiments"] - summary["required_n_experiments"])
        self.assertEqual(summary["marginal_experiments_to_strict_target"], 355)

    def test_unreachable_target_returns_null(self):
        summary = calculate(mae_inf=0.2, a=1.0, alpha=0.5, target_mae=0.15, strict_mae=0.1)["summary"]
        self.assertIsNone(summary["required_n"])
        self.assertIsNone(summary["required_n_experiments"])
        self.assertFalse(summary["target_achievable_within_n_max"])

    def test_curve_is_monotone_decreasing(self):
        curve = calculate()["summary"]["curve"]
        maes = [row["mae"] for row in curve]
        self.assertEqual(maes, sorted(maes, reverse=True))

    def test_rejects_non_stricter_target(self):
        with self.assertRaises(ValueError):
            calculate(target_mae=0.2, strict_mae=0.25)


if __name__ == "__main__":
    unittest.main()
