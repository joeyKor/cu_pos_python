import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QTextBrowser, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QAbstractItemView, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
import styles

class ProductInquiryPage(QWidget):
    backRequested = pyqtSignal()
    productSelected = pyqtSignal(str)
    
    def __init__(self, product_manager, sales_mode=False, parent=None):
        super().__init__(parent)
        self.product_manager = product_manager
        self.sales_mode = sales_mode
        self.selected_barcode = None
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet("background-color: #F8F9FA;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Header Frame
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("background-color: white; border-bottom: 2px solid #DEE2E6;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        self.lbl_title = QLabel("상품 조회/등록")
        self.lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("통합조회 > 상품 조회/등록")
        lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #7B68EE; font-weight: bold;")
        header_layout.addWidget(lbl_breadcrumb)
        main_layout.addWidget(header_frame)
        
        # 2. Main Content Area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(25)
        
        # Styles for inputs
        EDITABLE_STYLE = f"""
            QLineEdit {{
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 13pt;
                font-weight: bold;
                min-height: 45px;
            }}
            QLineEdit:focus {{
                border: 2px solid #7B68EE;
            }}
        """
        
        READONLY_STYLE = f"""
            QLineEdit {{
                background-color: #E2E8F0;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 13pt;
                font-weight: bold;
                min-height: 45px;
            }}
        """
        
        HIGHLIGHT_STYLE = f"""
            QLineEdit {{
                background-color: #FEF3C7;
                color: #B45309;
                border: 1px solid #FCD34D;
                border-radius: 4px;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 13pt;
                font-weight: bold;
                min-height: 45px;
            }}
        """
        
        LBL_STYLE = "font-size: 13pt; font-weight: bold; color: #475569;"
        
        # --- Left Column (Details Form) ---
        left_panel = QFrame()
        left_panel.setStyleSheet("background: transparent; border: none;")
        left_layout = QGridLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        left_layout.setColumnStretch(1, 1)
        
        # 바코드 (Search Input)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("바코드 번호를 스캔하거나 입력")
        self.txt_search.setStyleSheet(EDITABLE_STYLE)
        self.txt_search.textChanged.connect(self.on_search_changed)
        
        btn_search_name = QPushButton("상품명으로 조회")
        btn_search_name.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search_name.setFixedHeight(45)
        btn_search_name.setStyleSheet("""
            QPushButton {
                background-color: #2D3E50;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 4px;
                padding-left: 20px;
                padding-right: 20px;
                border: none;
            }
            QPushButton:hover { background-color: #1F2B38; }
        """)
        btn_search_name.clicked.connect(self.open_name_search_dialog)
        
        barcode_row = QHBoxLayout()
        barcode_row.addWidget(self.txt_search, stretch=1)
        barcode_row.addWidget(btn_search_name)
        
        lbl_bar = QLabel("바코드")
        lbl_bar.setStyleSheet(LBL_STYLE)
        left_layout.addWidget(lbl_bar, 0, 0)
        left_layout.addLayout(barcode_row, 0, 1)
        
        # 상품명
        self.txt_name = QLineEdit()
        self.txt_name.setReadOnly(True)
        self.txt_name.setStyleSheet(READONLY_STYLE)
        
        lbl_nm = QLabel("상품명")
        lbl_nm.setStyleSheet(LBL_STYLE)
        left_layout.addWidget(lbl_nm, 1, 0)
        left_layout.addWidget(self.txt_name, 1, 1)
        
        # 단가
        self.txt_price = QLineEdit()
        self.txt_price.setReadOnly(True)
        self.txt_price.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_price.setStyleSheet(READONLY_STYLE)
        
        lbl_pr = QLabel("단가")
        lbl_pr.setStyleSheet(LBL_STYLE)
        left_layout.addWidget(lbl_pr, 2, 0)
        left_layout.addWidget(self.txt_price, 2, 1)
        
        # 분류정보
        cat_box = QVBoxLayout()
        cat_box.setSpacing(8)
        self.txt_cat1 = QLineEdit()
        self.txt_cat1.setReadOnly(True)
        self.txt_cat1.setStyleSheet(READONLY_STYLE)
        self.txt_cat2 = QLineEdit()
        self.txt_cat2.setReadOnly(True)
        self.txt_cat2.setStyleSheet(READONLY_STYLE)
        self.txt_cat3 = QLineEdit()
        self.txt_cat3.setReadOnly(True)
        self.txt_cat3.setStyleSheet(READONLY_STYLE)
        cat_box.addWidget(self.txt_cat1)
        cat_box.addWidget(self.txt_cat2)
        cat_box.addWidget(self.txt_cat3)
        
        lbl_cat = QLabel("분류정보")
        lbl_cat.setStyleSheet(LBL_STYLE)
        left_layout.addWidget(lbl_cat, 3, 0, alignment=Qt.AlignmentFlag.AlignTop)
        left_layout.addLayout(cat_box, 3, 1)
        
        # 행사정보
        self.txt_promo_info = QTextBrowser()
        self.txt_promo_info.setFixedHeight(140)
        self.txt_promo_info.setStyleSheet(f"""
            QTextBrowser {{
                background-color: #E2E8F0;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 10px;
                font-size: 11pt;
                font-family: '{styles.FONT_FAMILY}';
                font-weight: bold;
            }}
        """)
        
        lbl_promo = QLabel("행사정보")
        lbl_promo.setStyleSheet(LBL_STYLE)
        left_layout.addWidget(lbl_promo, 4, 0, alignment=Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(self.txt_promo_info, 4, 1)
        
        content_layout.addWidget(left_panel, stretch=45)
        
        # --- Right Column (Product Image & Database Search Table) ---
        right_panel = QFrame()
        right_panel.setStyleSheet("background: transparent; border: none;")
        right_layout_v = QVBoxLayout(right_panel)
        right_layout_v.setContentsMargins(0, 0, 0, 0)
        right_layout_v.setSpacing(15)
        
        # Top half: Image Frame + Products Table
        top_row = QHBoxLayout()
        top_row.setSpacing(15)
        
        # Image Display
        self.lbl_product_image = QLabel()
        self.lbl_product_image.setFixedSize(180, 200)
        self.lbl_product_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_product_image.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 6px; background-color: white;")
        
        top_row.addWidget(self.lbl_product_image)
        
        # Products Search List Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["바코드", "상품명"])
        self.table.setFixedHeight(200)
        
        TABLE_QSS = f"""
            QTableWidget {{
                background-color: white;
                color: #333333;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                gridline-color: #F3F4F6;
                font-family: '{styles.FONT_FAMILY}';
                font-size: 11pt;
                selection-background-color: #EDE9FE;
                selection-color: #1E1B4B;
            }}
            QHeaderView::section {{
                background-color: #F3F4F6;
                color: #4B5563;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }}
        """
        self.table.setStyleSheet(TABLE_QSS)
        self.table.verticalScrollBar().setStyleSheet(styles.SCROLLBAR_STYLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.table.doubleClicked.connect(self.process_selection)
        
        header = self.table.horizontalHeader()
        self.table.setColumnWidth(0, 130)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        top_row.addWidget(self.table)
        right_layout_v.addLayout(top_row)
        
        # Bottom half: Additional Status Grid
        status_grid = QGridLayout()
        status_grid.setSpacing(12)
        status_grid.setColumnStretch(1, 1)
        status_grid.setColumnStretch(3, 1)
        
        # 1. 행사연관상품
        lbl_rel = QLabel("행사연관상품")
        lbl_rel.setStyleSheet(LBL_STYLE)
        self.txt_related = QLineEdit()
        self.txt_related.setReadOnly(True)
        self.txt_related.setStyleSheet(READONLY_STYLE)
        status_grid.addWidget(lbl_rel, 0, 0)
        status_grid.addWidget(self.txt_related, 0, 1, 1, 3) # Span across columns
        
        # 2. 금일판매수량 / 재고
        lbl_sales = QLabel("금일판매수량")
        lbl_sales.setStyleSheet(LBL_STYLE)
        self.txt_sales_qty = QLineEdit()
        self.txt_sales_qty.setReadOnly(True)
        self.txt_sales_qty.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_sales_qty.setStyleSheet(READONLY_STYLE)
        
        lbl_stock = QLabel("재고")
        lbl_stock.setStyleSheet(LBL_STYLE)
        self.txt_stock = QLineEdit()
        self.txt_stock.setReadOnly(True)
        self.txt_stock.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_stock.setStyleSheet(HIGHLIGHT_STYLE)
        
        status_grid.addWidget(lbl_sales, 1, 0)
        status_grid.addWidget(self.txt_sales_qty, 1, 1)
        status_grid.addWidget(lbl_stock, 1, 2)
        status_grid.addWidget(self.txt_stock, 1, 3)
        
        # 3. 판매불가여부 / 미성년자판매구분
        lbl_sale_status = QLabel("판매불가여부")
        lbl_sale_status.setStyleSheet(LBL_STYLE)
        self.txt_sale_status = QLineEdit()
        self.txt_sale_status.setReadOnly(True)
        self.txt_sale_status.setStyleSheet(READONLY_STYLE)
        
        lbl_minor = QLabel("미성년자판매구분")
        lbl_minor.setStyleSheet(LBL_STYLE)
        self.txt_minor_status = QLineEdit()
        self.txt_minor_status.setReadOnly(True)
        self.txt_minor_status.setStyleSheet(READONLY_STYLE)
        
        status_grid.addWidget(lbl_sale_status, 2, 0)
        status_grid.addWidget(self.txt_sale_status, 2, 1)
        status_grid.addWidget(lbl_minor, 2, 2)
        status_grid.addWidget(self.txt_minor_status, 2, 3)
        
        # 4. 발주가능여부
        lbl_order = QLabel("발주가능여부")
        lbl_order.setStyleSheet(LBL_STYLE)
        self.txt_order_status = QLineEdit()
        self.txt_order_status.setReadOnly(True)
        self.txt_order_status.setStyleSheet(READONLY_STYLE)
        
        status_grid.addWidget(lbl_order, 3, 0)
        status_grid.addWidget(self.txt_order_status, 3, 1)
        
        right_layout_v.addLayout(status_grid)
        content_layout.addWidget(right_panel, stretch=55)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # 3. Bottom Navigation
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(100)
        bottom_frame.setStyleSheet("background-color: #CAD2D9; border-top: 1px solid #CCC;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(30, 10, 30, 10)
        bottom_layout.setSpacing(20)
        
        self.btn_back = QPushButton("◀  이전 [CLEAR]")
        self.btn_back.setFixedSize(220, 65)
        self.btn_back.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 15pt; border-radius: 5px;")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.backRequested.emit)
        
        btn_action_text = "상품 추가" if self.sales_mode else "판매 등록"
        btn_action_color = "#10B981" if self.sales_mode else styles.PRIMARY_PURPLE
        btn_action_hover = "#059669" if self.sales_mode else "#6366F1"
        
        self.btn_select = QPushButton(btn_action_text)
        self.btn_select.setFixedSize(220, 65)
        self.btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_action_color};
                color: white;
                border-radius: 5px;
                font-size: 15pt;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: {btn_action_hover}; }}
        """)
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.clicked.connect(self.process_selection)
        
        bottom_layout.addWidget(self.btn_back)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_select)
        
        main_layout.addWidget(bottom_frame)
        
        # Load products list to table
        self.load_data()
        
        # Focus on search input by default
        self.txt_search.setFocus()
        
    def set_sales_mode(self, sales_mode):
        self.sales_mode = sales_mode
        btn_action_text = "상품 추가" if self.sales_mode else "판매 등록"
        btn_action_color = "#10B981" if self.sales_mode else styles.PRIMARY_PURPLE
        btn_action_hover = "#059669" if self.sales_mode else "#6366F1"
        
        self.btn_select.setText(btn_action_text)
        self.btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_action_color};
                color: white;
                border-radius: 5px;
                font-size: 15pt;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: {btn_action_hover}; }}
        """)
        
    def reset_ui(self):
        self.txt_search.blockSignals(True)
        self.txt_search.clear()
        self.txt_search.blockSignals(False)
        self.on_search_changed("")
        self.txt_search.setFocus()
        
    def load_data(self):
        self.products = self.product_manager.get_all_products()
        self.table.setRowCount(len(self.products))
        
        row = 0
        for barcode, data in self.products.items():
            self.table.setItem(row, 0, QTableWidgetItem(barcode))
            self.table.setItem(row, 1, QTableWidgetItem(data["name"]))
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 1).setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            row += 1
            
        if self.table.rowCount() > 0:
            self.table.selectRow(0)
            
    def on_search_changed(self, text):
        search_text = text.strip().lower()
        first_visible_row = -1
        
        for row in range(self.table.rowCount()):
            barcode_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            
            barcode = barcode_item.text().lower() if barcode_item else ""
            name = name_item.text().lower() if name_item else ""
            
            if search_text in barcode or search_text in name:
                self.table.setRowHidden(row, False)
                if first_visible_row == -1:
                    first_visible_row = row
            else:
                self.table.setRowHidden(row, True)
                
        # Block table signal to avoid recursions
        self.table.blockSignals(True)
        if first_visible_row != -1:
            self.table.selectRow(first_visible_row)
            # Update fields dynamically
            self.update_fields(self.table.item(first_visible_row, 0).text())
        else:
            self.table.clearSelection()
            self.update_fields("")
        self.table.blockSignals(False)
        
    def on_table_selection_changed(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
            
        selected_row = selected_ranges[0].topRow()
        barcode_item = self.table.item(selected_row, 0)
        if barcode_item:
            barcode = barcode_item.text()
            self.selected_barcode = barcode
            # Block search signal to avoid resetting filter
            self.txt_search.blockSignals(True)
            self.txt_search.setText(barcode)
            self.txt_search.blockSignals(False)
            self.update_fields(barcode)
            
    def update_fields(self, barcode):
        product = self.product_manager.get_product(barcode)
        if not product:
            self.txt_name.clear()
            self.txt_price.clear()
            self.txt_cat1.clear()
            self.txt_cat2.clear()
            self.txt_cat3.clear()
            self.txt_promo_info.clear()
            self.txt_related.clear()
            self.txt_sales_qty.clear()
            self.txt_stock.clear()
            self.txt_sale_status.clear()
            self.txt_minor_status.clear()
            self.txt_order_status.clear()
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(base_dir, "assets", "image", "cu_mascot_fullbody_white_background_1767715363864.png")
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                self.lbl_product_image.setPixmap(pixmap.scaled(180, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            return
            
        # Update details
        self.txt_name.setText(product["name"])
        self.txt_price.setText(f"{product['price']:,}")
        
        # Classifications
        classifications = self.get_classification(product.get("category", ""))
        self.txt_cat1.setText(classifications[0])
        self.txt_cat2.setText(classifications[1])
        self.txt_cat3.setText(classifications[2])
        
        # Promo info
        promo_info = self.get_promo_info(barcode, product.get("promo_type", 0))
        self.txt_promo_info.setText(promo_info)
        
        # Linked products
        if barcode in ["8801007835396", "8801007880303", "8801007348308"]:
            self.txt_related.setText("8801007880303, 8801007348308")
        elif product.get("category") == "drink":
            self.txt_related.setText("8801000000001, 8801000000002")
        elif product.get("category") == "snack":
            self.txt_related.setText("8801234567891, 8801234123456")
        else:
            self.txt_related.setText("없음")
            
        # Sales quantity
        if barcode in ["8801007835396", "8801007880303", "8801007348308"]:
            self.txt_sales_qty.setText("1")
        else:
            self.txt_sales_qty.setText("0")
            
        # Stock
        self.txt_stock.setText(str(product.get("stock", 0)))
        
        # Rest of details
        self.txt_sale_status.setText("정상")
        self.txt_minor_status.setText("판매가능")
        self.txt_order_status.setText("발주가능")
        
        # Load image (search in photo/ folder first, then assets/ folder)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = None
        for ext in ["png", "jpg", "jpeg", "webp"]:
            p = os.path.join(os.path.abspath("."), "photo", f"{barcode}.{ext}")
            if os.path.exists(p):
                img_path = p
                break
                
        if not img_path:
            for ext in ["png", "jpg", "jpeg"]:
                p = os.path.join(base_dir, "assets", "image", f"{barcode}.{ext}")
                if os.path.exists(p):
                    img_path = p
                    break
                    
        if not img_path:
            img_path = os.path.join(base_dir, "assets", "image", "cu_mascot_fullbody_white_background_1767715363864.png")
            
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.lbl_product_image.setPixmap(pixmap.scaled(180, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
    def get_classification(self, category):
        cat_lower = category.lower() if category else ""
        if "snack" in cat_lower or "과자" in cat_lower:
            return ["10 스낵류", "012 과자류", "045 봉지과자"]
        elif "drink" in cat_lower or "음료" in cat_lower:
            return ["11 음료류", "018 탄산음료", "054 콜라/사이다"]
        elif "candy" in cat_lower or "사탕" in cat_lower:
            return ["12 제과류", "015 사탕/껌", "062 막대사탕"]
        elif "jelly" in cat_lower or "젤리" in cat_lower:
            return ["12 제과류", "016 젤리류", "063 수입젤리"]
        elif "water" in cat_lower or "생수" in cat_lower:
            return ["11 음료류", "017 먹는샘물", "051 국산생수"]
        elif "핫바" in cat_lower or "hotbar" in cat_lower:
            return ["14 안주류", "023 육가공류", "069 핫바"]
        elif "식사" in cat_lower:
            return ["15 일식식사", "028 간편식사", "072 우동/샤브"]
        elif "면" in cat_lower:
            return ["16 면류", "031 라면류", "081 용기면/봉지면"]
        else:
            return ["99 기타류", "099 일반분류", "999 기타상품"]
            
    def get_promo_info(self, barcode, promo_type):
        if barcode in ["8801007835396", "8801007880303", "8801007348308"]:
            return (
                "채선당 냉장면 2종 중 1종 구매 시, CJ)\n"
                "핫바 2종 중 1종 증정\n"
                "행사기간 : 2026-06-01 ~ 2026-06-30\n"
                "행사요일 : 매일\n"
                "정육면체, 이금기, 풍년, 최네집 1종 구매\n"
                "시, CJ) 핫바 1종 증정\n"
                "행사기간 : 2026-06-01 ~ 2026-06-30\n"
                "행사요일 : 매일"
            )
        if promo_type == 1:
            return (
                "[1+1 증정 행사]\n"
                "행사기간 : 2026-06-01 ~ 2026-06-30\n"
                "행사요일 : 매일\n"
                "구매 시 동일 상품 1개 증정"
            )
        elif promo_type == 2:
            return (
                "[2+1 증정 행사]\n"
                "행사기간 : 2026-06-01 ~ 2026-06-30\n"
                "행사요일 : 매일\n"
                "2개 구매 시 1개 추가 증정"
            )
        return "행사 정보가 없습니다."

    def process_selection(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
            
        selected_row = selected_ranges[0].topRow()
        barcode_item = self.table.item(selected_row, 0)
        if barcode_item:
            self.selected_barcode = barcode_item.text()
            self.productSelected.emit(self.selected_barcode)

    def open_name_search_dialog(self):
        from ui_components import ProductNameSearchDialog
        dialog = ProductNameSearchDialog(self.product_manager, self)
        if dialog.exec():
            if dialog.selected_barcode:
                self.txt_search.setText(dialog.selected_barcode)
