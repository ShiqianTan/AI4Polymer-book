import itertools
import unittest

import _common  # noqa: F401
from ai4polymer_calc.schema import sequence_count, sequences_at_most_k_types
from ai4polymer_calc.topics.chemical_space import calculate


class ChemicalSpaceTests(unittest.TestCase):
    def test_random_matches_brute_force(self):
        for monomers, length in ((2, 3), (3, 2), (4, 3)):
            sequences = set(itertools.product(range(monomers), repeat=length))
            self.assertEqual(sequence_count(monomers, length, "random"), len(sequences))
            self.assertEqual(calculate(monomers=monomers, chain_length=length, copolymer="random")
                             ["summary"]["sequence_count"], len(sequences))

    def test_homopolymer_is_monomer_count(self):
        self.assertEqual(sequence_count(5, 7, "homopolymer"), 5)

    def test_alternating_matches_brute_force(self):
        for monomers in (2, 3, 4):
            length = 6
            sequences = {tuple(start if step % 2 == 0 else (start + offset) % monomers
                               for step in range(length))
                         for start in range(monomers)
                         for offset in range(1, monomers)}
            self.assertEqual(sequence_count(monomers, length, "alternating"), len(sequences))

    def test_block_matches_brute_force(self):
        monomers, length = 3, 5
        sequences = set()
        for first in range(monomers):
            for second in range(monomers):
                if first == second:
                    continue
                for split in range(1, length):
                    sequences.add(tuple([first] * split + [second] * (length - split)))
        self.assertEqual(sequence_count(monomers, length, "block"), len(sequences))

    def test_synthesizable_rule_matches_brute_force(self):
        monomers, length, max_distinct = 3, 3, 2
        brute = sum(1 for sequence in itertools.product(range(monomers), repeat=length)
                    if len(set(sequence)) <= max_distinct)
        self.assertEqual(sequences_at_most_k_types(monomers, length, max_distinct), brute)
        result = calculate(monomers=monomers, chain_length=length, copolymer="random")["summary"]
        self.assertEqual(result["synthesizable_count"], brute)
        self.assertAlmostEqual(result["synthesizable_fraction"], brute / monomers ** length)

    def test_exact_big_integers(self):
        result = calculate(monomers=10, chain_length=100, copolymer="random")["summary"]
        self.assertEqual(result["sequence_count"], 10 ** 100)
        self.assertEqual(result["log10_sequence_count"], 100.0)
        self.assertEqual(result["known_library_size"], 1_000_000)
        self.assertAlmostEqual(result["coverage_of_known_library"], 1e-94)

    def test_dataset_comparison_lists_known_libraries(self):
        rows = calculate()["summary"]["dataset_comparison"]
        names = {row["dataset"] for row in rows}
        self.assertIn("PI1M", names)
        self.assertIn("PoLyInfo", names)
        self.assertTrue(any(row["size"] is None for row in rows))

    def test_rejects_invalid_architecture(self):
        with self.assertRaises(ValueError):
            calculate(copolymer="gradient")


if __name__ == "__main__":
    unittest.main()
