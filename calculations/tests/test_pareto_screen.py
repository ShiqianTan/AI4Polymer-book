import unittest

import _common  # noqa: F401
from ai4polymer_calc.topics.pareto_screen import calculate


class ParetoScreenTests(unittest.TestCase):
    def test_block_space_is_exact_combinatorial_count(self):
        summary = calculate(monomers=10, chain_length=100)["summary"]
        self.assertEqual(summary["enumerated_candidates"], 10 * 9 * 99)
        self.assertEqual(summary["realizations_per_point"],
                         summary["enumerated_candidates"] // summary["distinct_objective_points"])

    def test_pareto_front_is_a_subset_and_covers_weighted_sum(self):
        summary = calculate()["summary"]
        self.assertLess(summary["pareto_front_points"], summary["distinct_objective_points"])
        self.assertLessEqual(summary["weighted_sum_points"], summary["pareto_front_points"])
        self.assertLessEqual(summary["epsilon_constraint_points"], summary["pareto_front_points"])
        self.assertGreater(summary["weighted_sum_coverage"], 0.0)
        self.assertGreater(summary["hypervolume"], 0.0)

    def test_weighted_sum_misses_non_convex_region(self):
        summary = calculate(weight_steps=101)["summary"]
        self.assertLess(summary["weighted_sum_coverage"], 1.0)

    def test_small_space_matches_brute_force(self):
        summary = calculate(monomers=3, chain_length=5)["summary"]
        self.assertEqual(summary["enumerated_candidates"], 3 * 2 * 4)
        self.assertEqual(summary["distinct_objective_points"], 4)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            calculate(monomers=0)
        with self.assertRaises(ValueError):
            calculate(reference=(0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
