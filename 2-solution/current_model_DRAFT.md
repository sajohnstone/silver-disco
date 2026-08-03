# Current Data Model (From Dataset Analysis) - DRAFT

**IMPORTANT**: This document describes the *current* data model as it appears in `transactions.csv`, not the proposed graph model. This serves as the baseline understanding of what the data actually contains.

## Introduction

The `transactions.csv` dataset contains 100 synthetic transaction records following the schema specified in the assignment brief. Each row represents a single financial transaction with associated metadata, fraud labels, and session information. This document examines the actual data patterns and field meanings to inform the graph model design.

## Field Analysis & Assumptions

### 1. `step` (integer, 1-743)
**Data pattern**: Values range from 4 to 737
**Assumption**: Represents sequential hours of simulated time. Lower numbers = earlier transactions.

### 2. `type` (string)
**Values observed**: CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER
**Patterns**:
- CASH_IN/CASH_OUT: Always between C-prefix and C900-prefix accounts
- PAYMENT: Always from C-prefix to M-prefix accounts
- TRANSFER: Between C-prefix accounts
- DEBIT: From C-prefix to M-prefix accounts (but merchant balances increase)
**Assumption**: Represents 5 distinct transaction types with specific role constraints.

### 3. `amount` (float)
**Data pattern**: Transaction amounts ranging from 0.0 to 11,373.02
**Note**: Contains 0.0 amounts for some DEBIT and CASH_OUT transactions
**Assumption**: Local currency amount; 0.0 amounts may represent authorization or fee-only transactions.

### 4. `nameOrig` (string)
**Patterns observed**:
- `C00000000xx`: 30 unique customer accounts (xx = 01-30)
- `M00000000xx`: 20 unique merchant accounts (xx = 01-20)  
- `C90000000xx`: 10 unique C900-prefix accounts (xx = 00-09)
**Assumption**: C = regular customer, M = merchant, C900 = special account type (possibly system/bank accounts).

### 5. `oldbalanceOrg` (float)
**Data pattern**: 
- C-prefix accounts: Positive balances (0.0 to ~9,631.0)
- M-prefix accounts: Always 0.0
- C900-prefix accounts: Very large balances (~440k to ~975k)
**Assumption**: Origin balance before transaction. Merchants show 0.0 (their balances not tracked).

### 6. `newbalanceOrig` (float)
**Data pattern**: 
- C-prefix: Updated after transaction
- M-prefix: Always 0.0  
- C900-prefix: Updated after transaction
**Assumption**: Origin balance after transaction. Consistent with `oldbalanceOrg - amount = newbalanceOrig` (allowing for floating point).

### 7. `nameDest` (string)
**Patterns observed**:
- Same prefixes as `nameOrig`
- Transaction type determines valid destination types:
  - CASH_IN: C900 → C
  - CASH_OUT: M → C900 (or C → C900)
  - PAYMENT: C → M
  - TRANSFER: C → C
  - DEBIT: M → C
**Assumption**: Destination account ID following same prefix conventions.

### 8. `oldbalanceDest` (float)
**Data pattern**:
- C-prefix: Positive balances
- M-prefix: 0.0 or small positive (~27-106)
- C900-prefix: Very large balances
**Note**: For PAYMENT transactions to merchants, `oldbalanceDest` = 0.0
**Assumption**: Destination balance before transaction.

### 9. `newbalanceDest` (float)  
**Data pattern**: 
- C-prefix: Updated balances
- M-prefix: 0.0 or updated (DEBIT transactions increase merchant balances)
- C900-prefix: Updated balances
**Assumption**: Destination balance after transaction.

### 10. `isFraud` (boolean)
**Data pattern**: 4 fraud transactions identified:
1. Line 24: C0000000001 → C0000000028, amount 11373.02 (full balance sweep)
2. Line 25: C0000000009 → C0000000001, amount 4795.13 (full balance sweep)  
3. Line 38: C0000000015 → C0000000003, amount 114.68
4. Line 63: C0000000010 → C0000000030, amount 229.31
5. Line 87: C0000000016 → C0000000027, amount 5937.28 (full balance sweep)
**Assumption**: True fraud label for investigation/ML training.

### 11. `isFlaggedFraud` (boolean)
**Data pattern**: Only 1 transaction flagged (line 25)
**Assumption**: Business rule flag (e.g., amount > threshold). Less sensitive than `isFraud`.

### 12. `device_id` (string)
**Data pattern**: 20 unique devices (Dxxxxx)
**Observed patterns**: 
- Some devices used across multiple accounts (potential mule detection)
- D23238, D40512, D37460 used in fraud transactions
**Assumption**: Device identifier for session tracking.

### 13. `ip_address` (string)
**Data pattern**: 20 unique IP addresses
**Observed patterns**:
- 96.82.0.165, 245.134.91.54 appear in multiple transactions
- IPs shared across accounts
**Assumption**: IP address for location/session tracking.

## Key Data Patterns Identified

### 1. Account Prefix Semantics
- **C00000000xx**: Regular customer accounts (~30 accounts)
- **M00000000xx**: Merchant accounts (~20 accounts)  
- **C90000000xx**: Special high-balance accounts (~10 accounts)
- **EXTERNAL**: Not present in dataset but mentioned in brief

### 2. Transaction Type Constraints
- CASH_IN: C900 → C (system to customer)
- CASH_OUT: C/M → C900 (customer/merchant to system)
- PAYMENT: C → M (customer to merchant)
- TRANSFER: C → C (customer to customer)
- DEBIT: C → M (customer to merchant, but merchant balance increases)

### 3. Fraud Patterns
- **Full balance sweeps**: 3 cases where `amount == oldbalanceOrg` and `newbalanceOrig == 0`
- **Device/IP sharing**: Fraud accounts share devices/IPs with other accounts
- **Clustering**: Multiple fraud transactions connected via accounts

### 4. Merchant Behavior
- `oldbalanceDest`/`newbalanceDest` = 0.0 for PAYMENT transactions
- Non-zero balances only for DEBIT transactions
- Never appear as origin in PAYMENT or TRANSFER

### 5. C900 Account Behavior
- Very large balances (440k-975k)
- Act as source for CASH_IN, destination for CASH_OUT
- Possibly represent bank/system accounts

## Data Quality Observations

1. **Consistent balances**: `newbalanceOrig ≈ oldbalanceOrg - amount` (allowing floating point)
2. **Valid type constraints**: No violations of observed transaction patterns
3. **Device/IP reuse**: Realistic pattern of shared sessions
4. **Fraud clustering**: Fraud accounts connected via transactions
5. **Complete data**: No missing values in sampled rows

---

**Assumptions used in this analysis**:
1. C/M/C900 prefixes indicate distinct account types
2. `step` represents sequential time units
3. 0.0 merchant balances indicate balances not tracked in this system
4. C900 accounts represent system/bank accounts
5. Device/IP values are unique identifiers for session tracking