---
title: Stay or Switch?
emoji: 🔄
sdk: gradio
sdk_version: 6.28.0
app_file: app.py
python_version: "3.12"
---

# Stay or Switch?

**A behavioral demonstration of AI memory portability and switching decisions**

This Gradio Space adds a user-decision layer to the COMSCI/ECON 206 project
*Stay or Switch? Strategic Memory Portability in Competing AI Assistants*. It
does not rerun the platform equilibrium model. Instead, it asks whether a
hypothetical user chooses to switch when a simplified benchmark predicts that
switching is attractive.

## Interaction flow

1. Receive one uniformly sampled fixed scenario.
2. Choose initially between staying with Assistant A and switching to B.
3. Complete four required 1–7 reflection ratings.
4. Reveal the normalized benchmark only after the initial response is recorded.
5. Make a final decision.
6. Compare with aggregate statistics from earlier anonymous plays in the
   current Space runtime.
7. Try another scenario as a new play.

## Scenario design

The catalog crosses three normalized memory-portability conditions—Full
(`r=0.20`), Partial (`r=0.35`), and None (`r=0.50`)—with four normalized
switching benefits (`g=0.15`, `0.30`, `0.45`, `0.60`). The benchmark predicts
Switch when `g>r` and Stay when `g<r`. There are no equality cases, and the 12
scenarios split evenly into six Stay and six Switch predictions.

These values are experimental demonstration parameters, not estimates of
actual AI products, switching costs, quality, or willingness to pay.

## Evidence boundary

This is an exploratory classroom demonstration, not a representative sample,
causal study, or IRB-approved population study. A decision that differs from
the benchmark is not automatically irrational or evidence of status-quo bias:
the benchmark omits trust, privacy, uncertainty, habit, and other legitimate
preferences. Deployment alone is not behavioral evidence.

## Privacy and storage

- The app does not request names, emails, account histories, IP addresses, or
  sensitive personal information.
- Optional reflection text is session-only and is never added to the aggregate.
- The peer display exposes only aggregate statistics, never raw response rows,
  free text, play IDs, or timestamps.
- Structured play aggregates exist only in process memory. There is no database
  or persistent participant-data backend, and aggregates reset on restart.
- Double submission of the same play ID is rejected.
- Gradio telemetry and its monitoring endpoint are disabled by the app.

## Local run

From this directory:

```bash
conda run -n cs206-ps2 python app.py
```

Then open `http://127.0.0.1:7860`.

The broader computational project and its evidence boundaries are maintained in
the [`ps2-memory-portability` branch](https://github.com/micL1222/gt-tools-demos/tree/ps2-memory-portability/ps2_memory_portability).
