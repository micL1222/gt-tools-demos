"""Sweeps, serialization, and figures for the memory-portability game."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
import json
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .model import (
    CostType,
    LL,
    LP,
    PL,
    PP,
    PURE_STRATEGIES,
    ModelParameters,
    enumerate_pure_bne,
    enumerate_pure_profile_diagnostics,
    expected_utility_locked,
    expected_utility_portable,
    rival_portability_probability,
    symmetric_low_type_mixed_equilibrium,
)


def full_support_prior_grid() -> list[float]:
    """Return p=0.01,...,0.99 from explicit integer construction."""

    return [index / 100 for index in range(1, 100)]


def low_cost_grid() -> list[float]:
    """Return c_L=0.00,0.05,...,1.15, all strictly below benchmark c_H=1.2."""

    return [index / 100 for index in range(0, 120, 5)]


def prior_sweep(parameters: ModelParameters) -> pd.DataFrame:
    """Evaluate all 16 pure profiles at every full-support prior value."""

    rows: list[dict[str, object]] = []
    for p_low in full_support_prior_grid():
        point = ModelParameters(parameters.c_low, parameters.c_high, p_low)
        for result in enumerate_pure_profile_diagnostics(point):
            strategy_a = next(
                item for item in PURE_STRATEGIES if item.name == result["strategy_A"]
            )
            strategy_b = next(
                item for item in PURE_STRATEGIES if item.name == result["strategy_B"]
            )
            rows.append(
                {
                    "p": p_low,
                    "strategy_A": result["strategy_A"],
                    "strategy_B": result["strategy_B"],
                    "is_bne": result["is_bne"],
                    "symmetric": result["symmetric"],
                    "A_low_action": strategy_a.low_action.value,
                    "A_high_action": strategy_a.high_action.value,
                    "B_low_action": strategy_b.low_action.value,
                    "B_high_action": strategy_b.high_action.value,
                    "max_deviation_gain": result["max_deviation_gain"],
                    "expected_payoff_A": result["expected_payoff_A"],
                    "expected_payoff_B": result["expected_payoff_B"],
                }
            )
    return pd.DataFrame(rows)


def mixed_equilibrium_sweep(parameters: ModelParameters) -> pd.DataFrame:
    """Calculate the symmetric low-type mixing candidate over interior priors."""

    rows = []
    for p_low in full_support_prior_grid():
        point = ModelParameters(parameters.c_low, parameters.c_high, p_low)
        mixed = symmetric_low_type_mixed_equilibrium(point)
        rows.append(
            {
                "p": p_low,
                "q_star": mixed["q_star"],
                "x_star": mixed["x_star"],
                "x_star_exact": mixed["x_star_exact"],
                "interior_mixed_exists": mixed["interior_mixed_exists"],
                "high_type_prefers_locked": mixed["high_type_prefers_locked"],
                "collapses_to_boundary_pure_pl": mixed["collapses_to_pure_pl"],
                "status": mixed["status"],
            }
        )
    return pd.DataFrame(rows)


def pl_sensitivity(parameters: ModelParameters) -> pd.DataFrame:
    """Classify the symmetric PL profile over (p,c_L) and verify its threshold."""

    rows = []
    for c_low in low_cost_grid():
        if c_low >= parameters.c_high:
            continue
        threshold = (1.0 + c_low) / 2.0
        for p_low in full_support_prior_grid():
            point = ModelParameters(c_low, parameters.c_high, p_low)
            computed = ("PL", "PL") in enumerate_pure_bne(point)
            analytical = (
                p_low >= threshold - 1e-10
                and (2.0 * p_low - 1.0) <= parameters.c_high + 1e-10
            )
            if computed != analytical:
                raise AssertionError(
                    f"PL threshold mismatch at p={p_low}, c_low={c_low}: "
                    f"computed={computed}, analytical={analytical}"
                )
            rows.append(
                {
                    "p": p_low,
                    "c_low": c_low,
                    "c_high": parameters.c_high,
                    "analytical_threshold_p": threshold,
                    "computed_pl_pl_is_bne": computed,
                    "analytical_pl_condition": analytical,
                    "agreement": computed == analytical,
                }
            )
    return pd.DataFrame(rows)


def plot_symmetric_pure_bne_by_p(sweep: pd.DataFrame, output_path: Path) -> Path:
    """Plot one track per symmetric candidate, preserving coexistence."""

    order = [LL.name, PL.name, LP.name, PP.name]
    matrix = np.zeros((len(order), len(full_support_prior_grid())))
    for row_index, strategy in enumerate(order):
        subset = sweep[
            (sweep["strategy_A"] == strategy)
            & (sweep["strategy_B"] == strategy)
        ].sort_values("p")
        matrix[row_index, :] = subset["is_bne"].astype(int).to_numpy()
    figure, axis = plt.subplots(figsize=(9, 3.8))
    image = axis.imshow(
        matrix,
        aspect="auto",
        interpolation="nearest",
        origin="upper",
        extent=[0.01, 0.99, len(order) - 0.5, -0.5],
    )
    axis.set_yticks(range(len(order)), [f"({name}, {name})" for name in order])
    axis.set_xlabel("Prior probability p that a platform is low-cost")
    axis.set_ylabel("Symmetric pure strategy profile")
    axis.set_title("Symmetric pure BNE correspondence (multiplicity preserved)")
    axis.axvline(0.6, linestyle="--", linewidth=1.2, label="PL threshold p = 0.60")
    axis.legend(loc="upper left")
    colorbar = figure.colorbar(image, ax=axis, ticks=[0, 1])
    colorbar.set_label("Computed BNE indicator")
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output_path


def plot_pl_sensitivity(sensitivity: pd.DataFrame, output_path: Path) -> Path:
    """Compare computed PL classification with p=(1+c_L)/2."""

    pivot = sensitivity.pivot(
        index="c_low", columns="p", values="computed_pl_pl_is_bne"
    ).sort_index()
    figure, axis = plt.subplots(figsize=(8.5, 5.2))
    image = axis.imshow(
        pivot.astype(int).to_numpy(),
        aspect="auto",
        interpolation="nearest",
        origin="lower",
        extent=[pivot.columns.min(), pivot.columns.max(), pivot.index.min(), pivot.index.max()],
    )
    p_line = np.linspace(0.5, 0.99, 200)
    c_line = 2.0 * p_line - 1.0
    valid = (c_line >= pivot.index.min()) & (c_line <= pivot.index.max())
    axis.plot(
        p_line[valid],
        c_line[valid],
        linestyle="--",
        linewidth=1.5,
        label=r"Analytical boundary $p=(1+c_L)/2$",
    )
    axis.set_xlabel("Prior probability p that a platform is low-cost")
    axis.set_ylabel(r"Low implementation cost $c_L$")
    axis.set_title(r"Computed existence region for symmetric $(PL,PL)$ BNE")
    axis.legend(loc="upper left")
    colorbar = figure.colorbar(image, ax=axis, ticks=[0, 1])
    colorbar.set_label("Computed PL equilibrium indicator")
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output_path


def build_benchmark_payload(
    parameters: ModelParameters,
    pygambit_result: dict[str, object],
    generation_context: dict[str, object],
) -> dict[str, object]:
    """Build the machine-readable benchmark verification record."""

    strategy_checks: dict[str, object] = {}
    for rival in PURE_STRATEGIES:
        q = rival_portability_probability(rival, parameters.p_low)
        type_rows = {}
        for cost_type in CostType:
            cost = parameters.cost(cost_type)
            eu_p = expected_utility_portable(q, cost)
            eu_l = expected_utility_locked(q)
            type_rows[cost_type.value] = {
                "cost": cost,
                "eu_portable": eu_p,
                "eu_locked": eu_l,
                "best_responses": [
                    action
                    for action, utility in (("P", eu_p), ("L", eu_l))
                    if utility >= max(eu_p, eu_l) - 1e-10
                ],
            }
        strategy_checks[rival.name] = {"q": q, "types": type_rows}
    diagnostics = enumerate_pure_profile_diagnostics(parameters)
    pure_bne = enumerate_pure_bne(parameters)
    mixed = symmetric_low_type_mixed_equilibrium(parameters)
    return {
        "model_title": "Stay or Switch? Strategic Memory Portability in Competing AI Assistants",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "c_low": parameters.c_low,
            "c_high": parameters.c_high,
            "p_low": parameters.p_low,
            "p_high": 1.0 - parameters.p_low,
            "independent_type_draws": True,
        },
        "payoff_definition": {
            "P,P": "2 - own_cost",
            "P,L": "-1 - own_cost",
            "L,P": "1",
            "L,L": "0",
            "evidence_boundary": "Normalized theoretical benchmark payoffs, not empirical profit estimates.",
        },
        "expected_utility_formulas": {
            "portable": "3q - 1 - c",
            "locked": "q",
            "portable_weak_best_response": "2q - 1 >= c",
        },
        "strategy_induced_q_and_type_checks": strategy_checks,
        "pure_profile_diagnostics": diagnostics,
        "pure_bne": [list(profile) for profile in pure_bne],
        "exactly_two_pure_bne_at_benchmark": set(pure_bne)
        == {("LL", "LL"), ("PL", "PL")},
        "asymmetric_pure_bne": [list(profile) for profile in pure_bne if profile[0] != profile[1]],
        "pl_threshold": (1.0 + parameters.c_low) / 2.0,
        "symmetric_low_type_mixed_candidate": mixed,
        "endpoint_convention": (
            "Formal sweeps use 0<p<1. At p=0 or p=1 a zero-probability type's "
            "action is not disciplined by the ordinary ex-ante BNE condition; endpoints "
            "must be reported separately."
        ),
        "pygambit_cross_check": pygambit_result,
        "environment": {
            "python": platform.python_version(),
            "architecture": platform.machine(),
            "platform": platform.platform(),
            "packages": _package_versions(
                ["numpy", "scipy", "pandas", "matplotlib", "pygambit", "nbformat", "nbclient", "ipykernel"]
            ),
        },
        "generation_context": generation_context,
    }


def write_json(payload: dict[str, object], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return path


def write_csv(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def _package_versions(packages: list[str]) -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for package in packages:
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            versions[package] = None
    return versions
