# Stay or Switch? Strategic Memory Portability in Competing AI Assistants

COMSCI/ECON 206 · Problem Set 2 · Phase 2–3 computational artifact

## Research question

**When do competing AI assistants voluntarily adopt memory portability when each platform privately knows its own portability implementation cost, and how does portability affect competition for users?**

This directory implements the main Bayesian portability game and extends it into social-choice, mechanism-design, and user-allocation analyses. It is deliberately separate from the course templates in the parent repository.

## Current phase scope

Implemented here:

- formal static incomplete-information model;
- analytical expected-utility benchmark;
- exhaustive type-level verification of all 16 pure strategy profiles;
- optional PyGambit Harsanyi-game cross-check and EFG export;
- symmetric low-type mixed-equilibrium calculation;
- full-support prior sweep;
- low-cost/prior sensitivity analysis;
- raw outputs, figures, tests, and an executed notebook.
- ex-ante social welfare with a normalized user-mobility component;
- a verified portability-incentive extension with exhaustive pure-BNE checks;
- a first-price/second-price allocation application with switching-hurdle reserves;
- deterministic Phase 3 outputs, figures, tests, and a second executed notebook.

Future work not implemented here:

- behavioral experiment or Hugging Face artifact;
- literature verification, poster, final paper, symposium review, or empirical claims.

## Model summary

Two generic platforms, A and B, independently draw private portability implementation costs (c_i\in\{c_L,c_H\}). Each observes only its own type and simultaneously chooses Portable (`P`) or Locked (`L`). The common prior is (Pr(c_i=c_L)=p).

A pure Bayesian strategy is ordered as `(low-type action, high-type action)`:

- `LL`, `PL`, `LP`, `PP`.

For own cost (c_i), normalized payoffs are:

| Own / rival action | Portable | Locked |
|---|---:|---:|
| Portable | (2-c_i) | (-1-c_i) |
| Locked | (1) | (0) |

If the rival is Portable with probability (q),

\[
EU(P\mid c_i)=3q-1-c_i,\qquad EU(L\mid c_i)=q.
\]

Portable is therefore a weak best response iff (2q-1\ge c_i). Because types are private, the solution concept is Bayesian Nash equilibrium (BNE), not a fixed complete-information 2×2 Nash equilibrium.

## Implemented benchmark results

At (c_L=0.2), (c_H=1.2), and (p=0.7), the exhaustive direct checker finds exactly two **pure** BNE:

- `(LL, LL)`;
- `(PL, PL)`.

It finds no asymmetric pure BNE at the benchmark. The type-contingent portability equilibrium becomes sustainable at

\[
p^*=\frac{1+c_L}{2}=0.6.
\]

`LL` remains an equilibrium, so the computation preserves multiplicity rather than selecting one outcome.

The baseline also has the symmetric type-specific mixed equilibrium implied by low-type indifference: high types choose Locked and low types choose Portable with probability

\[
x^*=\frac{1+c_L}{2p}=\frac67\approx0.8571428571.
\]

This mixed calculation is not presented as a general exhaustive catalog of every mixed BNE under every parameterization.

## Main computational experiments

1. Enumerate all (4\times4=16) pure type-contingent profiles and check each type of each platform separately.
2. Sweep (p=0.01,0.02,\ldots,0.99), excluding degenerate prior endpoints from the formal full-support analysis.
3. Calculate the symmetric low-type mixing candidate over the same grid.
4. Vary (p) and (c_L\in\{0,0.05,\ldots,1.15\}), hold (c_H=1.2), and compare the computed `PL` region with (p=(1+c_L)/2).

## Phase 3 implemented results

### Social choice

The stakeholders are Platform A, Platform B, and users. The normalized
collective objective is `W = u_A + u_B + U_user`, where users receive a
mobility benefit `m` only under mutual portability in this binary benchmark.
Cardinal comparability is an explicit modeling assumption.

At the benchmark:

- `(LL,LL)`: `W=0`;
- `(PL,PL)`: `W=1.68+0.49m`;
- `(PP,PP)`: `W=3+m`.

For `m=0.0,0.1,...,4.0`, the computed welfare ranking is always
`PP > PL > LL`. This does not make `(PP,PP)` a Phase 2 equilibrium: it is a
welfare comparator, while `(LL,LL)` and `(PL,PL)` are the benchmark pure BNE.

### Verified portability incentive

A Portable action receives a normalized verified-portability benefit `tau`:

