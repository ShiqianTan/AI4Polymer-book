import unittest

import _common  # noqa: F401
from ai4polymer_calc.topics.gnn_forward import calculate


class GnnForwardTests(unittest.TestCase):
    def test_flop_conservation(self):
        summary = calculate()["summary"]
        self.assertEqual(summary["total_flops"],
                         summary["message_passing_flops"] + summary["readout_flops"] + summary["mlp_head_flops"])

    def test_terms_sum_to_total(self):
        summary = calculate()["summary"]
        terms = summary["terms"]
        self.assertEqual(sum(term["flops"] for term in terms), summary["total_flops"])

    def test_readout_choice_changes_only_readout(self):
        attention = calculate(readout="attention")["summary"]
        summation = calculate(readout="sum")["summary"]
        self.assertEqual(attention["message_passing_flops"], summation["message_passing_flops"])
        self.assertEqual(attention["mlp_head_flops"], summation["mlp_head_flops"])
        self.assertEqual(attention["readout_flops"] - summation["readout_flops"], 4 * 100 * 256)
        self.assertEqual(summation["readout_flops"], 0)

    def test_head_count_does_not_change_flops(self):
        one = calculate(heads=1)["summary"]
        eight = calculate(heads=8)["summary"]
        self.assertEqual(one["total_flops"], eight["total_flops"])

    def test_parameters_positive_and_transformer_baseline(self):
        summary = calculate()["summary"]
        self.assertGreater(summary["parameters"], 0)
        self.assertGreater(summary["transformer_forward_flops"], 0)
        self.assertGreater(summary["inference_energy_estimate"], 0)

    def test_rejects_indivisible_heads(self):
        with self.assertRaises(ValueError):
            calculate(hidden=250, heads=8)


if __name__ == "__main__":
    unittest.main()
