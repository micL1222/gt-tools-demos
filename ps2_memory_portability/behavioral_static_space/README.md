---
title: Stay or Switch?
emoji: 🔄
colorFrom: blue
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
short_description: Behavioral demo of AI memory portability and switching.
---

# Stay or Switch?

A zero-build, client-side behavioral demonstration of AI memory portability and switching decisions for COMSCI/ECON 206.

## Research purpose

The broader project models whether platforms strategically provide portability.

This artifact asks a distinct user-level question: when a simplified benchmark suggests switching is attractive, would a hypothetical user switch?

It is an exploratory classroom demonstration, not representative, causal, or population-level evidence.

## Interaction

The page samples uniformly from 12 fixed scenarios. You:

1. choose Stay or Switch;
2. complete four required 1–7 reflection ratings;
3. reveal the simplified benchmark;
4. choose again; and
5. compare your result with earlier anonymous plays in the same open browser session.

For reproducible inspection, a valid scenario can be selected with a query parameter, for example:

`?scenario=FULL_030`

An invalid scenario ID safely falls back to random selection.

## Benchmark

The scenarios cross three portability conditions:

- Full portability: `r = 0.20`
- Partial portability: `r = 0.35`
- No portability: `r = 0.50`

with normalized switching benefits:

`g ∈ {0.15, 0.30, 0.45, 0.60}`

The simplified benchmark predicts:

- **Switch** if `g > r`
- **Stay** if `g < r`

There are no equality cases. Six scenarios predict Stay and six predict Switch.

These parameters are normalized demonstration assumptions, not empirical estimates of real products, product quality, or switching costs.

## Privacy

This Static Space has:

- no backend;
- no database;
- no analytics;
- no external behavioral-data API;
- no cookie-based tracking; and
- no persistent browser storage.

Optional reflection text remains only in the current page's memory. It is never added to peer summaries or transmitted by the application.

Refreshing or closing the page clears the current play, reflections, and peer history.

## Peer-comparison limitation

Because this free Static Space has no shared backend, peer summaries include only earlier plays from the **current browser-page session**.

They do not combine responses across different devices or browsers.

The current response is excluded from its own prior-peer snapshot, and no fake or seeded peer responses are used.

## Evidence boundary

A choice that differs from the simplified benchmark is **not automatically irrational or evidence of status-quo bias**.

The benchmark deliberately omits trust, privacy preferences, habit, uncertainty, attachment to existing personalization, and other real considerations.

This artifact does not establish:

- causal effects of portability;
- population-level preferences;
- empirical switching-cost values;
- actual AI-platform behavior; or
- status-quo bias among AI-assistant users.

## Source project

This Static Space is the public-deployment counterpart to the locally verified Gradio prototype in the [`ps2-memory-portability` project](https://github.com/micL1222/gt-tools-demos/tree/ps2-memory-portability/ps2_memory_portability).