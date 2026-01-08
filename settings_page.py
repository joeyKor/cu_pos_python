from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QPushButton, 
                             QHeaderView, QWidget, QComboBox, QAbstractItemView, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
import styles
from product_manager import ProductManager, CATEGORIES
from ui_components import CustomMessageDialog

class SettingsPage(QWidget):
    backRequested = pyqtSignal()

    def __init__(self, product_manager, receipt_manager, parent=None):
        super().__init__(parent)
        self.product_manager: ProductManager = product_manager
        self.receipt_manager = receipt_manager
        self.current_editing_barcode = None # Track currently editing item
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setStyleSheet(f"background-color: {styles.GRAY_BG};")
        
        # 1. Header
        self.create_header()
        
        # 2. Main Content
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Left Side - Product List
        self.create_left_panel()
        
        # Right Side - Form & Actions
        self.create_right_panel()
        
        self.main_layout.addWidget(self.content_widget, stretch=1)
        
        # 3. Bottom Navigation
        self.create_bottom_nav()
        
        # Load Data
        self.load_data()
        self.clear_form()

    def create_header(self):
        header_frame = QFrame()
        header_frame.setMinimumHeight(60)
        header_frame.setStyleSheet("background-color: white; border-bottom: 2px solid #DEE2E6;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        lbl_title = QLabel("상품 관리 설정")
        lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("설정 > 상품관리")
        lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #777;")
        header_layout.addWidget(lbl_breadcrumb)
        self.main_layout.addWidget(header_frame)

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
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 280) # Much wider Barcode
        self.table.setColumnWidth(2, 100) # Price
        self.table.setColumnWidth(3, 120) # Category
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name takes remaining (narrower)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.on_table_click)
        
        left_layout.addWidget(lbl_title)
        left_layout.addWidget(self.table)
        
        self.content_layout.addWidget(left_widget, stretch=60)

    def create_right_panel(self):
        right_widget = QWidget()
        right_widget.setStyleSheet(f"background-color: {styles.WHITE}; border: 1px solid {styles.BORDER_COLOR}; border-radius: 10px;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_form = QLabel("상품 정보 입력")
        lbl_form.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-bottom: 20px;")
        right_layout.addWidget(lbl_form)
        
        # Barcode with Counter
        barcode_header_layout = QHBoxLayout()
        lbl_barcode = QLabel("바코드 (13자리 숫자)")
        lbl_barcode.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR}; margin-top: 10px;")
        self.lbl_barcode_counter = QLabel("(0 / 13)")
        self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; margin-top: 10px; font-weight: bold;")
        barcode_header_layout.addWidget(lbl_barcode)
        barcode_header_layout.addStretch()
        barcode_header_layout.addWidget(self.lbl_barcode_counter)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setStyleSheet(styles.INPUT_STYLE)
        self.input_barcode.textChanged.connect(self.update_barcode_counter)
        
        lbl_name, self.input_name = self.create_input_field("상품명")
        lbl_price, self.input_price = self.create_input_field("단가 (원)")
        
        # Category Combo
        lbl_cat = QLabel("분류")
        lbl_cat.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR}; margin-top: 10px;")
        self.combo_category = QComboBox()
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.setEditable(True) # Allow custom categories
        self.combo_category.setStyleSheet(styles.COMBO_STYLE)
        
        right_layout.addLayout(barcode_header_layout) # Label + Counter
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
        
        self.btn_print_selected = QPushButton("선택 바코드 출력")
        self.btn_print_selected.setStyleSheet(styles.BUTTON_PURPLE_STYLE)
        self.btn_print_selected.clicked.connect(self.print_selected_barcode)
        
        self.btn_print_all = QPushButton("전체 바코드 출력")
        self.btn_print_all.setStyleSheet(styles.BUTTON_PURPLE_STYLE)
        self.btn_print_all.clicked.connect(self.print_all_barcodes)
        
        self.btn_clear = QPushButton("초기화 (입력창)")
        self.btn_clear.setStyleSheet(styles.BUTTON_BOTTOM_STYLE.replace("font-size: 10pt", "font-size: 12pt"))
        self.btn_clear.clicked.connect(self.clear_form)
        
        # Split print buttons horizontally
        print_btn_layout = QHBoxLayout()
        print_btn_layout.setSpacing(10)
        print_btn_layout.addWidget(self.btn_print_selected)
        print_btn_layout.addWidget(self.btn_print_all)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addLayout(print_btn_layout)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        
        right_layout.addLayout(btn_layout)
        
        self.content_layout.addWidget(right_widget, stretch=40)

    def create_bottom_nav(self):
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(100)
        bottom_frame.setStyleSheet("background-color: #CAD2D9; border-top: 1px solid #CCC;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(30, 10, 30, 10)
        
        btn_back = QPushButton("◀  이전 [CLEAR]")
        btn_back.setFixedSize(220, 65)
        btn_back.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 15pt; border-radius: 5px;")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.backRequested.emit)
        bottom_layout.addWidget(btn_back)
        
        bottom_layout.addStretch()
        self.main_layout.addWidget(bottom_frame)

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
        self.table.selectRow(row)
        barcode = self.table.item(row, 0).text()
        product = self.product_manager.get_product(barcode)
        
        if product:
            self.current_editing_barcode = barcode # Set current editing
            self.input_barcode.setText(barcode)
            self.input_name.setText(product["name"])
            self.input_price.setText(str(product["price"]))
            self.combo_category.setCurrentText(product["category"])

    def update_barcode_counter(self):
        length = len(self.input_barcode.text())
        self.lbl_barcode_counter.setText(f"({length} / 13)")
        if length == 13:
            self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.ACCENT_GREEN}; margin-top: 10px; font-weight: bold;")
        else:
            self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; margin-top: 10px; font-weight: bold;")

    def clear_form(self):
        self.current_editing_barcode = None # Reset
        self.input_barcode.setText("8801000000")
        self.input_barcode.setFocus()
        self.input_barcode.setCursorPosition(10)
        self.input_name.clear()
        self.input_price.clear()
        self.combo_category.setCurrentIndex(0)
        self.table.clearSelection()
        self.update_barcode_counter()

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
        
        # Validation: 13 digits numeric
        if len(barcode) != 13 or not barcode.isdigit():
            self.show_alert("경고", "바코드는 13자리 숫자로 입력해주세요.\n(예: 8801234567890)", 'warning')
            return
            
        try:
            price = int(price_str.replace(",", ""))
        except ValueError:
            self.show_alert("경고", "단가는 숫자여야 합니다.", 'warning')
            return
        
        # Duplicate Check
        existing_product = self.product_manager.get_product(barcode)
        
        if self.current_editing_barcode:
            # Scenario 1: Editing an existing item
            if self.current_editing_barcode != barcode:
                # Barcode was changed (Renaming)
                if existing_product:
                    # New barcode already exists on ANOTHER product
                    msg = f"바코드 [{barcode}]는 이미 등록된 상품입니다.\n기존 상품: {existing_product['name']}\n\n이 상품 정보를 현재 입력하신 정보로 변경하시겠습니까?"
                    if self.show_alert("중복 확인", msg, 'question'):
                        # Remove the original product being edited and overwrite the target barcode
                        self.product_manager.delete_product(self.current_editing_barcode)
                        self.product_manager.add_product(barcode, name, price, category)
                    else:
                        return
                else:
                    # Normal rename (barcode changed to a new unique one)
                    self.product_manager.update_product_key(self.current_editing_barcode, barcode, name, price, category)
            else:
                # Barcode didn't change, just update details
                self.product_manager.add_product(barcode, name, price, category)
        else:
            # Scenario 2: Adding a completely new product (or duplicate on enter)
            if existing_product:
                msg = f"바코드 [{barcode}]는 이미 등록된 상품입니다.\n기존 상품: {existing_product['name']}\n\n이 상품 정보를 현재 입력하신 정보로 변경하시겠습니까?"
                if self.show_alert("중복 확인", msg, 'question'):
                    self.product_manager.add_product(barcode, name, price, category)
                else:
                    return
            else:
                # Normal new addition
                self.product_manager.add_product(barcode, name, price, category)

        self.load_data()
        self.clear_form()
        self.show_alert("완료", "상품 정보가 저장되었습니다.", 'info')

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

    def generate_barcode_html(self, item_list):
        # item_list: list of (barcode, name, price)
        from ui_components import ReceiptPreviewDialog
        
        table_rows = ""
        for i in range(0, len(item_list), 3):
            table_rows += "<tr>"
            for j in range(3):
                if i + j < len(item_list):
                    barcode, name, price = item_list[i + j]
                    barcode_img = self.receipt_manager.generate_barcode_base64(barcode)
                    table_rows += f"""
                    <td class="label-box">
                        <div class="p-name">{name}</div>
                        <div class="p-price">{price:,}원</div>
                        <div class="p-barcode">
                            <img src="{barcode_img}" width="120" height="40">
                        </div>
                    </td>
                    """
                else:
                    table_rows += '<td class="label-box" style="border:none;"></td>'
            table_rows += "</tr>"
            
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Malgun Gothic', sans-serif; background: white; padding: 5px; color: black; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .label-box {{
                    border: 1px solid black;
                    padding: 10px 5px;
                    text-align: center;
                    width: 33.3%;
                    height: 110px;
                }}
                .p-name {{ font-size: 9pt; font-weight: bold; overflow: hidden; white-space: nowrap; color: black; }}
                .p-price {{ font-size: 10pt; font-weight: bold; color: black; margin: 3px 0; }}
                .p-barcode {{ margin-top: 5px; }}
            </style>
        </head>
        <body>
            <table>
                {table_rows}
            </table>
        </body>
        </html>
        """
        return html

    def print_selected_barcode(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        price_str = self.input_price.text().strip()
        
        if not barcode or not name or not price_str:
            self.show_alert("경고", "출력할 상품을 선택하거나 정보를 입력해주세요.", 'warning')
            return
            
        try:
            price = int(price_str.replace(",", ""))
        except ValueError:
            self.show_alert("경고", "단가는 숫자여야 합니다.", 'warning')
            return

        items = [(barcode, name, price)] * 18
        html = self.generate_barcode_html(items)
        
        from ui_components import ReceiptPreviewDialog
        dialog = ReceiptPreviewDialog(html, self)
        dialog.setFixedSize(450, 750)
        dialog.exec()

    def print_all_barcodes(self):
        products = self.product_manager.get_all_products()
        if not products:
            self.show_alert("알림", "등록된 상품이 없습니다.", 'info')
            return
            
        items = []
        for barcode, data in products.items():
            items.append((barcode, data["name"], data["price"]))
            
        html = self.generate_barcode_html(items)
        
        from ui_components import ReceiptPreviewDialog
        dialog = ReceiptPreviewDialog(html, self)
        dialog.setFixedSize(450, 750)
        dialog.exec()
