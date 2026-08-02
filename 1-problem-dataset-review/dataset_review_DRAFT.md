# Dataset Review Draft - For Review

**IMPORTANT**: This draft highlights critical issues with the current dataset. The actual data schema differs significantly from the assignment requirements.

We only need 100 rows of data

## Schema Analysis

### Expected Schema (Per Assignment Brief)
The assignment requires data with these columns:
- `step`: integer (1 unit = 1 hour of simulated time)
- `type`: string (CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER)
- `amount`: float (transaction amount)
- `nameOrig`: string (originating account ID with C/M prefixes)
- `oldbalanceOrg`: float (origin balance before transaction)
- `newbalanceOrig`: float (origin balance after transaction)
- `nameDest`: string (destination account ID)
- `oldbalanceDest`: float (destination balance before transaction)
- `newbalanceDest`: float (destination balance after transaction)
- `isFraud`: boolean (fraud label)
- `isFlaggedFraud`: boolean (flagged by existing business rule)
- `device_id`: string (device identifier)
- `ip_address`: string (IP address)

### Actual Dataset Schema
The current `data/transactions.csv` contains:
- `transaction_id`: Unique transaction ID
- `timestamp`: Date/time of transaction
- `amount`: Transaction amount
- `merchant_category`: Retail, online, grocery, etc.
- `card_type`: Visa, mastercard, amex, discover
- `card_last_4`: Last 4 digits of card
- `card_prefix`: Card BIN prefix
- `country`: Transaction country
- `device_id`: Device identifier
- `ip_address`: IP address
- `customer_id`: Customer identifier
- `customer_age`: Customer age
- `customer_income_tier`: Low, medium, high
- `transaction_hour`: Hour of transaction (0-23)
- `previous_chargebacks`: Count of previous chargebacks
- `days_since_last_transaction`: Days since last transaction
- `is_weekend`: Weekend indicator
- `is_international`: International transaction indicator
- `cluster_id`: Cluster assignment (0-4)
- `is_fraud`: Fraud label

## Critical Discrepancies

1. **Missing Balance Tracking**: The assignment requires balance columns (`oldbalanceOrg`, `newbalanceOrg`, `oldbalanceDest`, `newbalanceDest`) for tracking account balances. These are absent.

2. **Different Entity Structure**: The assignment expects account-to-account transactions with C/M prefixes. Current dataset has merchant/customer transactions without account balance tracking.

3. **Missing Transaction Types**: Required types (CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER) replaced by merchant categories.

4. **Additional Features**: Current dataset includes features not in the brief (customer demographics, chargeback history, time features).

## Patterns in Current Data

### Key Entities Identifiable
1. **Transactions** (10,000 total)
   - Unique transaction IDs
   - Timestamps spanning ~30 days
   - Amounts following exponential distribution (mean ~$50)

2. **Customers**
   - Unique customer IDs (CUST prefix)
   - Age and income tier attributes
   - No explicit account balances

3. **Merchants/Merchant Categories**
   - 7 merchant categories (retail, online, grocery, travel, dining, utilities, entertainment)
   - No explicit merchant accounts

4. **Devices**
   - 2,755 devices used for multiple transactions
   - Most shared device: DEV4652 (7 transactions)

### Fraud Patterns
- **Overall fraud rate**: 5% (500 transactions)
- **Cluster-based fraud**: Clusters 1 and 3 have highest fraud rates (7.32% and 7.43%)
- **No IP sharing**: Each IP appears only once (unrealistic for fraud detection)
- **Device sharing limited**: Some device reuse but not clustered as fraud mule pattern

### Data Quality Issues
1. **Unrealistic IP distribution**: Each transaction has unique IP address
2. **Missing balance continuity**: Cannot trace fund flows between accounts
3. **No account prefix convention**: No C/M prefixes to distinguish customer/merchant accounts
4. **No transaction type hierarchy**: Missing required CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER types

## Implications for Modelling

1. **Cannot implement balance sweep detection**: Without balance columns, cannot detect `oldbalanceOrg == amount` patterns.

2. **Limited graph connectivity**: Current schema lacks clear account-to-account relationships needed for multi-hop tracing.

3. **Different fraud detection approach**: Current data supports feature-based ML fraud detection but not graph-native fund flow analysis.

4. **Missing assignment patterns**: No zero-destination-balance merchant payments, no full-balance sweeps, no mule account clusters reachable within 2 hops.

## Recommendations

1. **Regenerate dataset** to match assignment schema exactly:
   - Include all required columns per brief
   - Implement C/M account prefix convention
   - Add balance tracking columns
   - Use required transaction types
   - Create realistic fraud patterns (balance sweeps, mule clusters)

2. **If keeping current schema**, note these limitations in analysis:
   - Model will focus on customer-merchant transactions
   - Cannot demonstrate graph-native fund flow analysis
   - Must adapt business questions to available data

## Assumptions Used in This File

1. Assignment brief schema requirements are authoritative.
2. Current dataset was generated from different requirements.
3. Analysis focuses on what's actually in the data, not what should be.
4. For live presentation, either dataset must match brief or rationale must explain adaptation.

---
**DRAFT FOR REVIEW** - Please review the schema discrepancy and decide whether to regenerate dataset or adapt analysis to current schema.