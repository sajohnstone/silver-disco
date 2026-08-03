# Business Questions & Query Sketches

## Overview

Three business questions for fraud detection using the proposed graph model (Transaction-as-Node with separate Customer/Merchant nodes and Device/IP entities).

## Question 1: Multi-hop Fund Flow with Device Correlation

### Description
"Find all customer accounts reachable within 3 transaction hops from a known fraud account, especially those sharing the same devices or IP addresses."

**Use case**: Identify mule account networks used to launder stolen funds through transaction chains and shared session data.

### Cypher Query Sketch
```cypher
// Q1: Multi-hop fund flow with device correlation
MATCH (fraud:Customer {customerId: $fraudAccountId})
MATCH path = (fraud)-[:SENT|RECEIVED_BY*1..3]-(other:Customer)
WHERE other <> fraud
WITH other, 
     [n IN nodes(path) WHERE n:Transaction] AS transactions
MATCH (tx:Transaction)-[:USED_DEVICE]->(d:Device)
WHERE tx IN transactions 
WITH other, d, COUNT(DISTINCT tx) AS sharedTxCount
WHERE sharedTxCount >= $minimumSharedTransactions
RETURN other.customerId, d.deviceId, sharedTxCount
ORDER BY sharedTxCount DESC
```

### Traversal Sketch
```
Start: Fraud Customer Node
  ↓
Traverse: (fraud)-[:SENT|RECEIVED_BY*1..3]-(other:Customer)
  ↓
Filter: Exclude self, collect Transaction nodes in path
  ↓
Correlate: Transaction-[:USED_DEVICE]->Device
  ↓
Aggregate: Count shared transactions per device
  ↓
Result: {customerId, deviceId, sharedTransactionCount}
```

**Path pattern**: Fraud Customer → Transaction → Customer → Transaction → Customer (max 3 hops)
**Key insight**: Mule accounts often share devices with fraudsters even if transaction amounts vary

## Question 2: Balance Sweep Pattern Detection

### Description  
"Find all TRANSFER transactions where the amount equals the origin account's entire balance, emptying the account (oldBalance == amount, newBalance == 0)."

**Use case**: Detect classic account takeover fraud where attackers transfer out the entire balance.

### Cypher Query Sketch
```cypher
// Q2: Balance sweep pattern detection
MATCH (c:Customer)-[sent:SENT]->(t:Transaction:IsFraud {type: "TRANSFER"})
WHERE abs(sent.oldBalance - t.amount) < $tolerance 
  AND sent.newBalance = 0
WITH c, t, sent
OPTIONAL MATCH (t)-[:USED_DEVICE]->(d:Device)
OPTIONAL MATCH (t)-[:FROM_IP]->(ip:IPAddress)
RETURN c.customerId, 
       t.amount, 
       t.step,
       d.deviceId,
       ip.ipAddress,
       sent.oldBalance AS originalBalance,
       sent.newBalance AS remainingBalance
ORDER BY t.amount DESC
```

### Traversal Sketch
```
Start: Customer Nodes
  ↓
Traverse: Customer-[:SENT]->Transaction:IsFraud {type: "TRANSFER"}
  ↓
Filter: WHERE sent.oldBalance ≈ amount AND sent.newBalance = 0
  ↓
Optional: Transaction-[:USED_DEVICE]->Device
  ↓
Optional: Transaction-[:FROM_IP]->IPAddress
  ↓
Result: {customerId, amount, step, deviceId, ipAddress, originalBalance, remainingBalance}
```

**Pattern**: Full account emptying with exact balance match
**Tolerance**: $tolerance for floating-point precision (e.g., 0.01)
**Enhancement**: Include device/IP for session correlation

## Question 3: Merchant Payment Anomalies with Session Risk

### Description
"Find merchants receiving unusually large PAYMENT transactions from customers who have recent fraud flags, especially when using the same devices as previous fraudulent transactions."

**Use case**: Detect collusive merchants facilitating fraud through inflated payments from compromised accounts.

### Cypher Query Sketch
```cypher
// Q3: Merchant payment anomalies with session risk
MATCH (cust:Customer)-[:SENT]->(flagged:Transaction:IsFlaggedFraud)
WHERE flagged.step > $recentStepThreshold
WITH cust, flagged
MATCH (cust)-[:SENT]->(payment:Transaction {type: "PAYMENT"})
WHERE payment.amount > $largePaymentThreshold
MATCH (payment)-[:RECEIVED_BY]->(merchant:Merchant)
MATCH (flagged)-[:USED_DEVICE]->(d:Device)
WHERE (payment)-[:USED_DEVICE]->(d)  // Same device
OPTIONAL MATCH (flagged)-[:FROM_IP]->(flaggedIp:IPAddress)
OPTIONAL MATCH (payment)-[:FROM_IP]->(paymentIp:IPAddress)
RETURN merchant.merchantId,
       payment.amount AS paymentAmount,
       flagged.amount AS flaggedAmount,
       d.deviceId,
       flaggedIp.ipAddress AS flaggedIp,
       paymentIp.ipAddress AS paymentIp,
       payment.step AS paymentStep,
       flagged.step AS flaggedStep
ORDER BY payment.amount DESC
```

### Traversal Sketch
```
Start: Customer Nodes
  ↓
Traverse: Customer-[:SENT]->Transaction:IsFlaggedFraud (recent)
  ↓
Continue: Same Customer-[:SENT]->Transaction {type: "PAYMENT"} (large amount)
  ↓
Destination: Transaction-[:RECEIVED_BY]->Merchant
  ↓
Session Correlation: Both transactions use same Device
  ↓
Optional: IP address correlation
  ↓
Result: {merchantId, paymentAmount, flaggedAmount, deviceId, IPs, steps}
```

**Temporal constraint**: `flagged.step > $recentStepThreshold` (e.g., last 48 hours)
**Amount threshold**: `payment.amount > $largePaymentThreshold` (business-defined)
**Session correlation**: Same device strengthens collusion evidence

## Implementation Notes

### Parameter Values
- **Q1**: `$minimumSharedTransactions = 2` (at least 2 transactions on shared device)
- **Q2**: `$tolerance = 0.01` (floating-point precision allowance)
- **Q3**: 
  - `$recentStepThreshold = currentStep - 48` (last 48 "hours")
  - `$largePaymentThreshold = 1000.0` (business-defined large payment)

### Index Recommendations
```cypher
CREATE INDEX transaction_type_idx FOR (t:Transaction) ON (t.type);
CREATE INDEX transaction_step_idx FOR (t:Transaction) ON (t.step);
CREATE INDEX customer_id_idx FOR (c:Customer) ON (c.customerId);
CREATE INDEX merchant_id_idx FOR (m:Merchant) ON (m.merchantId);
CREATE INDEX device_id_idx FOR (d:Device) ON (d.deviceId);
```

### Performance Considerations
1. **Q1 path limit**: `*1..3` prevents exponential path explosion
2. **Q2 tolerance**: Floating-point comparison with epsilon
3. **Q3 thresholds**: Parameterized for business rule flexibility
4. **Label usage**: `:IsFraud`/`:IsFlaggedFraud` labels enable efficient filtering

### Model Alignment Check
Each query leverages specific model features:
- **Q1**: Transaction nodes as intermediate hops, Device nodes for correlation
- **Q2**: Balance properties on SENT relationship, fraud labels on Transaction
- **Q3**: Separate Merchant nodes, device relationships for session correlation