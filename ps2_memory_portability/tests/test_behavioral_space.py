from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SPACE_DIR = Path(__file__).resolve().parents[1] / "behavioral_space"
sys.path.insert(0, str(SPACE_DIR))

from core import (  # noqa: E402
    BENEFIT_LEVELS,
    SCENARIO_BY_ID,
    SCENARIOS,
    STAY,
    STAY_CHOICE,
    SWITCH,
    SWITCH_CHOICE,
    agrees_with_benchmark,
    changed_choice,
    create_play_record,
    play_record_field_names,
    sample_scenario,
    validate_rating,
    validate_scenario_catalog,
)
from store import InMemoryPlayStore  # noqa: E402


def make_record(
    play_id: str,
    scenario_id: str = "FULL_030",
    initial_choice: str = SWITCH_CHOICE,
    final_choice: str = SWITCH_CHOICE,
    ratings: tuple[int, int, int, int] = (2, 3, 4, 5),
):
    return create_play_record(
        play_id=play_id,
        scenario=SCENARIO_BY_ID[scenario_id],
        initial_choice=initial_choice,
        final_choice=final_choice,
        perceived_switching_difficulty=ratings[0],
        personalization_concern=ratings[1],
        privacy_concern=ratings[2],
        trust=ratings[3],
    )


class ScenarioCatalogTests(unittest.TestCase):
    def test_exactly_twelve_unique_scenarios(self):
        self.assertEqual(len(SCENARIOS), 12)
        self.assertEqual(len({scenario.scenario_id for scenario in SCENARIOS}), 12)

    def test_three_conditions_and_four_benefit_levels(self):
        self.assertEqual(
            {scenario.portability_condition for scenario in SCENARIOS},
            {"Full", "Partial", "None"},
        )
        self.assertEqual(
            {scenario.normalized_benefit for scenario in SCENARIOS},
            set(BENEFIT_LEVELS),
        )

    def test_hurdle_mapping(self):
        hurdles = {
            scenario.portability_condition: scenario.normalized_hurdle
            for scenario in SCENARIOS
        }
        self.assertEqual(hurdles, {"Full": 0.20, "Partial": 0.35, "None": 0.50})

    def test_no_equality_and_balanced_predictions(self):
        self.assertTrue(
            all(
                scenario.normalized_benefit != scenario.normalized_hurdle
                for scenario in SCENARIOS
            )
        )
        predictions = [scenario.benchmark_prediction for scenario in SCENARIOS]
        self.assertEqual(predictions.count(STAY), 6)
        self.assertEqual(predictions.count(SWITCH), 6)

    def test_catalog_validator(self):
        result = validate_scenario_catalog()
        self.assertEqual(result["scenario_count"], 12)
        self.assertEqual(result["benchmark_stay_count"], 6)
        self.assertEqual(result["benchmark_switch_count"], 6)

    def test_seeded_sampling_is_deterministic(self):
        self.assertEqual(sample_scenario(seed=206), sample_scenario(seed=206))

    def test_full_015_predicts_stay(self):
        self.assertEqual(SCENARIO_BY_ID["FULL_015"].benchmark_prediction, STAY)

    def test_full_030_predicts_switch(self):
        self.assertEqual(SCENARIO_BY_ID["FULL_030"].benchmark_prediction, SWITCH)

    def test_partial_030_predicts_stay(self):
        self.assertEqual(SCENARIO_BY_ID["PARTIAL_030"].benchmark_prediction, STAY)

    def test_partial_045_predicts_switch(self):
        self.assertEqual(SCENARIO_BY_ID["PARTIAL_045"].benchmark_prediction, SWITCH)

    def test_none_045_predicts_stay(self):
        self.assertEqual(SCENARIO_BY_ID["NONE_045"].benchmark_prediction, STAY)

    def test_none_060_predicts_switch(self):
        self.assertEqual(SCENARIO_BY_ID["NONE_060"].benchmark_prediction, SWITCH)


