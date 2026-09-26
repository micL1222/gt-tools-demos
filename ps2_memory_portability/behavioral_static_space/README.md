---
title: Stay or Switch?
emoji: 🔄
colorFrom: blue
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
short_description: A behavioral demonstration of AI memory portability and switching decisions.
---

# Stay or Switch?

A zero-build, client-side behavioral demonstration of AI memory portability and
switching decisions for COMSCI/ECON 206.

## Research purpose

The broader project models whether platforms strategically provide portability.
This artifact asks a distinct user-level question: when a simplified benchmark
suggests switching is attractive, would a hypothetical user switch? It is an
exploratory classroom demonstration, not representative, causal, or population
evidence.

## Interaction

The page samples uniformly from 12 fixed scenarios. You choose Stay or Switch,
complete four required 1–7 reflection ratings, reveal the benchmark, choose
again, and can compare the result with earlier anonymous plays in the same open
browser page.

For reproducible inspection, a valid scenario can be selected with a query
parameter, for example `?scenario=FULL_030`. An invalid value safely falls back
to random selection.

## Benchmark

The scenarios cross Full (`r=0.20`), Partial (`r=0.35`), and None (`r=0.50`)
portability with normalized benefits `g=0.15`, `0.30`, `0.45`, and `0.60`.
The simplified benchmark predicts Switch if `g > r` and Stay if `g < r`.
There are no equality cases; six scenarios predict Stay and six predict Switch.
These parameters are normalized demonstration assumptions, not estimates for
real products, qualities, or switching costs.

## Privacy

This zero-build Static Space has no backend, database, analytics, external API,
cookie-based tracking, or browser persistence. Optional reflection text stays
only in current page memory and is never added to peer summaries or sent
anywhere. Refreshing or closing the page clears the current play, reflections,
and peer history.

## Peer-comparison limitation

Because this free Static Space has no shared backend, peer summaries include
only earlier plays from the current browser session. They do not combine
responses across different devices or browsers. The current response is
excluded from its own prior-peer snapshot, and no seed or fake peers are used.

## Evidence boundary

A choice that differs from the benchmark is not automatically irrational or
evidence of status-quo bias; the benchmark omits trust, privacy, habit,
uncertainty, attachment to personalization, and other real preferences. The
artifact does not establish causal effects, population preferences, actual
switching costs, or actual AI-user status-quo bias.

## Source project

The static package is an upload-ready counterpart to the locally verified
Gradio prototype in the [`ps2-memory-portability` branch](https://github.com/micL1222/gt-tools-demos/tree/ps2-memory-portability/ps2_memory_portability). Upload the five files named in `UPLOAD_MANIFEST.txt` to a manually created Hugging Face Static Space.
