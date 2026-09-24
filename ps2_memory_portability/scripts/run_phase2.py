#!/usr/bin/env python3
"""Regenerate every Phase 2 result, diagnostic table, and figure."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import math
from pathlib import Path
import platform
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from memory_portability.analysis import (  # noqa: E402
    build_benchmark_payload,
    mixed_equilibrium_sweep,
    plot_pl_sensitivity,
    plot_symmetric_pure_bne_by_p,
    pl_sensitivity,
    prior_sweep,
    write_csv,
    write_json,
)
from memory_portability.model import (  # noqa: E402
    LL,
    LP,
    PL,
    PP,
    CostType,
    ModelParameters,
    enumerate_pure_bne,
    expected_utility_locked,
    expected_utility_portable,
    rival_portability_probability,
    symmetric_low_type_mixed_equilibrium,
)
from memory_portability.pygambit_model import (  # noqa: E402
    PyGambitUnavailable,
    enumerate_pure_bne_pygambit,
    export_efg,
)


BENCHMARK = ModelParameters(c_low=0.2, c_high=1.2, p_low=0.7)
EXPECTED_PURE_BNE = {("LL", "LL"), ("PL", "PL")}


def assert_benchmark_mathematics() -> None:
    """Fail loudly if implementation and the pre-verified benchmark diverge."""

    expected = {
        "LL": {"q": 0.0, "Low": (-1.2, 0.0), "High": (-2.2, 0.0)},
        "PL": {"q": 0.7, "Low": (0.9, 0.7), "High": (-0.1, 0.7)},
        "LP": {"q": 0.3, "Low": (-0.3, 0.3), "High": (-1.3, 0.3)},
        "PP": {"q": 1.0, "Low": (1.8, 1.0), "High": (0.8, 1.0)},
    }
    strategies = {item.name: item for item in (LL, PL, LP, PP)}
    for name, values in expected.items():
        q = rival_portability_probability(strategies[name], BENCHMARK.p_low)
        if not math.isclose(q, values["q"], abs_tol=1e-12):
            raise AssertionError(f"Incorrect q for {name}: {q}")
        for cost_type in CostType:
            cost = BENCHMARK.cost(cost_type)
            observed = (
                expected_utility_portable(q, cost),
                expected_utility_locked(q),
            )
            target = values[cost_type.value]
            if not all(
                math.isclose(actual, wanted, abs_tol=1e-12)
                for actual, wanted in zip(observed, target)
            ):
                raise AssertionError(
                    f"Expected-utility mismatch for rival {name}, {cost_type.value}: "
                    f"observed={observed}, expected={target}"
                )
    direct = set(enumerate_pure_bne(BENCHMARK))
    if direct != EXPECTED_PURE_BNE:
        raise AssertionError(f"Benchmark pure BNE mismatch: {sorted(direct)}")
    if any(strategy_a != strategy_b for strategy_a, strategy_b in direct):
        raise AssertionError("Unexpected asymmetric pure BNE at the benchmark.")
    threshold_profiles = {
        p: set(enumerate_pure_bne(ModelParameters(0.2, 1.2, p)))
        for p in (0.59, 0.60, 0.61)
    }
    if ("PL", "PL") in threshold_profiles[0.59]:
        raise AssertionError("PL appeared below its analytical threshold.")
    if any(("PL", "PL") not in threshold_profiles[p] for p in (0.60, 0.61)):
        raise AssertionError("PL did not appear weakly at and above its threshold.")
    mixed = symmetric_low_type_mixed_equilibrium(BENCHMARK)
    if not math.isclose(float(mixed["x_star"]), 6 / 7, abs_tol=1e-12):
        raise AssertionError(f"Mixed benchmark mismatch: {mixed}")


def run_pygambit_cross_check() -> dict[str, object]:
    """Run and export the optional PyGambit cross-check when import succeeds."""

    try:
        solver_profiles = set(enumerate_pure_bne_pygambit(BENCHMARK))
    except PyGambitUnavailable as error:
        return {
            "ran": False,
            "available": False,
            "status": "unavailable",
            "reason": str(error),
            "pure_bne": None,
            "agrees_with_direct_checker": None,
            "efg_exported": False,
        }
    direct_profiles = set(enumerate_pure_bne(BENCHMARK))
    if solver_profiles != direct_profiles:
        raise AssertionError(
            "PyGambit/direct-checker disagreement: "
            f"PyGambit={sorted(solver_profiles)}, direct={sorted(direct_profiles)}"
        )
    efg_path = export_efg(
        BENCHMARK, PROJECT_ROOT / "outputs" / "memory_portability_benchmark.efg"
    )
    return {
        "ran": True,
        "available": True,
        "status": "passed",
        "pure_bne": [list(profile) for profile in sorted(solver_profiles)],
        "agrees_with_direct_checker": True,
        "efg_exported": True,
        "efg_path": str(efg_path.relative_to(PROJECT_ROOT)),
    }


def git_generation_context() -> dict[str, object]:
    repository_root = PROJECT_ROOT.parent
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "base_head_before_phase2_commit": head,
        "working_tree_clean_at_generation": not bool(status),
        "working_tree_status_at_generation": status or "clean",
    }


def validate_sweep(sweep) -> None:
    bne_rows = sweep[sweep["is_bne"]]
    for p_low, group in bne_rows.groupby("p"):
        observed = set(zip(group["strategy_A"], group["strategy_B"]))
        expected = {("LL", "LL")}
        if p_low >= 0.6 - 1e-10:
            expected.add(("PL", "PL"))
        if observed != expected:
            raise AssertionError(
                f"Unexpected sweep equilibria at p={p_low}: {sorted(observed)}"
            )


def package_version(package: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return "not installed"


def main() -> None:
    print("Phase 2 memory-portability regeneration")
    print(f"Python {platform.python_version()} · {platform.machine()} · {platform.system()}")
    print(
        "Packages:",
        ", ".join(
            f"{name}={package_version(name)}"
            for name in ("numpy", "pandas", "matplotlib", "pygambit", "nbformat", "nbclient")
        ),
    )
    assert_benchmark_mathematics()
    print("✓ Analytical formulas and benchmark pure/mixed results verified")

    pygambit_result = run_pygambit_cross_check()
    if pygambit_result["ran"]:
        print("✓ PyGambit pure equilibria agree with the direct checker")
    else:
        print(f"! PyGambit cross-check unavailable: {pygambit_result['reason']}")

    outputs = PROJECT_ROOT / "outputs"
    figures = PROJECT_ROOT / "figures"
    sweep = prior_sweep(BENCHMARK)
    validate_sweep(sweep)
    mixed_sweep = mixed_equilibrium_sweep(BENCHMARK)
    sensitivity = pl_sensitivity(BENCHMARK)

    write_csv(sweep, outputs / "pure_bne_p_sweep.csv")
    write_csv(mixed_sweep, outputs / "symmetric_mixed_equilibrium_p_sweep.csv")
    write_csv(sensitivity, outputs / "pl_equilibrium_sensitivity.csv")
    plot_symmetric_pure_bne_by_p(
        sweep, figures / "symmetric_pure_bne_by_p.png"
    )
    plot_pl_sensitivity(sensitivity, figures / "pl_equilibrium_threshold.png")
    payload = build_benchmark_payload(
        BENCHMARK,
        pygambit_result=pygambit_result,
        generation_context=git_generation_context(),
    )
    write_json(payload, outputs / "benchmark_verification.json")

    bne_rows = sweep[sweep["is_bne"]]
    pl_first_p = bne_rows[
        (bne_rows["strategy_A"] == "PL") & (bne_rows["strategy_B"] == "PL")
    ]["p"].min()
    mixed_benchmark = symmetric_low_type_mixed_equilibrium(BENCHMARK)
    print("✓ Wrote benchmark JSON, three CSV tables, and two figures")
    print(f"Pure benchmark BNE: {sorted(EXPECTED_PURE_BNE)}")
    print(f"First grid point with (PL,PL): p={pl_first_p:.2f}")
    print(
        "Benchmark low-type mixed portability probability: "
        f"{mixed_benchmark['x_star_exact']} = {mixed_benchmark['x_star']:.10f}"
    )


if __name__ == "__main__":
    main()
