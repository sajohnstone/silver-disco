# Neo4j Solutions Engineer Technical Assignment — Fraud Track

Position: Senior Solutions Engineer
Format: Live Data Model Review (60 Minutes)
Prework: Initial data model development

## 1. Objective & Philosophy

At Neo4j, Solutions Architects don't just write Cypher queries or build
standalone code; they design enterprise graph ecosystems that solve complex,
real-world business challenges. This exercise is an interactive data
modelling exercise: propose an original data model and present it during a
live discussion session.

Focus: intuition, design rationale, data modelling reasoning, and
problem-solving capability. Guide the panel through the solution, justify
graph model choices, and defend the approach against shifting live
requirements.

## 2. The Scenario: Payments Transaction Graph Modelling

Work with a sample of raw payments transaction data and design a property
graph model to represent it in Neo4j. Data includes transaction-level records
covering transaction type, amount, originating and destination accounts, and
account balances before and after each transaction.

Task: reason through the underlying entities and relationships, make and
justify modelling decisions, and explain how the model supports common
analytical questions — e.g. tracing the flow of funds between accounts and
identifying unusual transaction patterns.

Also evaluated on: ability to explain reasoning clearly, including
alternatives considered and why they weren't chosen.

## 3. Preparation and Deliverables

### 3.1 Dataset Review
- Review the sample transaction records and column reference.
- Summarise key entities (e.g. accounts, transactions) and relationships.
- Identify anything in the data itself — not stated in the column
  descriptions — that affects modelling.

**Deliverable:** short written summary — key entities, relationships,
notable patterns/ambiguities identified.

### 3.2 Graph Data Modeling
- Identify key entities (nodes) and their properties.
- Define relationships capturing interactions, including direction and
  cardinality.
- Decide how to represent transactions — as relationships, as nodes, or a
  mix — and be ready to justify the choice.
- State 2–3 questions the business would ask of this data, and explain how
  the model supports answering them.

**Deliverable:** arrows.app JSON export or shareable URL; written
explanation of modelling decisions including at least one alternative
approach considered and why it wasn't chosen.

### 3.3 Query Approach
- For each business question from 3.2, describe (plain language or Cypher
  sketch) how the model would be queried to answer it.
- No running Neo4j instance required — the goal is to show the model serves
  the questions it was designed for.

**Deliverable:** short written or Cypher-sketch walkthrough per business
question.

### 3.4 Walkthrough Discussion
- Walk through the model live, explain reasoning, respond to follow-up
  questions — including hypothetical changes to data or requirements.

**Deliverable:** none — live conversation only.

### 3.5 Submission Guidelines
Provide a shareable link or file containing: dataset review summary,
arrows.app export/URL, written modelling rationale (with alternatives
considered), query approach write-up per business question.

*(Per candidate correspondence with Neo4j: no advance submission is
required — materials are presented live on the day.)*

## 4. Live Interview Structure (60 Minutes)

| Duration | Element | Focus |
|---|---|---|
| 10 min | Meet the team / candidate Q&A | Ask the panel anything about working at Neo4j |
| 10 min | Data Model Deep Dive | Walkthrough of schema design decisions, alternatives considered |
| 30 min | Scaling / stress testing / iteration / new use cases | Collaborative whiteboarding on real-world edge cases |
| 10 min | Wrap-up & Q&A | Final panel alignment, candidate questions |

## Evaluation Criteria

- **Technical Accuracy** — correctness and soundness of the graph model.
- **Reasoning & Judgment** — quality of justification, treatment of
  tradeoffs and alternatives.
- **Attention to the Data** — whether patterns/ambiguities in the actual
  data were noticed, vs. relying on generic modelling conventions.
- **Communication** — clarity and organisation of written explanation.
- **Adaptability** — reasoning through follow-up questions and hypothetical
  changes live.

## Appendix: Sample Data

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

Sample rows:
```
step=1, type=PAYMENT, amount=9839.64, nameOrig=C1231006815, oldbalanceOrg=170136.00,
newbalanceOrig=160296.36, nameDest=M1979787155, oldbalanceDest=0.00, newbalanceDest=0.00,
isFraud=0, isFlaggedFraud=0, device_id=D48213, ip_address=203.0.113.42

step=1, type=TRANSFER, amount=181.00, nameOrig=C1305486145, oldbalanceOrg=181.00,
newbalanceOrig=0.00, nameDest=C553264065, oldbalanceDest=0.00, newbalanceDest=0.00,
isFraud=1, isFlaggedFraud=0, device_id=D77190, ip_address=198.51.100.17
```