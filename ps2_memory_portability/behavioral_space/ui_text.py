"""Audited user-facing language for the Stay or Switch? Space."""

EVIDENCE_BOUNDARY_SHORT = """
### Evidence Boundary

This is an **exploratory classroom demonstration**, not a representative or
causal study of AI-assistant users. Its numerical benefits and hurdles are
normalized scenario parameters—not estimates for real platforms. A choice that
differs from the benchmark is not automatically irrational or biased.
"""


EVIDENCE_BOUNDARY_FULL = """
## Evidence Boundary

This Space is a classroom behavioral demonstration linked to a
computational-microeconomics proposal.

- Responses are exploratory anonymous **plays**, not a representative sample
  of AI-assistant users.
- The demo cannot establish population-level effects or causal relationships.
- Numerical switching benefits and hurdles are normalized experimental
  parameters, not empirical estimates of real AI platforms.
- A Stay/Switch choice that differs from the benchmark is not automatically
  evidence of irrationality or status-quo bias; the benchmark omits many real
  preferences and risks.
- The Space does not collect names, email addresses, account histories, IP
  addresses, device fingerprints, or sensitive personal information.
- Optional reflection text remains only in the current Gradio session. It is
  not placed in the peer aggregate or persisted by the app.
"""


METHODS_TEXT = """
## How this demo works

The demo samples uniformly from **12 fixed scenarios**: three memory-portability
conditions (Full, Partial, None) crossed with four normalized switching-benefit
levels (`0.15`, `0.30`, `0.45`, `0.60`). The corresponding normalized hurdles
are `0.20`, `0.35`, and `0.50`. There are no equality cases.

The simplified rule is **Switch if `g > r`; Stay if `g < r`**. The hurdle `r`
is hidden until the initial decision and four reflection ratings are recorded.
The benchmark is a comparison point, not advice or a correct answer.

Peer comparison uses only aggregate statistics from earlier anonymous plays in
the current server process. The current play is excluded from that prior-play
snapshot and added only afterward. Free text is never aggregated. There is no
persistent participant-data backend; aggregates reset when the Space restarts.
"""


MODEL_CONNECTION_TEXT = """
## Connection to the Research Model

The platform-side model studies whether portability is strategically supplied.
The social-choice extension compares modeled outcomes, the mechanism extension
changes platform incentives, and the auction application represents portability
as reducing switching friction.

This artifact asks a different, user-level question:

> Even when modeled technical friction falls, does a human user actually choose
> to switch?

The layers are linked but distinct. This demonstration does not validate the
Bayesian equilibrium model, and deployment alone is not behavioral evidence.
Status-quo-bias research motivates the question; it does not establish that
AI-assistant users are status-quo biased.
"""


BENCHMARK_CAVEAT = (
    "This is a simplified benchmark, not a recommendation about what you should "
    "do. It intentionally ignores trust, privacy preferences, habit, uncertainty, "
    "attachment to existing personalization, service-quality dimensions not "
    "captured by g, and other personal considerations."
)


PII_WARNING = (
    "Optional, maximum 300 characters. Please do not enter your name, email, "
    "account details, health information, or other sensitive/personal information."
)
