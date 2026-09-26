from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = PROJECT_ROOT / "behavioral_static_space"
CATALOG_PATH = PROJECT_ROOT / "outputs" / "behavioral_scenario_catalog.csv"


class StaticSpacePackageTests(unittest.TestCase):
    def setUp(self):
        self.readme = (STATIC_DIR / "README.md").read_text(encoding="utf-8")
        self.html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        self.javascript = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        self.scenarios = json.loads(
            (STATIC_DIR / "scenarios.json").read_text(encoding="utf-8")
        )

    def test_required_upload_files_exist(self):
        for filename in ("README.md", "index.html", "styles.css", "app.js", "scenarios.json"):
            with self.subTest(filename=filename):
                self.assertTrue((STATIC_DIR / filename).is_file())

    def test_upload_manifest_lists_only_required_space_files(self):
        manifest = (STATIC_DIR / "UPLOAD_MANIFEST.txt").read_text(encoding="utf-8")
        self.assertEqual(
            manifest.splitlines(),
            ["README.md", "index.html", "styles.css", "app.js", "scenarios.json"],
        )

    def test_static_space_metadata_is_correct(self):
        front_matter = self.readme.split("---", 2)[1]
        self.assertIn("sdk: static", front_matter)
        self.assertIn("app_file: index.html", front_matter)
        for forbidden in ("sdk: gradio", "sdk_version", "python_version", "app_port"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, front_matter)

    def test_scenarios_have_exact_parity_with_canonical_csv(self):
        with CATALOG_PATH.open(encoding="utf-8", newline="") as handle:
            catalog = list(csv.DictReader(handle))
        expected = {
            row["scenario_id"]: (
                row["portability_condition"],
                float(row["normalized_benefit"]),
                float(row["normalized_hurdle"]),
                row["benchmark_prediction"],
            )
            for row in catalog
        }
        actual = {
            row["scenario_id"]: (
                row["condition"], row["benefit"], row["hurdle"], row["benchmark_prediction"]
            )
            for row in self.scenarios
        }
        self.assertEqual(actual, expected)

    def test_scenario_catalog_is_balanced(self):
        self.assertEqual(len(self.scenarios), 12)
        self.assertEqual(len({row["scenario_id"] for row in self.scenarios}), 12)
        self.assertEqual({row["condition"] for row in self.scenarios}, {"Full", "Partial", "None"})
        self.assertEqual({row["benefit"] for row in self.scenarios}, {0.15, 0.30, 0.45, 0.60})
        self.assertEqual(
            {row["condition"]: row["hurdle"] for row in self.scenarios},
            {"Full": 0.20, "Partial": 0.35, "None": 0.50},
        )
        predictions = [row["benchmark_prediction"] for row in self.scenarios]
        self.assertEqual(predictions.count("Stay"), 6)
        self.assertEqual(predictions.count("Switch"), 6)

    def test_html_has_core_accessible_elements_and_relative_assets(self):
        for element_id in (
            "main-content", "initial-decision-fieldset", "reveal-button",
            "benchmark-panel", "final-section", "submit-button", "peer-panel",
            "new-scenario-button", "clear-history-button", "configuration-error",
        ):
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)
        self.assertIn('href="./styles.css"', self.html)
        self.assertIn('src="./app.js"', self.html)
        self.assertIn("aria-live", self.html)
        self.assertNotIn("<script src=\"http", self.html.lower())

    def test_javascript_is_memory_only_and_has_no_external_endpoint(self):
        source = self.javascript.lower()
        for forbidden in (
            "localstorage", "indexeddb", "document.cookie", "eval(", "new function",
            "xmlhttprequest", "fetch(\"http", "fetch('http",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertIn('fetch("./scenarios.json")', self.javascript)
        self.assertIn("const priorPlays = []", self.javascript)

    def test_aggregate_record_excludes_text_and_identifiers(self):
        source = self.javascript
        record_section = source.split("function makeAggregateRecord", 1)[1].split("function summarize", 1)[0]
        for forbidden in (
            "initialReflection", "postReflection", "freeText", "email", "ipAddress",
            "userAgent", "timestamp", "playId",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, record_section)

    def test_readme_discloses_browser_session_limit_and_reset(self):
        self.assertTrue(
            "current browser session" in self.readme
            or "current browser-page session" in self.readme
        )
        self.assertIn("different devices or browsers", self.readme)
        self.assertIn("Refreshing or closing the page clears", self.readme)


if __name__ == "__main__":
    unittest.main()