class AgreementAndRatingTests(unittest.TestCase):
    def test_initial_choice_matches_benchmark(self):
        self.assertTrue(
            agrees_with_benchmark(SWITCH_CHOICE, SCENARIO_BY_ID["FULL_030"])
        )

    def test_disagreement_is_classified(self):
        self.assertFalse(
            agrees_with_benchmark(STAY_CHOICE, SCENARIO_BY_ID["FULL_030"])
        )

    def test_final_agreement_is_computed_in_record(self):
        record = make_record(
            "agreement",
            initial_choice=STAY_CHOICE,
            final_choice=SWITCH_CHOICE,
        )
        self.assertFalse(record.initial_benchmark_agreement)
        self.assertTrue(record.final_benchmark_agreement)

    def test_change_status(self):
        self.assertTrue(changed_choice(STAY_CHOICE, SWITCH_CHOICE))
        self.assertFalse(changed_choice(STAY_CHOICE, STAY_CHOICE))

    def test_all_valid_integer_ratings_are_accepted(self):
        self.assertEqual([validate_rating(i) for i in range(1, 8)], list(range(1, 8)))

    def test_missing_and_out_of_range_ratings_are_rejected(self):
        for value in (None, 0, 8, -1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_rating(value)

    def test_noninteger_rating_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_rating(3.5)


class AggregateStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPlayStore()

    def test_empty_peer_summary(self):
        snapshot = self.store.prior_snapshot("Full")
        self.assertEqual(snapshot.same_condition.play_count, 0)
        self.assertEqual(snapshot.overall.play_count, 0)
        self.assertIsNone(snapshot.overall.switch_rate)

    def test_add_one_play(self):
        self.assertTrue(self.store.add_play(make_record("one")))
        self.assertEqual(self.store.size(), 1)

    def test_duplicate_submission_is_rejected(self):
        self.assertTrue(self.store.add_play(make_record("same")))
        self.assertFalse(
            self.store.add_play(
                make_record("same", initial_choice=STAY_CHOICE, final_choice=STAY_CHOICE)
            )
        )
        self.assertEqual(self.store.size(), 1)

    def test_snapshot_and_add_excludes_current_play(self):
        first_snapshot, first_added = self.store.snapshot_and_add(make_record("first"))
        second_snapshot, second_added = self.store.snapshot_and_add(make_record("second"))
        self.assertTrue(first_added)
        self.assertTrue(second_added)
        self.assertEqual(first_snapshot.overall.play_count, 0)
        self.assertEqual(second_snapshot.overall.play_count, 1)
        self.assertEqual(self.store.size(), 2)

    def test_stay_switch_and_agreement_rates(self):
        self.store.add_play(make_record("switch"))
        self.store.add_play(
            make_record(
                "stay",
                initial_choice=STAY_CHOICE,
                final_choice=STAY_CHOICE,
            )
        )
        summary = self.store.prior_snapshot("Full").overall
        self.assertEqual(summary.stay_count, 1)
        self.assertEqual(summary.switch_count, 1)
        self.assertEqual(summary.stay_rate, 0.5)
        self.assertEqual(summary.switch_rate, 0.5)
        self.assertEqual(summary.benchmark_agreement_rate, 0.5)

    def test_rating_averages(self):
        self.store.add_play(make_record("low", ratings=(1, 2, 3, 4)))
        self.store.add_play(make_record("high", ratings=(7, 6, 5, 4)))
        summary = self.store.prior_snapshot("Full").overall
        self.assertEqual(summary.mean_switching_difficulty, 4.0)
        self.assertEqual(summary.mean_personalization_concern, 4.0)
        self.assertEqual(summary.mean_privacy_concern, 4.0)
        self.assertEqual(summary.mean_trust, 4.0)

    def test_condition_filtering(self):
        self.store.add_play(make_record("full", scenario_id="FULL_030"))
        self.store.add_play(
            make_record(
                "none",
                scenario_id="NONE_015",
                initial_choice=STAY_CHOICE,
                final_choice=STAY_CHOICE,
            )
        )
        snapshot = self.store.prior_snapshot("Full")
        self.assertEqual(snapshot.same_condition.play_count, 1)
        self.assertEqual(snapshot.overall.play_count, 2)

    def test_default_store_does_not_write_to_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            before = set(Path(directory).iterdir())
            with patch("builtins.open") as mocked_open:
                self.store.add_play(make_record("memory-only"))
            mocked_open.assert_not_called()
            after = set(Path(directory).iterdir())
        self.assertFalse(self.store.persistence_enabled)
        self.assertEqual(before, after)

    def test_aggregate_model_excludes_sensitive_and_free_text_fields(self):
        forbidden = {
            "name",
            "email",
            "ip",
            "ip_address",
            "username",
            "account_id",
            "device_fingerprint",
            "initial_reflection",
            "post_reflection",
            "free_text_reason",
        }
        self.assertTrue(play_record_field_names().isdisjoint(forbidden))

    def test_records_contain_only_structured_fields(self):
        self.store.add_play(make_record("structured"))
        record = self.store.records_for_testing()[0]
        self.assertFalse(hasattr(record, "initial_reflection"))
        self.assertFalse(hasattr(record, "post_reflection"))


if __name__ == "__main__":
    unittest.main()
