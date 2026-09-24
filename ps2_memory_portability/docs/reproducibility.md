# Reproducibility

## Recorded host

- Operating system: macOS 26.5.2
- Architecture: Apple Silicon (`arm64`)
- Isolated environment: Conda environment `cs206-ps2`
- Python used for the recorded run: 3.12.14
- Anaconda `base`: not modified

The machine's Apple system `python3` was 3.9.6 and Anaconda `base` exposed Python 3.13.5. Neither was used for the recorded Phase 2 execution.

## Create the environment

From a shell with Conda available:

```bash
conda create -y -n cs206-ps2 python=3.12 pip
conda run -n cs206-ps2 python -m pip install -r requirements.txt
```

Equivalent environment metadata is in `environment.yml`:

```bash
conda env create -f environment.yml
```

Register the kernel used by the notebook executor:

```bash
conda run -n cs206-ps2 python -m ipykernel install --user \
  --name cs206-ps2 --display-name "Python (cs206-ps2)"
```

## Regenerate all computational outputs

Run from `ps2_memory_portability/`:

```bash
conda run -n cs206-ps2 python scripts/run_phase2.py
```

Expected core summary:

- direct pure BNE: `(LL,LL)` and `(PL,PL)`;
- no asymmetric pure BNE at (p=0.7);
- `PL` first appears on the prior grid at (p=0.60);
- benchmark low-type mixed probability: (6/7\approx0.8571428571);
- three CSV outputs, one JSON record, and two PNG figures;
- an EFG file only if PyGambit imports and agrees with the direct checker.

The runner fails rather than writing a successful-looking record if the direct benchmark, threshold, or a completed PyGambit cross-check disagrees.

## Run tests

```bash
conda run -n cs206-ps2 python -m unittest discover -s tests -v
```

The PyGambit agreement test is skipped with a readable reason if PyGambit is unavailable. All other tests are independent of PyGambit.

## Build and execute the notebook

Rebuild the source notebook when its reviewed narrative changes:

```bash
conda run -n cs206-ps2 python scripts/build_notebook.py
```

Execute every cell in a fresh registered kernel and save the actual outputs:

```bash
conda run -n cs206-ps2 python scripts/execute_notebook.py
```

The executor sets the working directory to the project root. The notebook contains no absolute path to this computer.

## PyGambit on Apple Silicon

PyGambit 16.7.0 does not publish a macOS wheel on PyPI, so pip attempts a source build on this host. The direct Bayesian verifier is intentionally independent of that build. The recorded outcome of the actual installation and solver attempt is stored in `outputs/benchmark_verification.json`; an EFG export is created only after a real successful cross-check.

For this recorded run, the local PyGambit 16.7.0 installation imported successfully and the solver cross-check agreed exactly with the direct pure-BNE result: `(LL,LL)` and `(PL,PL)`. The benchmark EFG file was therefore exported. A cold import took roughly 12.5 seconds on the recorded host, so short external import timeouts can incorrectly make a working installation appear unavailable.

If a compatible local source build is unavailable, a fallback is to clone the repository in a Linux/Colab environment, install `requirements.txt`, and run the same runner. The course template warns that the PyGambit build can take several minutes there as well. Do not substitute the unrelated PyPI package named `gambit`.

## Output verification

`outputs/benchmark_verification.json` records:

- Python and package versions;
- host architecture;
- UTC generation time;
- the pre-commit repository HEAD;
- working-tree state at generation;
- actual PyGambit status;
- all type-level benchmark diagnostics.

The file intentionally does not embed the commit that contains itself. The exact submission commit should be reported separately after committing.

## Endpoint convention

The machine-readable sweeps contain only (p=0.01,0.02,\ldots,0.99). At (p=0) or (p=1), one type has zero probability and its action is not disciplined by the ordinary ex-ante BNE condition. Those endpoints are treated as boundary cases, not silently mixed with the full-support results.

## Phase 3 regeneration

Phase 3 uses only NumPy, pandas, Matplotlib, and the Python standard library in
the existing `cs206-ps2` environment. From `ps2_memory_portability/`, run:

```bash
conda run -n cs206-ps2 python scripts/run_phase3.py
```

The runner verifies the Phase 2 benchmark before generating the social-choice,
mechanism, and auction outputs. The mechanism grids are constructed from
integers. The auction uses seed `20603`, 100,000 common valuation draws, and the
same sample in all four mechanism/reserve conditions.

Build and execute the Phase 3 notebook with:

```bash
conda run -n cs206-ps2 python scripts/build_phase3_notebook.py
conda run -n cs206-ps2 python scripts/execute_phase3_notebook.py
```

Run all Phase 2 and Phase 3 tests with:

```bash
conda run -n cs206-ps2 python -m unittest discover -s tests -v
```

The full 400,000-row auction simulation is generated and validated in memory.
To avoid committing an unnecessarily large raw file, the repository records a
400-row deterministic validation sample, the complete four-condition summary,
and a JSON validation record containing the seed, formulas, analytical
allocation probabilities, simulated probabilities, and absolute errors.
