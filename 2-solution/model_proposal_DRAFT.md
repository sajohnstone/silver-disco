# Graph Model Proposal Draft - For Review

**IMPORTANT**: This is a draft proposal awaiting review. Based on Neo4j's "questions first" modelling principle and the actual dataset patterns.

## 1. Business Questions First (Per Neo4j Modelling Principle)

The model must support answering these core fraud detection questions:

### Q1: Multi-hop Fund Flow Tracing
"Find all accounts reachable within 3 hops from a known fraud account via TRANSFER relationships, especially those sharing devices/IPs."

*Use case*: Identify mule account networks used to launder stolen funds.

### Q2: Balance Sweep Pattern Detection  
"Find all TRANSFER transactions where amount equals origin balance, emptying the account (oldbalanceOrg == amount, newbalanceOrig == 0)."

*Use case*: Detect classic account takeover fraud where attackers sweep entire balances.

### Q3: Merchant Payment Anomalies
"Find merchants receiving unusually large PAYMENT transactions from customers with recent fraud flags."

*Use case*: Detect collusive merchants facilitating fraud through inflated payments.

## 2. Proposed Graph Model

### Nodes (Entities)

#### 1. Account Node
```
(:Account {
  accountId: String,      // e.g., "C0000000024", "M0000000016"
  type: String,           // "CUSTOMER" or "MERCHANT"
  currentBalance: Float,  // Latest known balance
  isActive: Boolean
})
```

**Properties justification**:
- `accountId` as primary identifier with C/M prefix preserved
- `type` as separate property for efficient filtering (CUSTOMER vs MERCHANT)
- `currentBalance` maintained via transaction updates
- `isActive` flag for account status tracking

#### 2. Transaction Node
```
(:Transaction {
  transactionId: String,  // Composite: "STEP_TYPE_AMOUNT_TIMESTAMP"
  step: Integer,          // 1-743 (hour unit)
  type: String,           // CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER
  amount: Float,
  isFraud: Boolean,
  isFlaggedFraud: Boolean,
  deviceId: String,       // e.g., "D91070"
  ipAddress: String       // e.g., "156.87.125.83"
})
```

**Properties justification**:
- `transactionId` as unique composite key
- `step` preserved for temporal analysis
- Fraud labels (`isFraud`, `isFlaggedFraud`) on transaction for direct querying
- Device/IP on transaction for session-based fraud detection

#### 3. Device Node (Optional Enhancement)
```
(:Device {
  deviceId: String,       // e.g., "D91070"
  riskScore: Float        // Calculated from fraud history
})
```

**Trade-off**: Could be property on Transaction, but as separate node enables:
- Finding all accounts using same device (mule detection)
- Device risk scoring across transactions

### Relationships

#### 1. Core Fund Flow Relationships
```
(:Account)-[:SENT {
  oldBalance: Float,
  newBalance: Float
}]->(:Transaction)

(:Transaction)-[:RECEIVED_BY {
  oldBalance: Float,
  newBalance: Float
}]->(:Account)
```

**Direction justification**: FROM origin TO transaction, FROM transaction TO destination
- Matches natural money flow direction
- Enables efficient path queries: `(fraudAcc)-[:SENT*1..3]->(:Transaction)-[:RECEIVED_BY]->(muleAcc)`

#### 2. Optional Enhancement Relationships
```
(:Transaction)-[:USED_DEVICE]->(:Device)
(:Transaction)-[:FROM_IP]->(:IPAddress)
(:Account)-[:SHARES_DEVICE_WITH]->(:Account)  // Derived relationship
```

## 3. Transaction Representation Decision

### Chosen Approach: **Transaction-as-Node (Intermediate Node Pattern)**

**Structure**: `Account --SENT--> Transaction --RECEIVED_BY--> Account`

**Why this over alternatives:**

1. **Versus Transaction-as-Relationship** (`Account -[TRANSFERS {amount: }]-> Account`):
   - *Rejected*: Cannot capture `device_id`, `ip_address`, fraud labels on relationship
   - *Rejected*: Complex for CASH_IN/OUT with EXTERNAL parties
   - *Rejected*: Hard to query "find all transactions from device X"

2. **Versus Hybrid Approach** (Transaction node + relationship properties):
   - *Considered*: Could put amount on relationship, metadata on node
   - *Rejected*: Breaks Neo4j pattern consistency; queries become complex

3. **Why Transaction-as-Node wins**:
   - ✅ **Query clarity**: Direct access to transaction properties (`isFraud`, `device_id`)
   - ✅ **Flexibility**: Handles all 5 transaction types uniformly
   - ✅ **Performance**: Indexes on `Transaction.type`, `Transaction.isFraud`, `Transaction.deviceId`
   - ✅ **Balance tracking**: `oldBalance`/`newBalance` on relationships preserves audit trail
   - ✅ **Path queries**: Natural 2-node pattern for money flow: `(src)-[:SENT]->(tx)-[:RECEIVED_BY]->(dst)`

## 4. Assumptions Made Explicit

