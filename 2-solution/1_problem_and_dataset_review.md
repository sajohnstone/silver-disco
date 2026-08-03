# Problem & Dataset Review

## Introduction

This analysis examines a synthetic payment transaction dataset to identify key entities, relationships, and patterns for fraud detection graph modelling. The dataset contains 100 transaction records representing 5 transaction types across 3 distinct account categories.

## Key Entities Identified

### 1. Customer Accounts (`C00000000xx`)
- **30 unique accounts** (C0000000001 to C0000000030)
- **Role**: Primary transaction originators/destinations
- **Behavior**: Participate in all transaction types
- **Balance pattern**: Moderate balances (0.0 to ~9,631.0)
- **Fraud involvement**: All 5 fraud transactions involve C-prefix accounts

### 2. Merchant Accounts (`M00000000xx`)  
- **20 unique accounts** (M0000000001 to M0000000020)
- **Role**: Payment recipients in PAYMENT/DEBIT transactions
- **Behavior**: 
  - Never originate PAYMENT or TRANSFER transactions
  - Only appear as destination in PAYMENT/DEBIT
  - Balances typically 0.0 (except DEBIT transactions)
- **Pattern**: `oldbalanceDest`/`newbalanceDest` = 0.0 for PAYMENT transactions

### 3. Special Accounts (`C90000000xx`)
- **10 unique accounts** (C9000000000 to C9000000009)
- **Role**: System/bank accounts for CASH_IN/CASH_OUT flows
- **Behavior**:
  - Very large balances (440k to 975k)
  - Source for CASH_IN transactions
  - Destination for CASH_OUT transactions
- **Assumption**: Represent bank/system liquidity pools

### 4. Transactions
- **5 distinct types**: CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER
- **Key properties**: amount, step (temporal), fraud labels, device/IP data
- **Pattern constraints**: Each type has specific valid origin/destination pairs

### 5. Session Entities
- **20 unique devices** (`Dxxxxx`)
- **20 unique IP addresses**
- **Pattern**: Shared across multiple accounts, enabling mule detection

## Key Relationships & Patterns

### Transaction Type Constraints
```
CASH_IN:    C900  → C      (system → customer)
CASH_OUT:   C/M   → C900   (customer/merchant → system)  
PAYMENT:    C     → M      (customer → merchant)
TRANSFER:   C     → C      (customer → customer)
DEBIT:      C     → M      (customer → merchant, merchant balance increases)
```

### Balance Tracking Patterns
1. **Customer balances**: Updated for all transaction types
2. **Merchant balances**: Typically 0.0, except DEBIT transactions increase them
3. **C900 balances**: Very large, act as system liquidity pools
4. **Balance consistency**: `newbalance ≈ oldbalance ± amount` (allowing floating point)

### Fraud Patterns Identified

#### 1. Full Balance Sweeps (3 instances)
- `amount == oldbalanceOrg` AND `newbalanceOrig == 0`
- Examples: 
  - C0000000001 → C0000000028: 11,373.02 (step 276)
  - C0000000009 → C0000000001: 4,795.13 (step 94) 
  - C0000000016 → C0000000027: 5,937.28 (step 504)

#### 2. Partial Fraud Transactions (2 instances)
- Smaller amounts that don't empty accounts
- Examples:
  - C0000000015 → C0000000003: 114.68 (step 323)
  - C0000000010 → C0000000030: 229.31 (step 414)

#### 3. Device/IP Sharing Patterns
- Fraud accounts share devices/IPs with other accounts
- Example devices in fraud: D23238, D40512, D37460
- Example IPs in fraud: 96.82.0.165, 245.134.91.54

### Temporal Patterns
- **Step range**: 4 to 737 (simulated hours)
- **Fraud distribution**: Steps 94, 276, 323, 414, 504
- **No clear time-clustering**: Fraud spread across timeline

## Ambiguities & Assumptions

### 1. Account Type Inference
**Assumption**: C-prefix = Customer, M-prefix = Merchant, C900-prefix = System account
**Ambiguity**: Brief mentions "EXTERNAL" party but not present in dataset

### 2. Merchant Balance Tracking
**Ambiguity**: Why `oldbalanceDest`/`newbalanceDest` = 0.0 for PAYMENT but not DEBIT?
**Assumption**: PAYMENT transactions don't track merchant-side balances; DEBIT does

### 3. Zero-Amount Transactions
**Ambiguity**: Several DEBIT and CASH_OUT transactions have `amount: 0.0`
**Assumption**: Represent authorization or fee-only transactions

### 4. Device/IP Semantics
**Ambiguity**: Are device_ids persistent per device or per session?
**Assumption**: Persistent device identifiers enabling cross-account correlation

### 5. C900 Account Purpose
**Ambiguity**: Exact role of C900 accounts not specified
**Assumption**: Bank/system liquidity pools for cash movement operations

### 6. isFlaggedFraud Business Rule
**Ambiguity**: Only 1 transaction flagged (line 25)
**Assumption**: Conservative business rule (e.g., very large amount threshold)

## Data Quality Assessment

### Strengths
1. **Consistent patterns**: Transaction types follow strict constraints
2. **Balance integrity**: `newbalance ≈ oldbalance ± amount` holds
3. **Realistic fraud clustering**: Fraud accounts connected via transactions
4. **Session data**: Device/IP sharing enables network analysis
5. **Complete data**: No missing values in sampled records

### Limitations (for modelling purposes)
1. **Small scale**: 100 transactions insufficient for statistical validation
2. **Synthetic nature**: Patterns may be overly clean vs real-world data
3. **Limited fraud cases**: Only 5 fraud instances for pattern learning
4. **No timestamps**: `step` is proxy but lacks real datetime context
5. **No merchant metadata**: Category, location, size missing

## Implications for Graph Modelling

### Critical Design Decisions
1. **Separate Customer/Merchant nodes**: Clear behavioral differences warrant distinct types
2. **Device/IP as first-class entities**: Essential for "show all transactions for this device/IP" queries
3. **Transaction-as-node pattern**: Required to capture all metadata (fraud labels, device, IP, amounts)
4. **Balance on relationships**: Preserves audit trail of exact changes per transaction

### Fraud Detection Opportunities
1. **Multi-hop tracing**: Follow funds through TRANSFER chains
2. **Device/IP correlation**: Find accounts sharing sessions with fraudsters
3. **Balance sweep detection**: Identify account-emptying transfers
4. **Merchant anomaly detection**: Spot unusual payment patterns

### Query Support Requirements
The graph model must efficiently support:
1. Pathfinding through transaction networks
2. Device/IP-based account correlation  
3. Temporal pattern detection (recent fraud flags)
4. Balance-based anomaly detection
5. Type-constrained relationship traversal

---

**Next Section**: [Solution](../2-solution/model_notes.md) - Graph data model design addressing these patterns and requirements.