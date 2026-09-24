#!/usr/bin/env python3
"""Generate and validate all Phase 3 welfare, mechanism, and auction results."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from memory_portability.analysis import full_support_prior_grid, write_csv, write_json  # noqa: E402
from memory_portability.auction import (  # noqa: E402
    DEFAULT_N,
    DEFAULT_SEED,
    RESERVES,
    auction_summary,
    plot_auction_allocation_probability,
    plot_auction_bid_functions,
    plot_auction_expected_payment,
    simulate_auction_conditions,
    validate_common_sample,
)
from memory_portability.mechanism import (  # noqa: E402
    enumerate_mechanism_pure_bne,
    incentive_grid,
    lock_in_high_type_threshold,
    lock_in_low_type_threshold,
    mechanism_sweep,
    minimum_incentive_for_pl,
    pl_prior_threshold,
    plot_ll_equilibrium_region,
    plot_pl_equilibrium_region,
    portability_advantage_with_incentive,
)
from memory_portability.model import (  # noqa: E402
    LL,
    PL,
    PP,
    ModelParameters,
    enumerate_pure_bne,
)
from memory_portability.social_choice import (  # noqa: E402
    evaluate_ex_ante_welfare,
    mobility_value_grid,
    plot_social_welfare_by_m,
    social_choice_table,
    welfare_ranking_changes,
)


BENCHMARK = ModelParameters(c_low=0.2, c_high=1.2, p_low=0.7)
EXPECTED_PHASE2_BNE = {("LL", "LL"), ("PL", "PL")}
SOCIAL_BENCHMARK_M = 1.0


def assert_phase2_regression() -> None:
    observed = set(enumerate_pure_bne(BENCHMARK))
    if observed != EXPECTED_PHASE2_BNE:
        raise AssertionError(f"Phase 2 pure BNE changed: {sorted(observed)}")


def validate_social_choice(frame) -> None:
    benchmark = {
        profile: evaluate_ex_ante_welfare(
            strategy, strategy, BENCHMARK, SOCIAL_BENCHMARK_M
        )
        for profile, strategy in (("LL", LL), ("PL", PL), ("PP", PP))
    }
    expected = {
        "LL": (0.0, 0.0, 0.0),
        "PL": (1.68, 0.49, 2.17),
        "PP": (3.0, 1.0, 4.0),
    }
    for profile, targets in expected.items():
        actual = benchmark[profile]
        observed = (
            actual["expected_total_platform_payoff"],
            actual["expected_user_mobility_payoff"],
            actual["expected_social_welfare"],
        )
        if not all(math.isclose(x, y, abs_tol=1e-12) for x, y in zip(observed, targets)):
            raise AssertionError(
                f"Social-choice benchmark mismatch for {profile}: {observed} != {targets}"
            )
    if len(frame) != 41 * 3:
        raise AssertionError(f"Unexpected social-choice sweep size: {len(frame)}")


def validate_mechanism_sweep(frame) -> None:
    pl_rows = frame[
        (frame["strategy_A"] == "PL") & (frame["strategy_B"] == "PL")
    ]
    computed_pl = pl_rows["is_bne"].to_numpy()
    analytical_pl = (
        (pl_rows["tau"] >= 1.0 + BENCHMARK.c_low - 2.0 * pl_rows["p"] - 1e-10)
        & (pl_rows["tau"] <= 1.0 + BENCHMARK.c_high - 2.0 * pl_rows["p"] + 1e-10)
    ).to_numpy()
    if not (computed_pl == analytical_pl).all():
        raise AssertionError("Computed PL mechanism region disagrees with its two type constraints.")

    ll_rows = frame[
        (frame["strategy_A"] == "LL") & (frame["strategy_B"] == "LL")
    ]
    analytical_ll = (
        ll_rows["tau"] <= lock_in_low_type_threshold(BENCHMARK.c_low) + 1e-10
    ).to_numpy()
    if not (ll_rows["is_bne"].to_numpy() == analytical_ll).all():
        raise AssertionError("Computed LL mechanism region disagrees with its threshold.")


def mechanism_threshold_payload(frame) -> dict[str, object]:
    checks = {}
    p04 = ModelParameters(BENCHMARK.c_low, BENCHMARK.c_high, 0.4)
    for tau in (0.39, 0.40, 0.41):
        checks[f"p_0.4_tau_{tau:.2f}"] = {
            "pure_bne": [list(row) for row in enumerate_mechanism_pure_bne(p04, tau)],
            "pl_pl_is_bne": ("PL", "PL") in enumerate_mechanism_pure_bne(p04, tau),
        }
    for tau in (1.19, 1.20, 1.21):
        checks[f"benchmark_tau_{tau:.2f}"] = {
            "pure_bne": [list(row) for row in enumerate_mechanism_pure_bne(BENCHMARK, tau)],
            "ll_ll_is_bne": ("LL", "LL") in enumerate_mechanism_pure_bne(BENCHMARK, tau),
        }
    asymmetric = frame[
        frame["is_bne"] & (frame["strategy_A"] != frame["strategy_B"])
    ]
    return {
        "parameters": {
            "c_low": BENCHMARK.c_low,
            "c_high": BENCHMARK.c_high,
            "benchmark_p": BENCHMARK.p_low,
        },
        "formulas": {
            "portable_expected_utility": "EU_tau(P|c)=3q-1-c+tau",
            "locked_expected_utility": "EU_tau(L|c)=q",
            "portable_best_response": "2q-1-c+tau>=0",
            "pl_prior_lower_threshold": "p>=(1+c_low-tau)/2",
            "pl_high_type_lock_upper_condition": "tau<=1+c_high-2p",
            "minimum_incentive_for_pl": "max(0,1+c_low-2p)",
        },
        "analytical_thresholds": {
            "pl_prior_threshold_at_tau_0": pl_prior_threshold(BENCHMARK.c_low, 0.0),
            "minimum_tau_for_pl_at_p_0.4": round(
                minimum_incentive_for_pl(0.4, BENCHMARK.c_low), 12
            ),
            "minimum_tau_for_pl_at_p_0.7": round(
                minimum_incentive_for_pl(0.7, BENCHMARK.c_low), 12
            ),
            "ll_low_type_indifference_tau": lock_in_low_type_threshold(BENCHMARK.c_low),
            "ll_high_type_indifference_tau": lock_in_high_type_threshold(BENCHMARK.c_high),
            "pl_high_type_lock_upper_tau_at_benchmark_p": round(
                1.0 + BENCHMARK.c_high - 2.0 * BENCHMARK.p_low, 12
            ),
            "pp_high_type_indifference_tau": round(
                max(0.0, BENCHMARK.c_high - 1.0), 12
            ),
        },
        "weak_best_response_note": "At tau=1+c_low, LL remains a weak pure BNE; it disappears immediately above that boundary.",
        "benchmark_checks": checks,
        "tau_zero_phase2_bne": [
            list(row) for row in enumerate_mechanism_pure_bne(BENCHMARK, 0.0)
        ],
        "high_type_advantage_against_ll": {
            f"tau_{tau:.2f}": round(
                portability_advantage_with_incentive(
                    0.0, BENCHMARK.c_high, tau
                ),
                12,
            )
            for tau in (2.19, 2.20, 2.21)
        },
        "grid": {
            "p_min": 0.01,
            "p_max": 0.99,
            "p_step": 0.01,
            "tau_min": 0.0,
            "tau_max": 2.5,
            "tau_step": 0.05,
            "rows": len(frame),
        },
        "asymmetric_pure_bne_rows": len(asymmetric),
        "asymmetric_profile_names": sorted(
            {tuple(row) for row in zip(asymmetric["strategy_A"], asymmetric["strategy_B"])}
        ),
    }


def auction_validation_payload(raw, summary) -> dict[str, object]:
    conditions = []
    for row in summary.itertuples(index=False):
        conditions.append(
            {
                "mechanism": row.mechanism,
                "reserve_regime": row.reserve_regime,
                "reserve": row.reserve,
                "analytical_allocation_probability": row.analytical_allocation_probability,
                "simulated_allocation_probability": row.allocation_probability,
                "absolute_error": row.allocation_probability_absolute_error,
            }
        )
    payment_pivot = summary.pivot(
        index="reserve_regime",
        columns="mechanism",
        values="expected_payment_unconditional",
    )
    return {
        "seed": DEFAULT_SEED,
        "N": DEFAULT_N,
        "value_distribution": "independent Uniform(0,1) normalized private values",
        "reserve_values": RESERVES,
        "scarce_resource": "one user's primary AI-assistant slot for the next service period",
        "tie_break": "Platform A wins an exact eligible tie",
        "stopping_rule": "Collect one bid per platform, apply the reserve, allocate at most one slot, compute payment, terminate.",
        "bidding_formulas": {
            "first_price": "b(v;r)=(v^2+r^2)/(2v) for v>=r; no eligible bid for v<r",
            "second_price": "b(v)=v",
        },
        "analytical_allocation_probability": "1-r^2",
        "same_valuation_sample_across_all_conditions": validate_common_sample(raw),
        "conditions": conditions,
        "unconditional_expected_payment_gap_first_minus_second": {
            regime: float(
                payment_pivot.loc[regime, "first_price"]
                - payment_pivot.loc[regime, "second_price"]
            )
            for regime in payment_pivot.index
        },
        "raw_rows_generated_in_memory": len(raw),
        "raw_file_committed": False,
        "sample_file_rows": 400,
    }


def main() -> None:
    print("Phase 3 welfare, mechanism, and auction regeneration")
    assert_phase2_regression()
    print("✓ Phase 2 benchmark preserved")

    outputs = PROJECT_ROOT / "outputs"
    figures = PROJECT_ROOT / "figures"

    social_sweep = social_choice_table(BENCHMARK, mobility_value_grid())
    validate_social_choice(social_sweep)
    social_benchmark = social_choice_table(BENCHMARK, [SOCIAL_BENCHMARK_M])
    write_csv(social_benchmark, outputs / "social_choice_benchmark.csv")
    write_csv(social_sweep, outputs / "social_choice_m_sweep.csv")
    plot_social_welfare_by_m(
        social_sweep, figures / "social_welfare_by_m.png"
    )
    ranking_changes = welfare_ranking_changes(social_sweep)
    print(f"✓ Social-choice sweep complete; ranking changes on grid: {len(ranking_changes)}")

    mechanism_frame = mechanism_sweep(
        BENCHMARK, full_support_prior_grid(), incentive_grid()
    )
    validate_mechanism_sweep(mechanism_frame)
    write_csv(mechanism_frame, outputs / "mechanism_p_tau_sweep.csv")
    thresholds = mechanism_threshold_payload(mechanism_frame)
    write_json(thresholds, outputs / "mechanism_thresholds.json")
    plot_pl_equilibrium_region(
        mechanism_frame,
        figures / "pl_equilibrium_region_with_incentive.png",
        BENCHMARK,
    )
    plot_ll_equilibrium_region(
        mechanism_frame,
        figures / "ll_equilibrium_region_with_incentive.png",
        BENCHMARK,
    )
    print("✓ Mechanism sweep complete; analytical PL and LL regions verified")

    raw = simulate_auction_conditions(n=DEFAULT_N, seed=DEFAULT_SEED)
    summary = auction_summary(raw)
    validation = auction_validation_payload(raw, summary)
    if not validation["same_valuation_sample_across_all_conditions"]:
        raise AssertionError("Auction conditions did not reuse the same valuations.")
    if max(row["absolute_error"] for row in validation["conditions"]) >= 0.01:
        raise AssertionError("Auction allocation simulation missed analytical tolerance.")
    write_csv(summary, outputs / "auction_summary.csv")
    sample = raw.groupby(
        ["mechanism", "reserve_regime"], sort=True, group_keys=False
    ).head(100)
    write_csv(sample, outputs / "auction_simulation_sample.csv")
    write_json(validation, outputs / "auction_validation.json")
    plot_auction_allocation_probability(
        summary, figures / "auction_allocation_probability.png"
    )
    plot_auction_expected_payment(
        summary, figures / "auction_expected_payment.png"
    )
    plot_auction_bid_functions(figures / "auction_bid_functions.png")
    print("✓ Auction simulation complete; analytical allocation probabilities verified")

    pp_row = social_benchmark[social_benchmark["strategy_profile"] == "(PP,PP)"].iloc[0]
    print(
        f"Social benchmark at m={SOCIAL_BENCHMARK_M:.1f}: "
        f"PP welfare={pp_row['expected_social_welfare']:.2f} "
        "(welfare comparator, not a Phase 2 equilibrium)"
    )
    print(
        "Mechanism thresholds: "
        f"tau_min(PL at p=.4)={minimum_incentive_for_pl(.4, .2):.2f}; "
        f"LL weak boundary={lock_in_low_type_threshold(.2):.2f}"
    )
    for row in summary.itertuples(index=False):
        print(
            f"Auction {row.mechanism}/{row.reserve_regime}: "
            f"allocation={row.allocation_probability:.4f}, "
            f"unconditional payment={row.expected_payment_unconditional:.4f}"
        )


if __name__ == "__main__":
    main()
