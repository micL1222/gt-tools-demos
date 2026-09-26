# Review-Ready Paper Evidence and Parity Audit

## Scope

This audit checks the official-template paper against repository snapshot
`f9523b0fdd3f5dc4739dd1f08fe1265e049c1271`. It is a technical and evidentiary
check, not peer review or participant evidence.

Official team code: FP10

Final paper: `submission/PS2-FP10-StayOrSwitch.pdf`

Final Overleaf source: `submission/PS2-FP10-StayOrSwitch-Overleaf-Source.zip`

## Claim parity

| Paper claim | Repository evidence | Audit result |
|---|---|---|
| Shared question concerns privately costly memory portability and user mobility | `README.md`, `docs/model_specification.md` | Exact scope retained; no new model added |
| Benchmark uses `c_L=.2`, `c_H=1.2`, `p=.7` | `outputs/benchmark_verification.json` | Matched |
| Pure BNE are `(LL,LL)` and `(PL,PL)` | `benchmark_verification.json`, direct checker, PyGambit | Matched; paper says exactly two *pure* BNE |
| Low-type mixing probability is `6/7` | `benchmark_verification.json` | Matched and bounded to the symmetric candidate |
| Welfare at `m=1` is `0`, `2.17`, `4` for LL/PL/PP | `outputs/social_choice_benchmark.csv` | Matched; PP labeled non-equilibrium comparator |
| Incentive threshold at `p=.4` is `tau=.4`; LL remains weak through `1.2` | `outputs/mechanism_thresholds.json` | Matched; no welfare-optimal incentive claimed |
| Auction uses `N=100000`, seed `20603`, reserves `.5/.2` | `outputs/auction_validation.json` | Matched |
| Allocation `.75193/.96004` and payments shown in paper | `outputs/auction_summary.csv` | Matched to displayed precision |
| Conditional efficiency equals one | `outputs/auction_summary.csv` | Matched and explicitly conditional |
| Behavioral artifact has 12 balanced scenarios and rule `Switch iff g>r` | `behavioral_scenario_catalog.csv`, `behavioral_validation.json` | Matched |
| Public Space is deployed and technically verified | `behavioral_validation.json`, public URL | Matched |
| No participant-level behavioral conclusion | evidence-boundary documents | Preserved throughout |
| Full regression suite passes | From `ps2_memory_portability/`: `conda run -n cs206-ps2 python -m unittest discover -s tests -v` | 85 passed, 0 skipped/failures/errors |

## Literature parity

The paper cites switching-cost lock-in, strategic compatibility, portability in
the 800-number setting, modeled privacy/security trade-offs, status-quo-bias
motivation, incomplete-information equilibrium, and standard auction
foundations only at the scope allowed by `docs/claim_source_map.md`. It does not
transfer empirical magnitudes to AI assistants or cite external literature for
project-generated equilibria.

## Cross-artifact status

- **GitHub:** same model, parameters, outputs, commit, commands, and limits.
- **Hugging Face:** same user-level decision setting, 12 scenarios, evidence
  boundary, and current-page-session privacy scope.
- **A0 poster:** not yet created; paper marks it planned and makes no parity
  claim.
- **Symposium/peer review/classroom auction:** not yet observed; no records are
  fabricated.

## Template compliance

- Official `sigconf,nonacm` driver and top-matter settings retained.
- Five main sections and Figure 1 confined to pages 1--2.
- Author Notes and references precede Appendices A--F.
- Figure 1 is LaTeX/TikZ-native.
- Official class, bibliography style, and annotation files are byte-identical
  to the supplied template.
- Source ZIP contains the clean and annotated drivers and all compile inputs.

## Build and release verification

- Clean `main.tex` build: 7 pages; Sections 1--5 and Figure 1 end on page 2;
  Author Notes begin on page 3; Appendices A--F are present.
- Final LaTeX log: citations and references resolved; no overfull boxes.
- Every page of the final PDF was rendered to PNG and visually inspected for
  clipping, overflow, collisions, unreadable text, and unintended blank pages.
- The source ZIP contains 22 files, excludes build products, and was extracted
  into a clean temporary directory. Both `main.tex` and `annotated.tex`
  compiled there to 7-page PDFs with resolved references and no overfull boxes.
- PS2 regression command was rerun from `ps2_memory_portability/`: 85 tests
  passed in 1.873 seconds; 0 failures, errors, or skips.
- Review-ready PDF SHA-256:
  `01604ed055d3d835566aec2ac67957803d8666345ed85e9e2671ddecd10e6966`.
- Overleaf source ZIP SHA-256:
  `6406aeb0aad8c99556a07076c842f15e2cfdcb493f23ebf711a3a409e3ed1322`.

## Manual facts still required

The official team code is FP10. The symposium session, finished A0 poster
reference, and post-September-28 evidence remain pending. See
`paper/MANUAL_INPUTS_REQUIRED.md`.
