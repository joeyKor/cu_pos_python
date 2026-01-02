from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QPushButton, 
                             QHeaderView, QWidget, QComboBox, QAbstractItemView)
from PyQt6.QtCore import Qt
import styles
from product_manager import ProductManager, CATEGORIES
from ui_components import CustomMessageDialog

class SettingsPage(QDialog):
    def __init__(self, product_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("상품 관리 설정")
        self.resize(1000, 600)
        self.product_manager: ProductManager = product_manager
        self.current_editing_barcode = None # Track currently editing item
        
        # Main Layout
        self.layout = QHBoxLayout(self)
        self.setStyleSheet(f"background-color: {styles.GRAY_BG};")
        
        # Left Side - Product List
        self.create_left_panel()
        
        # Right Side - Form & Actions
        self.create_right_panel()
        
        # Load Data
        self.load_data()

    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_title = QLabel("상품 목록")
        lbl_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-bottom: 10px;")
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["바코드", "상품명", "단가", "분류"])
        self.table.setStyleSheet(styles.TABLE_STYLE)
        
        # Resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name stretches
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.on_table_click)
        
        left_layout.addWidget(lbl_title)
        left_layout.addWidget(self.table)
        
        self.layout.addWidget(left_widget, stretch=60)

    def create_right_panel(self):
        right_widget = QWidget()
        right_widget.setStyleSheet(f"background-color: {styles.WHITE}; border: 1px solid {styles.BORDER_COLOR}; border-radius: 10px;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_form = QLabel("상품 정보 입력")
        lbl_form.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-bottom: 20px;")
        right_layout.addWidget(lbl_form)
        
        # Form Fields
        lbl_barcode, self.input_barcode = self.create_input_field("바코드 (5자리 숫자)")
        lbl_name, self.input_name = self.create_input_field("상품명")
        lbl_price, self.input_price = self.create_input_field("단가 (원)")
        
        # Category Combo
        lbl_cat = QLabel("분류")
        lbl_cat.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR}; margin-top: 10px;")
        self.combo_category = QComboBox()
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.setEditable(True) # Allow custom categories
        self.combo_category.setStyleSheet(styles.COMBO_STYLE)
        
        right_layout.addWidget(lbl_barcode) # Label
        right_layout.addWidget(self.input_barcode) # Input
        right_layout.addWidget(lbl_name)
        right_layout.addWidget(self.input_name)
        right_layout.addWidget(lbl_price)
        right_layout.addWidget(self.input_price)
        right_layout.addWidget(lbl_cat)
        right_layout.addWidget(self.combo_category)
        
        right_layout.addStretch()
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_add = QPushButton("추가 / 저장")
        self.btn_add.setStyleSheet(styles.BUTTON_GREEN_STYLE)
        self.btn_add.clicked.connect(self.save_product)
        
        self.btn_delete = QPushButton("선택 삭제")
        self.btn_delete.setStyleSheet(styles.BUTTON_RED_STYLE)
        self.btn_delete.clicked.connect(self.delete_product)
        
        self.btn_clear = QPushButton("초기화 (입력창)")
        self.btn_clear.setStyleSheet(styles.BUTTON_BOTTOM_STYLE.replace("font-size: 10pt", "font-size: 12pt"))
        self.btn_clear.clicked.connect(self.clear_form)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        
        right_layout.addLayout(btn_layout)
        
        self.layout.addWidget(right_widget, stretch=40)

    def create_input_field(self, label_text):
        label = QLabel(label_text)
        label.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR}; margin-top: 10px;")
        input_field = QLineEdit()
        input_field.setStyleSheet(styles.INPUT_STYLE)
        return label, input_field

    def load_data(self):
        products = self.product_manager.get_all_products()
        self.table.setRowCount(len(products))
        
        row = 0
        for barcode, data in products.items():
            self.table.setItem(row, 0, QTableWidgetItem(barcode))
            self.table.setItem(row, 1, QTableWidgetItem(data["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{data['price']:,}"))
            self.table.setItem(row, 3, QTableWidgetItem(data["category"]))
            
            # Alignments
            self.table.item(row, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            
            row += 1

    def on_table_click(self, row, col):
        barcode = self.table.item(row, 0).text()
        product = self.product_manager.get_product(barcode)
        
        if product:
            self.current_editing_barcode = barcode # Set current editing
            self.input_barcode.setText(barcode)
            self.input_name.setText(product["name"])
            self.input_price.setText(str(product["price"]))
            self.combo_category.setCurrentText(product["category"])

    def clear_form(self):
        self.current_editing_barcode = None # Reset
        self.input_barcode.clear()
        self.input_name.clear()
        self.input_price.clear()
        self.combo_category.setCurrentIndex(0)
        self.table.clearSelection()

    def show_alert(self, title, message, type='info'):
        dialog = CustomMessageDialog(title, message, type, self)
        dialog.exec()
        return dialog.result_value

    def save_product(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        price_str = self.input_price.text().strip()
        category = self.combo_category.currentText().strip()
        
        if not barcode or not name or not price_str:
            self.show_alert("경고", "모든 필드를 입력해주세요.", 'warning')
            return
        
        # Validation: 5 digits numeric
        if len(barcode) != 5 or not barcode.isdigit():
            self.show_alert("경고", "바코드는 5자리 숫자로 입력해주세요.\n(예: 12345)", 'warning')
            return
            
        try:
            price = int(price_str.replace(",", ""))
        except ValueError:
            self.show_alert("경고", "단가는 숫자여야 합니다.", 'warning')
            return
        
        # Handle Barcode Update (Renaming)
        if self.current_editing_barcode and self.current_editing_barcode != barcode:
            # User changed the barcode of an existing item
            # Check if new barcode already exists
            if self.product_manager.get_product(barcode):
                self.show_alert("오류", f"이미 존재하는 바코드입니다: {barcode}\n다른 번호를 사용해주세요.", 'warning')
                return
            
            # Update key preserving order
            self.product_manager.update_product_key(self.current_editing_barcode, barcode, name, price, category)
        else:
            # New product or same barcode
            self.product_manager.add_product(barcode, name, price, category)

        self.load_data()
        self.clear_form()
        self.show_alert("완료", "상품이 저장되었습니다.", 'info')

    def delete_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            self.show_alert("경고", "삭제할 상품을 선택해주세요.", 'warning')
            return
            
        barcode = self.table.item(current_row, 0).text()
        
        if self.show_alert("삭제 확인", f"바코드[{barcode}]\n상품을 삭제하시겠습니까?", 'question'):
            self.product_manager.delete_product(barcode)
            self.load_data()
            self.clear_form()
