import json
import os

# Default data from the original data.py to be used for initialization
DEFAULT_PRODUCTS = {
    "12345": {"name": "새우깡", "price": 3000, "category": "snack"},
    "12312": {"name": "콘칩", "price": 2000, "category": "snack"},
    "8801": {"name": "동아)나랑드파인P500m", "price": 2000, "category": "drink"},
    "8802": {"name": "#코카콜라P500ml", "price": 2300, "category": "drink"},
    "8803": {"name": "친환경)CU백색봉투대", "price": 100, "category": "etc"},
    "8804": {"name": "아이시스2L P6입", "price": 3600, "category": "water"},
    "8805": {"name": "유앤)포켓몬볼모양젤", "price": 1000, "category": "snack"},
    "8806": {"name": "츄파춥스12g", "price": 300, "category": "candy"},
    "8807": {"name": "트롤리지구젤리(낱개)", "price": 1000, "category": "jelly"},
    "8808": {"name": "트롤리지구젤리(낱개)", "price": 1000, "category": "jelly"},
}

CATEGORIES = ["일반상품", "소분상품", "신문/상품권", "쓰레기 봉투/화장", "GET 커피", "고구마"]

DATA_FILE = "products.json"

class ProductManager:
    def __init__(self):
        self.products = {}
        self.load_products()

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

    def add_product(self, barcode, name, price, category=""):
        self.products[barcode] = {"name": name, "price": price, "category": category}
        self.save_products()

    def update_product(self, barcode, name, price, category=""):
        if barcode in self.products:
            self.products[barcode]["name"] = name
            self.products[barcode]["price"] = price
            self.products[barcode]["category"] = category
            self.save_products()
            
    def update_product_key(self, old_barcode, new_barcode, name, price, category=""):
        """
        Updates the barcode (key) of a product while preserving its position in the dictionary.
        This is done by reconstructing the dictionary.
        """
        if old_barcode not in self.products:
            return False
            
        new_products = {}
        for key, value in self.products.items():
            if key == old_barcode:
                new_products[new_barcode] = {"name": name, "price": price, "category": category}
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
