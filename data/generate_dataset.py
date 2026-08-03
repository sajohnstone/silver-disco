import csv
import random
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter

def exponential_random(scale):
    """Generate exponential random variable without numpy."""
    return -scale * math.log(random.random())

def generate_fraud_dataset(n_samples=100, fraud_rate=0.05):
    """Generate synthetic transaction dataset matching assignment brief schema."""
    
    random.seed(42)
    
    # Define constants per assignment brief
    TRANSACTION_TYPES = ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']
    MAX_STEP = 743  # 1 unit = 1 hour of simulated time
    
    # Generate account pools
    customer_accounts = [f'C{i:010d}' for i in range(1, 31)]  # 30 customer accounts
    merchant_accounts = [f'M{i:010d}' for i in range(1, 21)]  # 20 merchant accounts
    
    # Add special bank accounts for CASH_IN/CASH_OUT (still C-prefixed but with special numbers)
    bank_accounts = [f'C{i:010d}' for i in range(9000000000, 9000000011)]  # 10 bank accounts
    
    # Initialize account balances
    account_balances = {}
    for account in customer_accounts:
        account_balances[account] = random.uniform(1000, 10000)  # Initial balance
    for account in merchant_accounts:
        account_balances[account] = 0.0  # Merchants start with 0 balance
    for account in bank_accounts:
        account_balances[account] = random.uniform(100000, 1000000)  # Large bank balances
    
    # Create device and IP pools for clustering
    device_pool = [f'D{random.randint(10000, 99999)}' for _ in range(20)]
    ip_pool = [f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}' 
               for _ in range(30)]
    
    # Create mule account cluster (4-5 accounts sharing device/IP)
    mule_accounts = random.sample(customer_accounts[5:15], 5)  # 5 mule accounts
    mule_device = random.choice(device_pool)
    mule_ip = random.choice(ip_pool)
    
    # Track transactions
    all_transactions = []
    fraud_target = int(n_samples * fraud_rate)
    
    # Generate base transactions
    for i in range(n_samples - fraud_target - 5):  # Reserve space for pattern frauds
        # Select transaction type with distribution
        weights = [0.15, 0.15, 0.15, 0.25, 0.3]  # Higher weight for PAYMENT and TRANSFER
        tx_type = random.choices(TRANSACTION_TYPES, weights=weights)[0]
        
        # Determine origin and destination based on transaction type
        if tx_type == 'PAYMENT':
            # PAYMENT: Customer -> Merchant
            nameOrig = random.choice(customer_accounts)
            nameDest = random.choice(merchant_accounts)
        elif tx_type == 'TRANSFER':
            # TRANSFER: Customer -> Customer OR Merchant -> Merchant
            if random.random() < 0.1:  # 10% chance of merchant-to-merchant transfer
                nameOrig = random.choice(merchant_accounts)
                nameDest = random.choice([acc for acc in merchant_accounts if acc != nameOrig])
            else:
                nameOrig = random.choice(customer_accounts)
                nameDest = random.choice([acc for acc in customer_accounts if acc != nameOrig])
        elif tx_type == 'CASH_IN':
            # CASH_IN: Bank -> Customer OR Bank -> Merchant (deposit to merchant account)
            if random.random() < 0.2:  # 20% chance of deposit to merchant
                nameOrig = random.choice(bank_accounts)
                nameDest = random.choice(merchant_accounts)
            else:
                nameOrig = random.choice(bank_accounts)
                nameDest = random.choice(customer_accounts)
        elif tx_type == 'CASH_OUT':
            # CASH_OUT: Customer -> Bank OR Merchant -> Bank (withdrawal from merchant)
            if random.random() < 0.15:  # 15% chance of merchant withdrawal
                nameOrig = random.choice(merchant_accounts)
                nameDest = random.choice(bank_accounts)
            else:
                nameOrig = random.choice(customer_accounts)
                nameDest = random.choice(bank_accounts)
        else:  # DEBIT
            # DEBIT: Customer -> Merchant (standard) OR Merchant -> Customer (refund)
            if random.random() < 0.05:  # 5% chance of merchant refund
                nameOrig = random.choice(merchant_accounts)
                nameDest = random.choice(customer_accounts)
            else:
                nameOrig = random.choice(customer_accounts)
                nameDest = random.choice(merchant_accounts)
        
        # Get current balances
        oldbalanceOrg = account_balances.get(nameOrig, 0.0)
        oldbalanceDest = account_balances.get(nameDest, 0.0)
        
        # Generate amount
        base_amount = exponential_random(50)
        if tx_type in ['TRANSFER', 'CASH_OUT', 'PAYMENT', 'DEBIT']:
            # For outgoing transactions, limit to available balance
            amount = min(base_amount, oldbalanceOrg * 0.8)  # Max 80% of balance
        else:
            amount = base_amount
        amount = round(amount, 2)
        
        # Calculate new balances
        newbalanceOrig = max(0.0, oldbalanceOrg - amount)
        
        # For merchants in PAYMENT transactions, keep balance at 0 (per sample data)
        if tx_type == 'PAYMENT' and nameDest.startswith('M'):
            newbalanceDest = 0.0
        else:
            newbalanceDest = oldbalanceDest + amount
        
        # Update account balances
        account_balances[nameOrig] = newbalanceOrig
        account_balances[nameDest] = newbalanceDest
        
        # Device and IP selection
        device_id = random.choice(device_pool)
        ip_address = random.choice(ip_pool)
        
        # Create transaction record
        transaction = {
            'step': random.randint(1, MAX_STEP),
            'type': tx_type,
            'amount': amount,
            'nameOrig': nameOrig,
            'oldbalanceOrg': oldbalanceOrg,
            'newbalanceOrig': newbalanceOrig,
            'nameDest': nameDest,
            'oldbalanceDest': oldbalanceDest,
            'newbalanceDest': newbalanceDest,
            'isFraud': 0,
            'isFlaggedFraud': 0,
            'device_id': device_id,
            'ip_address': ip_address
        }
        
        all_transactions.append(transaction)
    
    # ===== ADD REQUIRED FRAUD PATTERNS =====
    
    # 1. Add full-balance-sweep frauds (TRANSFER frauds that empty account)
    sweep_fraud_count = random.randint(2, 4)  # 2-4 sweep frauds
    for _ in range(sweep_fraud_count):
        # Find a customer account with sufficient balance
        eligible_accounts = [acc for acc in customer_accounts if account_balances[acc] > 500]
        if not eligible_accounts:
            continue
            
        nameOrig = random.choice(eligible_accounts)
        oldbalanceOrg = account_balances[nameOrig]
        amount = oldbalanceOrg  # Sweep entire balance
        
        # Choose destination (not a mule to keep pattern distinct)
        nameDest = random.choice([acc for acc in customer_accounts if acc != nameOrig and acc not in mule_accounts])
        oldbalanceDest = account_balances[nameDest]
        newbalanceDest = oldbalanceDest + amount
        
        # Update balances
        account_balances[nameOrig] = 0.0
        account_balances[nameDest] = newbalanceDest
        
        # Create sweep fraud transaction
        transaction = {
            'step': random.randint(1, MAX_STEP),
            'type': 'TRANSFER',
            'amount': amount,
            'nameOrig': nameOrig,
            'oldbalanceOrg': oldbalanceOrg,
            'newbalanceOrig': 0.0,
            'nameDest': nameDest,
            'oldbalanceDest': oldbalanceDest,
            'newbalanceDest': newbalanceDest,
            'isFraud': 1,
            'isFlaggedFraud': 1 if random.random() < 0.5 else 0,  # 50% detection
            'device_id': random.choice(device_pool),
            'ip_address': random.choice(ip_pool)
        }
        all_transactions.append(transaction)
    
    # 2. Add mule account cluster transactions
    # First, connect mule accounts to each other
    for i in range(len(mule_accounts) - 1):
        acc1 = mule_accounts[i]
        acc2 = mule_accounts[i + 1]
        balance1 = account_balances[acc1]
        
        if balance1 > 100:
            amount = random.uniform(50, min(200, balance1 * 0.3))
            amount = round(amount, 2)
            
            transaction = {
                'step': random.randint(1, MAX_STEP),
                'type': 'TRANSFER',
                'amount': amount,
                'nameOrig': acc1,
                'oldbalanceOrg': balance1,
                'newbalanceOrig': balance1 - amount,
                'nameDest': acc2,
                'oldbalanceDest': account_balances[acc2],
                'newbalanceDest': account_balances[acc2] + amount,
                'isFraud': 0,  # Non-fraud connection
                'isFlaggedFraud': 0,
                'device_id': mule_device,
                'ip_address': mule_ip
            }
            # Update balances
            account_balances[acc1] = balance1 - amount
            account_balances[acc2] = account_balances[acc2] + amount
            all_transactions.append(transaction)
    
    # Add a fraud transaction involving a mule account
    mule_fraud_count = random.randint(1, 2)
    for _ in range(mule_fraud_count):
        # Fraud from mule account to non-mule
        nameOrig = random.choice(mule_accounts)
        oldbalanceOrg = account_balances[nameOrig]
        
        if oldbalanceOrg > 100:
            amount = random.uniform(100, min(500, oldbalanceOrg * 0.5))
            amount = round(amount, 2)
            
            nameDest = random.choice([acc for acc in customer_accounts if acc not in mule_accounts])
            oldbalanceDest = account_balances[nameDest]
            
            transaction = {
                'step': random.randint(1, MAX_STEP),
                'type': 'TRANSFER',
                'amount': amount,
                'nameOrig': nameOrig,
                'oldbalanceOrg': oldbalanceOrg,
                'newbalanceOrig': oldbalanceOrg - amount,
                'nameDest': nameDest,
                'oldbalanceDest': oldbalanceDest,
                'newbalanceDest': oldbalanceDest + amount,
                'isFraud': 1,
                'isFlaggedFraud': 0,  # Not flagged by rule
                'device_id': mule_device,
                'ip_address': mule_ip
            }
            # Update balances
            account_balances[nameOrig] = oldbalanceOrg - amount
            account_balances[nameDest] = oldbalanceDest + amount
            all_transactions.append(transaction)
    
    # 3. Add other random frauds to reach target
    current_fraud_count = sum(1 for t in all_transactions if t['isFraud'] == 1)
    additional_frauds_needed = max(0, fraud_target - current_fraud_count)
    
    for _ in range(additional_frauds_needed):
        # Add fraud in various transaction types
        tx_type = random.choice(['PAYMENT', 'DEBIT', 'CASH_OUT'])
        
        if tx_type in ['PAYMENT', 'DEBIT']:
            if random.random() < 0.3:  # 30% chance merchant is origin for DEBIT (refund)
                nameOrig = random.choice(merchant_accounts)
                nameDest = random.choice(customer_accounts)
            else:
                nameOrig = random.choice(customer_accounts)
                nameDest = random.choice(merchant_accounts)
        else:  # CASH_OUT
            if random.random() < 0.2:  # 20% chance merchant is origin
                nameOrig = random.choice(merchant_accounts)
                nameDest = random.choice(bank_accounts)
            else:
                nameOrig = random.choice(customer_accounts)
                nameDest = random.choice(bank_accounts)
        
        oldbalanceOrg = account_balances[nameOrig]
        oldbalanceDest = account_balances[nameDest]
        
        # Fraud amount is unusually large
        amount = random.uniform(500, 2000) if random.random() < 0.7 else random.uniform(50, 200)
        amount = round(amount, 2)
        
        newbalanceOrig = max(0.0, oldbalanceOrg - amount)
        
        if tx_type == 'PAYMENT' and nameDest.startswith('M'):
            newbalanceDest = 0.0
        else:
            newbalanceDest = oldbalanceDest + amount
        
        # Update balances
        account_balances[nameOrig] = newbalanceOrig
        account_balances[nameDest] = newbalanceDest
        
        # Determine isFlaggedFraud
        isFlaggedFraud = 1 if amount > 1000 and random.random() < 0.3 else 0
        
        transaction = {
            'step': random.randint(1, MAX_STEP),
            'type': tx_type,
            'amount': amount,
            'nameOrig': nameOrig,
            'oldbalanceOrg': oldbalanceOrg,
            'newbalanceOrig': newbalanceOrig,
            'nameDest': nameDest,
            'oldbalanceDest': oldbalanceDest,
            'newbalanceDest': newbalanceDest,
            'isFraud': 1,
            'isFlaggedFraud': isFlaggedFraud,
            'device_id': random.choice(device_pool),
            'ip_address': random.choice(ip_pool)
        }
        all_transactions.append(transaction)
    
    # Shuffle transactions to mix fraud/non-fraud
    random.shuffle(all_transactions)
    
    return all_transactions

