import unittest

import _common  # noqa: F401
from ai4polymer_calc.sources import device
from ai4polymer_calc.topics.md_cost import calculate


class MdCostTests(unittest.TestCase):
    def test_ff_scales_with_atoms_and_steps(self):
        base = calculate(method="md-ff", atoms=1000, timesteps=1000)["summary"]
        double_atoms = calculate(method="md-ff", atoms=2000, timesteps=1000)["summary"]
        double_steps = calculate(method="md-ff", atoms=1000, timesteps=2000)["summary"]
        self.assertEqual(double_atoms["flops_or_force_evals"], 2 * base["flops_or_force_evals"])
        self.assertEqual(double_steps["flops_or_force_evals"], 2 * base["flops_or_force_evals"])

    def test_mlff_scales_with_atom_steps(self):
        base = calculate(method="md-mlff", atoms=1000, timesteps=1000)["summary"]
        doubled = calculate(method="md-mlff", atoms=2000, timesteps=1000)["summary"]
        self.assertEqual(doubled["atom_steps"], 2 * base["atom_steps"])
        self.assertEqual(doubled["flops_or_force_evals"], 2 * base["flops_or_force_evals"])

    def test_dft_scales_cubically(self):
        base = calculate(method="dft", atoms=100, timesteps=1)["summary"]
        doubled = calculate(method="dft", atoms=200, timesteps=1)["summary"]
        self.assertEqual(doubled["flops_or_force_evals"], 8 * base["flops_or_force_evals"])

    def test_gpu_hours_use_declared_device(self):
        summary = calculate(method="md-ff", atoms=1000, timesteps=1000,
                            device_id="a100-80gb-sxm", efficiency=0.5, gpus=2)["summary"]
        peak = device("a100-80gb-sxm")["bf16_tensor_flops_per_second"]
        expected_hours = summary["flops_or_force_evals"] / (peak * 0.5) / 3600
        self.assertAlmostEqual(summary["gpu_hours"], expected_hours, places=12)
        self.assertAlmostEqual(summary["wall_clock_hours"], expected_hours / 2, places=12)

    def test_required_summary_keys(self):
        summary = calculate()["summary"]
        for key in ("total_steps", "atom_steps", "flops_or_force_evals", "gpu_hours", "wall_clock_hours"):
            self.assertIn(key, summary)

    def test_rejects_unknown_method(self):
        with self.assertRaises(ValueError):
            calculate(method="md-quantum")


if __name__ == "__main__":
    unittest.main()
