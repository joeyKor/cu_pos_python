import json
import os
from datetime import datetime

class TransactionManager:
    def __init__(self, file_path="transactions.json", config_path="safe_config.json"):
        self.file_path = file_path
        self.config_path = config_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"safe_base_amt": 472000}, f)

    def save_transaction(self, items, total_amt, payment_method, received_amt=None, change_amt=0, payment_details=None):
        transaction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": items,
            "total_amt": total_amt,
            "payment_method": payment_method,
            "received_amt": received_amt if received_amt is not None else total_amt,
            "change_amt": change_amt,
            "payment_details": payment_details or {}
        }

        try:
            with open(self.file_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data.append(transaction)
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()
            return True
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return False

    def get_last_transaction(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    return data[-1]
            return None
        except Exception as e:
            print(f"Error reading last transaction: {e}")
            return None

    def get_cash_total(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cash_total = sum(t.get("total_amt", 0) for t in data if t.get("payment_method") == "Cash")
                return cash_total
        except Exception as e:
            print(f"Error calculating cash total: {e}")
            return 0

    def get_base_safe_amt(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("safe_base_amt", 472000)
        except:
            return 472000

    def set_base_safe_amt(self, amount):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"safe_base_amt": amount}, f)
            return True
        except Exception as e:
            print(f"Error saving base safe amount: {e}")
            return False
