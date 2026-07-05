import os
import sys
import json
import random
import datetime

# Mock database filename
os.makedirs("json", exist_ok=True)
MOCK_DB_FILE = os.path.join("json", "firebase_mock_db.json")

# Initial seed data for Mock Mode matching screenshots
DEFAULT_MOCK_DATA = {
    "users": {
        "R6H4Y1y78beOardDbsGC8BaHkxrr1": {
            "name": "아빠",
            "pin": "850216",
            "birthDate": "1993-03-11",
            "birthday": "erg",
            "email": "daddy@naver.com",
            "school": "보호자",
            "accounts": {
                "main": {
                    "accountNumber": "010-2792-9891-11",
                    "balance": 203050.2
                }
            },
            "transactions": {},
            "notifications": {}
        }
    }
}

class FirebaseManager:
    def __init__(self):
        self.is_mock = True
        self.db = None
        self.firestore_module = None
        self.mock_data = {}
        
        # Determine credentials path
        credentials_path = os.path.join(os.path.abspath("."), "json", "firebase_credentials.json")
        
        if os.path.exists(credentials_path):
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore as admin_firestore
                from google.cloud import firestore as google_firestore
                
                # Check if already initialized
                if not firebase_admin._apps:
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred)
                
                self.db = admin_firestore.client()
                self.firestore_module = google_firestore
                self.is_mock = False
                print("[Firebase] Successfully initialized Firestore client.")
            except Exception as e:
                print(f"[Firebase] Error initializing firebase-admin, falling back to Mock mode: {e}")
                self.init_mock_db()
        else:
            print(f"[Firebase] Credentials not found at {credentials_path}. Using Mock mode.")
            self.init_mock_db()

    def init_mock_db(self):
        self.is_mock = True
        if not os.path.exists(MOCK_DB_FILE):
            self.mock_data = DEFAULT_MOCK_DATA.copy()
            self.save_mock_db()
        else:
            try:
                with open(MOCK_DB_FILE, "r", encoding="utf-8") as f:
                    self.mock_data = json.load(f)
            except Exception:
                self.mock_data = DEFAULT_MOCK_DATA.copy()
                self.save_mock_db()
        print(f"[Firebase Mock] Mock database initialized using '{MOCK_DB_FILE}'.")

    def save_mock_db(self):
        try:
            with open(MOCK_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.mock_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[Firebase Mock] Error saving mock DB: {e}")

    def process_payment(self, account_number, pin_input, amount, store_name="DU순천점", bypass_pin=False):
        """
        Process the payment:
        1. Find account and parent user.
        2. Verify PIN.
        3. Withdraw funds and create transaction history & notifications.
        Returns: (success_bool, message_str, remaining_balance)
        """
        # Normalize account number candidates to handle different formatting
        candidates = [account_number]
        stripped = "".join(c for c in account_number if c.isdigit())
        
        # Candidate 1: standard formatting if 13 digits (010-2792-9891-11)
        if len(stripped) == 13:
            candidates.append(f"{stripped[:3]}-{stripped[3:7]}-{stripped[7:11]}-{stripped[11:]}")
        # Candidate 2: if 11 digits (mobile phone number), append "-11" suffix
        elif len(stripped) == 11:
            candidates.append(f"{stripped[:3]}-{stripped[3:7]}-{stripped[7:]}-11")
            
        # Candidate 3: if 13 characters with hyphens but missing suffix (e.g. 010-2792-9891)
        if len(account_number) == 13 and account_number.count('-') == 2:
            candidates.append(account_number + "-11")
            
        # Deduplicate candidates while preserving order
        unique_candidates = []
        for c in candidates:
            if c not in unique_candidates:
                unique_candidates.append(c)

        if self.is_mock:
            return False, "결제 서버와 연결되어 있지 않습니다. (credentials 파일 확인 필요)", 0.0
        else:
            return self._process_real_payment(unique_candidates, pin_input, amount, store_name, bypass_pin)

    def _process_mock_payment(self, candidates, pin_input, amount, store_name, bypass_pin=False):
        # 1. Find user & account
        found_uid = None
        found_user = None
        for uid, user_info in self.mock_data.get("users", {}).items():
            acc_info = user_info.get("accounts", {}).get("main", {})
            if acc_info.get("accountNumber") in candidates:
                found_uid = uid
                found_user = user_info
                break
                
        if not found_user:
            return False, "등록된 계좌를 찾을 수 없습니다.", 0.0
            
        # 2. Verify PIN
        if not bypass_pin and found_user.get("pin") != pin_input:
            return False, "비밀번호(PIN)가 일치하지 않습니다.", 0.0
            
        # 3. Check Balance
        main_account = found_user["accounts"]["main"]
        current_balance = float(main_account.get("balance", 0))
        if current_balance < amount:
            return False, f"잔액이 부족합니다.\n현재 잔액: {int(current_balance):,}원\n결제 금액: {int(amount):,}원", current_balance
            
        # 4. Withdraw (Transaction Simulation)
        new_balance = current_balance - amount
        main_account["balance"] = new_balance
        
        # 5. Add Transaction Log
        tx_id = f"mock_tx_{random.randint(100000, 999999)}"
        timestamp_str = datetime.datetime.now().strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초").replace("AM", "오전").replace("PM", "오후") + " UTC+9"
        
        if "transactions" not in found_user:
            found_user["transactions"] = {}
            
        found_user["transactions"][tx_id] = {
            "amount": amount,
            "balance_after": new_balance,
            "description": store_name,
            "is_deposit": False,
            "memo_to_me": "",
            "memo_to_recipient": "",
            "recipientName": store_name,
            "senderName": found_user.get("name", "고객"),
            "timestamp": timestamp_str,
            "type": "PAYMENT"
        }
        
        # 6. Add Notification
        notif_id = f"mock_notif_{random.randint(100000, 999999)}"
        if "notifications" not in found_user:
            found_user["notifications"] = {}
            
        found_user["notifications"][notif_id] = {
            "message": f"{store_name}에서 {int(amount):,}원이 결제되었습니다.",
            "read": False,
            "timestamp": timestamp_str
        }
        
        # Save Mock Database changes
        self.save_mock_db()
        return True, "결제가 정상적으로 완료되었습니다.", new_balance

    def _process_real_payment(self, candidates, pin_input, amount, store_name, bypass_pin=False):
        try:
            # 1. Search accounts subcollection group using "in" operator
            accounts_ref = self.db.collection_group('accounts')
            query = accounts_ref.where('accountNumber', 'in', candidates).limit(1)
            docs = list(query.stream())
            
            if not docs:
                return False, "등록된 계좌를 찾을 수 없습니다.", 0.0
                
            account_doc_ref = docs[0].reference
            user_doc_ref = account_doc_ref.parent.parent # users/{uid}
            
            user_snap = user_doc_ref.get()
            user_data = user_snap.to_dict()
            
            if not user_data:
                return False, "사용자 정보를 조회할 수 없습니다.", 0.0
                
            # 1.5 Update paymentState to 'processing'
            try:
                account_doc_ref.update({
                    'paymentState': {
                        'status': 'processing',
                        'amount': amount,
                        'storeName': store_name
                    }
                })
            except Exception as e_state:
                print(f"[Firebase] Error setting processing paymentState: {e_state}")
                
            # 2. Verify PIN
            if not bypass_pin and user_data.get('pin') != pin_input:
                # Update paymentState to 'failed' before returning
                try:
                    account_doc_ref.update({
                        'paymentState': {
                            'status': 'failed',
                            'amount': amount,
                            'storeName': store_name,
                            'message': "비밀번호(PIN)가 일치하지 않습니다."
                        }
                    })
                except Exception:
                    pass
                return False, "비밀번호(PIN)가 일치하지 않습니다.", 0.0
                
            # 3. Use Firestore Transaction for Atomic updates
            transaction = self.db.transaction()
            
            @self.firestore_module.transactional
            def update_in_transaction(tx, acc_ref, usr_ref, usr_name):
                acc_snap = acc_ref.get(transaction=tx)
                acc_data = acc_snap.to_dict()
                if not acc_data:
                    raise Exception("계좌 데이터를 읽을 수 없습니다.")
                    
                cur_bal = float(acc_data.get('balance', 0.0))
                if cur_bal < amount:
                    raise Exception(f"잔액이 부족합니다.\n현재 잔액: {int(cur_bal):,}원\n결제 금액: {int(amount):,}원")
                    
                new_bal = cur_bal - amount
                
                # Update Account Balance
                tx.update(acc_ref, {'balance': new_bal})
                
                # Add Transaction Document
                tx_ref = usr_ref.collection('transactions').document()
                tx.set(tx_ref, {
                    'amount': amount,
                    'balance_after': new_bal,
                    'description': store_name,
                    'is_deposit': False,
                    'memo_to_me': '',
                    'memo_to_recipient': '',
                    'recipientName': store_name,
                    'senderName': usr_name,
                    'timestamp': self.firestore_module.SERVER_TIMESTAMP,
                    'type': 'PAYMENT'
                })
                
                # Add Notification Document
                notif_ref = usr_ref.collection('notifications').document()
                tx.set(notif_ref, {
                    'message': f"{store_name}에서 {int(amount):,}원이 결제되었습니다.",
                    'read': False,
                    'timestamp': self.firestore_module.SERVER_TIMESTAMP
                })
                
                return new_bal

            user_name = user_data.get('name', '고객')
            new_balance = update_in_transaction(transaction, account_doc_ref, user_doc_ref, user_name)
            
            # Update paymentState to 'success'
            try:
                account_doc_ref.update({
                    'paymentState': {
                        'status': 'success',
                        'amount': amount,
                        'storeName': store_name,
                        'balanceAfter': new_balance
                    }
                })
            except Exception as e_state:
                print(f"[Firebase] Error setting success paymentState: {e_state}")
                
            return True, "결제가 정상적으로 완료되었습니다.", new_balance
            
        except Exception as e:
            error_msg = str(e)
            
            # Update paymentState to 'failed'
            try:
                if 'account_doc_ref' in locals():
                    account_doc_ref.update({
                        'paymentState': {
                            'status': 'failed',
                            'amount': amount,
                            'storeName': store_name,
                            'message': error_msg
                        }
                    })
            except Exception as e_state:
                print(f"[Firebase] Error setting failed paymentState: {e_state}")
                
            # Handle index missing error specifically
            if "FAILED_PRECONDITION" in error_msg or "index" in error_msg.lower():
                return False, f"데이터베이스 색인(Index) 설정이 필요합니다. 아래 에러 로그를 확인하고 색인을 생성해 주세요.\n\n{error_msg}", 0.0
            return False, f"결제 진행 중 오류가 발생했습니다:\n{error_msg}", 0.0

    def process_refund(self, account_number, amount, store_name="DU순천점"):
        """
        Process the refund:
        1. Find account and parent user.
        2. Deposit funds (new_balance = current_balance + amount).
        3. Write transaction log matching the requested format.
        """
        candidates = [account_number]
        stripped = "".join(c for c in account_number if c.isdigit())
        if len(stripped) == 13:
            candidates.append(f"{stripped[:3]}-{stripped[3:7]}-{stripped[7:11]}-{stripped[11:]}")
        elif len(stripped) == 11:
            candidates.append(f"{stripped[:3]}-{stripped[3:7]}-{stripped[7:]}-11")
        if len(account_number) == 13 and account_number.count('-') == 2:
            candidates.append(account_number + "-11")
            
        unique_candidates = []
        for c in candidates:
            if c not in unique_candidates:
                unique_candidates.append(c)
                
        if self.is_mock:
            return False, "결제 서버와 연결되어 있지 않습니다. (credentials 파일 확인 필요)", 0.0
        else:
            return self._process_real_refund(unique_candidates, amount, store_name)

    def _process_mock_refund(self, candidates, amount, store_name):
        # 1. Find user & account
        found_uid = None
        found_user = None
        for uid, user_info in self.mock_data.get("users", {}).items():
            acc_info = user_info.get("accounts", {}).get("main", {})
            if acc_info.get("accountNumber") in candidates:
                found_uid = uid
                found_user = user_info
                break
                
        if not found_user:
            return False, "등록된 계좌를 찾을 수 없습니다.", 0.0
            
        # 2. Deposit
        main_account = found_user["accounts"]["main"]
        current_balance = float(main_account.get("balance", 0))
        new_balance = current_balance + amount
        main_account["balance"] = new_balance
        
        # 3. Add Transaction Log
        tx_id = f"mock_tx_{random.randint(100000, 999999)}"
        timestamp_str = datetime.datetime.now().strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초").replace("AM", "오전").replace("PM", "오후") + " UTC+9"
        
        if "transactions" not in found_user:
            found_user["transactions"] = {}
            
        usr_name = found_user.get("name", "고객")
        found_user["transactions"][tx_id] = {
            "amount": amount,
            "balance_after": new_balance,
            "description": "환불",
            "is_deposit": True,
            "memo_from_sender": "반품",
            "memo_to_me": usr_name,
            "recipientName": usr_name,
            "senderName": store_name,
            "timestamp": timestamp_str,
            "type": "입금"
        }
        
        # 4. Add Notification
        notif_id = f"mock_notif_{random.randint(100000, 999999)}"
        if "notifications" not in found_user:
            found_user["notifications"] = {}
            
        found_user["notifications"][notif_id] = {
            "message": f"{store_name}에서 {int(amount):,}원이 반품(환불)되었습니다.",
            "read": False,
            "timestamp": timestamp_str
        }
        
        self.save_mock_db()
        return True, "반품 처리가 정상적으로 완료되었습니다.", new_balance

    def _process_real_refund(self, candidates, amount, store_name):
        try:
            # 1. Search accounts subcollection group using "in" operator
            accounts_ref = self.db.collection_group('accounts')
            query = accounts_ref.where('accountNumber', 'in', candidates).limit(1)
            docs = list(query.stream())
            
            if not docs:
                return False, "등록된 계좌를 찾을 수 없습니다.", 0.0
                
            account_doc_ref = docs[0].reference
            user_doc_ref = account_doc_ref.parent.parent # users/{uid}
            
            user_snap = user_doc_ref.get()
            user_data = user_snap.to_dict()
            
            if not user_data:
                return False, "사용자 정보를 조회할 수 없습니다.", 0.0
                
            # 2. Use Firestore Transaction for Atomic updates
            transaction = self.db.transaction()
            
            @self.firestore_module.transactional
            def update_in_transaction(tx, acc_ref, usr_ref, usr_name):
                acc_snap = acc_ref.get(transaction=tx)
                acc_data = acc_snap.to_dict()
                if not acc_data:
                    raise Exception("계좌 데이터를 읽을 수 없습니다.")
                    
                cur_bal = float(acc_data.get('balance', 0.0))
                new_bal = cur_bal + amount
                
                # Update Account Balance
                tx.update(acc_ref, {'balance': new_bal})
                
                # Add Transaction Document matching requested format
                tx_ref = usr_ref.collection('transactions').document()
                tx.set(tx_ref, {
                    'amount': amount,
                    'balance_after': new_bal,
                    'description': "반품",
                    'is_deposit': True,
                    'memo_from_sender': "반품",
                    'memo_to_me': usr_name,
                    'recipientName': usr_name,
                    'senderName': store_name,
                    'timestamp': self.firestore_module.SERVER_TIMESTAMP,
                    'type': '입금'
                })
                
                # Add Notification Document
                notif_ref = usr_ref.collection('notifications').document()
                tx.set(notif_ref, {
                    'message': f"{store_name}에서 {int(amount):,}원이 반품(환불)되었습니다.",
                    'read': False,
                    'timestamp': self.firestore_module.SERVER_TIMESTAMP
                })
                
                return new_bal
                
            user_name = user_data.get('name', '고객')
            new_balance = update_in_transaction(transaction, account_doc_ref, user_doc_ref, user_name)
            
            # Update paymentState to 'success' (for consistency)
            try:
                account_doc_ref.update({
                    'paymentState': {
                        'status': 'success',
                        'amount': amount,
                        'storeName': f"반품-{store_name}",
                        'balanceAfter': new_balance
                    }
                })
            except Exception:
                pass
                
            return True, "반품 처리가 정상적으로 완료되었습니다.", new_balance
            
        except Exception as e:
            return False, f"반품 처리 중 오류가 발생했습니다: {e}", 0.0
