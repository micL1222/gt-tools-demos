# Hugging Face Deployment Guide

## Original approach: Gradio prototype

- Local path: `ps2_memory_portability/behavioral_space/`
- Conda environment: `cs206-ps2`
- Python: 3.12
- Gradio: 6.28.0
- Space SDK: Gradio
- Intended slug: `ps2-stay-or-switch-memory-portability`

Local launch:

```bash
cd ps2_memory_portability/behavioral_space
conda run -n cs206-ps2 python app.py
```

The Space upload must contain only `app.py`, `core.py`, `store.py`,
`ui_text.py`, `requirements.txt`, and `README.md`. Do not upload the course
repository, outputs, tests, credentials, runtime data, or Git history.

## Hosting blocker

Local imports, callback validation, the 76-test suite, and the HTTP smoke test
passed on 2026-09-25. The subsequent credential check reported an authenticated
personal namespace of `mickeystk`. No token was printed or stored in this
repository.

Deployment was attempted on 2026-09-25 and stopped at repository creation with
HTTP 402. Hugging Face reported that Gradio and Docker Spaces on the free
`cpu-basic` tier require a paid plan. No Space repository was created, so there
is no Space URL, build status, or deployed revision to report.

## Chosen fallback: free Static Space

The project deliberately does not use a paid compute plan. The new
`behavioral_static_space/` package is a zero-build HTML, CSS, and vanilla
JavaScript upload package for a manually created Hugging Face **Static** Space.
Its manual upload procedure is in [hf_static_deployment.md](hf_static_deployment.md).

## Behavioral difference

The Gradio prototype's process-memory aggregate could be shared by users of
the same server runtime. A free Static Space has no backend, so its peer
comparison is deliberately limited to prior anonymous plays in the current
browser page session. It never combines responses across browsers or devices,
and refresh or close clears that in-memory history.

## Original runtime behavior

The original peer aggregate is deliberately memory-only. A Space rebuild,
restart, sleep/wake cycle, or process replacement clears all prior-play
statistics. This history is preserved for methodological transparency; the
Gradio prototype remains a locally verified reproducibility artifact.

## Historical verification requirements

A successful upload alone is insufficient. Deployment is complete only after:

1. the Space build reports a running status;
2. the public page responds successfully;
3. no immediate runtime error appears; and
4. initialization can be checked without adding a fake behavioral response.

Until those checks succeed, documentation and validation output must retain a
pending or failed deployment status and must not contain a guessed URL.
