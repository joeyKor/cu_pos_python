import json
import os

# Default data from the original data.py to be used for initialization
DEFAULT_PRODUCTS = {
    "8801234567891": {"name": "새우깡", "price": 3000, "category": "snack", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801234123456": {"name": "콘칩", "price": 2000, "category": "snack", "stock": 100, "promo_type": 1, "is_quick": False},
    "8801000000001": {"name": "동아)나랑드파인P500m", "price": 2000, "category": "drink", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801000000002": {"name": "#코카콜라P500ml", "price": 2300, "category": "drink", "stock": 100, "promo_type": 2, "is_quick": False},
    "8801000000003": {"name": "친환경)DU백색봉투대", "price": 100, "category": "etc", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801000000004": {"name": "아이시스2L P6입", "price": 3600, "category": "water", "stock": 100, "promo_type": 1, "is_quick": True},
    "8801000000005": {"name": "유앤)포켓몬볼모양젤", "price": 1000, "category": "snack", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801000000006": {"name": "츄파춥스12g", "price": 300, "category": "candy", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801000000007": {"name": "트롤리지구젤리(낱개)", "price": 1000, "category": "jelly", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801000000008": {"name": "트롤리지구젤리(낱개)", "price": 1000, "category": "jelly", "stock": 100, "promo_type": 0},
}

CATEGORIES = ["과자류", "음료류", "사탕류", "젤리류", "생수", "간편식사", "기타상품"]

# Create json directory if it doesn't exist
os.makedirs("json", exist_ok=True)
DATA_FILE = os.path.join("json", "products.json")
VOUCHER_FILE = os.path.join("json", "vouchers.json")

DEFAULT_VOUCHERS = {
    "9900012345678": {"product_barcode": "8801234567891", "name": "모바일)새우깡교환권", "price": 3000},
    "9900012345679": {"product_barcode": "8801234123456", "name": "모바일)콘칩교환권", "price": 2000},
    "9900012345680": {"product_barcode": "8801000000002", "name": "모바일)코카콜라교환권", "price": 2300},
    "9900012345681": {"product_barcode": "8801007835396", "name": "모바일)맥스봉직화꼬치바교환권", "price": 2500}
}

class ProductManager:
    def __init__(self):
        self.products = {}
        self.load_products()
        self.vouchers = {}
        self.load_vouchers()

    def load_products(self):
        if not os.path.exists(DATA_FILE):
            self.products = DEFAULT_PRODUCTS.copy()
            self.save_products()
        else:
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.products = DEFAULT_PRODUCTS.copy()
                self.save_products()

    def save_products(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error saving products: {e}")

    def get_product(self, barcode):
        return self.products.get(barcode)

    def add_product(self, barcode, name, price, category="", stock=0, promo_type=0, is_quick=False):
        self.products[barcode] = {"name": name, "price": price, "category": category, "stock": stock, "promo_type": promo_type, "is_quick": is_quick}
        self.save_products()

    def update_product(self, barcode, name, price, category="", stock=None, promo_type=None, is_quick=None):
        if barcode in self.products:
            self.products[barcode]["name"] = name
            self.products[barcode]["price"] = price
            self.products[barcode]["category"] = category
            if stock is not None:
                self.products[barcode]["stock"] = stock
            if promo_type is not None:
                self.products[barcode]["promo_type"] = promo_type
            if is_quick is not None:
                self.products[barcode]["is_quick"] = is_quick
            self.save_products()
            
    def update_product_key(self, old_barcode, new_barcode, name, price, category="", stock=0, promo_type=0, is_quick=False):
        """
        Updates the barcode (key) of a product while preserving its position in the dictionary.
        This is done by reconstructing the dictionary.
        """
        if old_barcode not in self.products:
            return False
            
        new_products = {}
        for key, value in self.products.items():
            if key == old_barcode:
                new_products[new_barcode] = {"name": name, "price": price, "category": category, "stock": stock, "promo_type": promo_type, "is_quick": is_quick}
            else:
                new_products[key] = value
        
        self.products = new_products
        self.save_products()
        return True

    def delete_product(self, barcode):
        if barcode in self.products:
            del self.products[barcode]
            self.save_products()

    def get_all_products(self):
        return self.products

    def reduce_stock(self, barcode, qty):
        if barcode in self.products:
            current_stock = self.products[barcode].get("stock", 0)
            self.products[barcode]["stock"] = max(0, current_stock - qty)
            self.save_products()
            return True
        return False

    def update_stock(self, barcode, new_stock):
        if barcode in self.products:
            self.products[barcode]["stock"] = new_stock
            self.save_products()
            return True
        return False
    def get_quick_items(self, limit=5):
        """ Returns up to 'limit' items marked as quick items """
        quick_list = []
        for bc, p in self.products.items():
            if p.get("is_quick", False):
                quick_list.append((bc, p))
                if len(quick_list) >= limit:
                    break
        return quick_list

    def load_vouchers(self):
        if not os.path.exists(VOUCHER_FILE):
            self.vouchers = DEFAULT_VOUCHERS.copy()
            self.save_vouchers()
        else:
            try:
                with open(VOUCHER_FILE, 'r', encoding='utf-8') as f:
                    self.vouchers = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.vouchers = DEFAULT_VOUCHERS.copy()
                self.save_vouchers()

    def save_vouchers(self):
        try:
            with open(VOUCHER_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.vouchers, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error saving vouchers: {e}")

    def get_voucher(self, barcode):
        return self.vouchers.get(barcode)

    def add_voucher(self, barcode, target_barcode, name, price):
        self.vouchers[barcode] = {
            "product_barcode": target_barcode,
            "name": name,
            "price": price
        }
        self.save_vouchers()

    def delete_voucher(self, barcode):
        if barcode in self.vouchers:
            del self.vouchers[barcode]
            self.save_vouchers()
            return True
        return False

    def get_all_vouchers(self):
        return self.vouchers
