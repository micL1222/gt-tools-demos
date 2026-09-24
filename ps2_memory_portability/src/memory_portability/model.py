"""Core Bayesian game for strategic memory portability.

This module is the source of truth for the Phase 2 benchmark.  Payoffs are
normalized theoretical quantities; they are not estimates of company profits.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import product
from typing import Iterable


DEFAULT_TOLERANCE = 1e-10


class CostType(str, Enum):
    """A platform's privately observed implementation-cost type."""

    LOW = "Low"
    HIGH = "High"


class Action(str, Enum):
    """A platform's portability action."""

    PORTABLE = "P"
    LOCKED = "L"


@dataclass(frozen=True)
class PureStrategy:
    """A complete action plan ordered as (low-type action, high-type action)."""

    name: str
    low_action: Action
    high_action: Action

    def action_for(self, cost_type: CostType) -> Action:
        return self.low_action if cost_type is CostType.LOW else self.high_action

    def as_dict(self) -> dict[str, str]:
        return {
            CostType.LOW.value: self.low_action.value,
            CostType.HIGH.value: self.high_action.value,
        }


LL = PureStrategy("LL", Action.LOCKED, Action.LOCKED)
PL = PureStrategy("PL", Action.PORTABLE, Action.LOCKED)
LP = PureStrategy("LP", Action.LOCKED, Action.PORTABLE)
PP = PureStrategy("PP", Action.PORTABLE, Action.PORTABLE)
PURE_STRATEGIES: tuple[PureStrategy, ...] = (LL, PL, LP, PP)
STRATEGY_BY_NAME = {strategy.name: strategy for strategy in PURE_STRATEGIES}


@dataclass(frozen=True)
class ModelParameters:
    """Parameters of the symmetric two-platform Bayesian game."""

    c_low: float = 0.2
    c_high: float = 1.2
    p_low: float = 0.7

    def __post_init__(self) -> None:
        if not 0 <= self.p_low <= 1:
            raise ValueError("p_low must lie in [0, 1].")
        if self.c_low < 0:
            raise ValueError("c_low must be nonnegative.")
        if self.c_low >= self.c_high:
            raise ValueError("The model requires c_low < c_high.")

    @property
    def prior_status(self) -> str:
        if self.p_low == 0:
            return "boundary_high_type_only"
        if self.p_low == 1:
            return "boundary_low_type_only"
        return "full_support"

    @property
    def has_full_support(self) -> bool:
        return self.prior_status == "full_support"

    def cost(self, cost_type: CostType) -> float:
        return self.c_low if cost_type is CostType.LOW else self.c_high


def payoff(own_action: Action, rival_action: Action, own_cost: float) -> float:
    """Return the platform's normalized benchmark payoff.

    Portable/Portable yields ``2 - cost``; unilateral Portable yields
    ``-1 - cost``; Locked against Portable yields 1; mutual Locked yields 0.
    """

    if own_action is Action.PORTABLE:
        return (2.0 if rival_action is Action.PORTABLE else -1.0) - own_cost
    return 1.0 if rival_action is Action.PORTABLE else 0.0


def expected_utility_portable(q: float, cost: float) -> float:
    """Expected utility of Portable: q(2-c)+(1-q)(-1-c)=3q-1-c."""

    _validate_probability(q, "q")
    return 3.0 * q - 1.0 - cost


def expected_utility_locked(q: float) -> float:
    """Expected utility of Locked: q."""

    _validate_probability(q, "q")
    return q


def expected_utility(action: Action, q: float, cost: float) -> float:
    """Expected utility of an action against rival portability probability q."""

    if action is Action.PORTABLE:
        return expected_utility_portable(q, cost)
    return expected_utility_locked(q)


def portability_advantage(q: float, cost: float) -> float:
    """EU(Portable)-EU(Locked), equal to 2q-1-cost."""

    return expected_utility_portable(q, cost) - expected_utility_locked(q)


