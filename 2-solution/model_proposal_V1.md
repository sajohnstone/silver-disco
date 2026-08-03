# Graph Model Proposal V1 - Updated per Review

**IMPORTANT**: This is an updated draft incorporating review feedback. Key changes: Device and IP as nodes, fraud labels as node labels, and refined account structure.

## 1. Business Questions (Unchanged)

The model must support answering these core fraud detection questions:

### Q1: Multi-hop Fund Flow Tracing
"Find all accounts reachable within 3 hops from a known fraud account via TRANSFER relationships, especially those sharing devices/IPs."

### Q2: Balance Sweep Pattern Detection  
"Find all TRANSFER transactions where amount equals origin balance, emptying the account (oldbalanceOrg == amount, newbalanceOrig == 0)."

### Q3: Merchant Payment Anomalies
"Find merchants receiving unusually large PAYMENT transactions from customers with recent fraud flags."

## 2. Updated Graph Model

### Nodes (Entities)

#### 1. Customer Node (For C-prefix accounts)
```
(:Customer {
  customerId: String,      // e.g., "C0000000024"
  currentBalance: Float,
  isActive: Boolean,
  createdAt: Integer       // Earliest transaction step
})
```

#### 2. Merchant Node (For M-prefix accounts)
```
(:Merchant {
  merchantId: String,      // e.g., "M0000000016"
  currentBalance: Float,
  isActive: Boolean,
  category: String         // Optional: inferred from transactions
})
```

#### 3. Transaction Node
```
(:Transaction {
  transactionId: String,   // Composite: "STEP_TYPE_AMOUNT_TIMESTAMP"
  step: Integer,           // 1-743 (hour unit)
  type: String,            // CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER
  amount: Float
})
```

#### 4. Fraud Labels on Transaction Node
Instead of properties, use node labels for fraud classification:
- `(:Transaction:IsFraud)` - Confirmed fraudulent transactions
- `(:Transaction:IsFlaggedFraud)` - Flagged by business rules
- Transactions can have both labels if applicable

#### 5. Device Node (Required per review)
```
(:Device {
  deviceId: String,        // e.g., "D91070"
  riskScore: Float,        // Calculated from fraud history
  firstSeen: Integer,      // Earliest transaction step
  lastSeen: Integer        // Latest transaction step
})
```

#### 6. IPAddress Node (Required per review)
```
(:IPAddress {
  ipAddress: String,       // e.g., "156.87.125.83"
  riskScore: Float,        // Calculated from fraud history  
  firstSeen: Integer,
  lastSeen: Integer,
  geolocation: String      // Optional: inferred from IP
})
```

### Relationships

#### 1. Core Fund Flow Relationships
```
(:Customer|Merchant)-[:SENT {
  oldBalance: Float,
  newBalance: Float
}]->(:Transaction)

(:Transaction)-[:RECEIVED_BY {
  oldBalance: Float,
  newBalance: Float
}]->(:Customer|Merchant)
```

**Note**: Customer/Merchant distinction eliminates need for `type` property on Account nodes.

#### 2. Device and IP Relationships (Required per review)
```
(:Transaction)-[:USED_DEVICE]->(:Device)
(:Transaction)-[:FROM_IP]->(:IPAddress)
```

**Derived relationships for query optimization** (optional):
```
(:Customer)-[:SHARED_DEVICE_WITH]->(:Customer)
(:Merchant)-[:SHARED_IP_WITH]->(:Customer)
```

## 3. Transaction Representation

### Chosen Approach: **Transaction-as-Node with Separate Customer/Merchant Nodes**

**Structure**: 
- `Customer --SENT--> Transaction --RECEIVED_BY--> Customer|Merchant`
- `Merchant --SENT--> Transaction --RECEIVED_BY--> Customer|Merchant`

**Why this approach after review:**

1. **Customer/Merchant Separation**: 
   - Clear distinction between account types (C vs M prefixes)
   - Enables type-safe queries: `MATCH (c:Customer)-[:SENT]->(:Transaction)`
   - Better semantic alignment with business concepts

2. **Device/IP as First-Class Nodes** (per review):
   - Supports direct queries: "Show all transactions for this IP or DeviceID"
   - Enables device/IP risk scoring
   - Facilitates network detection through shared device/IP patterns

3. **Fraud as Node Labels** (per review):
   - More efficient filtering: `MATCH (t:Transaction:IsFraud)`
   - Clearer data model semantics
   - Supports multiple classification systems if needed

4. **Rejects Previous Alternative**: Flat relationship model remains rejected for reasons in original proposal.

## 4. Assumptions Made Explicit

### A1: Customer/Merchant Separation
**Assumption**: C-prefix accounts become `Customer` nodes, M-prefix become `Merchant` nodes.
*Why*: Clear business distinction; enables type-specific queries and validation.

