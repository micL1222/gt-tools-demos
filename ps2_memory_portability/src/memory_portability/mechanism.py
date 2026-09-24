"""Verified-portability incentive extension of the Phase 2 Bayesian game."""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .model import (
    Action,
    CostType,
    DEFAULT_TOLERANCE,
    LL,
    PL,
    PURE_STRATEGIES,
    ModelParameters,
    PureStrategy,
    expected_utility_locked,
    expected_utility_portable,
    rival_portability_probability,
)


def _validate_incentive(tau: float) -> None:
    if tau < 0:
        raise ValueError("tau must be nonnegative.")


def expected_utility_portable_with_incentive(
    q: float, cost: float, tau: float
) -> float:
    """Return 3q-1-cost+tau for a verified Portable action."""

    _validate_incentive(tau)
    return expected_utility_portable(q, cost) + tau


def portability_advantage_with_incentive(
    q: float, cost: float, tau: float
) -> float:
    """Return EU_tau(P)-EU_tau(L)=2q-1-cost+tau."""

    return expected_utility_portable_with_incentive(
        q, cost, tau
    ) - expected_utility_locked(q)


def pl_prior_threshold(c_low: float, tau: float) -> float:
    """Lower prior threshold (1+c_L-tau)/2 for the low type in PL."""

    if c_low < 0:
        raise ValueError("c_low must be nonnegative.")
    _validate_incentive(tau)
    return (1.0 + c_low - tau) / 2.0


def minimum_incentive_for_pl(p_low: float, c_low: float) -> float:
    """Minimum nonnegative incentive satisfying the PL low-type constraint."""

    if not 0 <= p_low <= 1:
        raise ValueError("p_low must lie in [0, 1].")
    if c_low < 0:
        raise ValueError("c_low must be nonnegative.")
    return max(0.0, 1.0 + c_low - 2.0 * p_low)


def lock_in_low_type_threshold(c_low: float) -> float:
    """Incentive at which a low type is indifferent against rival LL."""

    return 1.0 + c_low


def lock_in_high_type_threshold(c_high: float) -> float:
    """Incentive at which a high type is indifferent against rival LL."""

    return 1.0 + c_high


