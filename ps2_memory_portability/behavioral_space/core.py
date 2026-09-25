"""Deterministic behavioral-scenario and response logic for Stay or Switch?."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import random
import secrets
from typing import Iterable


STAY = "Stay"
SWITCH = "Switch"
STAY_CHOICE = "Stay with Assistant A"
SWITCH_CHOICE = "Switch to Assistant B"
CHOICES = (STAY_CHOICE, SWITCH_CHOICE)
BENEFIT_LEVELS = (0.15, 0.30, 0.45, 0.60)


@dataclass(frozen=True)
class PortabilityCondition:
    label: str
    id_prefix: str
    hurdle: float
    description: str
    description_short: str


CONDITIONS = (
    PortabilityCondition(
        label="Full",
        id_prefix="FULL",
        hurdle=0.20,
        description=(
            "Your core personalization can move to Assistant B with high fidelity, "
            "including relevant preferences, selected project context, and portable "
            "memory summaries."
        ),
        description_short="Core personalization transfers with high fidelity.",
    ),
    PortabilityCondition(
        label="Partial",
        id_prefix="PARTIAL",
        hurdle=0.35,
        description=(
            "Some preferences and selected memory summaries can transfer, but part "
            "of your interaction history and personalization would need to be rebuilt."
        ),
        description_short="Some memory transfers; some personalization must be rebuilt.",
    ),
    PortabilityCondition(
        label="None",
        id_prefix="NONE",
        hurdle=0.50,
        description=(
            "Your existing personalization does not meaningfully transfer. You would "
            "need to rebuild preferences and context with Assistant B."
        ),
        description_short="Personalization does not meaningfully transfer.",
    ),
)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    portability_condition: str
    condition_description: str
    condition_description_short: str
    normalized_benefit: float
    normalized_hurdle: float
    benchmark_net_advantage: float
    benchmark_prediction: str


def benchmark_prediction(benefit: float, hurdle: float) -> str:
    """Return the simplified benchmark prediction; equality is intentionally invalid."""

    if benefit == hurdle:
        raise ValueError("The fixed catalog must not contain equality cases.")
    return SWITCH if benefit > hurdle else STAY


def build_scenarios() -> tuple[Scenario, ...]:
    scenarios: list[Scenario] = []
    for condition in CONDITIONS:
        for benefit in BENEFIT_LEVELS:
            prediction = benchmark_prediction(benefit, condition.hurdle)
            scenarios.append(
                Scenario(
                    scenario_id=f"{condition.id_prefix}_{int(round(benefit * 100)):03d}",
                    portability_condition=condition.label,
                    condition_description=condition.description,
                    condition_description_short=condition.description_short,
                    normalized_benefit=benefit,
                    normalized_hurdle=condition.hurdle,
                    benchmark_net_advantage=round(benefit - condition.hurdle, 2),
                    benchmark_prediction=prediction,
                )
            )
    return tuple(scenarios)


SCENARIOS = build_scenarios()
SCENARIO_BY_ID = {scenario.scenario_id: scenario for scenario in SCENARIOS}


def sample_scenario(seed: int | None = None) -> Scenario:
    """Uniformly sample a fixed scenario, with deterministic seeding for tests."""

    if seed is None:
        return secrets.choice(SCENARIOS)
    return random.Random(seed).choice(SCENARIOS)


def get_scenario(scenario_id: str) -> Scenario:
    try:
        return SCENARIO_BY_ID[scenario_id]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario ID: {scenario_id}") from exc


def choice_label(choice: str) -> str:
    if choice in (STAY, STAY_CHOICE):
        return STAY
    if choice in (SWITCH, SWITCH_CHOICE):
        return SWITCH
    raise ValueError("Choice must be Stay with Assistant A or Switch to Assistant B.")


def agrees_with_benchmark(choice: str, scenario: Scenario) -> bool:
    return choice_label(choice) == scenario.benchmark_prediction


def changed_choice(initial_choice: str, final_choice: str) -> bool:
    return choice_label(initial_choice) != choice_label(final_choice)


def validate_rating(value: object) -> int:
    if value is None or isinstance(value, bool):
        raise ValueError("Each reflection rating is required.")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Reflection ratings must be integers from 1 to 7.") from exc
    if not numeric.is_integer() or not 1 <= numeric <= 7:
        raise ValueError("Reflection ratings must be integers from 1 to 7.")
    return int(numeric)


@dataclass(frozen=True)
class PlayRecord:
    """Structured, non-identifying fields allowed in the runtime aggregate."""

    play_id: str
    scenario_id: str
    portability_condition: str
    benefit: float
    hurdle: float
    benchmark_prediction: str
    initial_choice: str
    final_choice: str
    changed_choice: bool
    initial_benchmark_agreement: bool
    final_benchmark_agreement: bool
    perceived_switching_difficulty: int
    personalization_concern: int
    privacy_concern: int
    trust: int


def create_play_record(
    *,
    play_id: str,
    scenario: Scenario,
    initial_choice: str,
    final_choice: str,
    perceived_switching_difficulty: object,
    personalization_concern: object,
    privacy_concern: object,
    trust: object,
) -> PlayRecord:
    if not play_id or not isinstance(play_id, str):
        raise ValueError("A nonempty play ID is required.")
    initial = choice_label(initial_choice)
    final = choice_label(final_choice)
    return PlayRecord(
        play_id=play_id,
        scenario_id=scenario.scenario_id,
        portability_condition=scenario.portability_condition,
        benefit=scenario.normalized_benefit,
        hurdle=scenario.normalized_hurdle,
        benchmark_prediction=scenario.benchmark_prediction,
        initial_choice=initial,
        final_choice=final,
        changed_choice=initial != final,
        initial_benchmark_agreement=initial == scenario.benchmark_prediction,
        final_benchmark_agreement=final == scenario.benchmark_prediction,
        perceived_switching_difficulty=validate_rating(perceived_switching_difficulty),
        personalization_concern=validate_rating(personalization_concern),
        privacy_concern=validate_rating(privacy_concern),
        trust=validate_rating(trust),
    )


def play_record_field_names() -> set[str]:
    return {field.name for field in fields(PlayRecord)}


def scenario_rows(scenarios: Iterable[Scenario] = SCENARIOS) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for scenario in scenarios:
        row = asdict(scenario)
        row.pop("condition_description")
        rows.append(row)
    return rows


def validate_scenario_catalog(
    scenarios: Iterable[Scenario] = SCENARIOS,
) -> dict[str, object]:
    items = tuple(scenarios)
    ids = [scenario.scenario_id for scenario in items]
    predictions = [scenario.benchmark_prediction for scenario in items]
    conditions = {scenario.portability_condition for scenario in items}
    benefits = {scenario.normalized_benefit for scenario in items}
    hurdles = {
        scenario.portability_condition: scenario.normalized_hurdle
        for scenario in items
    }

    assert len(items) == 12
    assert len(ids) == len(set(ids)) == 12
    assert conditions == {"Full", "Partial", "None"}
    assert benefits == set(BENEFIT_LEVELS)
    assert hurdles == {"Full": 0.20, "Partial": 0.35, "None": 0.50}
    assert all(
        scenario.normalized_benefit != scenario.normalized_hurdle
        for scenario in items
    )
    assert predictions.count(STAY) == 6
    assert predictions.count(SWITCH) == 6

    return {
        "scenario_count": len(items),
        "condition_count": len(conditions),
        "benefit_levels": sorted(benefits),
        "hurdle_mapping": hurdles,
        "benchmark_stay_count": predictions.count(STAY),
        "benchmark_switch_count": predictions.count(SWITCH),
    }
