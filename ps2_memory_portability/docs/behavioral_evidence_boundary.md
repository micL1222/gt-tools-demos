# Behavioral Evidence Boundary

## What the Space demonstrates

- A structured hypothetical Stay/Switch decision under one of 12 fixed memory-
  portability scenarios.
- An initial decision made before the exact benchmark hurdle is revealed.
- Self-reflection on perceived difficulty, personalization loss, privacy, and
  trust.
- A transparent comparison with the simplified rule `Switch iff g > r`.
- A second decision after benchmark disclosure and a neutral indication of
  whether the decision changed or matches the benchmark.
- Aggregate comparison with earlier anonymous plays in the current runtime.
- A reproducible way to explore departures from a deliberately incomplete
  benchmark.

## What the Space does not establish

- A causal effect of portability on switching.
- Population-level preferences of AI-assistant users.
- Actual status-quo bias among AI users or classroom players.
- Actual switching costs, implementation costs, willingness to pay, or product
  quality.
- That a benchmark-matching decision is more rational or better than another
  decision.
- That real firms follow the project's Bayesian equilibria.
- That deployment or anonymous use validates the economic model.

## User-facing language

> This Space is a classroom behavioral demonstration linked to a
> computational-microeconomics proposal.
>
> Responses are exploratory anonymous plays, not a representative sample of
> AI-assistant users. The demo cannot establish population-level effects or
> causal relationships.
>
> Numerical switching benefits and hurdles are normalized experimental
> parameters, not empirical estimates of real AI platforms.
>
> A Stay/Switch choice that differs from the benchmark is not automatically
> evidence of irrationality or status-quo bias; the benchmark omits many real
> preferences and risks.
>
> The application does not request or store names, email addresses, account
> histories, IP addresses, device fingerprints, or sensitive personal
> information. Optional reflection text remains session-only and is never
> placed in the peer aggregate or persisted by the app.

## Storage and privacy boundary

The default store exists only in Python process memory. It retains structured,
non-identifying plays until the server process restarts, then resets. There is
no Google Sheet, Hugging Face Dataset, analytics tracker, hidden database, or
Git write path. The peer display exposes only aggregates and never displays raw
response rows or reflection text.

The app explicitly disables Gradio telemetry and the Gradio monitoring
endpoint. It adds no analytics tracker or custom cookie.

## Static deployment variant

The free Static Space is a client-side counterpart to the Gradio prototype. It
has no server runtime, backend, or shared response store. Public Static
deployment does not create a shared behavioral dataset. Any peer comparison is
local to the current browser page session and disappears on refresh or close.
It does not combine responses across devices or browsers.

Hosting and framework infrastructure may process ordinary HTTP requests to
serve the application, but the application code does not use those requests to
create identifiers or behavioral records beyond the structured fields listed
in the artifact specification.