def calculate_summary_stats(transactions):
    """Calculate and return summary statistics for the dataset."""
    
    stats = {}
    
    # Basic counts
    stats['total_transactions'] = len(transactions)
    fraud_count = sum(1 for t in transactions if t['isFraud'] == 1)
    stats['fraud_count'] = fraud_count
    stats['fraud_rate'] = fraud_count / len(transactions)
    
    # Transaction type distribution
    type_counts = Counter(t['type'] for t in transactions)
    stats['type_distribution'] = dict(type_counts)
    
    # Fraud by type
    fraud_by_type = Counter(t['type'] for t in transactions if t['isFraud'] == 1)
    stats['fraud_by_type'] = dict(fraud_by_type)
    
    # Check for required patterns
    sweep_frauds = [
        t for t in transactions 
        if t['type'] == 'TRANSFER' and 
        t['isFraud'] == 1 and 
        abs(float(t['oldbalanceOrg']) - float(t['amount'])) < 0.01 and 
        float(t['newbalanceOrig']) == 0
    ]
    stats['sweep_fraud_count'] = len(sweep_frauds)
    
    # Account prefix distribution
    orig_prefixes = Counter(t['nameOrig'][0] for t in transactions)
    dest_prefixes = Counter(t['nameDest'][0] for t in transactions)
    stats['orig_prefix_dist'] = dict(orig_prefixes)
    stats['dest_prefix_dist'] = dict(dest_prefixes)
    
    # Merchant zero balances in PAYMENT
    merchant_payments = [
        t for t in transactions 
        if t['type'] == 'PAYMENT' and t['nameDest'].startswith('M')
    ]
    zero_balance_merchants = [
        t for t in merchant_payments 
        if float(t['oldbalanceDest']) == 0 and float(t['newbalanceDest']) == 0
    ]
    stats['merchant_payments'] = len(merchant_payments)
    stats['zero_balance_merchant_payments'] = len(zero_balance_merchants)
    
    # Device/IP sharing analysis
    device_counts = Counter(t['device_id'] for t in transactions)
    ip_counts = Counter(t['ip_address'] for t in transactions)
    
    shared_devices = {device: count for device, count in device_counts.items() if count > 1}
    shared_ips = {ip: count for ip, count in ip_counts.items() if count > 1}
    
    stats['shared_devices'] = len(shared_devices)
    stats['shared_ips'] = len(shared_ips)
    stats['max_device_shared'] = max(shared_devices.values()) if shared_devices else 0
    stats['max_ip_shared'] = max(shared_ips.values()) if shared_ips else 0
    
    # Find mule-like patterns (accounts sharing device/IP)
    device_to_accounts = defaultdict(set)
    ip_to_accounts = defaultdict(set)
    
    for t in transactions:
        device_to_accounts[t['device_id']].add(t['nameOrig'])
        ip_to_accounts[t['ip_address']].add(t['nameOrig'])
        device_to_accounts[t['device_id']].add(t['nameDest'])
        ip_to_accounts[t['ip_address']].add(t['nameDest'])
    
    # Find device/IP shared by multiple accounts (potential mule pattern)
    multi_account_devices = {device: accounts for device, accounts in device_to_accounts.items() if len(accounts) > 2}
    multi_account_ips = {ip: accounts for ip, accounts in ip_to_accounts.items() if len(accounts) > 2}
    
    stats['multi_account_devices'] = len(multi_account_devices)
    stats['multi_account_ips'] = len(multi_account_ips)
    
    # Count M-prefix as origin (should have some now)
    m_as_origin = sum(1 for t in transactions if t['nameOrig'].startswith('M'))
    stats['m_as_origin_count'] = m_as_origin
    
    return stats

