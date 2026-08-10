import json
import os

# Default data optimized for installation with requested products
DEFAULT_PRODUCTS = {
    "8801111900010": {"name": "초코파이", "price": 1700, "category": "과자류", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801111900027": {"name": "새우깡", "price": 1900, "category": "과자류", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801111900034": {"name": "양파링", "price": 2200, "category": "과자류", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900041": {"name": "빅파이", "price": 1300, "category": "과자류", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900058": {"name": "칸쵸", "price": 1400, "category": "과자류", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900065": {"name": "코코볼", "price": 4500, "category": "과자류", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900072": {"name": "진라면", "price": 1400, "category": "간편식사", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801111900089": {"name": "짜파게티", "price": 1700, "category": "간편식사", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801111900096": {"name": "신라면", "price": 1200, "category": "간편식사", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801111900102": {"name": "콜라", "price": 1600, "category": "음료류", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801111900119": {"name": "사이다", "price": 1400, "category": "음료류", "stock": 100, "promo_type": 0, "is_quick": True},
    "8801111900126": {"name": "환타", "price": 1300, "category": "음료류", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900133": {"name": "카페라떼", "price": 3500, "category": "음료류", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900140": {"name": "아메리카노", "price": 2200, "category": "음료류", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900157": {"name": "스크류바", "price": 1300, "category": "기타상품", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900164": {"name": "돼지바", "price": 1400, "category": "기타상품", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900171": {"name": "죠스바", "price": 1200, "category": "기타상품", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900188": {"name": "월드콘", "price": 2500, "category": "기타상품", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900195": {"name": "구구콘", "price": 2600, "category": "기타상품", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900201": {"name": "연필", "price": 800, "category": "기타상품", "stock": 100, "promo_type": 0, "is_quick": False},
    "8801111900218": {"name": "지우개", "price": 1300, "category": "기타상품", "stock": 100, "promo_type": 0, "is_quick": False}
}

CATEGORIES = ["과자류", "음료류", "사탕류", "젤리류", "생수", "간편식사", "기타상품"]

# Create json directory if it doesn't exist
os.makedirs("json", exist_ok=True)
DATA_FILE = os.path.join("json", "products.json")
VOUCHER_FILE = os.path.join("json", "vouchers.json")

DEFAULT_VOUCHERS = {
    "9900012345678": {"product_barcode": "8801111900027", "name": "모바일)새우깡교환권", "price": 1900},
    "9900012345679": {"product_barcode": "8801111900102", "name": "모바일)콜라교환권", "price": 1600}
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

    def get_all_products(self):
        return self.products

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

    def reduce_stock(self, barcode, qty):
        if barcode in self.products:
            # Prevent negative stock by using max
            current_stock = self.products[barcode].get("stock", 0)
            self.products[barcode]["stock"] = max(0, current_stock - qty)
            self.save_products()

    def get_quick_items(self, limit=5):
        quick_list = []
        for bc, data in self.products.items():
            if data.get("is_quick", False):
                quick_list.append((bc, data))
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

    def get_all_vouchers(self):
        return self.vouchers

    def add_voucher(self, barcode, product_barcode, name, price, status="unused"):
        self.vouchers[barcode] = {"product_barcode": product_barcode, "name": name, "price": price, "status": status}
        self.save_vouchers()

    def update_voucher(self, barcode, product_barcode, name, price, status="unused"):
        if barcode in self.vouchers:
            self.vouchers[barcode] = {"product_barcode": product_barcode, "name": name, "price": price, "status": status}
            self.save_vouchers()

    def update_voucher_key(self, old_barcode, new_barcode, product_barcode, name, price, status="unused"):
        if old_barcode not in self.vouchers:
            return False
        new_vouchers = {}
        for key, value in self.vouchers.items():
            if key == old_barcode:
                new_vouchers[new_barcode] = {"product_barcode": product_barcode, "name": name, "price": price, "status": status}
            else:
                new_vouchers[key] = value
        self.vouchers = new_vouchers
        self.save_vouchers()
        return True

    def mark_voucher_used(self, barcode):
        if barcode in self.vouchers:
            self.vouchers[barcode]["status"] = "used"
            self.save_vouchers()
            return True
        return False

    def delete_voucher(self, barcode):
        if barcode in self.vouchers:
            del self.vouchers[barcode]
            self.save_vouchers()
