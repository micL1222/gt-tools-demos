# Static Behavioral Space Manual Test Checklist

Open the Static Space after upload, or run the local static server described in
the deployment guide. Use the query parameter in the address bar to select the
following deterministic checks.

| Test | URL suffix | Expected benchmark |
|---|---|---|
| A — Full 0.15 | `?scenario=FULL_015` | Stay |
| B — Full 0.30 | `?scenario=FULL_030` | Switch |
| C — Partial 0.30 | `?scenario=PARTIAL_030` | Stay |
| D — Partial 0.45 | `?scenario=PARTIAL_045` | Switch |
| E — None 0.45 | `?scenario=NONE_045` | Stay |
| F — None 0.60 | `?scenario=NONE_060` | Switch |

For each test:

1. Confirm the page initially shows condition, description, and `g`, but not
   `r`, `g-r`, or the prediction.
2. Select an initial choice and all four 1–7 reflection ratings; confirm the
   benchmark cannot be revealed when any required response is missing.
3. Reveal the benchmark and confirm the initial controls are locked.
4. Confirm `g`, `r`, `g-r`, and the expected benchmark are displayed.
5. Select and submit a final decision; confirm duplicate clicking does not add
   another play.

Also verify:

- The first submitted play receives the empty prior-peer state and does not
  count itself as a peer.
- `Try another scenario` keeps prior browser-session history available without
  reloading the page.
- `Clear browser-session peer history` clears only the current page's memory.
- Refreshing the page clears the current play and prior-peer history.
- Optional reflection text is not displayed in peer summaries and no
  participant data is sent anywhere.