\[
EU_\tau(P\mid c)=3q-1-c+\tau,\qquad EU_\tau(L\mid c)=q.
\]

For symmetric `PL`, the low-type threshold becomes
`p >= (1+c_L-tau)/2`, subject also to the high type remaining willing to lock.
At `p=0.4`, the minimum incentive is `tau=0.4`; at the benchmark `p=0.7`, it
is zero. `(LL,LL)` remains a weak BNE through `tau=1.2` and disappears only
above that boundary. At the benchmark, `PL` remains weakly sustainable through
its high-type boundary `tau=0.8`, while `PP` first appears weakly at `tau=0.2`.
Thus the mechanism can expand portability equilibria without resolving
equilibrium selection. No welfare-optimal `tau` is claimed because financing
and mechanism costs are not modeled.

### Auction/allocation application

The scarce resource is one user's primary AI-assistant slot for the next
service period. Two platforms have iid normalized private values
`Uniform(0,1)`. The user's switching hurdle is modeled as a reserve:
`r_locked=0.5` and `r_portable=0.2`.

Using 100,000 common seeded valuation draws:

- locked allocation probability: `0.75193` versus analytical `0.75`;
- portable allocation probability: `0.96004` versus analytical `0.96`;
- unconditional expected payment, first price: `0.41788` locked and `0.36320` portable;
- unconditional expected payment, second price: `0.41818` locked and `0.36414` portable.

Conditional allocative efficiency is one in all four benchmark conditions.
First- and second-price payments are close, consistent with benchmark revenue
equivalence; portability's central modeled effect is the lower reserve and
higher feasible-allocation probability. The user is not literally auctioned.
See `docs/auction_boundary.md`.

## Directory structure

```text
ps2_memory_portability/
├── README.md
├── requirements.txt
├── environment.yml
├── docs/
│   ├── model_specification.md
│   ├── reproducibility.md
│   ├── phase3_open_questions.md
│   ├── phase3_model_specification.md
│   └── auction_boundary.md
├── notebooks/
│   ├── 01_memory_portability_bayesian_game.ipynb
│   └── 02_social_choice_mechanism_auction.ipynb
├── src/memory_portability/
│   ├── __init__.py
│   ├── model.py
│   ├── pygambit_model.py
│   ├── analysis.py
│   ├── social_choice.py
│   ├── mechanism.py
│   └── auction.py
├── scripts/
│   ├── run_phase2.py
│   ├── build_notebook.py
│   ├── execute_notebook.py
│   ├── run_phase3.py
│   ├── build_phase3_notebook.py
│   └── execute_phase3_notebook.py
├── tests/
│   ├── test_model.py
│   ├── test_social_choice.py
│   ├── test_mechanism.py
│   └── test_auction.py
├── outputs/
└── figures/
```

## Environment setup

The tested environment uses Python 3.12 in an isolated Conda environment named `cs206-ps2`. Do not modify Anaconda `base`.

From this directory:

```bash
conda env create -f environment.yml
conda run -n cs206-ps2 python -m ipykernel install --user \
  --name cs206-ps2 --display-name "Python (cs206-ps2)"
```

If the environment already exists:

```bash
conda run -n cs206-ps2 python -m pip install -r requirements.txt
```

PyGambit is isolated in `pygambit_model.py`. The direct type-level checker in `model.py` is authoritative and does not import PyGambit. See `docs/reproducibility.md` and `outputs/benchmark_verification.json` for the actual cross-check status of the recorded run.

In the recorded Phase 2 run, PyGambit 16.7.0 imported successfully, its pure-equilibrium solver returned the same two pure BNE as the direct checker, and the benchmark EFG export was written. PyGambit remains optional so that the core analysis is still reproducible on systems where its compiled dependency cannot be installed.

## Regenerate outputs

Run one command from this directory:

```bash
conda run -n cs206-ps2 python scripts/run_phase2.py
```

The runner validates the benchmark, attempts the PyGambit cross-check, writes the JSON and CSV results, and regenerates both figures. It fails if the core benchmark, threshold, or solver agreement is wrong.

Generate all Phase 3 outputs from the same directory with:

```bash
conda run -n cs206-ps2 python scripts/run_phase3.py
```

This runner first checks that the Phase 2 benchmark remains unchanged, then
generates and validates the social-choice, mechanism, and auction results.

## Run tests

```bash
conda run -n cs206-ps2 python -m unittest discover -s tests -v
```

