import unittest

import _common  # noqa: F401
from ai4polymer_calc.schema import validate_result
from ai4polymer_calc.topics.bo_variants import calculate


class BoVariantsTests(unittest.TestCase):
    def test_batch_design_effect(self):
        for size, correlation in ((8, 0.5), (4, 0.2), (1, 0.9)):
            summary = calculate(batch_size=size, batch_correlation=correlation)["summary"]
            expected = size / (1.0 + (size - 1) * correlation)
            self.assertAlmostEqual(summary["batch_effective_size"], expected, places=9)
            self.assertAlmostEqual(summary["batch_information_retained"], expected / size, places=9)

    def test_small_correlation_keeps_information(self):
        summary = calculate(batch_size=8, batch_correlation=1e-9)["summary"]
        self.assertAlmostEqual(summary["batch_information_retained"], 1.0, places=6)

    def test_constrained_expectations(self):
        summary = calculate(batch_size=8, feasible_fraction=0.3)["summary"]
        self.assertAlmostEqual(summary["expected_feasible_per_batch"], 2.4, places=9)
        self.assertAlmostEqual(summary["probability_zero_feasible_batch"], 0.7 ** 8, places=9)
        self.assertAlmostEqual(summary["expected_experiments_per_feasible"], 1.0 / 0.3, places=9)

    def test_multifidelity_speedup(self):
        summary = calculate(fidelity_cost_ratio=0.05, screening_pass_fraction=0.2)["summary"]
        self.assertAlmostEqual(summary["ladder_cost_high_fidelity_equivalent"], 0.25, places=9)
        self.assertAlmostEqual(summary["fidelity_speedup"], 4.0, places=9)

    def test_cost_aware_budget_split(self):
        summary = calculate(budget=1000, expensive_cost_ratio=20.0)["summary"]
        self.assertAlmostEqual(summary["cheap_evaluations_in_budget"], 1000.0, places=9)
        self.assertAlmostEqual(summary["expensive_evaluations_in_budget"], 50.0, places=9)
        self.assertAlmostEqual(summary["cost_aware_information_threshold"], 0.05, places=9)

    def test_hit_expectations(self):
        summary = calculate(budget=1000, top_fraction=0.001)["summary"]
        self.assertAlmostEqual(summary["expected_hits_in_budget"], 1.0, places=9)
        self.assertAlmostEqual(summary["expected_experiments_per_hit"], 1000.0, places=9)

    def test_result_contract(self):
        validate_result(calculate())

    def test_rejects_invalid_inputs(self):
        for bad in ({"batch_correlation": 0.0}, {"feasible_fraction": 0.0},
                    {"top_fraction": 1.5}, {"budget": 0}, {"expensive_cost_ratio": 0.0}):
            with self.assertRaises(ValueError):
                calculate(**bad)


if __name__ == "__main__":
    unittest.main()
