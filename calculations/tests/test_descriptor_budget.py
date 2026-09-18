import math
import unittest

import _common  # noqa: F401
from ai4polymer_calc.schema import REQUIRED_KEYS
from ai4polymer_calc.topics.descriptor_budget import calculate


class DescriptorBudgetTests(unittest.TestCase):
    def test_morgan_is_packed_bits(self):
        result = calculate(representation="morgan", n_bits=2048)
        summary = result["summary"]
        self.assertEqual(summary["feature_dim"], 2048)
        self.assertEqual(summary["bytes_per_molecule"], 256)
        self.assertEqual(summary["bits_per_molecule"], 2048)

    def test_birthday_collision_closed_form(self):
        library = 1_000_000
        for n_bits in (16, 32, 64):
            result = calculate(representation="morgan", n_bits=n_bits, library_size=library)
            expected = (library * (library - 1) / 2) / 2 ** n_bits
            self.assertAlmostEqual(result["summary"]["expected_collisions"], expected, places=6)
            self.assertAlmostEqual(result["summary"]["collision_probability"],
                                   1 - math.exp(-expected), places=12)

    def test_collision_risk_falls_with_more_bits(self):
        small = calculate(n_bits=16)["summary"]["collision_probability"]
        large = calculate(n_bits=64)["summary"]["collision_probability"]
        self.assertGreater(small, large)
        self.assertGreaterEqual(large, 0.0)
        self.assertLessEqual(large, 1.0)

    def test_other_representations_use_declared_widths(self):
        mordred = calculate(representation="mordred")["summary"]
        self.assertEqual(mordred["feature_dim"], 1826)
        self.assertEqual(mordred["bytes_per_molecule"], 1826 * 4)
        graph = calculate(representation="graph", atoms=100, bonds=105)["summary"]
        self.assertEqual(graph["feature_dim"], 100 * 64 + 105 * 16)
        psmiles = calculate(representation="psmiles", atoms=100, bonds=105)["summary"]
        self.assertEqual(psmiles["feature_dim"], 100 * 2 + 105 + 6)

    def test_comparison_count_is_exact(self):
        result = calculate(library_size=1000)["summary"]
        self.assertEqual(result["pairwise_comparison_count"], 1000 * 999 // 2)

    def test_rejects_non_ecfp4_radius(self):
        with self.assertRaises(ValueError):
            calculate(representation="morgan", radius=3)

    def test_contract_keys(self):
        result = calculate()
        self.assertEqual(set(result), set(REQUIRED_KEYS))


if __name__ == "__main__":
    unittest.main()
