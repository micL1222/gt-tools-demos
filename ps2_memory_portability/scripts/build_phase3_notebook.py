#!/usr/bin/env python3
"""Build the reviewed Phase 3 notebook from tested package calls."""

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "notebooks" / "02_social_choice_mechanism_auction.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str, tags: list[str] | None = None):
    cell = nbf.v4.new_code_cell(text.strip())
    if tags:
        cell.metadata["tags"] = tags
    return cell


cells = [
    markdown(
        r"""
# Stay or Switch?

## Phase 3: Welfare, Incentives, and User Allocation

**COMSCI/ECON 206 · Problem Set 2 · Phase 3 computational artifact**

This notebook extends the verified Bayesian portability model through three
connected lenses: social choice, mechanism design, and a stylized auction for a
mobile user's primary-assistant slot. All new parameters are normalized
benchmark assumptions, not empirical estimates.

The first code cell regenerates the Phase 3 outputs through the tested runner.
"""
    ),
    code(
        r"""
from pathlib import Path
import subprocess
import sys

working_directory = Path.cwd().resolve()
PROJECT_ROOT = next(
    candidate for candidate in (working_directory, working_directory.parent)
    if (candidate / "src" / "memory_portability").is_dir()
)
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

run = subprocess.run(
    [sys.executable, str(PROJECT_ROOT / "scripts" / "run_phase3.py")],
    cwd=PROJECT_ROOT, check=True, capture_output=True, text=True,
)
print(run.stdout)
""",
        ["regenerate"],
    ),
    code(
        r"""
import json
import pandas as pd
from IPython.display import Image, display

from memory_portability.mechanism import (
    enumerate_mechanism_pure_bne, minimum_incentive_for_pl,
)
from memory_portability.model import ModelParameters, enumerate_pure_bne
from memory_portability.social_choice import evaluate_ex_ante_welfare

BENCHMARK = ModelParameters(0.2, 1.2, 0.7)
""",
        ["imports"],
    ),
    markdown(
        r"""
### 1. Link to Phase 2

Phase 2 models two platforms that privately observe low or high portability
implementation costs and simultaneously choose Portable or Locked. At
`c_L=0.2`, `c_H=1.2`, and `p=0.7`, the verified pure BNE are `(LL,LL)` and
`(PL,PL)`. The coexistence of lock-in and type-contingent portability creates
an equilibrium-selection problem.
"""
    ),
    code(
        r"""
print("Phase 2 pure BNE:", enumerate_pure_bne(BENCHMARK))
""",
        ["phase2-regression"],
    ),
    markdown(
        r"""
### 2. Why Strategic Equilibrium Is Not a Welfare Criterion

BNE asks whether any type has a profitable unilateral deviation. Social choice
instead compares stakeholder outcomes under a stated collective objective. A
profile can score highly in welfare without being strategically sustainable,
and an equilibrium can persist without maximizing the modeled objective.

### 3. Social-Choice Stakeholders and Alternatives

Stakeholders are Platform A, Platform B, and users. Realized alternatives are
`(P,P)`, `(P,L)`, `(L,P)`, and `(L,L)`. The calculations below compare complete
Bayesian strategy profiles `(LL,LL)`, `(PL,PL)`, and `(PP,PP)` ex ante over
private types; these must not be confused with realized action profiles.

### 4. User Mobility Benefit

The binary benchmark sets `U_user(P,P)=m` and zero otherwise. Mutual support is
required for the full modeled interoperability benefit. This deliberately
excludes possible value from unilateral portability.

### 5. Ex-Ante Welfare Calculation

The normalized utilitarian objective is `W=u_A+u_B+U_user`. The tested
enumerator visits all four joint type states and reuses the original Phase 2
payoff function. Cardinal comparability is a modeling assumption.
"""
    ),
    code(
        r"""
social = pd.read_csv(PROJECT_ROOT / "outputs" / "social_choice_benchmark.csv")
display(social)
""",
        ["social-choice"],
    ),
    markdown(
        r"""
### 6. Equilibrium vs Welfare Comparison

At the benchmark, `W_LL=0`, `W_PL=1.68+0.49m`, and `W_PP=3+m`. On the tested
`m` grid, `PP > PL > LL`; however, `(PP,PP)` is labeled as a welfare comparator
rather than a Phase 2 equilibrium.
"""
    ),
    code(
        r"""
display(Image(filename=str(PROJECT_ROOT / "figures" / "social_welfare_by_m.png")))
""",
        ["figure"],
    ),
    markdown(
        r"""
### 7. Mechanism-Design Motivation

The welfare comparison exposes a gap between strategic sustainability and the
collective benchmark. The mechanism exercise asks how the equilibrium
correspondence changes when verified portability earns an additional benefit.

### 8. Portability Incentive `tau`

For a Portable action,

\[
EU_\tau(P\mid c)=3q-1-c+\tau,
\]

while `EU_tau(L|c)=q`. The neutral term *portability incentive* can represent
certification, ecosystem access, or a compliance credit; financing is not
modeled.

### 9. Analytical Threshold Shift

For `PL`, the low-type condition is
`p >= (1+c_L-tau)/2`, or `tau_min=max(0,1+c_L-2p)`. The high type must also
prefer Locked: `tau <= 1+c_H-2p`. At the benchmark, `PL` remains weakly
sustainable through `tau=0.8`, while `PP` first appears weakly at `tau=0.2`.
"""
    ),
    code(
        r"""
for tau in (0.39, 0.40, 0.41):
    point = ModelParameters(0.2, 1.2, 0.4)
    print(f"p=.4, tau={tau:.2f}:", enumerate_mechanism_pure_bne(point, tau))
print("Minimum tau for PL at p=.4:", minimum_incentive_for_pl(0.4, 0.2))
""",
        ["mechanism"],
    ),
    markdown(
        r"""
### 10. Full Computational Mechanism Sweep

The computation evaluates all 16 pure profiles at every combination of 99
interior prior values and 51 incentive values from 0 through 2.5. The plots
show the computed regions and analytical type boundaries.
"""
    ),
    code(
        r"""
mechanism = pd.read_csv(PROJECT_ROOT / "outputs" / "mechanism_p_tau_sweep.csv")
thresholds = json.loads((PROJECT_ROOT / "outputs" / "mechanism_thresholds.json").read_text())
print("Mechanism rows:", len(mechanism))
print("Thresholds:", thresholds["analytical_thresholds"])
display(Image(filename=str(PROJECT_ROOT / "figures" / "pl_equilibrium_region_with_incentive.png")))
""",
        ["mechanism", "figure"],
    ),
    markdown(
        r"""
### 11. Why Equilibrium Selection Remains

`(LL,LL)` remains a weak BNE at `tau=1.2` and disappears only above that
boundary. A moderate incentive can therefore create or expand portability
equilibria while leaving lock-in available. This mechanism changes equilibrium
existence without automatically selecting the collectively preferred profile.
"""
    ),
    code(
        r"""
display(Image(filename=str(PROJECT_ROOT / "figures" / "ll_equilibrium_region_with_incentive.png")))
""",
        ["figure"],
    ),
    markdown(
        r"""
### 12. Auction / Allocation Application

The final lens asks how portability-induced reductions in switching friction
change competition for a mobile user. It is a stylized allocation analogy, not
a proposal to sell users.

### 13. Scarce Resource, Participants, Values, Information

- Scarce resource: one user's primary AI-assistant slot for the next service period.
- Participants: Platform A and Platform B.
- Values: iid normalized private values `Uniform(0,1)`.
- Information: each platform observes its own value; the distribution,
  mechanism, and reserve are common knowledge.
- Bids: one sealed bid per platform.
- Allocation: highest eligible bid; at most one winner.
- Tie rule: Platform A wins an exact eligible tie.
- Stopping rule: collect bids, apply the reserve, allocate, compute payment,
  and terminate.

### 14. First-Price Mechanism

The winner pays its own bid. Participating types use

\[
b_{FPA}(v;r)=\frac{v^2+r^2}{2v},\quad v\ge r,
\]

and types below `r` submit no eligible bid.

### 15. Second-Price Mechanism

Platforms bid truthfully. The highest eligible bidder wins and pays
`max(second-highest bid,r)`.

### 16. Locked vs Portable Switching Hurdle

The user's reserve is `r_locked=0.5` or `r_portable=0.2`. The reserve is placed
on the user side rather than subtracted from platform values. These are
normalized assumptions, not measured switching costs.
"""
    ),
    code(
        r"""
display(Image(filename=str(PROJECT_ROOT / "figures" / "auction_bid_functions.png")))
""",
        ["figure"],
    ),
    markdown(
        r"""
### 17. Simulation Results

The seeded Monte Carlo simulation uses 100,000 identical valuation profiles in
all four mechanism/reserve conditions. The analytical allocation probability
is `1-r^2`.
"""
    ),
    code(
        r"""
auction = pd.read_csv(PROJECT_ROOT / "outputs" / "auction_summary.csv")
display(auction)
display(Image(filename=str(PROJECT_ROOT / "figures" / "auction_allocation_probability.png")))
display(Image(filename=str(PROJECT_ROOT / "figures" / "auction_expected_payment.png")))
""",
        ["auction", "figure"],
    ),
    markdown(
        r"""
### 18. What the Auction Supports

Lowering the reserve raises feasible allocation from approximately 0.75 to
0.96 under both mechanisms. First- and second-price expected payments are close
under the symmetric risk-neutral benchmark, consistent with revenue-equivalence
logic. The portability result comes primarily through the user's lower hurdle.

### 19. Auction Boundary

The user is not literally sold. Values, reserves, and the primary-assistant
slot are normalized abstractions. The model omits multi-homing, repetition,
quality dynamics, privacy heterogeneity, network effects, entry, endogenous
user values, and multi-user markets.

### 20. Integrated Interpretation

The Bayesian game identifies decentralized equilibrium behavior and
multiplicity. Social choice compares those equilibria with a transparent user
mobility objective. Mechanism design shifts adoption incentives but reveals
that selection can remain unresolved. The auction then illustrates one channel
through which portability can matter for users: a lower switching hurdle makes
competitive reallocation feasible more often.

### 21. Limitations

- All new parameters are normalized and uncalibrated.
- Cardinal welfare comparability is assumed.
- The incentive has no financing or administrative cost.
- Equilibrium selection is not solved.
- The auction relies on symmetric, risk-neutral independent private values.
- The binary portability and one-user abstractions omit market dynamics.
- No behavioral or real-user evidence is included.

### 22. Reproducibility

From `ps2_memory_portability/`:

```bash
conda run -n cs206-ps2 python scripts/run_phase3.py
conda run -n cs206-ps2 python -m unittest discover -s tests -v
conda run -n cs206-ps2 python scripts/execute_phase3_notebook.py
```

See `docs/phase3_model_specification.md`, `docs/auction_boundary.md`, and
`docs/reproducibility.md` for formal assumptions and evidence boundaries.
"""
    ),
]

notebook = nbf.v4.new_notebook(cells=cells)
notebook.metadata = {
    "kernelspec": {
        "display_name": "Python (cs206-ps2)",
        "language": "python",
        "name": "cs206-ps2",
    },
    "language_info": {"name": "python", "version": "3.12"},
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(notebook, OUTPUT)
print(f"Wrote {OUTPUT.relative_to(PROJECT_ROOT)}")
