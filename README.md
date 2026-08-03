# Neo4j Fraud Detection Technical Interview Prep

Technical interview preparation for a Senior Solutions Engineer role at Neo4j, focusing on Fraud (Payments Transaction Graph Modelling) track.

## Project Overview

This repository contains materials for a 60-minute live panel presentation and whiteboard discussion. The assignment involves designing a graph data model for payment transaction fraud detection using synthetic transaction data.

## Tech Stack

- **Development Environment**: opencode (interactive CLI tool for software engineering)
- **AI Model**: deepseek/deepseek-v3.2 via OpenRouter
- **Data**: Synthetic transaction dataset (100 records)
- **Documentation**: Markdown files following Neo4j's three-part deck structure
- **Visualization**: arrows.app for graph model design

## Getting Started

### 1. Review the Assignment Brief
Read `docs/assignment_brief.md` for the complete assignment requirements and evaluation criteria.

### 2. Understand the Data Structure
Examine `data/transactions.csv` containing 100 synthetic transaction records with:
- 5 transaction types (CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER)
- Account IDs with C/M/C900 prefixes
- Fraud labels and device/IP session data
- Balance tracking before/after transactions

### 3. Explore the Three-Part Structure
The project follows Neo4j's required presentation format:

1. **Problem & Dataset Review** (`1-problem-dataset-review/`)
   - Key entities, relationships, and data patterns
   - Dataset characteristics and limitations

2. **Solution** (`2-solution/`)
   - Graph data model design
   - Entity and relationship definitions
   - Assumptions and trade-offs
   - Arrows.app visualization

3. **Queries** (`3-queries/`)
   - 2-3 business questions
   - Cypher query sketches for fraud detection

### 4. Review the Draft Process
All analytical files follow a two-step workflow:
- **DRAFT files** (`*_DRAFT.md`): Initial proposals awaiting review
- **Final files**: Created only after explicit review and decisions

### 5. Understand Constraints
- All data is synthetic (no real transaction data)
- Must be personally explainable and defensible live
- Simple, explainable modelling choices favored over clever ones
- No live Neo4j instance required (graph-native thinking only)

## File Structure

```
neo4j-fraud-assignment/
├── docs/                          # Assignment materials
│   ├── assignment_brief.md        # Official brief
│   ├── ai_usage_policy.md         # Neo4j AI policy
│   └── neo4j_modelling_references.md  # Neo4j principles
├── data/                          # Synthetic dataset
│   ├── generate_dataset.py        # Data generator
│   └── transactions.csv           # Generated data (100 rows)
├── 1-problem-dataset-review/      # Section 1: Problem
├── 2-solution/                    # Section 2: Solution
└── 3-queries/                     # Section 3: Queries
```

## AI Usage Policy Compliance

This project follows Neo4j's AI usage policy:
- All drafts are clearly labelled for human review
- Final outputs are written in human's own words
- No silent invention of facts about Neo4j or datasets
- Assumptions are explicitly documented
- All decisions are personally verifiable and defensible

## Quick Start for Presentation

1. Use `README.md` as your slide deck outline
2. Present sections 1, 2, 3 in order
3. Reference concrete examples from `transactions.csv`
4. Use arrows.app visualization for model walkthrough
5. Demo Cypher queries with sample data patterns

## License & Attribution

This project is for Neo4j technical interview preparation. All materials are created following Neo4j's assignment guidelines and AI usage policy. Synthetic data generated for educational purposes only.