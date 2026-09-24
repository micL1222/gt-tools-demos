"""Tests for the verified-portability incentive extension."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from memory_portability.mechanism import (  # noqa: E402
    enumerate_mechanism_profile_diagnostics,
    enumerate_mechanism_pure_bne,
    expected_utility_portable_with_incentive,
    lock_in_high_type_threshold,
    lock_in_low_type_threshold,
    minimum_incentive_for_pl,
    pl_prior_threshold,
    portability_advantage_with_incentive,
)
from memory_portability.model import ModelParameters, enumerate_pure_bne  # noqa: E402


BENCHMARK = ModelParameters(0.2, 1.2, 0.7)


class MechanismTests(unittest.TestCase):
    def test_zero_incentive_reproduces_phase2(self):
        self.assertEqual(
            set(enumerate_mechanism_pure_bne(BENCHMARK, 0.0)),
            set(enumerate_pure_bne(BENCHMARK)),
        )

    def test_expected_payoff_formula(self):
        self.assertAlmostEqual(
            expected_utility_portable_with_incentive(0.4, 0.2, 0.3),
            3 * 0.4 - 1 - 0.2 + 0.3,
        )
        self.assertAlmostEqual(
            portability_advantage_with_incentive(0.4, 0.2, 0.3),
            2 * 0.4 - 1 - 0.2 + 0.3,
        )

    def test_pl_threshold_forms(self):
        self.assertAlmostEqual(pl_prior_threshold(0.2, 0.4), 0.4)
        self.assertAlmostEqual(minimum_incentive_for_pl(0.4, 0.2), 0.4)
        self.assertAlmostEqual(minimum_incentive_for_pl(0.7, 0.2), 0.0)

    def test_pl_below_at_and_above_exact_incentive(self):
        parameters = ModelParameters(0.2, 1.2, 0.4)
        self.assertNotIn(("PL", "PL"), enumerate_mechanism_pure_bne(parameters, 0.39))
        self.assertIn(("PL", "PL"), enumerate_mechanism_pure_bne(parameters, 0.40))
        self.assertIn(("PL", "PL"), enumerate_mechanism_pure_bne(parameters, 0.41))

    def test_pl_high_type_upper_boundary_at_benchmark(self):
        self.assertIn(("PL", "PL"), enumerate_mechanism_pure_bne(BENCHMARK, 0.8))
        self.assertNotIn(("PL", "PL"), enumerate_mechanism_pure_bne(BENCHMARK, 0.8001))

    def test_pp_appears_at_high_type_boundary(self):
        self.assertNotIn(("PP", "PP"), enumerate_mechanism_pure_bne(BENCHMARK, 0.19))
        self.assertIn(("PP", "PP"), enumerate_mechanism_pure_bne(BENCHMARK, 0.20))

    def test_ll_remains_at_moderate_incentive(self):
        self.assertIn(("LL", "LL"), enumerate_mechanism_pure_bne(BENCHMARK, 0.4))

    def test_ll_low_type_boundary_uses_weak_best_response(self):
        self.assertAlmostEqual(lock_in_low_type_threshold(0.2), 1.2)
        self.assertIn(("LL", "LL"), enumerate_mechanism_pure_bne(BENCHMARK, 1.2))
        self.assertNotIn(("LL", "LL"), enumerate_mechanism_pure_bne(BENCHMARK, 1.2001))

    def test_high_type_indifference_threshold(self):
        self.assertAlmostEqual(lock_in_high_type_threshold(1.2), 2.2)
        self.assertLess(portability_advantage_with_incentive(0.0, 1.2, 2.19), 0.0)
        self.assertAlmostEqual(portability_advantage_with_incentive(0.0, 1.2, 2.2), 0.0)
        self.assertGreater(portability_advantage_with_incentive(0.0, 1.2, 2.21), 0.0)

    def test_all_sixteen_profiles_are_evaluated(self):
        rows = enumerate_mechanism_profile_diagnostics(BENCHMARK, 0.4)
        self.assertEqual(len(rows), 16)
        self.assertEqual(
            len({(row["strategy_A"], row["strategy_B"]) for row in rows}), 16
        )

    def test_negative_incentive_is_rejected(self):
        with self.assertRaises(ValueError):
            enumerate_mechanism_pure_bne(BENCHMARK, -0.1)


if __name__ == "__main__":
    unittest.main()
