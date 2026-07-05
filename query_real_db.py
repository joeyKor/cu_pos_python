import os
from firebase_manager import FirebaseManager

def query_real_db():
    print("--- Querying Real Firestore Database ---")
    mgr = FirebaseManager()
    if mgr.is_mock:
        print("Manager is in MOCK mode. Cannot query real database.")
        return
        
    db = mgr.db
    
    # 1. Search accountNumber
    account_number = "010-2792-9891-11"
    print(f"Searching for account number: {account_number}")
    
    accounts_ref = db.collection_group('accounts')
    query = accounts_ref.where('accountNumber', '==', account_number)
    docs = list(query.stream())
    
    if not docs:
        print("Account not found in real Firestore database.")
        return
        
    main_doc = docs[0]
    main_data = main_doc.to_dict()
    main_path = main_doc.reference.path
    print(f"Found account document at path: {main_path}")
    print(f"Document Data: {main_data}")
    
    # Get user document (parent of parent)
    user_ref = main_doc.reference.parent.parent
    user_snap = user_ref.get()
    user_data = user_snap.to_dict()
    print(f"Parent User Path: {user_ref.path}")
    print(f"User Name: {user_data.get('name')}")
    print(f"User PIN: {user_data.get('pin')}")
    
    # List transactions
    print("\n--- Transactions in Firestore ---")
    tx_docs = list(user_ref.collection('transactions').stream())
    print(f"Total Transactions: {len(tx_docs)}")
    for doc in tx_docs:
        data = doc.to_dict()
        print(f"ID: {doc.id} | Amount: {data.get('amount')} | Desc: {data.get('description')} | Timestamp: {data.get('timestamp')}")
        
    # List notifications
    print("\n--- Notifications in Firestore ---")
    notif_docs = list(user_ref.collection('notifications').stream())
    print(f"Total Notifications: {len(notif_docs)}")
    for doc in notif_docs:
        data = doc.to_dict()
        print(f"ID: {doc.id} | Msg: {data.get('message')} | Read: {data.get('read')} | Timestamp: {data.get('timestamp')}")

if __name__ == "__main__":
    query_real_db()
