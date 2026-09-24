"""Social-choice calculations built on the verified Phase 2 platform game.

All utilities are normalized model quantities.  Cardinal comparability between
platform payoffs and the user-mobility component is an explicit benchmark
assumption, not an empirical claim.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .model import (
    Action,
    CostType,
    LL,
    PL,
    PP,
    ModelParameters,
    PureStrategy,
    enumerate_pure_bne,
    payoff,
)


SOCIAL_CHOICE_STRATEGIES: tuple[PureStrategy, ...] = (LL, PL, PP)


def user_mobility_benefit(
    action_a: Action, action_b: Action, mobility_value: float
) -> float:
    """Return the binary benchmark user benefit.

    Full mobility requires mutual portability in this deliberately simple
    two-platform benchmark.  Unilateral portability is assigned zero user
    benefit here, even though it may have value in a richer model.
    """

    if mobility_value < 0:
        raise ValueError("mobility_value must be nonnegative.")
    return (
        float(mobility_value)
        if action_a is Action.PORTABLE and action_b is Action.PORTABLE
        else 0.0
    )


def joint_type_probability(
    type_a: CostType, type_b: CostType, p_low: float
) -> float:
    """Probability of one joint type state under independent draws."""

    if not 0 <= p_low <= 1:
        raise ValueError("p_low must lie in [0, 1].")
    probability_a = p_low if type_a is CostType.LOW else 1.0 - p_low
    probability_b = p_low if type_b is CostType.LOW else 1.0 - p_low
    return probability_a * probability_b


def evaluate_ex_ante_welfare(
    strategy_a: PureStrategy,
    strategy_b: PureStrategy,
    parameters: ModelParameters,
    mobility_value: float,
) -> dict[str, object]:
    """Enumerate all four type states and return ex-ante welfare components."""

    if mobility_value < 0:
        raise ValueError("mobility_value must be nonnegative.")
    totals = {
        "expected_platform_payoff_A": 0.0,
        "expected_platform_payoff_B": 0.0,
        "expected_user_mobility_payoff": 0.0,
    }
    states: list[dict[str, object]] = []
    for type_a, type_b in product(CostType, repeat=2):
        probability = joint_type_probability(type_a, type_b, parameters.p_low)
        action_a = strategy_a.action_for(type_a)
        action_b = strategy_b.action_for(type_b)
        payoff_a = payoff(action_a, action_b, parameters.cost(type_a))
        payoff_b = payoff(action_b, action_a, parameters.cost(type_b))
        user_payoff = user_mobility_benefit(
            action_a, action_b, mobility_value
        )
        total_welfare = payoff_a + payoff_b + user_payoff
        totals["expected_platform_payoff_A"] += probability * payoff_a
        totals["expected_platform_payoff_B"] += probability * payoff_b
        totals["expected_user_mobility_payoff"] += probability * user_payoff
        states.append(
            {
                "type_A": type_a.value,
                "type_B": type_b.value,
                "probability": probability,
                "action_A": action_a.value,
                "action_B": action_b.value,
                "platform_payoff_A": payoff_a,
                "platform_payoff_B": payoff_b,
                "user_mobility_payoff": user_payoff,
                "social_welfare": total_welfare,
            }
        )
    total_platform = (
        totals["expected_platform_payoff_A"]
        + totals["expected_platform_payoff_B"]
    )
    return {
        "strategy_A": strategy_a.name,
        "strategy_B": strategy_b.name,
        "strategy_profile": f"({strategy_a.name},{strategy_b.name})",
        "m": float(mobility_value),
        **totals,
        "expected_total_platform_payoff": total_platform,
        "expected_social_welfare": (
            total_platform + totals["expected_user_mobility_payoff"]
        ),
        "state_details": states,
    }


def mobility_value_grid() -> list[float]:
    """Return the deterministic m=0.0,0.1,...,4.0 sensitivity grid."""

    return [index / 10 for index in range(41)]


def social_choice_table(
    parameters: ModelParameters,
    mobility_values: Iterable[float],
    strategies: Iterable[PureStrategy] = SOCIAL_CHOICE_STRATEGIES,
) -> pd.DataFrame:
    """Evaluate welfare and Phase 2 equilibrium status for selected profiles."""

    pure_bne = set(enumerate_pure_bne(parameters))
    rows: list[dict[str, object]] = []
    for mobility_value in mobility_values:
        for strategy in strategies:
            result = evaluate_ex_ante_welfare(
                strategy, strategy, parameters, mobility_value
            )
            result.pop("state_details")
            result["phase2_pure_bne_at_benchmark"] = (
                strategy.name,
                strategy.name,
            ) in pure_bne
            rows.append(result)
    frame = pd.DataFrame(rows)
    frame["welfare_rank_at_m"] = frame.groupby("m")[
        "expected_social_welfare"
    ].rank(method="dense", ascending=False).astype(int)
    return frame


def welfare_ranking_changes(frame: pd.DataFrame) -> list[dict[str, object]]:
    """Return grid points at which the computed welfare ordering changes."""

    changes: list[dict[str, object]] = []
    previous: tuple[str, ...] | None = None
    for mobility_value, group in frame.groupby("m", sort=True):
        ordering = tuple(
            group.sort_values(
                ["expected_social_welfare", "strategy_profile"],
                ascending=[False, True],
            )["strategy_profile"]
        )
        if previous is not None and ordering != previous:
            changes.append({"m": float(mobility_value), "ordering": list(ordering)})
        previous = ordering
    return changes


def plot_social_welfare_by_m(frame: pd.DataFrame, output_path: Path) -> Path:
    """Plot collective welfare without presenting non-equilibria as predictions."""

    figure, axis = plt.subplots(figsize=(8.5, 5.0))
    for profile, group in frame.groupby("strategy_profile", sort=False):
        is_bne = bool(group["phase2_pure_bne_at_benchmark"].iloc[0])
        label = f"{profile} ({'Phase 2 pure BNE' if is_bne else 'welfare comparator only'})"
        ordered = group.sort_values("m")
        axis.plot(
            ordered["m"], ordered["expected_social_welfare"],
            linewidth=2.0, label=label,
        )
    axis.set_xlabel("Normalized user mobility value m")
    axis.set_ylabel("Expected normalized social welfare")
    axis.set_title("Welfare comparison across Bayesian strategy profiles")
    axis.legend(loc="upper left")
    axis.grid(alpha=0.2)
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output_path