def save_to_csv(transactions, filename='transactions.csv'):
    """Save transactions to CSV file."""
    
    if not transactions:
        return
    
    fieldnames = ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig',
                  'nameDest', 'oldbalanceDest', 'newbalanceDest', 'isFraud', 'isFlaggedFraud',
                  'device_id', 'ip_address']
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)

def main():
    """Generate dataset and save to CSV, then print summary statistics."""
    
    print("Generating transaction dataset matching assignment brief...")
    
    # Generate ~100 transactions as specified in AGENTS.md
    transactions = generate_fraud_dataset(n_samples=100, fraud_rate=0.05)
    
    print(f"Generated {len(transactions)} transactions")
    print(f"Columns: {list(transactions[0].keys())}")
    
    # Save to CSV
    csv_path = 'transactions.csv'
    save_to_csv(transactions, csv_path)
    print(f"\nDataset saved to {csv_path}")
    
    # Calculate and display summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    stats = calculate_summary_stats(transactions)
    
    print(f"\n1. Basic Statistics:")
    print(f"   Total transactions: {stats['total_transactions']}")
    print(f"   Fraud count: {stats['fraud_count']}")
    print(f"   Fraud rate: {stats['fraud_rate']:.2%}")
    
    print(f"\n2. Transaction Type Distribution:")
    for tx_type, count in stats['type_distribution'].items():
        fraud_count = stats['fraud_by_type'].get(tx_type, 0)
        print(f"   {tx_type}: {count} transactions ({count/stats['total_transactions']:.1%}), {fraud_count} fraud")
    
    print(f"\n3. Required Patterns Check:")
    print(f"   Full-balance-sweep frauds: {stats['sweep_fraud_count']} (TRANSFER, oldbalanceOrg == amount, newbalanceOrig == 0)")
    print(f"   Account prefix 'C' (customers/banks): {stats['orig_prefix_dist'].get('C', 0)} origins, {stats['dest_prefix_dist'].get('C', 0)} destinations")
    print(f"   Account prefix 'M' (merchants): {stats['orig_prefix_dist'].get('M', 0)} origins, {stats['dest_prefix_dist'].get('M', 0)} destinations")
    print(f"   M-prefix as origin count: {stats['m_as_origin_count']}")
    print(f"   Merchant PAYMENT transactions: {stats['merchant_payments']}")
    print(f"   Zero-balance merchant payments: {stats['zero_balance_merchant_payments']} ({stats['zero_balance_merchant_payments']/max(1, stats['merchant_payments']):.1%})")
    
    print(f"\n4. Device/IP Sharing (for mule detection):")
    print(f"   Devices used multiple times: {stats['shared_devices']}")
    print(f"   Max transactions per device: {stats['max_device_shared']}")
    print(f"   IPs used multiple times: {stats['shared_ips']}")
    print(f"   Max transactions per IP: {stats['max_ip_shared']}")
    print(f"   Devices used by >2 accounts (mule indicator): {stats['multi_account_devices']}")
    print(f"   IPs used by >2 accounts (mule indicator): {stats['multi_account_ips']}")
    
    # Show sample fraud transactions
    fraud_txs = [t for t in transactions if t['isFraud'] == 1]
    print(f"\n5. Fraud Transactions Sample (first 3):")
    for i, tx in enumerate(fraud_txs[:3]):
        sweep_indicator = " [SWEEP]" if (tx['type'] == 'TRANSFER' and abs(float(tx['oldbalanceOrg']) - float(tx['amount'])) < 0.01 and float(tx['newbalanceOrig']) == 0) else ""
        print(f"   {i+1}. Step {tx['step']}, {tx['type']}{sweep_indicator}: {tx['nameOrig']} -> {tx['nameDest']}, "
              f"Amount: ${float(tx['amount']):.2f}, Flagged: {tx['isFlaggedFraud']}, "
              f"Device: {tx['device_id']}, IP: {tx['ip_address']}")
    
    # Show some normal transactions for comparison
    normal_txs = [t for t in transactions if t['isFraud'] == 0][:2]
    print(f"\n6. Normal Transactions Sample (first 2):")
    for i, tx in enumerate(normal_txs):
        print(f"   {i+1}. Step {tx['step']}, {tx['type']}: {tx['nameOrig']} -> {tx['nameDest']}, "
              f"Amount: ${float(tx['amount']):.2f}")
    
    # Show CASH_IN/CASH_OUT examples
    cash_txs = [t for t in transactions if t['type'] in ['CASH_IN', 'CASH_OUT']][:2]
    print(f"\n7. CASH_IN/CASH_OUT Examples (first 2):")
    for i, tx in enumerate(cash_txs):
        print(f"   {i+1}. Step {tx['step']}, {tx['type']}: {tx['nameOrig']} -> {tx['nameDest']}, "
              f"Amount: ${float(tx['amount']):.2f}")
    
    return transactions, stats

