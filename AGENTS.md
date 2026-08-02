# AGENTS.md

## Project context

This project supports a technical interview deliverable for a Senior Solutions
Engineer role at Neo4j. The track is **Fraud (Payments Transaction Graph
Modelling)**. Live panel review is 60 minutes; no written materials are
submitted ahead of time — everything here is prep for a live, on-the-day
presentation and whiteboard discussion.

**Full assignment brief:** see `docs/assignment_brief.md`
**AI usage policy (must be followed):** see `docs/ai_usage_policy.md`
**Neo4j modelling reference material:** see `docs/neo4j_modelling_references.md`

## Non-negotiable ground rules

1. **All data is synthetic.** No real transaction data exists or should be
   sourced. Generate a representative synthetic dataset from the column
   reference in the brief.
2. **I must be able to personally explain and defend every
   decision live**, per Neo4j's AI Usage Policy. Do not produce polished
   "final" prose in analysis files — produce clearly labelled **drafts** that
   I will review, verify, and rewrite in my own words before use. Flag
   this explicitly at the end of any analytical file you write.
3. **Do not silently invent facts about Neo4j, the dataset, or the interview
   process.** If something is ambiguous, state it as an assumption in the
   relevant file rather than guessing silently.
4. Favour simple, explainable modelling choices over clever ones. The
   evaluation criteria explicitly reward reasoning and clarity over
   sophistication.
5. You may draw on the principles in `docs/neo4j_modelling_references.md`
   when proposing the model, but do not cite external links or sources
   inside the deck-facing files themselves (`dataset_review.md`,
   `model_notes.md`, `assumptions_tradeoffs.md`, `business_questions.md`).
   Those should read as my own reasoning, in my own words — references are
   for shaping the draft, not for quoting in the output.

## What "done" looks like

This is the exact deck structure committed to Neo4j in writing. Every output file maps to one of these three sections — nothing
extra, nothing missing:

1. **Problem & dataset review** — key entities, relationships, and any
   patterns/ambiguities identified in the data.
2. **Solution** — data model (entities, relationships, transaction
   representation), link to the arrows.app model, and assumptions/trade-offs
   including at least one alternative approach considered and rejected.
3. **Queries** — 2–3 business questions, each with a query/traversal sketch.

`README.md` should present the finished material in exactly this three-part
order, ready for me to lift straight into slides.

## Review checkpoint — mandatory workflow for the model and assumptions

The data model and its assumptions are the parts of this project I must be
able to defend most deeply live, so these are **never written straight to
final files**. Follow this two-step process every time:

**Step 1 — Propose, don't finalise.**
When asked to design the graph model, write a draft to
`2-solution/model_proposal_DRAFT.md` (not `model_notes.md`). This draft must
include:
- Proposed entities/nodes and properties
- Proposed relationships (direction, cardinality)
- Proposed transaction representation (node vs relationship vs hybrid) with
  reasoning
