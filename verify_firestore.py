import os
import json
from firebase_manager import FirebaseManager

def test_mock_db():
    print("--- Testing FirebaseManager in Mock Mode ---")
    
    # 1. Initialize manager
    mgr = FirebaseManager()
    
    print(f"Mock mode active: {mgr.is_mock}")
    
    # Check if mock db has the default account
    account = "010-2792-9891-11"
    pin = "850216"
    
    # Read original balance before payment to compare
    original_balance = 0.0
    mock_db_path = os.path.join("json", "firebase_mock_db.json")
    if os.path.exists(mock_db_path):
        try:
            with open(mock_db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                uid = "R6H4Y1y78beOardDbsGC8BaHkxrr1"
                original_balance = data["users"][uid]["accounts"]["main"]["balance"]
        except Exception:
            original_balance = 203050.2
    else:
        original_balance = 203050.2
        
    print(f"Original Balance: {original_balance}")
    
    pay_amount = 5000.0
    print(f"\n1. Processing payment of {int(pay_amount):,} won with account '{account}' and PIN '{pin}'...")
    success, msg, balance = mgr.process_payment(account, pin, pay_amount, "테스트가게")
    print(f"Result: Success={success}, Message='{msg}', Remaining Balance={balance}")
    
    if not success:
        print("FAILED: Payment should have succeeded.")
        return False
        
    # Check that mock db has updated balance
    with open(mock_db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    uid = "R6H4Y1y78beOardDbsGC8BaHkxrr1"
    saved_balance = data["users"][uid]["accounts"]["main"]["balance"]
    print(f"Saved balance in mock database file: {saved_balance}")
    if abs(saved_balance - balance) > 0.01:
        print("FAILED: Balance in DB file does not match returned balance.")
        return False
        
    if abs(saved_balance - (original_balance - pay_amount)) > 0.01:
        print(f"FAILED: Balance decrement is incorrect. Expected: {original_balance - pay_amount}, Got: {saved_balance}")
        return False
        
    # Check transactions
    transactions = data["users"][uid]["transactions"]
    print(f"\nTransactions in mock database: {len(transactions)} items")
    latest_tx = None
    for tx_id, tx_info in transactions.items():
        if tx_info.get("description") == "테스트가게":
            latest_tx = tx_info
            
    if latest_tx:
        print(f"Found Latest Transaction:")
        print(f"  - Amount: {latest_tx['amount']}")
        print(f"  - Balance After: {latest_tx['balance_after']}")
        print(f"  - Recipient Name: {latest_tx['recipientName']}")
        print(f"  - Sender Name: {latest_tx['senderName']}")
        print(f"  - Timestamp: {latest_tx['timestamp']}")
        print(f"  - Type: {latest_tx['type']}")
    else:
        print("FAILED: Could not find logged transaction in DB.")
        return False
        
    # Check notifications
    notifications = data["users"][uid]["notifications"]
    print(f"\nNotifications in mock database: {len(notifications)} items")
    latest_notif = None
    for notif_id, notif_info in notifications.items():
        if "테스트가게" in notif_info.get("message", ""):
            latest_notif = notif_info
            
    if latest_notif:
        print(f"Found Latest Notification:")
        print(f"  - Message: '{latest_notif['message']}'")
        print(f"  - Read: {latest_notif['read']}")
        print(f"  - Timestamp: {latest_notif['timestamp']}")
    else:
        print("FAILED: Could not find logged notification in DB.")
        return False
        
    # Test wrong PIN
    print("\n2. Processing payment with incorrect PIN...")
    success_wrong_pin, msg_wrong_pin, _ = mgr.process_payment(account, "999999", 5000.0, "테스트가게")
    print(f"Result: Success={success_wrong_pin}, Message='{msg_wrong_pin}'")
    if success_wrong_pin:
        print("FAILED: Payment should have failed with wrong PIN.")
        return False
        
    # Test insufficient balance
    print("\n3. Processing payment with excessive amount (insufficient balance)...")
    success_low_bal, msg_low_bal, _ = mgr.process_payment(account, pin, 999999.0, "테스트가게")
    print(f"Result: Success={success_low_bal}, Message='{msg_low_bal}'")
    if success_low_bal:
        print("FAILED: Payment should have failed due to insufficient funds.")
        return False
        
    print("\nMock Mode tests passed successfully!")
    return True

if __name__ == "__main__":
    test_mock_db()