if __name__ == "__main__":
    transactions, stats = main()

def calculate_summary_stats(transactions):
    """Calculate and return summary statistics for the dataset."""
    
    stats = {}
    
    # Basic counts
    stats['total_transactions'] = len(transactions)
    fraud_count = sum(1 for t in transactions if t['isFraud'] == 1)
    stats['fraud_count'] = fraud_count
    stats['fraud_rate'] = fraud_count / len(transactions)
    
    # Transaction type distribution
    type_counts = Counter(t['type'] for t in transactions)
    stats['type_distribution'] = dict(type_counts)
    
    # Fraud by type
    fraud_by_type = Counter(t['type'] for t in transactions if t['isFraud'] == 1)
    stats['fraud_by_type'] = dict(fraud_by_type)
    
    # Check for required patterns
    sweep_frauds = [
        t for t in transactions 
        if t['type'] == 'TRANSFER' and 
        t['isFraud'] == 1 and 
        abs(t['oldbalanceOrg'] - t['amount']) < 0.01 and 
        t['newbalanceOrig'] == 0
    ]
    stats['sweep_fraud_count'] = len(sweep_frauds)
    
    # Account prefix distribution
    orig_prefixes = Counter(t['nameOrig'][0] for t in transactions if t['nameOrig'] != 'EXTERNAL')
    dest_prefixes = Counter(t['nameDest'][0] for t in transactions if t['nameDest'] != 'EXTERNAL')
    stats['orig_prefix_dist'] = dict(orig_prefixes)
    stats['dest_prefix_dist'] = dict(dest_prefixes)
    
    # Merchant zero balances in PAYMENT
    merchant_payments = [
        t for t in transactions 
        if t['type'] == 'PAYMENT' and t['nameDest'].startswith('M')
    ]
    zero_balance_merchants = [
        t for t in merchant_payments 
        if t['oldbalanceDest'] == 0 and t['newbalanceDest'] == 0
    ]
    stats['merchant_payments'] = len(merchant_payments)
    stats['zero_balance_merchant_payments'] = len(zero_balance_merchants)
    
    # Device/IP sharing analysis
    device_counts = Counter(t['device_id'] for t in transactions)
    ip_counts = Counter(t['ip_address'] for t in transactions)
    
    shared_devices = {device: count for device, count in device_counts.items() if count > 1}
    shared_ips = {ip: count for ip, count in ip_counts.items() if count > 1}
    
    stats['shared_devices'] = len(shared_devices)
    stats['shared_ips'] = len(shared_ips)
    stats['max_device_shared'] = max(shared_devices.values()) if shared_devices else 0
    stats['max_ip_shared'] = max(shared_ips.values()) if shared_ips else 0
    
    # Find mule-like patterns (accounts sharing device/IP)
    device_to_accounts = defaultdict(set)
    ip_to_accounts = defaultdict(set)
    
    for t in transactions:
        if t['nameOrig'] != 'EXTERNAL':
            device_to_accounts[t['device_id']].add(t['nameOrig'])
            ip_to_accounts[t['ip_address']].add(t['nameOrig'])
        if t['nameDest'] != 'EXTERNAL':
            device_to_accounts[t['device_id']].add(t['nameDest'])
            ip_to_accounts[t['ip_address']].add(t['nameDest'])
    
    # Find device/IP shared by multiple accounts (potential mule pattern)
    multi_account_devices = {device: accounts for device, accounts in device_to_accounts.items() if len(accounts) > 2}
    multi_account_ips = {ip: accounts for ip, accounts in ip_to_accounts.items() if len(accounts) > 2}
    
    stats['multi_account_devices'] = len(multi_account_devices)
    stats['multi_account_ips'] = len(multi_account_ips)
    
    return stats