def mechanism_type_incentive_check(
    prescribed_strategy: PureStrategy,
    rival_strategy: PureStrategy,
    cost_type: CostType,
    parameters: ModelParameters,
    tau: float,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict[str, object]:
    """Check one type's incentive constraint under the portability incentive."""

    _validate_incentive(tau)
    q = rival_portability_probability(rival_strategy, parameters.p_low)
    cost = parameters.cost(cost_type)
    prescribed = prescribed_strategy.action_for(cost_type)
    eu_portable = expected_utility_portable_with_incentive(q, cost, tau)
    eu_locked = expected_utility_locked(q)
    prescribed_utility = (
        eu_portable if prescribed is Action.PORTABLE else eu_locked
    )
    alternative_utility = (
        eu_locked if prescribed is Action.PORTABLE else eu_portable
    )
    deviation_gain = max(0.0, alternative_utility - prescribed_utility)
    return {
        "type": cost_type.value,
        "cost": cost,
        "q": q,
        "tau": tau,
        "prescribed_action": prescribed.value,
        "eu_portable": eu_portable,
        "eu_locked": eu_locked,
        "deviation_gain": deviation_gain,
        "prescribed_is_best_response": deviation_gain <= tolerance,
    }


def evaluate_mechanism_profile(
    strategy_a: PureStrategy,
    strategy_b: PureStrategy,
    parameters: ModelParameters,
    tau: float,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict[str, object]:
    """Evaluate all four type-level constraints for one mechanism profile."""

    if not parameters.has_full_support:
        raise ValueError("Mechanism profile checks require 0 < p_low < 1.")
    _validate_incentive(tau)
    checks_a = {
        cost_type.value: mechanism_type_incentive_check(
            strategy_a, strategy_b, cost_type, parameters, tau, tolerance
        )
        for cost_type in CostType
    }
    checks_b = {
        cost_type.value: mechanism_type_incentive_check(
            strategy_b, strategy_a, cost_type, parameters, tau, tolerance
        )
        for cost_type in CostType
    }
    all_checks = [*checks_a.values(), *checks_b.values()]

    def expected_payoff(
        own_strategy: PureStrategy, rival_strategy: PureStrategy
    ) -> float:
        q = rival_portability_probability(rival_strategy, parameters.p_low)
        total = 0.0
        for cost_type, probability in (
            (CostType.LOW, parameters.p_low),
            (CostType.HIGH, 1.0 - parameters.p_low),
        ):
            action = own_strategy.action_for(cost_type)
            utility = (
                expected_utility_portable_with_incentive(
                    q, parameters.cost(cost_type), tau
                )
                if action is Action.PORTABLE
                else expected_utility_locked(q)
            )
            total += probability * utility
        return total

    return {
        "p": parameters.p_low,
        "tau": tau,
        "strategy_A": strategy_a.name,
        "strategy_B": strategy_b.name,
        "symmetric": strategy_a.name == strategy_b.name,
        "is_bne": all(bool(row["prescribed_is_best_response"]) for row in all_checks),
        "max_deviation_gain": max(float(row["deviation_gain"]) for row in all_checks),
        "expected_payoff_A": expected_payoff(strategy_a, strategy_b),
        "expected_payoff_B": expected_payoff(strategy_b, strategy_a),
        "A_checks": checks_a,
        "B_checks": checks_b,
    }


def enumerate_mechanism_profile_diagnostics(
    parameters: ModelParameters,
    tau: float,
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[dict[str, object]]:
    """Evaluate all 16 pure strategy profiles under the mechanism."""

    return [
        evaluate_mechanism_profile(a, b, parameters, tau, tolerance)
        for a, b in product(PURE_STRATEGIES, repeat=2)
    ]


def enumerate_mechanism_pure_bne(
    parameters: ModelParameters,
    tau: float,
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[tuple[str, str]]:
    """Return every pure BNE under the portability incentive."""

    return [
        (str(row["strategy_A"]), str(row["strategy_B"]))
        for row in enumerate_mechanism_profile_diagnostics(
            parameters, tau, tolerance
        )
        if row["is_bne"]
    ]


def incentive_grid() -> list[float]:
    """Return tau=0.00,0.05,...,2.50 using integer construction."""

    return [index / 100 for index in range(0, 251, 5)]


def mechanism_sweep(
    parameters: ModelParameters,
    p_values: Iterable[float],
    tau_values: Iterable[float] | None = None,
) -> pd.DataFrame:
    """Evaluate all profiles over a deterministic (p,tau) grid."""

    if tau_values is None:
        tau_values = incentive_grid()
    rows: list[dict[str, object]] = []
    for p_low in p_values:
        point = ModelParameters(parameters.c_low, parameters.c_high, p_low)
        for tau in tau_values:
            for result in enumerate_mechanism_profile_diagnostics(point, tau):
                rows.append(
                    {
                        key: result[key]
                        for key in (
                            "p", "tau", "strategy_A", "strategy_B", "symmetric",
                            "is_bne", "max_deviation_gain", "expected_payoff_A",
                            "expected_payoff_B",
                        )
                    }
                )
    return pd.DataFrame(rows)


def _plot_equilibrium_region(
    sweep: pd.DataFrame,
    strategy: PureStrategy,
    output_path: Path,
    parameters: ModelParameters,
) -> Path:
    subset = sweep[
        (sweep["strategy_A"] == strategy.name)
        & (sweep["strategy_B"] == strategy.name)
    ]
    pivot = subset.pivot(index="tau", columns="p", values="is_bne").sort_index()
    figure, axis = plt.subplots(figsize=(8.8, 5.2))
    image = axis.imshow(
        pivot.astype(int).to_numpy(),
        aspect="auto", interpolation="nearest", origin="lower",
        extent=[pivot.columns.min(), pivot.columns.max(), pivot.index.min(), pivot.index.max()],
    )
    p_line = np.linspace(0.01, 0.99, 300)
    if strategy is PL:
        lower = 1.0 + parameters.c_low - 2.0 * p_line
        upper = 1.0 + parameters.c_high - 2.0 * p_line
        axis.plot(p_line, lower, "--", linewidth=1.6, label=r"Low-type boundary $\tau=1+c_L-2p$")
        axis.plot(p_line, upper, ":", linewidth=1.6, label=r"High-type lock boundary $\tau=1+c_H-2p$")
        title = r"Pure-BNE region for symmetric $(PL,PL)$"
    else:
        axis.axhline(
            lock_in_low_type_threshold(parameters.c_low),
            linestyle="--", linewidth=1.6,
            label=r"Low-type indifference $\tau=1+c_L=1.2$",
        )
        axis.axhline(
            lock_in_high_type_threshold(parameters.c_high),
            linestyle=":", linewidth=1.6,
            label=r"High-type indifference $\tau=1+c_H=2.2$",
        )
        title = r"Pure-BNE region for symmetric $(LL,LL)$"
    axis.set_xlim(0.01, 0.99)
    axis.set_ylim(0.0, 2.5)
    axis.set_xlabel("Prior probability p that a platform is low-cost")
    axis.set_ylabel(r"Verified portability incentive $\tau$")
    axis.set_title(title)
    axis.legend(loc="upper right")
    colorbar = figure.colorbar(image, ax=axis, ticks=[0, 1])
    colorbar.set_label("Computed pure-BNE indicator")
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output_path


def plot_pl_equilibrium_region(
    sweep: pd.DataFrame, output_path: Path, parameters: ModelParameters
) -> Path:
    return _plot_equilibrium_region(sweep, PL, output_path, parameters)


def plot_ll_equilibrium_region(
    sweep: pd.DataFrame, output_path: Path, parameters: ModelParameters
) -> Path:
    return _plot_equilibrium_region(sweep, LL, output_path, parameters)
