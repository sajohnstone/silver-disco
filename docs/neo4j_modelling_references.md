# Neo4j Modelling Reference Material

These are official Neo4j resources to draw on when proposing the graph
model. Use them to shape reasoning and vocabulary in the DRAFT files — do
not cite or link them directly in the finalised, deck-facing files
(`dataset_review.md`, `model_notes.md`, `assumptions_tradeoffs.md`,
`business_questions.md`). Those files should read as Stu's own reasoning.

## 1. Graph Data Modeling — Getting Started
https://neo4j.com/docs/getting-started/data-modeling/

Core idea: a data model defines how information is organized in a database,
and a good data model makes querying and understanding your data easier. In
Neo4j, data models have a graph structure — nodes, relationships, and
properties, rather than tables and foreign keys.

## 2. Graph Modeling Tips
https://neo4j.com/docs/getting-started/data-modeling/modeling-tips/

Core idea, directly relevant to this assignment: **start from the questions
you want to ask of the data, not from the raw schema.** Knowing the kinds of
queries you need to run should drive structural decisions — e.g. if a value
needs to be queried by range or matched against other entities, it likely
shouldn't just be a plain property; it may need to be its own node or
captured on a relationship.

This directly supports the assignment's own required approach: state the
business questions first (3.2), then justify the model against them (3.2),
then prove it out with query sketches (3.3). The model proposal draft should
be built in that order — questions first, then structure — not schema first,
questions bolted on after.

## How to use these in the draft workflow

When generating `2-solution/model_proposal_DRAFT.md`, reason explicitly
through:
1. What are the 2–3 business questions this model needs to answer?
2. What structure (nodes vs relationships, transaction as node vs edge)
   best serves those specific questions, per the "questions first" principle
   above?
3. What are the trade-offs of that structure vs an alternative, and why was
   the alternative set aside?

This keeps the proposal grounded in Neo4j's own stated modelling philosophy,
which should make it easier for Stu to defend the choices as
Neo4j-idiomatic, not just technically valid.