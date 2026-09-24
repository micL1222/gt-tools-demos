"""Tests for the stylized user-slot auction application."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from memory_portability.auction import (  # noqa: E402
    analytical_allocation_probability,
    auction_summary,
    first_price_equilibrium_bid,
    first_price_outcome,
    second_price_outcome,
    second_price_truthful_bid,
    simulate_auction_conditions,
    validate_common_sample,
)


class AuctionRuleTests(unittest.TestCase):
    def test_first_price_bid_at_reserve(self):
        for reserve in (0.2, 0.5):
            self.assertAlmostEqual(
                first_price_equilibrium_bid(reserve, reserve), reserve
            )

    def test_first_price_below_reserve_is_not_eligible(self):
        self.assertIsNone(first_price_equilibrium_bid(0.49, 0.5))

    def test_first_price_uses_reserve_adjusted_formula(self):
        self.assertAlmostEqual(first_price_equilibrium_bid(0.8, 0.5), 0.55625)
        self.assertNotAlmostEqual(first_price_equilibrium_bid(0.8, 0.5), 0.4)

    def test_second_price_bid_is_truthful(self):
        self.assertEqual(second_price_truthful_bid(0.73), 0.73)

    def test_no_allocation_when_both_values_below_reserve(self):
        self.assertTrue(first_price_outcome(0.4, 0.3, 0.5)["no_allocation"])
        self.assertTrue(second_price_outcome(0.4, 0.3, 0.5)["no_allocation"])

    def test_first_price_winner_pays_own_bid(self):
        outcome = first_price_outcome(0.8, 0.6, 0.5)
        self.assertEqual(outcome["winner"], "A")
        self.assertAlmostEqual(outcome["payment"], outcome["bid_A"])

    def test_second_price_payment_uses_reserve_floor(self):
        outcome = second_price_outcome(0.8, 0.3, 0.5)
        self.assertEqual(outcome["winner"], "A")
        self.assertAlmostEqual(outcome["payment"], 0.5)
        competitive = second_price_outcome(0.8, 0.6, 0.5)
        self.assertAlmostEqual(competitive["payment"], 0.6)

    def test_ties_go_to_platform_a(self):
        self.assertEqual(first_price_outcome(0.8, 0.8, 0.5)["winner"], "A")
        self.assertEqual(second_price_outcome(0.8, 0.8, 0.5)["winner"], "A")

    def test_analytical_allocation_probabilities(self):
        self.assertAlmostEqual(analytical_allocation_probability(0.5), 0.75)
        self.assertAlmostEqual(analytical_allocation_probability(0.2), 0.96)


class AuctionSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = simulate_auction_conditions(n=50_000, seed=20603)
        cls.summary = auction_summary(cls.raw)

    def test_same_valuation_sample_is_used_everywhere(self):
        self.assertTrue(validate_common_sample(self.raw))

    def test_simulated_allocation_matches_analytical_probability(self):
        self.assertTrue(
            (self.summary["allocation_probability_absolute_error"] < 0.01).all()
        )

    def test_both_mechanisms_allocate_identically_for_same_reserve(self):
        pivot = self.summary.pivot(
            index="reserve_regime", columns="mechanism", values="allocation_probability"
        )
        for regime in pivot.index:
            self.assertAlmostEqual(
                pivot.loc[regime, "first_price"],
                pivot.loc[regime, "second_price"],
            )

    def test_revenue_equivalence_is_approximately_visible(self):
        pivot = self.summary.pivot(
            index="reserve_regime",
            columns="mechanism",
            values="expected_payment_unconditional",
        )
        for regime in pivot.index:
            self.assertLess(
                abs(
                    pivot.loc[regime, "first_price"]
                    - pivot.loc[regime, "second_price"]
                ),
                0.01,
            )

    def test_highest_value_bidder_wins_conditionally(self):
        self.assertTrue(
            (self.summary["efficiency_conditional_on_allocation"] == 1.0).all()
        )


if __name__ == "__main__":
    unittest.main()
