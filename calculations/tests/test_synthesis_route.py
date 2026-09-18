import unittest

import _common  # noqa: F401
from ai4polymer_calc.topics.synthesis_route import calculate


class SynthesisRouteTests(unittest.TestCase):
    def test_exhaustive_search_grows_as_b_to_the_d(self):
        summary = calculate(branching=50, depth=5)["summary"]
        self.assertEqual(summary["exhaustive_nodes"], 50 ** 5)

    def test_beam_search_keeps_only_the_top_k(self):
        summary = calculate(branching=50, depth=5, beam=10)["summary"]
        self.assertEqual(summary["beam_nodes"], 50 + 4 * 10 * 50)
        self.assertGreater(summary["pruning_ratio"], 1.0)

    def test_route_yield_decays_with_steps(self):
        summary = calculate(step_yield=0.8, depth=5)["summary"]
        self.assertAlmostEqual(summary["route_yield"], 0.8 ** 5)
        curve = summary["yield_curve"]
        self.assertAlmostEqual(curve[0]["total_yield"], 0.8)
        self.assertLess(curve[-1]["total_yield"], curve[0]["total_yield"])

    def test_target_yield_sets_the_step_limit(self):
        self.assertEqual(calculate(step_yield=0.8, target_yield=0.3)["summary"]["max_steps_at_target"], 5)

    def test_funnel_survivors_are_the_product_of_pass_rates(self):
        summary = calculate(initial_candidates=8910, feasibility=0.6,
                            route_length_pass=0.6, yield_pass=0.5, cost_pass=0.4)["summary"]
        expected = 8910 * 0.6 * 0.6 * 0.5 * 0.4
        self.assertAlmostEqual(summary["final_survivors"], expected)
        self.assertAlmostEqual(summary["overall_pass"], 0.6 * 0.6 * 0.5 * 0.4)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            calculate(branching=0)
        with self.assertRaises(ValueError):
            calculate(step_yield=1.5)
        with self.assertRaises(ValueError):
            calculate(target_yield=0.0)


if __name__ == "__main__":
    unittest.main()
