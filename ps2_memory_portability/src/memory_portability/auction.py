"""Stylized single-user allocation mechanisms for the Phase 3 application."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_SEED = 20603
DEFAULT_N = 100_000
RESERVES = {"locked": 0.5, "portable": 0.2}


def _validate_value_and_reserve(value: float, reserve: float) -> None:
    if not 0 <= value <= 1:
        raise ValueError("The Uniform(0,1) benchmark requires value in [0, 1].")
    if not 0 <= reserve <= 1:
        raise ValueError("The benchmark reserve must lie in [0, 1].")


def first_price_equilibrium_bid(value: float, reserve: float) -> float | None:
    """Symmetric equilibrium bid, or None for a type below the reserve."""

    _validate_value_and_reserve(value, reserve)
    if value < reserve:
        return None
    return (value * value + reserve * reserve) / (2.0 * value)


def second_price_truthful_bid(value: float) -> float:
    """Truthful benchmark bid in the second-price mechanism."""

    if not 0 <= value <= 1:
        raise ValueError("The Uniform(0,1) benchmark requires value in [0, 1].")
    return value


def _winner_from_bids(
    bid_a: float | None, bid_b: float | None, reserve: float
) -> str | None:
    eligible_a = bid_a is not None and bid_a >= reserve
    eligible_b = bid_b is not None and bid_b >= reserve
    if not eligible_a and not eligible_b:
        return None
    if eligible_a and (not eligible_b or float(bid_a) >= float(bid_b)):
        return "A"
    return "B"


def first_price_outcome(value_a: float, value_b: float, reserve: float) -> dict[str, object]:
    """Apply the one-shot first-price rule; exact eligible ties go to A."""

    bid_a = first_price_equilibrium_bid(value_a, reserve)
    bid_b = first_price_equilibrium_bid(value_b, reserve)
    winner = _winner_from_bids(bid_a, bid_b, reserve)
    payment = 0.0 if winner is None else float(bid_a if winner == "A" else bid_b)
    winner_value = 0.0 if winner is None else (value_a if winner == "A" else value_b)
    return {
        "bid_A": bid_a,
        "bid_B": bid_b,
        "winner": winner,
        "no_allocation": winner is None,
        "payment": payment,
        "winner_value": winner_value,
        "winner_utility": winner_value - payment,
    }


def second_price_outcome(value_a: float, value_b: float, reserve: float) -> dict[str, object]:
    """Apply the one-shot second-price rule; exact eligible ties go to A."""

    _validate_value_and_reserve(value_a, reserve)
    _validate_value_and_reserve(value_b, reserve)
    bid_a = second_price_truthful_bid(value_a)
    bid_b = second_price_truthful_bid(value_b)
    winner = _winner_from_bids(bid_a, bid_b, reserve)
    if winner is None:
        payment = 0.0
        winner_value = 0.0
    elif winner == "A":
        payment = max(bid_b, reserve)
        winner_value = value_a
    else:
        payment = max(bid_a, reserve)
        winner_value = value_b
    return {
        "bid_A": bid_a,
        "bid_B": bid_b,
        "winner": winner,
        "no_allocation": winner is None,
        "payment": payment,
        "winner_value": winner_value,
        "winner_utility": winner_value - payment,
    }


def analytical_allocation_probability(reserve: float) -> float:
    """Return 1-r^2 for two iid Uniform(0,1) values."""

    if not 0 <= reserve <= 1:
        raise ValueError("reserve must lie in [0, 1].")
    return 1.0 - reserve * reserve


def generate_valuation_sample(
    n: int = DEFAULT_N, seed: int = DEFAULT_SEED
) -> tuple[np.ndarray, np.ndarray]:
    """Generate one common deterministic sample for every condition."""

    if n <= 0:
        raise ValueError("n must be positive.")
    generator = np.random.default_rng(seed)
    return generator.uniform(size=n), generator.uniform(size=n)


def _condition_frame(
    values_a: np.ndarray,
    values_b: np.ndarray,
    mechanism: str,
    reserve_regime: str,
    reserve: float,
) -> pd.DataFrame:
    if values_a.shape != values_b.shape:
        raise ValueError("values_a and values_b must have the same shape.")
    eligible_a = values_a >= reserve
    eligible_b = values_b >= reserve
    if mechanism == "first_price":
        bids_a = np.where(
            eligible_a,
            (values_a * values_a + reserve * reserve) / (2.0 * values_a),
            np.nan,
        )
        bids_b = np.where(
            eligible_b,
            (values_b * values_b + reserve * reserve) / (2.0 * values_b),
            np.nan,
        )
    elif mechanism == "second_price":
        bids_a = values_a.copy()
        bids_b = values_b.copy()
    else:
        raise ValueError("mechanism must be 'first_price' or 'second_price'.")

    allocated = eligible_a | eligible_b
    a_wins = eligible_a & (~eligible_b | (bids_a >= bids_b))
    b_wins = allocated & ~a_wins
    winner = np.where(a_wins, "A", np.where(b_wins, "B", "None"))
    if mechanism == "first_price":
        payment = np.where(a_wins, bids_a, np.where(b_wins, bids_b, 0.0))
    else:
        payment = np.where(
            a_wins,
            np.maximum(bids_b, reserve),
            np.where(b_wins, np.maximum(bids_a, reserve), 0.0),
        )
    winner_value = np.where(
        a_wins, values_a, np.where(b_wins, values_b, 0.0)
    )
    highest_value = np.where(values_a >= values_b, "A", "B")
    highest_won = allocated & (winner == highest_value)
    return pd.DataFrame(
        {
            "sample_id": np.arange(values_a.size),
            "v_A": values_a,
            "v_B": values_b,
            "mechanism": mechanism,
            "reserve_regime": reserve_regime,
            "reserve": reserve,
            "bid_A": bids_a,
            "bid_B": bids_b,
            "winner": winner,
            "no_allocation": ~allocated,
            "payment": payment,
            "winner_value": winner_value,
            "winner_utility": winner_value - payment,
            "user_compensation": payment,
            "highest_value_platform": highest_value,
            "highest_value_platform_won": highest_won,
            "allocative_efficiency": highest_won.astype(float),
            "efficient_given_allocation": np.where(allocated, highest_won, np.nan),
        }
    )


def simulate_auction_conditions(
    n: int = DEFAULT_N,
    seed: int = DEFAULT_SEED,
    reserves: dict[str, float] = RESERVES,
) -> pd.DataFrame:
    """Simulate all four conditions with the same valuation profiles."""

    values_a, values_b = generate_valuation_sample(n=n, seed=seed)
    frames = [
        _condition_frame(values_a, values_b, mechanism, regime, reserve)
        for mechanism in ("first_price", "second_price")
        for regime, reserve in reserves.items()
    ]
    return pd.concat(frames, ignore_index=True)


def auction_summary(raw: pd.DataFrame) -> pd.DataFrame:
    """Summarize allocation, payments, utility, and efficiency by condition."""

    rows: list[dict[str, object]] = []
    for (mechanism, regime, reserve), group in raw.groupby(
        ["mechanism", "reserve_regime", "reserve"], sort=True
    ):
        allocated = group[~group["no_allocation"]]
        rows.append(
            {
                "mechanism": mechanism,
                "reserve_regime": regime,
                "reserve": reserve,
                "n": len(group),
                "allocation_probability": 1.0 - group["no_allocation"].mean(),
                "no_allocation_probability": group["no_allocation"].mean(),
                "analytical_allocation_probability": analytical_allocation_probability(reserve),
                "allocation_probability_absolute_error": abs(
                    1.0 - group["no_allocation"].mean()
                    - analytical_allocation_probability(reserve)
                ),
                "expected_payment_unconditional": group["payment"].mean(),
                "expected_payment_conditional": allocated["payment"].mean(),
                "expected_winner_utility_unconditional": group["winner_utility"].mean(),
                "expected_winner_utility_conditional": allocated["winner_utility"].mean(),
                "probability_highest_value_platform_wins": group[
                    "highest_value_platform_won"
                ].mean(),
                "efficiency_conditional_on_allocation": allocated[
                    "efficient_given_allocation"
                ].mean(),
            }
        )
    return pd.DataFrame(rows)


def validate_common_sample(raw: pd.DataFrame) -> bool:
    """Verify identical valuation profiles were used in every condition."""

    reference: pd.DataFrame | None = None
    for _, group in raw.groupby(["mechanism", "reserve_regime"], sort=True):
        values = group.sort_values("sample_id")[["sample_id", "v_A", "v_B"]].reset_index(drop=True)
        if reference is None:
            reference = values
        elif not values.equals(reference):
            return False
    return True


def plot_auction_allocation_probability(
    summary: pd.DataFrame, output_path: Path
) -> Path:
    pivot = summary.pivot(
        index="reserve_regime", columns="mechanism", values="allocation_probability"
    ).reindex(["locked", "portable"])
    pivot = pivot.rename(
        columns={"first_price": "First price", "second_price": "Second price"}
    )
    axis = pivot.plot(kind="bar", figsize=(8.0, 4.8), ylim=(0, 1), rot=0)
    axis.set_xlabel("Switching-hurdle regime")
    axis.set_ylabel("Simulated allocation probability")
    axis.set_title("Lower switching hurdle expands feasible user reallocation")
    axis.legend(title="Mechanism")
    axis.figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    axis.figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(axis.figure)
    return output_path


def plot_auction_expected_payment(summary: pd.DataFrame, output_path: Path) -> Path:
    pivot = summary.pivot(
        index="reserve_regime",
        columns="mechanism",
        values="expected_payment_unconditional",
    ).reindex(["locked", "portable"])
    pivot = pivot.rename(
        columns={"first_price": "First price", "second_price": "Second price"}
    )
    axis = pivot.plot(kind="bar", figsize=(8.0, 4.8), rot=0)
    axis.set_xlabel("Switching-hurdle regime")
    axis.set_ylabel("Expected payment (unconditional)")
    axis.set_title("Expected user compensation across allocation mechanisms")
    axis.legend(title="Mechanism")
    axis.figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    axis.figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(axis.figure)
    return output_path


def plot_auction_bid_functions(output_path: Path) -> Path:
    values = np.linspace(0.001, 1.0, 1000)
    figure, axis = plt.subplots(figsize=(8.0, 4.8))
    for regime, reserve in RESERVES.items():
        eligible = values >= reserve
        bids = (values[eligible] ** 2 + reserve ** 2) / (2.0 * values[eligible])
        axis.plot(values[eligible], bids, linewidth=2, label=f"First price, {regime} r={reserve}")
    axis.plot(values, values, "--", linewidth=1.8, label="Second price, truthful b(v)=v")
    axis.set_xlabel("Normalized platform value v")
    axis.set_ylabel("Eligible bid b(v)")
    axis.set_title("Benchmark bidding strategies and switching-hurdle reserves")
    axis.legend(loc="upper left")
    axis.grid(alpha=0.2)
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output_path
