import json
from pathlib import Path
import unittest

import _common
from _common import DEFAULT_INPUTS, TOPIC_MODULES, calculate_all
from ai4polymer_calc.paths import PROJECT
from ai4polymer_calc.reproduce import run, scenarios, verify_results
from ai4polymer_calc.schema import OPTIONAL_KEYS, REQUIRED_KEYS, read_json_object, result, validate_result


class ContractTests(unittest.TestCase):
    def test_every_topic_returns_required_keys_and_valid_json(self):
        allowed = set(REQUIRED_KEYS) | set(OPTIONAL_KEYS)
        for name, payload in calculate_all().items():
            with self.subTest(topic=name):
                self.assertEqual(set(REQUIRED_KEYS) - set(payload), set())
                self.assertTrue(set(payload) <= allowed)
                self.assertEqual(payload["schema_version"], 1)
                validate_result(payload)
                text = json.dumps(payload, ensure_ascii=False, allow_nan=False)
                self.assertEqual(json.loads(text)["calculation"], name)
                self.assertTrue(payload["assumptions"])

    def test_default_inputs_cover_every_topic(self):
        self.assertEqual(set(DEFAULT_INPUTS), set(TOPIC_MODULES))

    def test_result_rejects_non_finite(self):
        with self.assertRaises(ValueError):
            result(calculation="x", model="m", scenario={}, sources=[{"id": "s"}],
                   summary={"value": float("nan")}, assumptions=["a"])

    def test_result_rejects_extra_keys(self):
        with self.assertRaises(ValueError):
            validate_result({"schema_version": 1, "calculation": "x", "model": "m", "scenario": {},
                             "sources": [{"id": "s"}], "summary": {}, "assumptions": ["a"], "extra": 1})

    def test_read_json_rejects_nan(self):
        path = PROJECT / "results" / "nan-probe.json"
        path.write_text('{"value": NaN}', encoding="utf-8")
        try:
            with self.assertRaises(ValueError):
                read_json_object(path)
        finally:
            path.unlink()


class ReproduceTests(unittest.TestCase):
    def test_scenarios_reference_registered_topics(self):
        for row in scenarios():
            self.assertIn(row["topic"], TOPIC_MODULES)

    def test_reproduce_writes_paired_files_and_verifies(self):
        report = run()
        self.assertTrue(report["generated"])
        index = PROJECT / "results" / "README.md"
        self.assertTrue(index.exists())
        for slug in report["generated"]:
            for extension in ("json", "md"):
                path = PROJECT / "results" / f"{slug}.{extension}"
                self.assertTrue(path.exists(), msg=str(path))
                if extension == "json":
                    read_json_object(path)
        self.assertGreaterEqual(verify_results()["verified_artifacts"], len(report["generated"]) * 2)


if __name__ == "__main__":
    unittest.main()
