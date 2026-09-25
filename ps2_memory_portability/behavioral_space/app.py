"""Gradio application for the Stay or Switch? behavioral demonstration."""

from __future__ import annotations

import os
from uuid import uuid4

import gradio as gr

from core import (
    CHOICES,
    SCENARIO_BY_ID,
    STAY,
    SWITCH,
    agrees_with_benchmark,
    choice_label,
    create_play_record,
    sample_scenario,
    validate_rating,
)
from store import AggregateSummary, InMemoryPlayStore, PeerSnapshot
from ui_text import (
    BENCHMARK_CAVEAT,
    EVIDENCE_BOUNDARY_FULL,
    EVIDENCE_BOUNDARY_SHORT,
    METHODS_TEXT,
    MODEL_CONNECTION_TEXT,
    PII_WARNING,
)


STORE = InMemoryPlayStore()

CSS = """
.scenario-card, .benchmark-card, .peer-card {
  border: 1px solid var(--border-color-primary);
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
  background: var(--block-background-fill);
}
.muted-note { color: var(--body-text-color-subdued); }
"""


def _new_session_state() -> dict[str, object]:
    scenario = sample_scenario()
    return {
        "play_id": uuid4().hex,
        "scenario_id": scenario.scenario_id,
        "initial_choice": None,
        "perceived_switching_difficulty": None,
        "personalization_concern": None,
        "privacy_concern": None,
        "trust": None,
        "initial_reflection": "",
        "benchmark_revealed": False,
        "final_choice": None,
        "post_reflection": "",
        "submitted": False,
    }


def _scenario_markdown(state: dict[str, object]) -> str:
    scenario = SCENARIO_BY_ID[str(state["scenario_id"])]
    return f"""
### Your scenario

Imagine that you have used **Assistant A for two years**. It has learned your
writing preferences, recurring projects, and interaction habits.

**Assistant B** is now available and offers a normalized expected benefit of
**g = {scenario.normalized_benefit:.2f}** compared with staying on A. This can
represent better expected quality, usefulness, or fit; it is not a measured
dollar benefit or a real-product estimate.

**Memory portability: {scenario.portability_condition}**

{scenario.condition_description}

Make your own decision first. A simplified benchmark will be revealed only
after your initial decision and reflection are recorded.
"""


def _benchmark_markdown(state: dict[str, object]) -> str:
    scenario = SCENARIO_BY_ID[str(state["scenario_id"])]
    agreement = agrees_with_benchmark(str(state["initial_choice"]), scenario)
    relationship = "matches" if agreement else "differs from"
    return f"""
## Simplified Benchmark

| Quantity | Value |
|---|---:|
| Normalized switching benefit | `g = {scenario.normalized_benefit:.2f}` |
| Modeled switching hurdle | `r = {scenario.normalized_hurdle:.2f}` |
| Net benchmark advantage | `g - r = {scenario.benchmark_net_advantage:+.2f}` |
| Benchmark prediction | **{scenario.benchmark_prediction.upper()}** |

Rule: **Switch if `g > r`; Stay if `g < r`.**

Your recorded initial decision **{relationship} the benchmark**. {BENCHMARK_CAVEAT}
"""


