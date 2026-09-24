"""Independent checks for the Bayesian memory-portability implementation."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from memory_portability.model import (  # noqa: E402
    Action,
    LL,
    LP,
    PL,
    PP,
    ModelParameters,
    enumerate_pure_bne,
    enumerate_pure_profile_diagnostics,
    evaluate_pure_profile,
    expected_utility_locked,
    expected_utility_portable,
    payoff,
    portability_advantage,
    portable_is_best_response,
    rival_portability_probability,
    symmetric_low_type_mixed_equilibrium,
)
from memory_portability.pygambit_model import (  # noqa: E402
    PyGambitUnavailable,
    enumerate_pure_bne_pygambit,
)


BENCHMARK = ModelParameters(0.2, 1.2, 0.7)


class FormulaTests(unittest.TestCase):
    def test_payoff_values_for_every_action_pair(self):
        cost = 0.2
        expected = {
            (Action.PORTABLE, Action.PORTABLE): 1.8,
            (Action.PORTABLE, Action.LOCKED): -1.2,
            (Action.LOCKED, Action.PORTABLE): 1.0,
            (Action.LOCKED, Action.LOCKED): 0.0,
        }
        for actions, value in expected.items():
            with self.subTest(actions=actions):
                self.assertAlmostEqual(payoff(*actions, cost), value)

    def test_expected_utility_formulas(self):
        for q, cost in [(0.0, 0.2), (0.3, 1.2), (0.7, 0.2), (1.0, 1.2)]:
            with self.subTest(q=q, cost=cost):
                self.assertAlmostEqual(expected_utility_portable(q, cost), 3 * q - 1 - cost)
                self.assertAlmostEqual(expected_utility_locked(q), q)
                self.assertAlmostEqual(portability_advantage(q, cost), 2 * q - 1 - cost)

    def test_portability_condition_including_weak_equality(self):
        self.assertFalse(portable_is_best_response(0.59, 0.2))
        self.assertTrue(portable_is_best_response(0.60, 0.2))
        self.assertTrue(portable_is_best_response(0.61, 0.2))


class StrategyAndBenchmarkTests(unittest.TestCase):
    def test_rival_portability_probabilities(self):
        self.assertAlmostEqual(rival_portability_probability(LL, 0.7), 0.0)
        self.assertAlmostEqual(rival_portability_probability(PL, 0.7), 0.7)
        self.assertAlmostEqual(rival_portability_probability(LP, 0.7), 0.3)
        self.assertAlmostEqual(rival_portability_probability(PP, 0.7), 1.0)

    def test_benchmark_expected_payoff_values(self):
        expected = {
            "LL": (0.0, (-1.2, 0.0), (-2.2, 0.0)),
            "PL": (0.7, (0.9, 0.7), (-0.1, 0.7)),
            "LP": (0.3, (-0.3, 0.3), (-1.3, 0.3)),
            "PP": (1.0, (1.8, 1.0), (0.8, 1.0)),
        }
        for strategy in (LL, PL, LP, PP):
            q, low_values, high_values = expected[strategy.name]
            self.assertAlmostEqual(rival_portability_probability(strategy, 0.7), q)
            self.assertAlmostEqual(expected_utility_portable(q, 0.2), low_values[0])
            self.assertAlmostEqual(expected_utility_locked(q), low_values[1])
            self.assertAlmostEqual(expected_utility_portable(q, 1.2), high_values[0])
            self.assertAlmostEqual(expected_utility_locked(q), high_values[1])

    def test_all_sixteen_profiles_are_evaluated(self):
        rows = enumerate_pure_profile_diagnostics(BENCHMARK)
        self.assertEqual(len(rows), 16)
        self.assertEqual(
            {(row["strategy_A"], row["strategy_B"]) for row in rows},
            {(a.name, b.name) for a in (LL, PL, LP, PP) for b in (LL, PL, LP, PP)},
        )

    def test_benchmark_has_exactly_two_pure_bne(self):
        self.assertEqual(
            set(enumerate_pure_bne(BENCHMARK)),
            {("LL", "LL"), ("PL", "PL")},
        )

    def test_benchmark_has_no_asymmetric_pure_bne(self):
        self.assertFalse(
            [profile for profile in enumerate_pure_bne(BENCHMARK) if profile[0] != profile[1]]
        )

    def test_candidate_symmetric_profiles_have_expected_status(self):
        expected = {"LL": True, "PL": True, "LP": False, "PP": False}
        for strategy in (LL, PL, LP, PP):
            with self.subTest(strategy=strategy.name):
                result = evaluate_pure_profile(strategy, strategy, BENCHMARK)
                self.assertEqual(result["is_bne"], expected[strategy.name])


class ThresholdMixedAndEndpointTests(unittest.TestCase):
    def test_pl_threshold_below_at_and_above(self):
        self.assertNotIn(("PL", "PL"), enumerate_pure_bne(ModelParameters(0.2, 1.2, 0.59)))
        self.assertIn(("PL", "PL"), enumerate_pure_bne(ModelParameters(0.2, 1.2, 0.60)))
        self.assertIn(("PL", "PL"), enumerate_pure_bne(ModelParameters(0.2, 1.2, 0.61)))

    def test_benchmark_mixed_equilibrium_is_six_sevenths(self):
        result = symmetric_low_type_mixed_equilibrium(BENCHMARK)
        self.assertTrue(result["interior_mixed_exists"])
        self.assertEqual(result["x_star_exact"], "6/7")
        self.assertTrue(math.isclose(result["x_star"], 6 / 7, abs_tol=1e-12))
        self.assertTrue(result["high_type_prefers_locked"])

    def test_mixed_expression_at_threshold_collapses_to_pure_pl(self):
        result = symmetric_low_type_mixed_equilibrium(ModelParameters(0.2, 1.2, 0.6))
        self.assertFalse(result["interior_mixed_exists"])
        self.assertTrue(result["collapses_to_pure_pl"])
        self.assertAlmostEqual(result["x_star"], 1.0)

    def test_no_interior_low_type_mix_below_threshold(self):
        result = symmetric_low_type_mixed_equilibrium(ModelParameters(0.2, 1.2, 0.59))
        self.assertFalse(result["interior_mixed_exists"])
        self.assertGreater(result["x_star"], 1.0)

    def test_endpoints_are_flagged_and_rejected_by_formal_checker(self):
        for p, expected_status in ((0.0, "boundary_high_type_only"), (1.0, "boundary_low_type_only")):
            parameters = ModelParameters(0.2, 1.2, p)
            self.assertEqual(parameters.prior_status, expected_status)
            with self.assertRaisesRegex(ValueError, "require 0 < p_low < 1"):
                enumerate_pure_bne(parameters)
            mixed = symmetric_low_type_mixed_equilibrium(parameters)
            self.assertEqual(mixed["status"], expected_status)
            self.assertFalse(mixed["interior_mixed_exists"])


class PyGambitAgreementTests(unittest.TestCase):
    def test_pygambit_agrees_with_direct_checker_when_available(self):
        try:
            solver = set(enumerate_pure_bne_pygambit(BENCHMARK))
        except PyGambitUnavailable as error:
            self.skipTest(str(error))
        self.assertEqual(solver, set(enumerate_pure_bne(BENCHMARK)))


if __name__ == "__main__":
    unittest.main()
