"""Tests for the Phase 3 social-choice extension."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from memory_portability.model import Action, LL, PL, PP, ModelParameters  # noqa: E402
from memory_portability.social_choice import (  # noqa: E402
    evaluate_ex_ante_welfare,
    mobility_value_grid,
    social_choice_table,
    user_mobility_benefit,
    welfare_ranking_changes,
)


BENCHMARK = ModelParameters(0.2, 1.2, 0.7)


class SocialChoiceTests(unittest.TestCase):
    def test_user_benefit_requires_mutual_portability(self):
        for action_a in Action:
            for action_b in Action:
                expected = 2.0 if action_a is Action.PORTABLE and action_b is Action.PORTABLE else 0.0
                self.assertEqual(user_mobility_benefit(action_a, action_b, 2.0), expected)

    def test_negative_mobility_value_is_rejected(self):
        with self.assertRaises(ValueError):
            user_mobility_benefit(Action.PORTABLE, Action.PORTABLE, -0.1)

    def test_ll_welfare_is_zero(self):
        result = evaluate_ex_ante_welfare(LL, LL, BENCHMARK, 3.0)
        self.assertAlmostEqual(result["expected_total_platform_payoff"], 0.0)
        self.assertAlmostEqual(result["expected_user_mobility_payoff"], 0.0)
        self.assertAlmostEqual(result["expected_social_welfare"], 0.0)

    def test_pl_benchmark_formula(self):
        for mobility_value in (0.0, 1.0, 4.0):
            result = evaluate_ex_ante_welfare(
                PL, PL, BENCHMARK, mobility_value
            )
            self.assertAlmostEqual(result["expected_total_platform_payoff"], 1.68)
            self.assertAlmostEqual(
                result["expected_user_mobility_payoff"], 0.49 * mobility_value
            )
            self.assertAlmostEqual(
                result["expected_social_welfare"], 1.68 + 0.49 * mobility_value
            )

    def test_pp_benchmark_formula(self):
        for mobility_value in (0.0, 1.0, 4.0):
            result = evaluate_ex_ante_welfare(
                PP, PP, BENCHMARK, mobility_value
            )
            self.assertAlmostEqual(result["expected_platform_payoff_A"], 1.5)
            self.assertAlmostEqual(result["expected_platform_payoff_B"], 1.5)
            self.assertAlmostEqual(result["expected_social_welfare"], 3.0 + mobility_value)

    def test_state_probabilities_sum_to_one(self):
        result = evaluate_ex_ante_welfare(PL, PL, BENCHMARK, 1.0)
        self.assertTrue(
            math.isclose(
                sum(row["probability"] for row in result["state_details"]),
                1.0,
                abs_tol=1e-12,
            )
        )

    def test_sweep_labels_equilibrium_status_and_rankings(self):
        frame = social_choice_table(BENCHMARK, mobility_value_grid())
        self.assertEqual(len(frame), 41 * 3)
        status = {
            row.strategy_profile: row.phase2_pure_bne_at_benchmark
            for row in frame[frame["m"] == 0.0].itertuples()
        }
        self.assertEqual(status, {"(LL,LL)": True, "(PL,PL)": True, "(PP,PP)": False})
        self.assertEqual(welfare_ranking_changes(frame), [])
        for _, group in frame.groupby("m"):
            ordering = list(group.sort_values("welfare_rank_at_m")["strategy_profile"])
            self.assertEqual(ordering, ["(PP,PP)", "(PL,PL)", "(LL,LL)"])


if __name__ == "__main__":
    unittest.main()