### A1: Account Type Inference
**Assumption**: `C` prefix = CUSTOMER, `M` prefix = MERCHANT, `EXTERNAL` = special system account.
*Why*: Matches assignment brief sample data pattern.

### A2: Balance Consistency
**Assumption**: `newbalanceOrig`/`newbalanceDest` from CSV become `Account.currentBalance` via transaction processing.
*Why*: Enables real-time balance queries without recalculating history.

### A3: Device/IP as First-Class Entities
**Assumption**: `device_id` and `ip_address` warrant separate nodes for mule detection.
*Trade-off*: Adds complexity but enables `MATCH (d:Device)<-[:USED_DEVICE]-(:Transaction)-[:SENT|RECEIVED_BY]->(a:Account)` queries.

### A4: Step as Temporal Proxy
**Assumption**: `step` (1-743) represents sequential hours; lower step = earlier transaction.
*Why*: Enables time-window fraud patterns without actual timestamps.

### A5: EXTERNAL as Special Account
**Assumption**: CASH_IN/CASH_OUT with `EXTERNAL` party gets a system Account node.
*Why*: Maintains consistent `Account-Transaction-Account` pattern for all transaction types.

## 5. Alternative Approach Considered and Rejected

### Alternative: **Flat Relationship Model**
```
(:Account)-[:TRANSACTED_WITH {
  step: Integer,
  type: String,
  amount: Float,
  isFraud: Boolean,
  deviceId: String,
  ipAddress: String,
  oldBalanceOrg: Float,
  newBalanceOrg: Float,
  oldBalanceDest: Float,
  newBalanceDest: Float
}]->(:Account)
```

**Why rejected**:

1. **Relationship Property Bloat**: 11+ properties on every relationship
   - Neo4j best practice: Keep relationship properties minimal
   - Query performance degrades with property-heavy relationships

2. **Query Complexity**:
   - To find "all transactions from device D91070": must scan ALL relationships
   - Versus: `MATCH (t:Transaction {deviceId: "D91070"})` with index

3. **Balance Update Problem**:
   - No clear single source of truth for current account balance
   - Requires traversing all relationships to calculate balance

4. **Loses Transaction Identity**:
   - Cannot easily reference a specific transaction in investigations
   - No natural key for transaction-level fraud flagging

**Evidence from dataset**: With 4 full-balance-sweep frauds and device/IP sharing patterns, the Transaction-as-Node model better serves the required business questions.

## 6. How Model Serves Business Questions

### Q1: Multi-hop Fund Flow Tracing
```cypher
// Find mule accounts within 3 hops of fraud account, sharing device
MATCH (fraud:Account {accountId: $fraudAccountId})
MATCH path = (fraud)-[:SENT|RECEIVED_BY*1..3]-(other:Account)
WHERE other <> fraud
WITH other, 
     [n IN nodes(path) WHERE n:Transaction] AS transactions
WHERE ANY(tx IN transactions WHERE tx.deviceId = $suspiciousDevice)
RETURN other.accountId, COUNT(DISTINCT transactions) AS connectionStrength
```

### Q2: Balance Sweep Pattern Detection
```cypher
// Find TRANSFER transactions emptying accounts
MATCH (a:Account)-[sent:SENT]->(t:Transaction {type: "TRANSFER"})
WHERE abs(sent.oldBalance - t.amount) < 0.01 
  AND sent.newBalance = 0
  AND t.isFraud = true
RETURN a.accountId, t.amount, t.step
ORDER BY t.amount DESC
```

### Q3: Merchant Payment Anomalies  
```cypher
// Find merchants receiving large payments from recently flagged customers
MATCH (cust:Account {type: "CUSTOMER"})
WHERE EXISTS {
  MATCH (cust)-[:SENT]->(tx:Transaction)
  WHERE tx.isFlaggedFraud = true AND tx.step > $recentStep
}
MATCH (cust)-[:SENT]->(payment:Transaction {type: "PAYMENT"})
MATCH (payment)-[:RECEIVED_BY]->(merchant:Account {type: "MERCHANT"})
WHERE payment.amount > $threshold
RETURN merchant.accountId, payment.amount, payment.step
```

## 7. Arrows.app Model Representation

**Node Types**:
1. `Account` (yellow) - Customer/Merchant/External
2. `Transaction` (blue) - All transaction types
3. `Device` (green) - Optional enhancement
4. `IPAddress` (gray) - Optional enhancement

**Relationship Types**:
1. `SENT` (from Account to Transaction)
2. `RECEIVED_BY` (from Transaction to Account)
3. `USED_DEVICE` (from Transaction to Device)
4. `FROM_IP` (from Transaction to IPAddress)

**Visual Layout**: Hub-and-spoke with Transaction nodes as hubs connecting Account nodes.

---
**DRAFT FOR REVIEW** - Please review the proposed model, assumptions, and rejected alternative. Key decisions needing review:
1. Transaction-as-Node vs Transaction-as-Relationship
2. Device/IP as separate nodes vs properties
3. Balance tracking approach on relationships
4. EXTERNAL account handling