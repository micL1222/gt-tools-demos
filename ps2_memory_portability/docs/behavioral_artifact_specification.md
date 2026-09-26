# Behavioral Artifact Specification

## Behavioral question

**Does lowering technical switching friction through memory portability
actually translate into user switching, or do perceived difficulty,
personalization concerns, privacy concerns, trust, and status-quo persistence
create additional behavioral friction?**

*Stay or Switch?* is an exploratory classroom demonstration, not a
representative, causal, or IRB-approved population study.

## Connection to the economics model

The economic model and behavioral artifact address distinct units of analysis:

1. Game theory asks whether platforms strategically supply portability.
2. Social choice compares modeled equilibrium outcomes with a normalized
   collective objective.
3. Mechanism design changes platform incentives through `tau`.
4. The auction application represents portability as lowering a switching
   hurdle and increasing feasible competitive allocation.
5. The behavioral artifact asks whether a hypothetical user chooses to switch
   when a simplified user-level benchmark favors switching.

The artifact does not simulate platform BNE and does not validate the Bayesian
equilibrium model. Status-quo-bias research motivates the user-level question;
it does not establish status-quo bias among AI-assistant users.

## Fixed scenario design

Each scenario combines one portability condition with one normalized expected
benefit from moving to Assistant B.

| Condition | Normalized hurdle `r` | Interpretation |
|---|---:|---|
| Full | 0.20 | Core preferences, selected project context, and memory summaries transfer with high fidelity. |
| Partial | 0.35 | Some preferences and summaries transfer; some personalization must be rebuilt. |
| None | 0.50 | Existing personalization does not meaningfully transfer. |

The benefit levels are `g ∈ {0.15, 0.30, 0.45, 0.60}`. Crossing the three
conditions with the four levels produces 12 fixed scenarios. The Partial value
`0.35` is a new behavioral-demonstration parameter; it does not replace the
Phase 3 locked/portable auction hurdles. All values are normalized assumptions,
not empirical estimates.

Stable scenario IDs are `FULL_015` through `FULL_060`, `PARTIAL_015` through
`PARTIAL_060`, and `NONE_015` through `NONE_060`. Public assignment is uniform
over the fixed catalog. The sampler accepts a seed for deterministic tests.

## Simplified benchmark

The rule is:

- predict **Switch** if `g > r`;
- predict **Stay** if `g < r`.

There are no equality cases. The catalog intentionally contains six Stay and
six Switch predictions. The interface calls this a “simplified benchmark,”
never a correct or rational answer.

## Interaction flow

1. The app displays a hypothetical two-year relationship with Assistant A, a
   portability condition, and `g`; it does not reveal `r`.
2. The user makes an initial Stay/Switch decision.
3. The user completes required 1–7 ratings for perceived switching difficulty,
   personalization-loss concern, privacy concern, and trust in Assistant B.
4. The user may enter a session-only reflection of at most 300 characters, with
   a warning against personal or sensitive information.
5. On benchmark reveal, the app immutably records the initial decision and
   ratings, then displays `g`, `r`, `g-r`, and the prediction.
6. The user makes a final Stay/Switch decision and may add another session-only
   reflection.
7. Before adding the current play, the app snapshots earlier anonymous plays
   for the same portability condition and overall.
8. The app displays prior aggregate counts, rates, agreement, and rating means,
   then adds the current structured response exactly once.
9. “Try Another Scenario” creates a new play ID and clears session inputs.

## Session state

The current Gradio session holds a random play ID, scenario ID, initial and
final choices, four ratings, optional reflections, benchmark-reveal status, and
submission status. Optional text remains session-only and may disappear on a
new scenario or runtime restart.

## Runtime aggregate

The thread-safe in-memory store records only:

- play and scenario IDs;
- portability condition, benefit, hurdle, and benchmark prediction;
- initial and final choice;
- change status and initial/final benchmark agreement; and
- the four structured ratings.

The store uses a lock around reads and writes and a submitted-play-ID set to
prevent duplicate counting. It has no disk or database backend. Free text is
not part of the aggregate model.

## Peer-play logic

The peer snapshot precedes insertion of the current response. It reports the
number of prior plays, Stay/Switch counts and rates, benchmark-agreement rate,
and mean ratings for the same portability condition and overall. When there are
no prior plays, the app says so and displays no fabricated peers. Raw rows,
free text, IDs, and timestamps are never shown.

## Interpretation and limitations

An initial or final decision can match or differ from the benchmark. A
difference is not labeled a mistake, irrationality, or bias because `g-r`
omits trust, privacy, uncertainty, habit, attachment to personalization, and
other preferences. Anonymous plays are not independent participants when a
person can play repeatedly. Runtime aggregates reset on restart and do not
support population inference, causal effects, actual switching-cost estimates,
willingness-to-pay estimates, or claims about real platform behavior.

## Static deployment variant

The original Gradio prototype remains the locally verified design reference: it
uses a thread-safe process-memory aggregate shared by users of that server
runtime. The separate free Static Space preserves the same 12 scenarios,
benchmark rule, decision flow, reflection measures, text safeguards, and
evidence claims, but has no server runtime.

Its equivalent aggregate is an in-memory JavaScript array scoped only to the
currently open browser page. It snapshots prior plays before adding the current
one, but cannot combine plays across browsers or devices. Refreshing or closing
the page clears the aggregate and all optional text. This hosting change does
not change the scenario design, benchmark, or interpretation of any future
plays.