### A2: Device/IP as Required Nodes
**Assumption**: `device_id` and `ip_address` create `Device` and `IPAddress` nodes respectively.
*Why per review*: Essential for queries like "Show me all transactions for this IP or DeviceID".

### A3: Fraud as Node Labels  
**Assumption**: `isFraud` and `isFlaggedFraud` become node labels instead of properties.
*Why per review*: Better Neo4j pattern for categorical flags; enables label-based indexing.

### A4: External Party Handling
**Assumption**: CASH_IN/CASH_OUT with `EXTERNAL` creates a special `Customer` node with `customerId: "EXTERNAL"`.
*Why*: Maintains consistent transaction pattern; `EXTERNAL` acts as system customer.

### A5: Balance Tracking on Relationships
**Assumption**: `oldBalance`/`newBalance` stored on `SENT` and `RECEIVED_BY` relationships.
*Why*: Preserves exact balance changes per transaction; enables audit trails.

## 5. Alternative Considered and Rejected

### Alternative: **Single Account Node with Type Property**
```
(:Account {
  accountId: String,
  type: "CUSTOMER"|"MERCHANT",  // Property instead of separate labels
  currentBalance: Float
})
```

**Why rejected after review**:

1. **Query Complexity**: Need to filter by `type` property constantly
2. **Semantic Mismatch**: Customers and Merchants have different behaviors and attributes
3. **Type Safety**: Cannot enforce Customer-only or Merchant-only relationships
4. **Future Extensibility**: Hard to add Merchant-specific properties (category, location, etc.)

**Evidence**: The dataset shows clear behavioral differences (merchants have zero destination balances, customers perform transfers), warranting separate node types.

## 6. How Updated Model Serves Business Questions

### Q1: Multi-hop Fund Flow Tracing (Enhanced)
```cypher
// Find mule accounts sharing devices/IPs within 3 hops
MATCH (fraud:Customer {customerId: $fraudId})
MATCH path = (fraud)-[:SENT|RECEIVED_BY*1..3]-(other:Customer)
WHERE other <> fraud
WITH other, 
     [n IN nodes(path) WHERE n:Transaction] AS transactions
MATCH (tx:Transaction)-[:USED_DEVICE]->(d:Device)
WHERE tx IN transactions AND d.deviceId = $suspiciousDevice
RETURN other.customerId, COUNT(DISTINCT tx) AS sharedTransactionCount
```

### Q2: Balance Sweep Pattern Detection
```cypher
// Find TRANSFER transactions emptying customer accounts (with fraud label)
MATCH (c:Customer)-[sent:SENT]->(t:Transaction:IsFraud {type: "TRANSFER"})
WHERE abs(sent.oldBalance - t.amount) < 0.01 
  AND sent.newBalance = 0
RETURN c.customerId, t.amount, t.step
ORDER BY t.amount DESC
```

### Q3: Merchant Payment Anomalies (Enhanced with Device/IP)
```cypher
// Find merchants receiving large payments from flagged customers on shared devices
MATCH (cust:Customer)-[:SENT]->(flagged:Transaction:IsFlaggedFraud)
WHERE flagged.step > $recentStep
MATCH (cust)-[:SENT]->(payment:Transaction {type: "PAYMENT"})
MATCH (payment)-[:RECEIVED_BY]->(merchant:Merchant)
MATCH (flagged)-[:USED_DEVICE]->(d:Device)
WHERE payment.amount > $threshold 
  AND (payment)-[:USED_DEVICE]->(d)  // Same device as flagged transaction
RETURN merchant.merchantId, payment.amount, d.deviceId
```

## 7. Arrows.app Model Representation

**Node Types**:
1. `Customer` (blue) - C-prefix accounts
2. `Merchant` (green) - M-prefix accounts  
3. `Transaction` (yellow) - All transaction types
4. `Device` (orange) - Device nodes (required)
5. `IPAddress` (purple) - IP nodes (required)

**Relationship Types**:
1. `SENT` (from Customer/Merchant to Transaction)
2. `RECEIVED_BY` (from Transaction to Customer/Merchant)
3. `USED_DEVICE` (from Transaction to Device) - required
4. `FROM_IP` (from Transaction to IPAddress) - required

**Visual Layout**: Star schema with Transaction as center, connecting Customers, Merchants, Devices, and IPs.

---

**UPDATED DRAFT** - Key changes from original proposal:
1. ✓ Separate Customer and Merchant nodes instead of single Account node
2. ✓ Device and IP as required nodes (not optional)
3. ✓ Fraud as node labels instead of properties
4. ✗ Rejected flat relationship model alternative removed
5. ✓ Updated Cypher queries reflecting new node types

**Remaining decisions for review**:
1. Handling of EXTERNAL party for CASH_IN/OUT
2. Whether to include derived relationships (SHARED_DEVICE_WITH)
3. Property names and types alignment with dataset