- Every assumption made, listed explicitly and separately from the model
  itself (e.g. "Assumption: M-prefix = merchant account — not stated in the
  column reference")
- At least one alternative approach considered and why it was set aside

Clearly label the file as a **draft proposal for my review** — do not
present it as finished output, and do not write `model_notes.md` or
`assumptions_tradeoffs.md` in the same step.

**Step 2 — Wait for review.**
Stop after Step 1 and prompt I will review the draft. Only after I have
responded with explicit accept/reject/edit decisions on the model and each
assumption should `model_notes.md` and `assumptions_tradeoffs.md` be
written — and they should reflect my decisions, in my own reasoning,
not simply be the draft copied over.

This same propose-then-review pattern applies to the dataset review
(`1-problem-dataset-review/`) and business questions (`3-queries/`) as well:
draft first, flag for review, only finalise after I have weighed in.

## Project structure

```
neo4j-fraud-assignment/
├── docs/
│   ├── assignment_brief.md              # full text of the official brief
│   ├── ai_usage_policy.md               # Neo4j's AI usage policy, for reference
│   └── neo4j_modelling_references.md    # official Neo4j modelling principles, for reference
├── data/
│   ├── generate_dataset.py        # synthetic dataset generator
│   └── transactions.csv           # generated output (supports section 1 and 2)
├── 1-problem-dataset-review/
│   ├── dataset_review_DRAFT.md    # proposed draft — awaits my review
│   └── dataset_review.md          # finalised after review, in my own words
├── 2-solution/
│   ├── model_proposal_DRAFT.md    # proposed model + assumptions — awaits my review
│   ├── model_notes.md             # finalised after review
│   ├── arrows_export.json         # arrows.app model export (or notes + link)
│   └── assumptions_tradeoffs.md   # finalised after review, in my own words
├── 3-queries/
│   ├── business_questions_DRAFT.md # proposed questions + sketches — awaits my review
│   └── business_questions.md      # finalised after review
└── README.md                      # sections 1, 2, 3 in order — deck-ready
```

## Dataset generation requirements

`data/generate_dataset.py` should produce `data/transactions.csv` matching
this schema exactly (from the official brief):

| Column | Type | Description |
|---|---|---|
| step | integer | 1 unit = 1 hour of simulated time (1–743) |
| type | string | CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER |
| amount | float | transaction amount, local currency |
| nameOrig | string | originating account ID |
| oldbalanceOrg | float | origin balance before transaction |
| newbalanceOrig | float | origin balance after transaction |
| nameDest | string | destination account ID |
| oldbalanceDest | float | destination balance before transaction |
| newbalanceDest | float | destination balance after transaction |
| isFraud | boolean | fraud label for the transaction |
| isFlaggedFraud | boolean | flagged by an existing business rule |
| device_id | string | identifier for the device the transaction was initiated from |
| ip_address | string | IP address the transaction was initiated from |

Target ~50–100 rows — enough to reason from and pull concrete examples out
of, not a full production-scale dataset. This is a reasoning aid, not a
deliverable. Deliberately include these patterns (they are the basis for the
fraud narrative and query demos):

- **A handful of full-balance-sweep fraud transactions**: `type=TRANSFER`,
  `oldbalanceOrg == amount`, `newbalanceOrig == 0`, `isFraud=1`.
- **A small mule-account cluster (4–5 accounts)** that share a `device_id` or
  `ip_address` with a known fraud account, reachable within 2 hops via
  transactions — this is the multi-hop graph-native detection story.
- **Account ID prefix convention**: `C` = customer account, `M` = merchant
  account, consistent with the two sample rows in the brief. Include both.
- **Zero destination balances on merchant PAYMENT transactions** (matching
  the sample data pattern — merchant-side balances aren't tracked).
- Normal, non-fraud variety across all five transaction types for realism.

After generation, do not assume the patterns are correct — report summary
stats (fraud count, cluster membership, prefix distribution) so I can
visually confirm the dataset actually contains what was asked for.

## Style and output conventions

- Markdown files: plain, direct, no filler. Bullet points over paragraphs
  where possible — this will be lifted into slides.
- Cypher sketches: illustrative, not necessarily runnable against a live
  instance (no Neo4j instance is required for this track) — but should be
  syntactically plausible and reflect the actual model in `model_notes.md`.
- Every DRAFT and finalised file in `1-problem-dataset-review/` and
  `2-solution/` must end with a short "Assumptions used in this file" note
  if any were made, so nothing is silently baked in.
- Do not fabricate a citation, statistic, or Neo4j product claim. If unsure,
  say so rather than filling the gap.

## Explicitly out of scope

- No running Neo4j Aura instance (that's the Data & AI track, not this one).
- No live coding or AI use during the actual live panel — this repo is prep
  only.
- No deck/slide file needs to be generated here — I will build the deck
  manually from these source files.