def portable_is_best_response(
    q: float, cost: float, tolerance: float = DEFAULT_TOLERANCE
) -> bool:
    """Whether Portable is a weak best response."""

    return portability_advantage(q, cost) >= -tolerance


def rival_portability_probability(strategy: PureStrategy, p_low: float) -> float:
    """Probability that a rival following ``strategy`` chooses Portable."""

    _validate_probability(p_low, "p_low")
    low = 1.0 if strategy.low_action is Action.PORTABLE else 0.0
    high = 1.0 if strategy.high_action is Action.PORTABLE else 0.0
    return p_low * low + (1.0 - p_low) * high


def type_incentive_check(
    prescribed_strategy: PureStrategy,
    rival_strategy: PureStrategy,
    cost_type: CostType,
    parameters: ModelParameters,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict[str, object]:
    """Check one type's prescribed action against its only alternative."""

    q = rival_portability_probability(rival_strategy, parameters.p_low)
    cost = parameters.cost(cost_type)
    prescribed = prescribed_strategy.action_for(cost_type)
    alternative = (
        Action.LOCKED if prescribed is Action.PORTABLE else Action.PORTABLE
    )
    eu_portable = expected_utility_portable(q, cost)
    eu_locked = expected_utility_locked(q)
    prescribed_utility = expected_utility(prescribed, q, cost)
    alternative_utility = expected_utility(alternative, q, cost)
    deviation_gain = max(0.0, alternative_utility - prescribed_utility)
    best_actions: list[str] = []
    best_value = max(eu_portable, eu_locked)
    if eu_portable >= best_value - tolerance:
        best_actions.append(Action.PORTABLE.value)
    if eu_locked >= best_value - tolerance:
        best_actions.append(Action.LOCKED.value)
    return {
        "type": cost_type.value,
        "cost": cost,
        "q": q,
        "prescribed_action": prescribed.value,
        "alternative_action": alternative.value,
        "eu_portable": eu_portable,
        "eu_locked": eu_locked,
        "prescribed_utility": prescribed_utility,
        "alternative_utility": alternative_utility,
        "deviation_gain": deviation_gain,
        "best_actions": best_actions,
        "prescribed_is_best_response": deviation_gain <= tolerance,
    }


def evaluate_pure_profile(
    strategy_a: PureStrategy,
    strategy_b: PureStrategy,
    parameters: ModelParameters,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict[str, object]:
    """Evaluate all four type-level incentive constraints at one profile.

    The formal checker is restricted to full-support priors.  At p=0 or p=1,
    a zero-probability type's action is not disciplined by the ordinary
    ex-ante Bayesian game, so callers must treat those cases separately.
    """

    if not parameters.has_full_support:
        raise ValueError(
            "Pure-BNE profile checks require 0 < p_low < 1; "
            f"received {parameters.prior_status}."
        )
    checks_a = {
        cost_type.value: type_incentive_check(
            strategy_a, strategy_b, cost_type, parameters, tolerance
        )
        for cost_type in CostType
    }
    checks_b = {
        cost_type.value: type_incentive_check(
            strategy_b, strategy_a, cost_type, parameters, tolerance
        )
        for cost_type in CostType
    }
    all_checks = [*checks_a.values(), *checks_b.values()]
    q_a = rival_portability_probability(strategy_b, parameters.p_low)
    q_b = rival_portability_probability(strategy_a, parameters.p_low)
    expected_payoff_a = sum(
        probability
        * expected_utility(strategy_a.action_for(cost_type), q_a, parameters.cost(cost_type))
        for cost_type, probability in (
            (CostType.LOW, parameters.p_low),
            (CostType.HIGH, 1.0 - parameters.p_low),
        )
    )
    expected_payoff_b = sum(
        probability
        * expected_utility(strategy_b.action_for(cost_type), q_b, parameters.cost(cost_type))
        for cost_type, probability in (
            (CostType.LOW, parameters.p_low),
            (CostType.HIGH, 1.0 - parameters.p_low),
        )
    )
    return {
        "strategy_A": strategy_a.name,
        "strategy_B": strategy_b.name,
        "symmetric": strategy_a.name == strategy_b.name,
        "is_bne": all(bool(check["prescribed_is_best_response"]) for check in all_checks),
        "max_deviation_gain": max(float(check["deviation_gain"]) for check in all_checks),
        "expected_payoff_A": expected_payoff_a,
        "expected_payoff_B": expected_payoff_b,
        "A_checks": checks_a,
        "B_checks": checks_b,
    }


def enumerate_pure_profile_diagnostics(
    parameters: ModelParameters,
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[dict[str, object]]:
    """Evaluate all 4 x 4 pure type-contingent strategy profiles."""

    return [
        evaluate_pure_profile(strategy_a, strategy_b, parameters, tolerance)
        for strategy_a, strategy_b in product(PURE_STRATEGIES, repeat=2)
    ]


def enumerate_pure_bne(
    parameters: ModelParameters,
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[tuple[str, str]]:
    """Return every pure BNE as readable ``(strategy_A, strategy_B)`` names."""

    return [
        (str(row["strategy_A"]), str(row["strategy_B"]))
        for row in enumerate_pure_profile_diagnostics(parameters, tolerance)
        if row["is_bne"]
    ]


def symmetric_low_type_mixed_equilibrium(
    parameters: ModelParameters,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict[str, object]:
    """Calculate the symmetric low-type mixing candidate.

    High types are fixed at Locked.  Low-type indifference requires
    q*=(1+c_low)/2 and therefore x*=q*/p.  The helper labels only 0<x*<1 as
    an interior mixed equilibrium; x*=1 is a pure-strategy boundary.
    """

    q_star = (1.0 + parameters.c_low) / 2.0
    if not parameters.has_full_support:
        return {
            "p": parameters.p_low,
            "q_star": q_star,
            "x_star": None,
            "x_star_exact": None,
            "interior_mixed_exists": False,
            "collapses_to_pure_pl": False,
            "high_type_prefers_locked": None,
            "status": parameters.prior_status,
            "formula": "x* = (1 + c_low) / (2p)",
        }
    x_star = q_star / parameters.p_low
    high_advantage = portability_advantage(q_star, parameters.c_high)
    high_locked = high_advantage <= tolerance
    interior = tolerance < x_star < 1.0 - tolerance and high_locked
    collapses = abs(x_star - 1.0) <= tolerance and high_locked
    exact = (
        (Fraction(1) + Fraction(str(parameters.c_low)))
        / (2 * Fraction(str(parameters.p_low)))
    )
    if interior:
        status = "interior_symmetric_type_specific_mixed_equilibrium"
    elif collapses:
        status = "boundary_x_equals_one_pure_pl"
    elif x_star > 1.0 + tolerance:
        status = "infeasible_x_above_one"
    elif q_star > 1.0 + tolerance:
        status = "infeasible_q_above_one"
    elif not high_locked:
        status = "high_type_not_willing_to_lock"
    else:
        status = "no_distinct_interior_mixed_equilibrium"
    return {
        "p": parameters.p_low,
        "q_star": q_star,
        "x_star": x_star,
        "x_star_exact": str(exact),
        "interior_mixed_exists": interior,
        "collapses_to_pure_pl": collapses,
        "high_type_prefers_locked": high_locked,
        "high_type_portability_advantage": high_advantage,
        "status": status,
        "formula": "x* = (1 + c_low) / (2p)",
    }


def strategy_names(strategies: Iterable[PureStrategy] = PURE_STRATEGIES) -> list[str]:
    """Return strategy names in the canonical LL, PL, LP, PP order."""

    return [strategy.name for strategy in strategies]


def _validate_probability(value: float, label: str) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{label} must lie in [0, 1].")
