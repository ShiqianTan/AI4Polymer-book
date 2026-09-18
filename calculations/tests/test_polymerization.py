import unittest

import _common  # noqa: F401
from ai4polymer_calc.topics.polymerization import calculate


class PolymerizationTests(unittest.TestCase):
    def test_carothers_matches_one_over_one_minus_p(self):
        rows = calculate(step_conversions="0.99,0.999")["summary"]["step_growth"]
        self.assertAlmostEqual(rows[0]["number_average_dp"], 100.0)
        self.assertAlmostEqual(rows[1]["number_average_dp"], 1000.0)

    def test_step_growth_dispersity_tends_to_two(self):
        rows = calculate(step_conversions="0.9,0.99,0.999")["summary"]["step_growth"]
        for row in rows:
            self.assertAlmostEqual(row["dispersity"], 1.0 + row["conversion"])

    def test_living_dispersity_tends_to_one(self):
        rows = calculate(living_ratios="50,100,200")["summary"]["living"]
        self.assertGreater(rows[0]["dispersity"], rows[1]["dispersity"])
        self.assertGreater(rows[1]["dispersity"], rows[2]["dispersity"])
        self.assertLess(rows[-1]["dispersity"], 1.02)

    def test_ideal_random_copolymer_tracks_the_feed(self):
        row = next(r for r in calculate()["summary"]["copolymer"] if r["r1"] == 1.0)
        self.assertAlmostEqual(row["instantaneous_F1"], 0.5)
        self.assertAlmostEqual(row["run_length_1"], 2.0)
        self.assertEqual(row["classification"], "无规")

    def test_alternating_pair_has_short_runs(self):
        row = next(r for r in calculate()["summary"]["copolymer"] if r["r1"] == 0.1 and r["r2"] == 0.1)
        self.assertEqual(row["classification"], "交替倾向")
        self.assertLess(row["run_length_1"], 1.2)

    def test_composition_drift_depletes_the_preferred_monomer(self):
        row = next(r for r in calculate()["summary"]["copolymer"] if r["r1"] == 10.0 and r["r2"] == 0.1)
        self.assertEqual(row["classification"], "梯度/组成漂移")
        drift = row["drift"]
        self.assertLess(drift[-1]["feed_f1"], drift[0]["feed_f1"])
        self.assertAlmostEqual(drift[-1]["conversion"], 0.99, places=9)

    def test_flory_distribution_peaks_near_the_number_average(self):
        flory = calculate()["summary"]["flory"]
        self.assertAlmostEqual(flory["dispersity"], 1.99)
        peak = flory["n"][flory["weight_fraction"].index(max(flory["weight_fraction"]))]
        self.assertLess(abs(peak - flory["number_average_dp"]), 10)

    def test_poisson_distribution_is_narrow_and_centred(self):
        poisson = calculate()["summary"]["poisson"]
        self.assertLess(poisson["dispersity"], 1.02)
        peak = poisson["n"][poisson["number_fraction"].index(max(poisson["number_fraction"]))]
        self.assertLess(abs(peak - poisson["number_average_dp"]), 5)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            calculate(step_conversions="1.5")
        with self.assertRaises(ValueError):
            calculate(copolymer_pairs="0.1")
        with self.assertRaises(ValueError):
            calculate(living_ratios="0")


if __name__ == "__main__":
    unittest.main()
