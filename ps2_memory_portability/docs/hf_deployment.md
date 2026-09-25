# Hugging Face Deployment Guide

## Artifact location and environment

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

## Authentication and deployment status

Local imports, callback validation, the 76-test suite, and the HTTP smoke test
passed on 2026-09-25. The subsequent credential check reported an authenticated
personal namespace of `mickeystk`. No token was printed or stored in this
repository.

Deployment was attempted on 2026-09-25 and stopped at repository creation with
HTTP 402. Hugging Face reported that Gradio and Docker Spaces on the free
`cpu-basic` tier require a PRO subscription. No Space repository was created,
so there is no Space URL, build status, or deployed revision to report.

To retry, enable a Hugging Face plan that permits Gradio Space creation for the
authenticated namespace, confirm `hf auth whoami`, and run:

```bash
conda run -n cs206-ps2 python \
  ps2_memory_portability/scripts/deploy_behavioral_space.py
```

## Reproducible deployment method

Authenticate using the Hugging Face CLI credential store if needed:

```bash
conda run -n cs206-ps2 hf auth login
```

Check authentication without printing a token:

```bash
conda run -n cs206-ps2 hf auth whoami
```

Deployment uses `huggingface_hub.HfApi`: verify the namespace, check whether
the intended repository already exists, create a Gradio Space only when safe,
and upload the six-file manifest above. Never embed a token in code or a shell
command.

After authentication, deploy or retry with:

```bash
conda run -n cs206-ps2 python \
  ps2_memory_portability/scripts/deploy_behavioral_space.py
```

The deployment script refuses to overwrite an existing Space unless its README
contains this project's marker and it contains no unexpected files. A different
clear slug can be supplied with `--slug` if the intended slug belongs to an
unrelated project.

## Runtime behavior

The peer aggregate is deliberately memory-only. A Space rebuild, restart,
sleep/wake cycle, or process replacement clears all prior-play statistics. This
is expected, is shown in the UI, and is preferable to silently persisting
classroom responses.

## Verification requirements

A successful upload alone is insufficient. Deployment is complete only after:

1. the Space build reports a running status;
2. the public page responds successfully;
3. no immediate runtime error appears; and
4. initialization can be checked without adding a fake behavioral response.

Until those checks succeed, documentation and validation output must retain a
pending or failed deployment status and must not contain a guessed URL.
