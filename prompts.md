## Task 1 — Generate synthetic dataset

```
Read AGENTS.md and docs/assignment_brief.md. Create data/generate_dataset.py
per the dataset generation requirements in AGENTS.md, run it, and write
output to data/transactions.csv. Report the summary stats you were asked to
report (fraud count, cluster membership, prefix distribution).
```

**Status:** run
**Notes:**

---

## Task 2 — Dataset review

```
Read data/transactions.csv and docs/assignment_brief.md section 3.1. Write
the dataset review draft to 1-problem-dataset-review/dataset_review_DRAFT.md
per AGENTS.md. Flag any patterns or ambiguities you notice in the actual
data, not just the schema.
```

**Status:** run
**Notes:**

---

## Task 2b — Dataset review (finalise, after my review)

```
I revieed the \1-problem-dataset-review\dataset_review_DRAFT.md.  update data/generate_dataset.py. run it, and outpit to data/transactions.csv
```

**Status:** run
**Notes:**

---

## Task 3c — Model proposal (draft)

```
Using docs/neo4j_modelling_references.md and the finalised dataset review in
1-problem-dataset-review/dataset_review.md, propose the graph model in
2-solution/model_proposal_DRAFT.md per AGENTS.md. Include entities,
relationships, transaction representation, assumptions and trade-offs 
rejected alternative. Stop after writing it and wait for my review.
```

**Status:** run
**Notes:**

---

## Task 3d — Dataset review

```
I've just noticed that nameOrig based on sample data should just be either Mxxxxx or Cxxxxx there was not external.  No M prefixed data has been generated.  update data/generate_dataset.py. run it, and outpit to data/transactions.csv

```

**Status:** run
**Notes:**

---


## Task 3e — Model + assumptions (finalise, after my review)

```
I've reviewed 2-solution/model_proposal_DRAFT.md. Here are my decisions:
1. DeviceId, ipAddress feel like they should be nodes to support questions like "Show me all the transactions for this IP or DeviceID".
2. isFraud, isFlaggedFraud feels like they could be labels.  
3. looking at the relationships this would only work if all transactions stayed in the same org.  I would assume this is we should probably break out accounts into two nodes accounts and say customer and merchant?
4. Agree with relationships for device and ip address (same as point 1)
3. Reject the total flat model for reasons given remove the alternative section
write to 2-solution/model_proposal_V1.md
```

**Status:** run
**Notes:**

---


## Task 3f — data catalog

```
look at the data/transactions.csv and create a document called
2-solution/current_model_DRAFT.md we just need to include an intro and a list of the fields + or assumption of what they mean
```

**Status:** run
**Notes:**

---

## Task 4a — README.md

```
Within the project write a readme.md about what it's for.  Tech used e.g openCode + Deepseek v3.2 + OpenRouter.  How to set this up for someone new.  
We can keep it brief we don't need how to exaplin how to install opencode etc.
```

**Status:** run
**Notes:**

---

## Task 4 — Business questions + query sketches (draft)

```
Using 2-solution/model_notes.md, draft 2-3 business questions this graph
model should answer and a Cypher/traversal sketch for each, into
3-queries/business_questions_DRAFT.md per AGENTS.md. Stop after writing it
and wait for my review.
```

**Status:** not yet run
**Notes:**

---

## Task 4b — Business questions (finalise, after my review)

```
I've reviewed 3-queries/business_questions_DRAFT.md. Here are my decisions:
[fill in]. Write the finalised version to 3-queries/business_questions.md
per AGENTS.md.
```

**Status:** not yet run
**Notes:**

---

## Task 5 — README (pull it together)

```
Using the finalised files in 1-problem-dataset-review/, 2-solution/, and
3-queries/, write README.md presenting the three sections in order
(Problem & dataset review, Solution, Queries) per AGENTS.md, ready for me to
lift into slides.
```

**Status:** not yet run
**Notes:**

---

## Ad hoc / troubleshooting prompts

Log anything off-script here — corrections, re-runs, or one-off asks that
didn't fit the plan above.