# COMSCI/ECON 206 PS2 Review-Ready Paper

This source tree is derived from the official
`COMSCI_ECON206_PS2_Overleaf_Student_Template`. It preserves the supplied
`sigconf,nonacm` ACM layout, five main sections, Author Notes, references,
Appendices A--F, LaTeX-native teaser figure, and clean/annotated drivers.

## Compile

Set `main.tex` as the Overleaf main document and use pdfLaTeX. The included
`acmart.cls` and `ACM-Reference-Format.bst` make the ZIP self-contained.

Local equivalent:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The clean PDF is built from `main.tex`. `annotated.tex` is retained only as a
working-copy driver for the official guidance rail.

## Evidence snapshot

- GitHub computational/deployment snapshot: `f9523b0fdd3f5dc4739dd1f08fe1265e049c1271`
- Public behavioral Space revision: `9ffb3cadcb80d558cb1d4473d227a383b8a5aa50`
- Test status at paper build: 85 passed, 0 skipped, 0 failures, 0 errors
- Behavioral conclusion: none claimed
- Classroom-auction, A0-poster, symposium, and peer-review evidence: pending

See `MANUAL_INPUTS_REQUIRED.md` before submission and the repository-level
`docs/review_ready_paper_audit.md` for claim parity.