def save_to_csv(transactions, filename='transactions.csv'):
    """Save transactions to CSV file."""
    
    if not transactions:
        return
    
    fieldnames = ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig',
                  'nameDest', 'oldbalanceDest', 'newbalanceDest', 'isFraud', 'isFlaggedFraud',
                  'device_id', 'ip_address']
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)

def main():
    """Generate dataset and save to CSV, then print summary statistics."""
    
    print("Generating transaction dataset matching assignment brief...")
    
    # Generate ~100 transactions as specified in AGENTS.md
    transactions = generate_fraud_dataset(n_samples=100, fraud_rate=0.05)
    
    print(f"Generated {len(transactions)} transactions")
    print(f"Columns: {list(transactions[0].keys())}")
    
    # Save to CSV
    csv_path = 'transactions.csv'
    save_to_csv(transactions, csv_path)
    print(f"\nDataset saved to {csv_path}")
    
    # Calculate and display summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    stats = calculate_summary_stats(transactions)
    
    print(f"\n1. Basic Statistics:")
    print(f"   Total transactions: {stats['total_transactions']}")
    print(f"   Fraud count: {stats['fraud_count']}")
    print(f"   Fraud rate: {stats['fraud_rate']:.2%}")
    
    print(f"\n2. Transaction Type Distribution:")
    for tx_type, count in stats['type_distribution'].items():
        fraud_count = stats['fraud_by_type'].get(tx_type, 0)
        print(f"   {tx_type}: {count} transactions ({count/stats['total_transactions']:.1%}), {fraud_count} fraud")
    
    print(f"\n3. Required Patterns Check:")
    print(f"   Full-balance-sweep frauds: {stats['sweep_fraud_count']} (TRANSFER, oldbalanceOrg == amount, newbalanceOrig == 0)")
    print(f"   Account prefix 'C' (customers): {stats['orig_prefix_dist'].get('C', 0)} origins, {stats['dest_prefix_dist'].get('C', 0)} destinations")
    print(f"   Account prefix 'M' (merchants): {stats['orig_prefix_dist'].get('M', 0)} origins, {stats['dest_prefix_dist'].get('M', 0)} destinations")
    print(f"   Merchant PAYMENT transactions: {stats['merchant_payments']}")
    print(f"   Zero-balance merchant payments: {stats['zero_balance_merchant_payments']} ({stats['zero_balance_merchant_payments']/max(1, stats['merchant_payments']):.1%})")
    
    print(f"\n4. Device/IP Sharing (for mule detection):")
    print(f"   Devices used multiple times: {stats['shared_devices']}")
    print(f"   Max transactions per device: {stats['max_device_shared']}")
    print(f"   IPs used multiple times: {stats['shared_ips']}")
    print(f"   Max transactions per IP: {stats['max_ip_shared']}")
    print(f"   Devices used by >2 accounts (mule indicator): {stats['multi_account_devices']}")
    print(f"   IPs used by >2 accounts (mule indicator): {stats['multi_account_ips']}")
    
    # Show sample fraud transactions
    fraud_txs = [t for t in transactions if t['isFraud'] == 1]
    print(f"\n5. Fraud Transactions Sample (first 3):")
    for i, tx in enumerate(fraud_txs[:3]):
        sweep_indicator = " [SWEEP]" if (tx['type'] == 'TRANSFER' and abs(tx['oldbalanceOrg'] - tx['amount']) < 0.01 and tx['newbalanceOrig'] == 0) else ""
        print(f"   {i+1}. Step {tx['step']}, {tx['type']}{sweep_indicator}: {tx['nameOrig']} -> {tx['nameDest']}, "
              f"Amount: ${tx['amount']:.2f}, Flagged: {tx['isFlaggedFraud']}, "
              f"Device: {tx['device_id']}, IP: {tx['ip_address']}")
    
    # Show some normal transactions for comparison
    normal_txs = [t for t in transactions if t['isFraud'] == 0][:2]
    print(f"\n6. Normal Transactions Sample (first 2):")
    for i, tx in enumerate(normal_txs):
        print(f"   {i+1}. Step {tx['step']}, {tx['type']}: {tx['nameOrig']} -> {tx['nameDest']}, "
              f"Amount: ${tx['amount']:.2f}")
    
    return transactions, stats

if __name__ == "__main__":
    transactions, stats = main()