# Future Paper Evidence Map

This map separates three kinds of support for the future two-page paper:
published literature, results produced by this project's stated model, and
artifacts that make those results auditable.

## Motivation

- **Literature:** `farrell2007coordination` for lock-in and competition;
  `jeon2023compatibility` for endogenous compatibility and data portability;
  `viard2007switching` for a setting-specific empirical portability analogy.
- **Model result:** None required. Motivation should not present the benchmark
  parameter values as empirical facts.
- **Artifact evidence:** The literature review and evidence matrix are the
  audit trail; no simulation output is needed for the motivation claim.
- **Boundary:** Digital-platform and toll-free-number evidence motivates the
  question but does not estimate the effect of AI memory portability.

## Game Theory

- **Literature:** `jeon2023compatibility` is the closest strategic analogue;
  `farrell2007coordination` provides the switching-cost foundation.
- **Our result:** At `c_L=0.2`, `c_H=1.2`, and `p=0.7`, the direct checker finds
  pure BNE `(LL,LL)` and `(PL,PL)`, plus the documented symmetric low-type mixed
  candidate. The `PL` threshold is `p*=(1+c_L)/2=0.6`.
- **Artifact evidence:** [`benchmark_verification.json`](../outputs/benchmark_verification.json),
  [`pure_bne_p_sweep.csv`](../outputs/pure_bne_p_sweep.csv),
  [`symmetric_mixed_equilibrium_p_sweep.csv`](../outputs/symmetric_mixed_equilibrium_p_sweep.csv),
  and [`01_memory_portability_bayesian_game.ipynb`](../notebooks/01_memory_portability_bayesian_game.ipynb).
- **Boundary:** Jeon et al. do not supply our private implementation-cost types,
  static BNE, or exact equilibrium multiplicity.

## Social Choice

- **Literature:** `kim2026portability` for a modeled platform-welfare comparison
  with network benefits and breach risk; `oecd2021portability` for policy
  implementation context.
- **Our result:** Under the normalized collective objective, the benchmark
  comparison ranks `PP > PL > LL` across the implemented `m` grid. `PP` is a
  welfare comparator, not a Phase 2 equilibrium claim.
- **Artifact evidence:** [`social_choice_benchmark.csv`](../outputs/social_choice_benchmark.csv),
  [`social_choice_m_sweep.csv`](../outputs/social_choice_m_sweep.csv), and
  [`02_social_choice_mechanism_auction.ipynb`](../notebooks/02_social_choice_mechanism_auction.ipynb).
- **Boundary:** Cardinal comparability and the user-mobility term are modeling
  assumptions, not quantities estimated by the cited literature.

## Mechanism Design

- **Literature:** `jeon2023compatibility` motivates why changing switching
  friction can change compatibility incentives. `myerson1981optimal` is only
  broad private-information/mechanism-design context.
- **Our result:** The verified-portability incentive changes the low-type `PL`
  threshold to `p >= (1+c_L-tau)/2`, while `(LL,LL)` can persist; at `p=0.4`,
  the minimum weak-support threshold is `tau=0.4`.
- **Artifact evidence:** [`mechanism_thresholds.json`](../outputs/mechanism_thresholds.json),
  [`mechanism_p_tau_sweep.csv`](../outputs/mechanism_p_tau_sweep.csv), and the
  Phase 3 notebook.
- **Boundary:** `tau` is reduced-form and uncosted. It is neither an empirically
  estimated subsidy nor a Myerson-optimal mechanism.

## Auction

- **Literature:** `vickrey1961counterspeculation` for the second-price
  truthful-bidding benchmark; `myerson1981optimal` for general single-object
  private-information auction design.
- **Our result:** With two iid `Uniform(0,1)` values, lowering the reserve-like
  switching hurdle from `r=0.5` to `r=0.2` raises analytical allocation
  probability from `0.75` to `0.96`; simulations closely match these values and
  produce close first- and second-price expected payments.
- **Artifact evidence:** [`auction_validation.json`](../outputs/auction_validation.json),
  [`auction_summary.csv`](../outputs/auction_summary.csv), the Phase 3 notebook,
  and [`auction_boundary.md`](auction_boundary.md).
- **Boundary:** The user is not auctioned. The first-price bid function with a
  reserve is derived inside the implemented benchmark under its stated
  assumptions, not attributed to Vickrey or Myerson. The reserve values are not
  empirical estimates.

## Behavioral Artifact

- **Literature:** `samuelson1988statusquo` motivates a hypothesis about
  persistence beyond technical switching cost.
- **Our result:** **NOT YET COLLECTED.** No participant behavior or AI-user
  response is available.
- **Artifact evidence:** None. The Hugging Face Stay/Switch artifact is planned.
- **Permitted wording:** “Status-quo bias motivates testing whether observed
  Stay/Switch decisions depart from a simplified switching-cost benchmark.”
- **Prohibited wording:** “Our participants exhibit status-quo bias.”

## Limitations and Real-World Impact

- **Literature:** `kim2026portability` for the breach-risk trade-off;
  `oecd2021portability` for legal, technical, privacy, and implementation
  challenges; `viard2007switching` as an analogy whose magnitude is not
  transferable.
- **Our result:** The model is a transparent conditional exercise, not a market
  calibration.
- **Artifact evidence:** [`phase3_open_questions.md`](phase3_open_questions.md),
  [`phase3_model_specification.md`](phase3_model_specification.md), and the
  README evidence boundary.

## Recommended Main-Text Citations

For a two-page limit, use a minimum high-value set rather than listing every
verified source:

- **Motivation (2–3 citations):** Farrell and Klemperer (2007), Jeon et al.
  (2023), and Viard (2007).
- **Closest prior work (1 citation):** Jeon et al. (2023); avoid repeating it if
  already cited in the same paragraph.
- **Digital-platform limitation (optional 1 citation):** Kim (2026), especially
  if breach risk or network benefits appear in the text.
- **Behavioral artifact (1 citation):** Samuelson and Zeckhauser (1988).
- **Auction benchmark (1 citation, at most 2):** Vickrey (1961); add Myerson
  (1981) only if the text discusses mechanism design under private information
  beyond the standard second-price benchmark.

The OECD report and Klemperer (1995) are best reserved for the appendix or
documentation unless a specific policy or classic-survey sentence needs them.
