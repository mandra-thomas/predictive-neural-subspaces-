# Inventory of AI-tool use (for the author's disclosure statement)

Prepared on 25 November 2026 by Claude (Anthropic), working as Claude Code, at the author's request. This file is
not the AI-use statement: it lists, as factually as the record allows, which tasks AI tools performed, so the author
can write the statement after checking the course's disclosure requirements. Where the record does not show who did
something, the file says so and leaves it for the author to confirm.

## Tools

- **Claude Code** (Anthropic's Claude, run as a coding agent in the author's terminal and VS Code). It read and wrote
  files, ran commands locally and prepared jobs for the PACE ICE cluster, and committed and pushed to the repository.
- **AI subagents.** Further Claude instances that Claude Code launched to review, audit or draft specific pieces.
  These are the "independent reviews" mentioned in older versions of the documents. They were briefed without the
  main session's conclusions, but they are the same kind of model and are not human review.
- No other AI tools appear in the repository record. The author should add any others used, for example for the
  proposal or the talk.

## What the record shows AI tools did

**Repository history.** All 75 commits (16 to 25 November 2026) carry the author's git identity, but many were
written and made by Claude Code in sessions the author directed. The git author field therefore does not show who
wrote a change.

**Registered study (16 to 22 November; `master`, tag `freeze-2026-11-23-post-talk`).** This list comes from the draft
AI statement previously in `report/main.tex`, which Claude drafted and the author had not yet confirmed. Claude was
used to:
- plan the analysis and adversarially review the plan; the amendment file says an adversarial review of the analysis
  plan produced D1 to D9 and A1 to A11;
- write the analysis library, the numbered scripts and the tests;
- run the analyses and the exploratory pilots (A12 to A16), locally and on PACE ICE;
- carry out the literature review in `reports/` and `research_notes/`;
- draft the report, the presentation slides and the figures, with further AI agents reviewing the drafts.

The same draft stated that the author set the research question, wrote the proposal, made the design decisions and
amendments, and checked the results. **The author should confirm or correct each of these, item by item.**

**Post-talk work (23 to 25 November; branch `pilot-timescale-fix`).** From the working sessions:
- *Timescale follow-ups (A17).*
  - Claude proposed the plan.
  - The author made several choices:
    - the latent model as a core part;
    - MOs only;
    - the scope of the branch;
    - running everything immediately;
    - block-switch alignment as a small part.
  - Claude wrote the amendment text, code, tests, figures and office-hours notes, ran the analyses, and wrote the
    results and the review note.
- *Calibrated simulation and latent model (A18 parts A and B).*
  - The author pasted task lists and reviews asking for the simulation and later a bounded latent-model test.
  - Claude designed the specification, gate and stopping rule; wrote and committed the amendments before running;
    wrote the code (`pns.synth` extensions, `pns.sim_a18`, `pns.lds`, scripts 26 and 27) and tests; ran everything;
    and wrote the results.
  - Two AI subagents audited part A, and Claude applied their corrections.
- *Sensitivity check (A19).* The author asked for one narrowly scoped, documented sensitivity analysis. Claude wrote
  the specification, script and results and committed the specification first.
- *Reviews of 25 November.*
  - At the author's request, six AI subagents audited code, statistics, numbers, the mathematical walkthrough, the
    course report and the repository.
  - Claude verified their main claims and corrected the documents, with three subagents doing the walkthrough,
    briefing and slide edits.
  - A further subagent audited the rewritten report for omissions and for its numbers.
- *Documents.*
  - Claude wrote `RESULTS.md`, `README.md`, `ANALYSIS_LOG.md` entries and the amendment entries from A17 on.
  - Claude also wrote the two explainers in `reports/` (the briefing and the mathematical walkthrough), the
    office-hours notes, and the untracked TA office-hours deck.
- *Report.* Claude rewrote `report/main.tex` on 25 November: the structure, all new text, the derivation section, the
  simulation figure (`report/scripts/make_figures.py`) and the bibliography additions. The author asked for the
  rewrite and set its framing constraints:
  - no claim that drift is the established cause;
  - no claim that stimulus memory is a new discovery;
  - the briefing kept separate;
  - the AI-use statement left to the author.

## What the record does not show

- Which parts of the code, text and figures the author read, checked or edited by hand.
- Whether the author independently verified any numbers. Every verification in the record was done by Claude or AI
  subagents.
- How the proposal, the talk and the original research question were produced.

## Points the course may want disclosed

- AI tools designed, coded, ran and interpreted the post hoc analyses (A17 to A19), under the author's direction and
  approval.
- AI tools drafted the report text, figures and slides.
- No human other than the author reviewed the analysis, and the record does not show how much of it the author
  checked personally.