The core tests do not require PyGambit. Its agreement test is explicitly skipped if the optional dependency cannot import.

## Build and execute the notebook

The tracked notebook is generated from reviewed Markdown and lightweight calls to the package:

```bash
conda run -n cs206-ps2 python scripts/build_notebook.py
conda run -n cs206-ps2 python scripts/execute_notebook.py
```

`execute_notebook.py` launches a fresh `cs206-ps2` kernel and saves actual cell outputs. The notebook's first code cell calls `run_phase2.py`, so a top-to-bottom execution regenerates the underlying results without hidden manual state.

Build and execute the Phase 3 notebook with:

```bash
conda run -n cs206-ps2 python scripts/build_phase3_notebook.py
conda run -n cs206-ps2 python scripts/execute_phase3_notebook.py
```

## Output inventory

- `outputs/benchmark_verification.json`: parameters, formulas, all 16 profile diagnostics, pure BNE, mixed benchmark, environment, and PyGambit status.
- `outputs/pure_bne_p_sweep.csv`: all 16 profiles at each of 99 full-support prior values.
- `outputs/symmetric_mixed_equilibrium_p_sweep.csv`: analytical low-type mixing candidate over the prior grid.
- `outputs/pl_equilibrium_sensitivity.csv`: computed and analytical `PL` classification over the ((p,c_L)) grid.
- `outputs/memory_portability_benchmark.efg`: written only after a successful PyGambit construction and solver agreement.
- `figures/symmetric_pure_bne_by_p.png`: multiplicity-preserving symmetric pure-equilibrium tracks.
- `figures/pl_equilibrium_threshold.png`: computed `PL` region with the analytical boundary.
- `outputs/social_choice_benchmark.csv`: benchmark welfare decomposition at `m=1`.
- `outputs/social_choice_m_sweep.csv`: welfare and equilibrium status over the `m` grid.
- `outputs/mechanism_p_tau_sweep.csv`: all 16 profiles over 99 priors and 51 incentive values.
- `outputs/mechanism_thresholds.json`: formulas, boundary checks, and sweep diagnostics.
- `outputs/auction_summary.csv`: four-condition allocation, payment, utility, and efficiency summary.
- `outputs/auction_validation.json`: seed, assumptions, analytical comparisons, and revenue gaps.
- `outputs/auction_simulation_sample.csv`: deterministic 400-row validation sample.
- `figures/social_welfare_by_m.png`: welfare comparison with equilibrium labels.
- `figures/pl_equilibrium_region_with_incentive.png`: computed `PL` region and both type boundaries.
- `figures/ll_equilibrium_region_with_incentive.png`: persistence of lock-in under incentives.
- `figures/auction_allocation_probability.png`: locked versus portable allocation probability.
- `figures/auction_expected_payment.png`: unconditional expected payments.
- `figures/auction_bid_functions.png`: reserve-adjusted first-price and truthful second-price bids.

## Reproducibility conventions

- The formal prior grid is constructed from integers, not floating-point stepping.
- It includes (p=0.60) exactly as a reported grid value.
- Formal sweeps use (0<p<1); `p=0` and `p=1` are flagged as boundary cases.
- Equilibrium logic uses unrounded values and an explicit numerical tolerance.
- Saved CSVs expose profile-level diagnostics rather than only selected equilibria.
- The notebook imports the tested source package instead of duplicating the model.

## Evidence boundary and limitations

The code establishes computational properties of the benchmark model under the stated assumptions. It does not show that actual platforms have these costs or payoffs, that a particular equilibrium will be selected, or that users are better off.

Key limitations are normalized payoffs, binary portability, symmetric platforms,
independent private types, cardinal welfare comparability, unresolved equilibrium
selection, an uncosted reduced-form incentive, and a stylized one-user auction
that abstracts from actual market dynamics. No behavioral or real-user evidence
has been collected.

## AI-use disclosure

Student intellectual decisions include the research question, memory-portability framing, choice of a static incomplete-information game, players, types, actions, strategic interpretation, benchmark model, and computational questions.

AI/Codex assistance includes code implementation, debugging, mathematical and computational verification, organization, test construction, and documentation support. Codex did not originate the research question or the project's economic contribution.

## Remaining work

The social-choice, mechanism-design, and auction decisions formerly listed as
open Phase 3 questions are now implemented under the explicit normalized
assumptions above. Remaining work includes literature verification, a separate
Hugging Face behavioral artifact, the paper, poster, and symposium review
materials. None is represented as complete here.