def reveal_benchmark(
    state: dict[str, object],
    initial_choice: str | None,
    switching_difficulty: object,
    personalization_concern: object,
    privacy_concern: object,
    trust: object,
    initial_reflection: str | None,
):
    state = dict(state or {})
    if state.get("benchmark_revealed"):
        return (
            state,
            "Your initial response is already recorded.",
            gr.update(),
            gr.update(),
            *(gr.update() for _ in range(6)),
        )
    if initial_choice not in CHOICES:
        return (
            state,
            "Please choose Stay or Switch before revealing the benchmark.",
            gr.update(),
            gr.update(),
            *(gr.update() for _ in range(6)),
        )
    try:
        ratings = [
            validate_rating(switching_difficulty),
            validate_rating(personalization_concern),
            validate_rating(privacy_concern),
            validate_rating(trust),
        ]
    except ValueError as exc:
        return (
            state,
            str(exc),
            gr.update(),
            gr.update(),
            *(gr.update() for _ in range(6)),
        )
    reflection = (initial_reflection or "").strip()
    if len(reflection) > 300:
        return (
            state,
            "Optional reflection must be at most 300 characters.",
            gr.update(),
            gr.update(),
            *(gr.update() for _ in range(6)),
        )

    state.update(
        {
            "initial_choice": initial_choice,
            "perceived_switching_difficulty": ratings[0],
            "personalization_concern": ratings[1],
            "privacy_concern": ratings[2],
            "trust": ratings[3],
            "initial_reflection": reflection,
            "benchmark_revealed": True,
        }
    )
    return (
        state,
        "Initial decision and reflection recorded. They cannot be replaced for this play.",
        gr.update(value=_benchmark_markdown(state), visible=True),
        gr.update(visible=True),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


def _format_summary(title: str, summary: AggregateSummary) -> str:
    if summary.play_count == 0:
        return f"### {title}\n\nNo earlier anonymous plays are available."
    return f"""
### {title}

- Prior anonymous plays: **{summary.play_count}**
- Stay: **{summary.stay_count}** ({summary.stay_rate:.0%})
- Switch: **{summary.switch_count}** ({summary.switch_rate:.0%})
- Benchmark agreement: **{summary.benchmark_agreement_rate:.0%}**
- Mean perceived switching difficulty: **{summary.mean_switching_difficulty:.2f} / 7**
- Mean personalization concern: **{summary.mean_personalization_concern:.2f} / 7**
- Mean privacy concern: **{summary.mean_privacy_concern:.2f} / 7**
- Mean trust in Assistant B: **{summary.mean_trust:.2f} / 7**
"""


def _peer_markdown(
    state: dict[str, object], snapshot: PeerSnapshot, current_final_choice: str
) -> str:
    scenario = SCENARIO_BY_ID[str(state["scenario_id"])]
    final = choice_label(current_final_choice)
    relation = "matches" if final == scenario.benchmark_prediction else "differs from"
    if snapshot.overall.play_count == 0:
        empty_note = (
            "**No earlier anonymous plays are available in this Space runtime yet.** "
            "No seed or fake peer data are shown."
        )
    else:
        empty_note = (
            "The summaries below include only plays submitted before yours in this "
            "server runtime."
        )
    return f"""
## Compare with Earlier Anonymous Plays

{empty_note}

**Your final decision:** {final}

**Simplified benchmark:** {scenario.benchmark_prediction}
**Comparison:** Your final decision {relation} the benchmark.

{_format_summary(f"Same portability condition ({scenario.portability_condition})", snapshot.same_condition)}

{_format_summary("Overall prior plays", snapshot.overall)}

Peer statistics are descriptive only. They do not rank decisions and reset when
the Space process restarts.
"""


def submit_final_choice(
    state: dict[str, object],
    final_choice: str | None,
    post_reflection: str | None,
):
    state = dict(state or {})
    if not state.get("benchmark_revealed"):
        return (
            state,
            "Reveal the benchmark before making a final decision.",
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    if state.get("submitted"):
        return (
            state,
            "This play was already submitted and was not counted again.",
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    if final_choice not in CHOICES:
        return (
            state,
            "Please choose a final Stay or Switch decision.",
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    reflection = (post_reflection or "").strip()
    if len(reflection) > 300:
        return (
            state,
            "Optional reflection must be at most 300 characters.",
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )

    scenario = SCENARIO_BY_ID[str(state["scenario_id"])]
    record = create_play_record(
        play_id=str(state["play_id"]),
        scenario=scenario,
        initial_choice=str(state["initial_choice"]),
        final_choice=final_choice,
        perceived_switching_difficulty=state["perceived_switching_difficulty"],
        personalization_concern=state["personalization_concern"],
        privacy_concern=state["privacy_concern"],
        trust=state["trust"],
    )

    prior_snapshot, added = STORE.snapshot_and_add(record)
    if not added:
        return (
            state,
            "This play was already submitted and was not counted again.",
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )

    state.update(
        {
            "final_choice": final_choice,
            "post_reflection": reflection,
            "submitted": True,
        }
    )
    changed = "changed" if record.changed_choice else "kept"
    return (
        state,
        f"Play submitted once. You {changed} your decision after the benchmark.",
        gr.update(value=_peer_markdown(state, prior_snapshot, final_choice), visible=True),
        gr.update(visible=True),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


def begin_new_play():
    state = _new_session_state()
    return (
        state,
        gr.update(value=_scenario_markdown(state)),
        gr.update(value=None, interactive=True),
        gr.update(value=None, interactive=True),
        gr.update(value=None, interactive=True),
        gr.update(value=None, interactive=True),
        gr.update(value=None, interactive=True),
        gr.update(value="", interactive=True),
        "",
        gr.update(value="", visible=False),
        gr.update(visible=False),
        gr.update(value=None, interactive=True),
        gr.update(value="", interactive=True),
        gr.update(interactive=True),
        "",
        gr.update(value="", visible=False),
        gr.update(visible=False),
    )


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Stay or Switch?", analytics_enabled=False) as demo:
        session_state = gr.State({})

        gr.Markdown(
            "# Stay or Switch?\n"
            "**A behavioral demonstration of AI memory portability and switching decisions**"
        )
        gr.Markdown(EVIDENCE_BOUNDARY_SHORT)
        scenario_card = gr.Markdown("Loading a scenario…", elem_classes="scenario-card")

        gr.Markdown("## 1. What would you do?")
        initial_choice = gr.Radio(choices=list(CHOICES), label="Initial decision")

        gr.Markdown("## 2. Self-reflection")
        with gr.Row():
            switching_difficulty = gr.Radio(
                choices=list(range(1, 8)),
                label="Perceived switching difficulty",
                info="1 = Very easy · 7 = Very difficult",
            )
            personalization_concern = gr.Radio(
                choices=list(range(1, 8)),
                label="Personalization-loss concern",
                info="1 = Not concerned · 7 = Very concerned",
            )
        with gr.Row():
            privacy_concern = gr.Radio(
                choices=list(range(1, 8)),
                label="Privacy or data-handling concern",
                info="1 = Not concerned · 7 = Very concerned",
            )
            trust = gr.Radio(
                choices=list(range(1, 8)),
                label="Trust in Assistant B",
                info="1 = Very low trust · 7 = Very high trust",
            )
        initial_reflection = gr.Textbox(
            label="Optional: Why did you initially choose Stay or Switch?",
            info=PII_WARNING,
            lines=2,
            max_lines=3,
            max_length=300,
        )
        reveal_button = gr.Button("Reveal benchmark", variant="primary")
        reveal_status = gr.Markdown()

        benchmark_panel = gr.Markdown(
            value="", visible=False, elem_classes="benchmark-card"
        )

        with gr.Group(visible=False) as final_group:
            gr.Markdown("## 3. Your final decision")
            final_choice = gr.Radio(
                choices=list(CHOICES),
                label="After seeing the simplified benchmark, what would you choose now?",
            )
            post_reflection = gr.Textbox(
                label="Optional: What mattered most in keeping or changing your decision?",
                info=PII_WARNING,
                lines=2,
                max_lines=3,
                max_length=300,
            )
            submit_button = gr.Button("Submit final decision", variant="primary")
            submit_status = gr.Markdown()

        peer_panel = gr.Markdown(value="", visible=False, elem_classes="peer-card")
        new_button = gr.Button("Try Another Scenario", visible=False)

        with gr.Accordion("How this demo works", open=False):
            gr.Markdown(METHODS_TEXT)
        with gr.Accordion("Connection to the research model", open=False):
            gr.Markdown(MODEL_CONNECTION_TEXT)
        with gr.Accordion("Full evidence boundary and privacy policy", open=False):
            gr.Markdown(EVIDENCE_BOUNDARY_FULL)

        reveal_button.click(
            reveal_benchmark,
            inputs=[
                session_state,
                initial_choice,
                switching_difficulty,
                personalization_concern,
                privacy_concern,
                trust,
                initial_reflection,
            ],
            outputs=[
                session_state,
                reveal_status,
                benchmark_panel,
                final_group,
                initial_choice,
                switching_difficulty,
                personalization_concern,
                privacy_concern,
                trust,
                initial_reflection,
            ],
        )
        submit_button.click(
            submit_final_choice,
            inputs=[session_state, final_choice, post_reflection],
            outputs=[
                session_state,
                submit_status,
                peer_panel,
                new_button,
                final_choice,
                post_reflection,
                submit_button,
            ],
        )
        new_outputs = [
            session_state,
            scenario_card,
            initial_choice,
            switching_difficulty,
            personalization_concern,
            privacy_concern,
            trust,
            initial_reflection,
            reveal_status,
            benchmark_panel,
            final_group,
            final_choice,
            post_reflection,
            submit_button,
            submit_status,
            peer_panel,
            new_button,
        ]
        new_button.click(begin_new_play, outputs=new_outputs)
        demo.load(begin_new_play, outputs=new_outputs)

    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        show_error=True,
        css=CSS,
        enable_monitoring=False,
    )
