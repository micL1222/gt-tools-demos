#!/usr/bin/env python3
"""Execute the Phase 3 notebook in a fresh kernel and save actual outputs."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "02_social_choice_mechanism_auction.ipynb"

notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
NotebookClient(
    notebook,
    timeout=900,
    kernel_name="cs206-ps2",
    resources={"metadata": {"path": str(PROJECT_ROOT)}},
).execute()
nbformat.validate(notebook)
nbformat.write(notebook, NOTEBOOK_PATH)
print(f"Executed {NOTEBOOK_PATH.relative_to(PROJECT_ROOT)} with no cell errors")
