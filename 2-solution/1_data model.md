# Data Model (Entities, Relationships, Transaction Representation)

## Model Overview

Transaction-as-node graph model with separate Customer/Merchant nodes and first-class Device/IP entities for fraud detection.

## Entities (Nodes)

### 1. Customer Node
**Label**: `:Customer`
**Purpose**: Regular customer accounts (C-prefix in dataset)
**Properties**:
- `customerId: String` - Unique identifier (e.g., "C0000000024")
- `currentBalance: Float` - Latest known balance
- `isActive: Boolean` - Account status flag
- `createdAt: Integer` - Earliest transaction step

### 2. Merchant Node  
**Label**: `:Merchant`
**Purpose**: Merchant accounts (M-prefix in dataset)
**Properties**:
- `merchantId: String` - Unique identifier (e.g., "M0000000016")
- `currentBalance: Float` - Latest known balance
- `isActive: Boolean` - Account status flag
- `category: String` - Optional merchant category

### 3. Transaction Node
**Label**: `:Transaction` (with optional fraud labels: `:IsFraud`, `:IsFlaggedFraud`)
**Purpose**: All transaction records as central nodes
**Properties**:
- `transactionId: String` - Composite key (e.g., "STEP_TYPE_AMOUNT_TIMESTAMP")
- `step: Integer` - Temporal unit (1-743 hours)
- `type: String` - CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER
- `amount: Float` - Transaction amount

### 4. Device Node
**Label**: `:Device`
**Purpose**: Device session tracking for mule detection
**Properties**:
- `deviceId: String` - Unique device identifier (e.g., "D91070")
- `riskScore: Float` - Calculated from fraud history
- `firstSeen: Integer` - Earliest transaction step
- `lastSeen: Integer` - Latest transaction step

### 5. IPAddress Node
**Label**: `:IPAddress`
**Purpose**: IP address tracking for location-based fraud detection
**Properties**:
- `ipAddress: String` - IP address (e.g., "156.87.125.83")
- `riskScore: Float` - Calculated from fraud history
- `firstSeen: Integer` - Earliest transaction step
- `lastSeen: Integer` - Latest transaction step
- `geolocation: String` - Optional inferred location

## Relationships

### Core Fund Flow Relationships

#### 1. SENT Relationship
**Pattern**: `(:Customer|Merchant)-[:SENT]->(:Transaction)`
**Direction**: From account to transaction
**Properties**:
- `oldBalance: Float` - Account balance before transaction
- `newBalance: Float` - Account balance after transaction
**Purpose**: Tracks money outflow with exact balance changes

#### 2. RECEIVED_BY Relationship
**Pattern**: `(:Transaction)-[:RECEIVED_BY]->(:Customer|Merchant)`
**Direction**: From transaction to account
**Properties**:
- `oldBalance: Float` - Account balance before transaction
- `newBalance: Float` - Account balance after transaction
**Purpose**: Tracks money inflow with exact balance changes

### Session Relationships

####'an( 3. USED_DEVICE Relationship
**Pattern**: `(:Transaction)-[:USED_DEVICE]->(:Device)`
**Purpose**: Links transaction to originating device
**Properties**: None (device metadata on Device node)

#### 4. FROM_IP Relationship
**Pattern**: `(:Transaction)-[:FROM_IP]->(:IPAddress)`
**Purpose**: Links transaction to originating IP address
**Properties**: None (IP metadata on IPAddress node)

## Transaction Representation

### Chosen Pattern: Transaction-as-Node (Intermediate Node)

**Structure**:
```
(:Customer)-[:SENT {oldBalance, newBalance}]->(:Transaction)
            -[:RECEIVED_BY {oldBalance, newBalance}]->(:Customer|Merchant)
            -[:USED_DEVICE]->(:Device)
            -[:FROM_IP]->(:IPAddress)
```

**Visual Metaphor**: Star schema with Transaction as hub connecting all entities

### Why This Representation

1. **Metadata Preservation**: All transaction attributes (amount, type, fraud labels, device, IP) on single node
2. **Query Efficiency**: Direct access to transaction properties without traversing relationships
3. **Balance Audit Trail**: Exact balance changes stored on relationships for forensic tracing
4. **Session Correlation**: Device/IP as separate nodes enables "show all transactions for this device/IP"
5. **Type Constraints**: Natural enforcement through Customer/Merchant node types

### Alternative Representations Considered and Rejected

#### 1. Transaction-as-Relationship (Rejected)
```
(:Customer)-[:TRANSFERS {amount, type, fraud, device, ip}]->(:Customer)
```
**Why rejected**: Cannot capture all metadata; relationships should have minimal properties

#### 2. Single Account Node with Type Property (Rejected)
```
(:Account {type: "CUSTOMER"|"MERCHANT"})
```
**Why rejected**: Breaks semantic distinction; harder to enforce type-safe relationships

## Model Alignment with Business Questions

### Q1: Multi-hop Fund Flow Tracing
**Supported by**: Transaction nodes as intermediate hops, Customer nodes for account identity

### Q2: Balance Sweep Pattern Detection
**Supported by**: Balance properties on SENT relationship, fraud labels on Transaction nodes

### Q3: Merchant Payment Anomalies  
**Supported by**: Separate Merchant nodes, device/IP relationships for session correlation

## Implementation Notes

### Node Creation Rules
1. Customer nodes: Created from C-prefix `nameOrig`/`nameDest`
2. Merchant nodes: Created from M-prefix `nameOrig`/`nameDest`
3. Transaction nodes: Each CSV row becomes a Transaction node
4. Device/IP nodes: Created from unique `device_id`/`ip_address` values

### Fraud Label Application
- `isFraud = 1` → Apply `:IsFraud` label to Transaction node
- `isFlaggedFraud = 1` → Apply `:IsFlaggedFraud` label to Transaction node
- Nodes can have both labels if applicable

### Balance Property Population
– `oldBalance` on SENT/RECEIVED_BY = `oldbalanceOrg`/`oldbalanceDest`
– `newBalance` on SENT/RECEIVED_BY = `newbalanceOrig`/`newbalanceDest`

## Arrows.app Visualization

See `1_model.json` for visual representation. Key layout:
- Left side: Customer/Merchant nodes
- Center: Transaction nodes (hub)
- Right side: Device/IP nodes
- Color coding by entity type
- Relationships showing money flow and session connections