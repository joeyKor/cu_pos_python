from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QPushButton, 
                             QHeaderView, QWidget, QComboBox, QAbstractItemView, QFrame, QScrollArea, QCheckBox, QTabWidget)
import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
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
        self.current_editing_v_barcode = None # Track currently editing voucher item
        self.selected_image_path = None
        self.image_deleted = False
        
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
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #DEE2E6;
                background-color: transparent;
            }}
            QTabBar::tab {{
                background-color: #E2E8F0;
                color: #4A5568;
                border: 1px solid #CBD5E0;
                border-bottom-color: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: {styles.s(10)}px {styles.s(20)}px;
                font-weight: bold;
                font-size: {styles.fs(14)};
                font-family: '{styles.FONT_FAMILY}';
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {styles.PRIMARY_PURPLE};
                border-color: #DEE2E6;
                border-bottom: 2px solid white;
            }}
        """)
        
        # Tab 1: Product Management
        self.product_tab = QWidget()
        self.product_tab_layout = QHBoxLayout(self.product_tab)
        self.product_tab_layout.setContentsMargins(10, 10, 10, 10)
        self.product_tab_layout.setSpacing(20)
        
        self.create_left_panel()
        self.create_right_panel()
        
        self.product_tab_layout.addWidget(self.left_card, stretch=60)
        self.product_tab_layout.addWidget(self.right_card, stretch=40)
        self.tab_widget.addTab(self.product_tab, "일반상품 관리")
        
        # Tab 2: Voucher Management
        self.voucher_tab = QWidget()
        self.voucher_tab_layout = QHBoxLayout(self.voucher_tab)
        self.voucher_tab_layout.setContentsMargins(10, 10, 10, 10)
        self.voucher_tab_layout.setSpacing(20)
        
        self.create_voucher_left_panel()
        self.create_voucher_right_panel()
        
        self.voucher_tab_layout.addWidget(self.v_left_card, stretch=60)
        self.voucher_tab_layout.addWidget(self.v_right_card, stretch=40)
        self.tab_widget.addTab(self.voucher_tab, "모바일 상품권 관리")
        
        self.content_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.content_widget, stretch=1)
        
        # 3. Bottom Navigation
        self.create_bottom_nav()
        
        # Load Data
        self.load_data()
        self.clear_form()
        self.load_voucher_data()
        self.clear_v_form()

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
        # Left card frame
        self.left_card = QFrame()
        self.left_card.setObjectName("left_card")
        self.left_card.setStyleSheet("""
            QFrame#left_card {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        left_layout = QVBoxLayout(self.left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)
        
        # Header layout for Title and Search Bar
        header_row = QHBoxLayout()
        
        lbl_title = QLabel("상품 목록")
        lbl_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        header_row.addWidget(lbl_title)
        
        header_row.addStretch()
        
        # Modern Search Input
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔍 상품명 또는 바코드 검색...")
        self.input_search.setFixedWidth(styles.s(260))
        self.input_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(8)}px;
                padding: {styles.s(8)}px {styles.s(12)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(12)};
                color: {styles.TEXT_COLOR};
            }}
            QLineEdit:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
            }}
        """)
        self.input_search.textChanged.connect(self.filter_products)
        header_row.addWidget(self.input_search)
        
        left_layout.addLayout(header_row)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["바코드", "상품명", "단가", "재고", "행사", "분류", "단축"])
        
        # Customize table style for a highly polished card table view
        SETTINGS_TABLE_STYLE = f"""
            QTableWidget {{
                background-color: white;
                color: {styles.TEXT_COLOR};
                border: none;
                gridline-color: #F3F4F6;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                selection-background-color: #EDE9FE;
                selection-color: {styles.TEXT_COLOR};
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F3F4F6;
                padding-top: {styles.s(8)}px;
                padding-bottom: {styles.s(8)}px;
            }}
            QTableWidget::item:selected {{
                background-color: #EDE9FE;
                color: {styles.TEXT_COLOR};
                font-weight: bold;
            }}
            QHeaderView::section {{
                background-color: #F3F4F6;
                color: #4B5563;
                padding: {styles.s(8)}px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
        """
        self.table.setStyleSheet(SETTINGS_TABLE_STYLE)
        self.table.verticalScrollBar().setStyleSheet(styles.SCROLLBAR_STYLE)
        
        # Resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumHeight(styles.s(45))
        self.table.setColumnWidth(0, styles.s(140)) # Barcode
        self.table.setColumnWidth(1, styles.s(220)) # Name
        self.table.setColumnWidth(2, styles.s(90))  # Price
        self.table.setColumnWidth(3, styles.s(70))  # Stock
        self.table.setColumnWidth(4, styles.s(70))  # Promo
        self.table.setColumnWidth(5, styles.s(100)) # Category
        self.table.setColumnWidth(6, styles.s(60))  # Quick
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(styles.s(45))
        self.table.cellClicked.connect(self.on_table_click)
        
        left_layout.addWidget(self.table)

    def create_right_panel(self):
        # Modern UI Form Styling Override
        MODERN_INPUT_STYLE = f"""
            QLineEdit {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                padding: {styles.s(10)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                color: {styles.TEXT_COLOR};
            }}
            QLineEdit:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
            }}
        """
        
        MODERN_COMBO_STYLE = f"""
            QComboBox {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                padding: {styles.s(10)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                color: black;
            }}
            QComboBox:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
                color: black;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid #D1D5DB;
                selection-background-color: #EDE9FE;
                selection-color: black;
                color: black;
            }}
        """
        
        MODERN_CHECKBOX_STYLE = f"""
            QCheckBox {{
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                color: {styles.PRIMARY_PURPLE};
                font-weight: bold;
                padding: {styles.s(5)}px 0px;
            }}
        """
        
        MODERN_BTN_GREEN = f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(15)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """
        
        MODERN_BTN_PURPLE = f"""
            QPushButton {{
                background-color: {styles.PRIMARY_PURPLE};
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #6366F1;
            }}
            QPushButton:pressed {{
                background-color: {styles.DARK_PURPLE};
            }}
        """
        
        MODERN_BTN_RED = f"""
            QPushButton {{
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:pressed {{
                background-color: #B91C1C;
            }}
        """
        
        MODERN_BTN_GRAY = f"""
            QPushButton {{
                background-color: #F3F4F6;
                color: #4B5563;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E5E7EB;
                color: #1F2937;
            }}
            QPushButton:pressed {{
                background-color: #D1D5DB;
            }}
        """

        # Right container card frame
        self.right_card = QFrame()
        self.right_card.setObjectName("right_card")
        self.right_card.setFixedWidth(styles.s(420)) # Increased width for comfort
        self.right_card.setStyleSheet("""
            QFrame#right_card {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        right_layout = QVBoxLayout(self.right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(styles.s(15))
        
        # Title of the form
        lbl_form = QLabel("상품 정보 입력")
        lbl_form.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        right_layout.addWidget(lbl_form)
        
        # Scroll Area for the form fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; } QWidget { background-color: transparent; }")
        scroll.verticalScrollBar().setStyleSheet(styles.SCROLLBAR_STYLE)
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(styles.s(10))
        form_layout.setContentsMargins(0, 0, 5, 0)
        
        # Barcode Input
        barcode_header_layout = QHBoxLayout()
        lbl_barcode = QLabel("바코드")
        lbl_barcode.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        
        self.lbl_barcode_counter = QLabel("(0 / 13)")
        self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; font-weight: bold;")
        
        barcode_header_layout.addWidget(lbl_barcode)
        barcode_header_layout.addWidget(self.lbl_barcode_counter)
        barcode_header_layout.addStretch()
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("바코드를 스캔하거나 입력하세요")
        self.input_barcode.setStyleSheet(MODERN_INPUT_STYLE)
        self.input_barcode.textChanged.connect(self.update_barcode_counter)
        
        lbl_name, self.input_name = self.create_input_field("상품명")
        lbl_price, self.input_price = self.create_input_field("단가 (원)")
        lbl_stock, self.input_stock = self.create_input_field("재고 수량")
        
        # Apply modern styling
        self.input_name.setStyleSheet(MODERN_INPUT_STYLE)
        self.input_name.setPlaceholderText("상품명을 입력하세요")
        self.input_price.setStyleSheet(MODERN_INPUT_STYLE)
        self.input_price.setPlaceholderText("예: 2,000")
        self.input_stock.setStyleSheet(MODERN_INPUT_STYLE)
        self.input_stock.setPlaceholderText("예: 100")
        
        # Promotion Combo
        lbl_promo = QLabel("행사 종류")
        lbl_promo.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.combo_promo = QComboBox()
        self.combo_promo.addItems(["없음", "1+1", "2+1"])
        self.combo_promo.setStyleSheet(MODERN_COMBO_STYLE)
        
        # Category Combo
        lbl_cat = QLabel("분류")
        lbl_cat.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.combo_category = QComboBox()
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.setEditable(True)
        self.combo_category.setStyleSheet(MODERN_COMBO_STYLE)
        
        # Quick Item Checkbox
        self.check_quick = QCheckBox("메인 화면 단축 버튼 등록")
        self.check_quick.setStyleSheet(MODERN_CHECKBOX_STYLE)
        
        # Assemble form with side-by-side elements
        form_layout.addLayout(barcode_header_layout)
        form_layout.addWidget(self.input_barcode)
        
        form_layout.addWidget(lbl_name)
        form_layout.addWidget(self.input_name)
        
        # Row 3: Price & Stock Side-by-Side
        price_stock_layout = QHBoxLayout()
        price_stock_layout.setSpacing(10)
        
        price_col = QVBoxLayout()
        price_col.setSpacing(4)
        price_col.addWidget(lbl_price)
        price_col.addWidget(self.input_price)
        
        stock_col = QVBoxLayout()
        stock_col.setSpacing(4)
        stock_col.addWidget(lbl_stock)
        stock_col.addWidget(self.input_stock)
        
        price_stock_layout.addLayout(price_col)
        price_stock_layout.addLayout(stock_col)
        form_layout.addLayout(price_stock_layout)
        
        # Row 4: Promo & Category Side-by-Side
        promo_cat_layout = QHBoxLayout()
        promo_cat_layout.setSpacing(10)
        
        promo_col = QVBoxLayout()
        promo_col.setSpacing(4)
        promo_col.addWidget(lbl_promo)
        promo_col.addWidget(self.combo_promo)
        
        cat_col = QVBoxLayout()
        cat_col.setSpacing(4)
        cat_col.addWidget(lbl_cat)
        cat_col.addWidget(self.combo_category)
        
        promo_cat_layout.addLayout(promo_col)
        promo_cat_layout.addLayout(cat_col)
        form_layout.addLayout(promo_cat_layout)
        
        form_layout.addWidget(self.check_quick)
        
        # Row 5: Product Image Layout
        lbl_img_section = QLabel("상품 이미지")
        lbl_img_section.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-top: 5px;")
        form_layout.addWidget(lbl_img_section)
        
        img_row_layout = QHBoxLayout()
        img_row_layout.setSpacing(15)
        
        self.lbl_image_preview = QLabel("이미지 없음")
        self.lbl_image_preview.setFixedSize(styles.s(120), styles.s(120))
        self.lbl_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image_preview.setStyleSheet("""
            QLabel {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: #F9FAFB;
                color: #6B7280;
                font-weight: bold;
            }
        """)
        
        img_btn_layout = QVBoxLayout()
        img_btn_layout.setSpacing(8)
        
        self.btn_select_image = QPushButton("이미지 찾기")
        self.btn_select_image.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_select_image.setFixedHeight(styles.s(36))
        self.btn_select_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_image.clicked.connect(self.select_product_image)
        
        self.btn_clear_image = QPushButton("이미지 삭제")
        self.btn_clear_image.setStyleSheet(MODERN_BTN_GRAY)
        self.btn_clear_image.setFixedHeight(styles.s(36))
        self.btn_clear_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_image.clicked.connect(self.clear_product_image)
        
        img_btn_layout.addWidget(self.btn_select_image)
        img_btn_layout.addWidget(self.btn_clear_image)
        img_btn_layout.addStretch()
        
        img_row_layout.addWidget(self.lbl_image_preview)
        img_row_layout.addLayout(img_btn_layout)
        img_row_layout.addStretch()
        form_layout.addLayout(img_row_layout)
        
        form_layout.addStretch()
        
        scroll.setWidget(form_container)
        right_layout.addWidget(scroll)
        
        # Action Buttons Panel
        btn_panel = QVBoxLayout()
        btn_panel.setSpacing(styles.s(6))
        
        self.btn_add = QPushButton("추가 / 저장 (F12)")
        self.btn_add.setStyleSheet(MODERN_BTN_GREEN)
        self.btn_add.setFixedHeight(styles.s(45))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.save_product)
        btn_panel.addWidget(self.btn_add)
        
        # Barcode printing group
        print_group = QFrame()
        print_group.setStyleSheet("QFrame { background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; } QLabel { border: none; background: transparent; }")
        print_layout = QVBoxLayout(print_group)
        print_layout.setContentsMargins(8, 8, 8, 8)
        print_layout.setSpacing(4)
        
        lbl_print_title = QLabel("바코드 출력")
        lbl_print_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; font-weight: bold; color: #4B5563; background: transparent;")
        print_layout.addWidget(lbl_print_title)
        
        print_btn_layout = QHBoxLayout()
        print_btn_layout.setSpacing(6)
        
        self.btn_print_selected = QPushButton("선택 출력")
        self.btn_print_selected.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_print_selected.setFixedHeight(styles.s(36))
        self.btn_print_selected.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print_selected.clicked.connect(self.print_selected_barcode)
        
        self.btn_print_all = QPushButton("전체 출력")
        self.btn_print_all.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_print_all.setFixedHeight(styles.s(36))
        self.btn_print_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print_all.clicked.connect(self.print_all_barcodes)
        
        print_btn_layout.addWidget(self.btn_print_selected)
        print_btn_layout.addWidget(self.btn_print_all)
        print_layout.addLayout(print_btn_layout)
        
        btn_panel.addWidget(print_group)
        
        # Delete & Clear buttons
        manage_btn_layout = QHBoxLayout()
        manage_btn_layout.setSpacing(6)
        
        self.btn_delete = QPushButton("선택 삭제")
        self.btn_delete.setStyleSheet(MODERN_BTN_RED)
        self.btn_delete.setFixedHeight(styles.s(36))
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_product)
        
        self.btn_clear = QPushButton("초기화")
        self.btn_clear.setStyleSheet(MODERN_BTN_GRAY)
        self.btn_clear.setFixedHeight(styles.s(36))
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_form)
        
        manage_btn_layout.addWidget(self.btn_delete)
        manage_btn_layout.addWidget(self.btn_clear)
        btn_panel.addLayout(manage_btn_layout)
        
        right_layout.addLayout(btn_panel)

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
            self.table.setItem(row, 3, QTableWidgetItem(str(data.get("stock", 0))))
            promo_text = "1+1" if data.get("promo_type") == 1 else "2+1" if data.get("promo_type") == 2 else "없음"
            self.table.setItem(row, 4, QTableWidgetItem(promo_text))
            self.table.setItem(row, 5, QTableWidgetItem(data["category"]))
            
            is_quick = data.get("is_quick", False)
            quick_text = "★ 등록" if is_quick else ""
            self.table.setItem(row, 6, QTableWidgetItem(quick_text))
            
            # Alignments
            self.table.item(row, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 6).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            
            row += 1
            
        if hasattr(self, 'v_table'):
            self.load_voucher_data()

    def on_table_click(self, row, col):
        self.table.selectRow(row)
        barcode = self.table.item(row, 0).text()
        product = self.product_manager.get_product(barcode)
        
        if product:
            self.current_editing_barcode = barcode # Set current editing
            self.input_barcode.setText(barcode)
            self.input_name.setText(product["name"])
            self.input_price.setText(str(product["price"]))
            self.input_stock.setText(str(product.get("stock", 0)))
            self.combo_promo.setCurrentIndex(product.get("promo_type", 0))
            db_category = product.get("category", "")
            combo_text = db_category
            if db_category == "snack": combo_text = "과자류"
            elif db_category == "drink": combo_text = "음료류"
            elif db_category == "candy": combo_text = "사탕류"
            elif db_category == "jelly": combo_text = "젤리류"
            elif db_category == "water": combo_text = "생수"
            elif db_category == "etc": combo_text = "기타상품"
            self.combo_category.setCurrentText(combo_text)
            self.check_quick.setChecked(product.get("is_quick", False))
            self.selected_image_path = None
            self.image_deleted = False
            self.update_image_preview()

    def filter_products(self):
        search_text = self.input_search.text().strip().lower()
        for row in range(self.table.rowCount()):
            barcode_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            
            barcode = barcode_item.text().lower() if barcode_item else ""
            name = name_item.text().lower() if name_item else ""
            
            if search_text in barcode or search_text in name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def update_barcode_counter(self):
        length = len(self.input_barcode.text())
        self.lbl_barcode_counter.setText(f"({length} / 13)")
        if length == 13:
            self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: #10B981; font-weight: bold;")
        else:
            self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; font-weight: bold;")

    def clear_form(self):
        self.current_editing_barcode = None # Reset
        self.input_barcode.setText("8801000000")
        self.input_barcode.setFocus()
        self.input_barcode.setCursorPosition(10)
        self.input_name.clear()
        self.input_price.clear()
        self.input_stock.setText("100")
        self.combo_promo.setCurrentIndex(0)
        self.combo_category.setCurrentIndex(0)
        self.check_quick.setChecked(False)
        self.table.clearSelection()
        self.update_barcode_counter()
        self.selected_image_path = None
        self.image_deleted = False
        self.update_image_preview()

    def show_alert(self, title, message, type='info'):
        dialog = CustomMessageDialog(title, message, type, self)
        dialog.exec()
        return dialog.result_value

    def save_product(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        price_str = self.input_price.text().strip()
        stock_str = self.input_stock.text().strip()
        promo_type = self.combo_promo.currentIndex()
        category = self.combo_category.currentText().strip()
        is_quick = self.check_quick.isChecked()
        
        if not barcode or not name or not price_str or not stock_str:
            self.show_alert("경고", "모든 필드를 입력해주세요.", 'warning')
            return
        
        # Validation: 13 digits numeric
        if len(barcode) != 13 or not barcode.isdigit():
            self.show_alert("경고", "바코드는 13자리 숫자로 입력해주세요.\n(예: 8801234567890)", 'warning')
            return
            
        try:
            price = int(price_str.replace(",", ""))
            stock = int(stock_str.replace(",", ""))
        except ValueError:
            self.show_alert("경고", "단가와 재고는 숫자여야 합니다.", 'warning')
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
                        self.product_manager.add_product(barcode, name, price, category, stock, promo_type)
                    else:
                        return
                else:
                    # Normal rename (barcode changed to a new unique one)
                    self.product_manager.update_product_key(self.current_editing_barcode, barcode, name, price, category, stock, promo_type)
            else:
                # Barcode didn't change, just update details
                self.product_manager.add_product(barcode, name, price, category, stock, promo_type)
        else:
            # Scenario 2: Adding a completely new product (or duplicate on enter)
            if existing_product:
                msg = f"바코드 [{barcode}]는 이미 등록된 상품입니다.\n기존 상품: {existing_product['name']}\n\n이 상품 정보를 현재 입력하신 정보로 변경하시겠습니까?"
                if self.show_alert("중복 확인", msg, 'question'):
                    self.product_manager.add_product(barcode, name, price, category, stock, promo_type)
                else:
                    return
            else:
                # Normal new addition
                self.product_manager.add_product(barcode, name, price, category, stock, promo_type)

        # Image Processing (Save / Delete / Move)
        if self.image_deleted:
            # Delete existing image
            existing_path = self.get_existing_image_path(barcode)
            if existing_path:
                try:
                    os.remove(existing_path)
                except Exception as e:
                    print(f"Error removing image: {e}")
        elif self.selected_image_path:
            # Delete any existing image for this barcode to avoid extension duplicates (.png vs .jpg)
            for ext in ["png", "jpg", "jpeg", "webp"]:
                p = f"photo/{barcode}.{ext}"
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except:
                        pass
            # Copy new image
            try:
                os.makedirs("photo", exist_ok=True)
                ext = self.selected_image_path.split(".")[-1]
                import shutil
                shutil.copy(self.selected_image_path, f"photo/{barcode}.{ext}")
            except Exception as e:
                print(f"Error copying image: {e}")
        # Handle rename image
        elif self.current_editing_barcode and self.current_editing_barcode != barcode:
            old_img_path = self.get_existing_image_path(self.current_editing_barcode)
            if old_img_path:
                ext = old_img_path.split(".")[-1]
                new_img_path = f"photo/{barcode}.{ext}"
                try:
                    os.makedirs("photo", exist_ok=True)
                    # Clear any existing file at new path
                    if os.path.exists(new_img_path):
                        os.remove(new_img_path)
                    import shutil
                    shutil.move(old_img_path, new_img_path)
                except Exception as e:
                    print(f"Error moving image on rename: {e}")

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
            
            # Delete image
            existing_path = self.get_existing_image_path(barcode)
            if existing_path:
                try:
                    os.remove(existing_path)
                except Exception as e:
                    print(f"Error deleting image on product delete: {e}")
                    
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

    def select_product_image(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "이미지 파일 (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self.selected_image_path = file_path
            self.image_deleted = False
            self.update_image_preview()
            
    def clear_product_image(self):
        self.selected_image_path = None
        self.image_deleted = True
        self.update_image_preview()
        
    def update_image_preview(self):
        barcode = self.input_barcode.text().strip()
        pixmap = QPixmap()
        
        if self.selected_image_path:
            pixmap.load(self.selected_image_path)
        elif self.image_deleted:
            pixmap = QPixmap()
        else:
            existing_path = self.get_existing_image_path(barcode)
            if existing_path:
                pixmap.load(existing_path)
                
        if pixmap.isNull():
            self.lbl_image_preview.setText("이미지 없음")
            self.lbl_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.lbl_image_preview.setPixmap(
                pixmap.scaled(styles.s(120), styles.s(120), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
            
    def get_existing_image_path(self, barcode):
        if not barcode:
            return None
        for ext in ["png", "jpg", "jpeg", "webp"]:
            path = f"photo/{barcode}.{ext}"
            if os.path.exists(path):
                return path
        return None

    def create_voucher_left_panel(self):
        self.v_left_card = QFrame()
        self.v_left_card.setObjectName("v_left_card")
        self.v_left_card.setStyleSheet("""
            QFrame#v_left_card {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        v_left_layout = QVBoxLayout(self.v_left_card)
        v_left_layout.setContentsMargins(20, 20, 20, 20)
        v_left_layout.setSpacing(15)
        
        header_row = QHBoxLayout()
        lbl_title = QLabel("모바일 상품권 목록")
        lbl_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        header_row.addWidget(lbl_title)
        header_row.addStretch()
        
        self.v_input_search = QLineEdit()
        self.v_input_search.setPlaceholderText("🔍 상품권명 또는 바코드 검색...")
        self.v_input_search.setFixedWidth(styles.s(260))
        self.v_input_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(8)}px;
                padding: {styles.s(8)}px {styles.s(12)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(12)};
                color: {styles.TEXT_COLOR};
            }}
            QLineEdit:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
            }}
        """)
        self.v_input_search.textChanged.connect(self.filter_vouchers)
        header_row.addWidget(self.v_input_search)
        v_left_layout.addLayout(header_row)
        
        self.v_table = QTableWidget()
        self.v_table.setColumnCount(4)
        self.v_table.setHorizontalHeaderLabels(["상품권 바코드", "상품권 이름", "교환 대상 상품", "가격"])
        
        SETTINGS_TABLE_STYLE = f"""
            QTableWidget {{
                background-color: white;
                color: {styles.TEXT_COLOR};
                border: none;
                gridline-color: #F3F4F6;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                selection-background-color: #EDE9FE;
                selection-color: {styles.TEXT_COLOR};
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F3F4F6;
                padding-top: {styles.s(8)}px;
                padding-bottom: {styles.s(8)}px;
            }}
            QTableWidget::item:selected {{
                background-color: #EDE9FE;
                color: {styles.TEXT_COLOR};
                font-weight: bold;
            }}
            QHeaderView::section {{
                background-color: #F3F4F6;
                color: #4B5563;
                padding: {styles.s(8)}px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
        """
        self.v_table.setStyleSheet(SETTINGS_TABLE_STYLE)
        self.v_table.verticalScrollBar().setStyleSheet(styles.SCROLLBAR_STYLE)
        
        header = self.v_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumHeight(styles.s(45))
        self.v_table.setColumnWidth(0, styles.s(150)) # Barcode
        self.v_table.setColumnWidth(1, styles.s(200)) # Name
        self.v_table.setColumnWidth(2, styles.s(200)) # Target
        self.v_table.setColumnWidth(3, styles.s(90))  # Price
        
        self.v_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.v_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.v_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.v_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.v_table.verticalHeader().setVisible(False)
        self.v_table.verticalHeader().setDefaultSectionSize(styles.s(45))
        self.v_table.cellClicked.connect(self.on_v_table_click)
        
        v_left_layout.addWidget(self.v_table)

    def create_voucher_right_panel(self):
        MODERN_INPUT_STYLE = f"""
            QLineEdit {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                padding: {styles.s(10)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                color: {styles.TEXT_COLOR};
            }}
            QLineEdit:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
            }}
        """
        
        MODERN_COMBO_STYLE = f"""
            QComboBox {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                padding: {styles.s(10)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                color: black;
            }}
            QComboBox:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
                color: black;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid #D1D5DB;
                selection-background-color: #EDE9FE;
                selection-color: black;
                color: black;
            }}
        """
        
        MODERN_BTN_GREEN = f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(15)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """
        
        MODERN_BTN_RED = f"""
            QPushButton {{
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:pressed {{
                background-color: #B91C1C;
            }}
        """
        
        MODERN_BTN_GRAY = f"""
            QPushButton {{
                background-color: #F3F4F6;
                color: #4B5563;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E5E7EB;
                color: #1F2937;
            }}
            QPushButton:pressed {{
                background-color: #D1D5DB;
            }}
        """
        
        MODERN_BTN_PURPLE = f"""
            QPushButton {{
                background-color: {styles.PRIMARY_PURPLE};
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #6366F1;
            }}
            QPushButton:pressed {{
                background-color: {styles.DARK_PURPLE};
            }}
        """

        self.v_right_card = QFrame()
        self.v_right_card.setObjectName("v_right_card")
        self.v_right_card.setFixedWidth(styles.s(420))
        self.v_right_card.setStyleSheet("""
            QFrame#v_right_card {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        v_right_layout = QVBoxLayout(self.v_right_card)
        v_right_layout.setContentsMargins(20, 20, 20, 20)
        v_right_layout.setSpacing(styles.s(15))
        
        lbl_form = QLabel("상품권 정보 입력")
        lbl_form.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        v_right_layout.addWidget(lbl_form)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; } QWidget { background-color: transparent; }")
        scroll.verticalScrollBar().setStyleSheet(styles.SCROLLBAR_STYLE)
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(styles.s(10))
        form_layout.setContentsMargins(0, 0, 5, 0)
        
        # Voucher Barcode
        barcode_header_layout = QHBoxLayout()
        lbl_barcode = QLabel("상품권 바코드 (13자리)")
        lbl_barcode.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.v_lbl_barcode_counter = QLabel("(0 / 13)")
        self.v_lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; font-weight: bold;")
        barcode_header_layout.addWidget(lbl_barcode)
        barcode_header_layout.addWidget(self.v_lbl_barcode_counter)
        barcode_header_layout.addStretch()
        
        self.v_input_barcode = QLineEdit()
        self.v_input_barcode.setPlaceholderText("상품권 바코드를 스캔하거나 입력하세요")
        self.v_input_barcode.setStyleSheet(MODERN_INPUT_STYLE)
        self.v_input_barcode.textChanged.connect(self.update_v_barcode_counter)
        
        # Target Product Dropdown
        lbl_target = QLabel("교환 대상 상품")
        lbl_target.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-top: {styles.s(5)}px;")
        self.v_combo_target_prod = QComboBox()
        self.v_combo_target_prod.setStyleSheet(MODERN_COMBO_STYLE)
        self.v_combo_target_prod.currentIndexChanged.connect(self.on_target_product_changed)
        
        # Voucher Name
        lbl_name = QLabel("상품권 이름")
        lbl_name.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR}; font-weight: bold;")
        self.v_input_name = QLineEdit()
        self.v_input_name.setStyleSheet(MODERN_INPUT_STYLE)
        self.v_input_name.setPlaceholderText("상품권 명칭 입력")
        
        # Voucher Value (Price)
        lbl_price = QLabel("가치 (금액)")
        lbl_price.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR}; font-weight: bold;")
        self.v_input_price = QLineEdit()
        self.v_input_price.setStyleSheet(MODERN_INPUT_STYLE)
        self.v_input_price.setPlaceholderText("예: 3,000")
        
        form_layout.addLayout(barcode_header_layout)
        form_layout.addWidget(self.v_input_barcode)
        
        form_layout.addWidget(lbl_target)
        form_layout.addWidget(self.v_combo_target_prod)
        
        # Row 3: Name & Price Side-by-Side
        name_price_layout = QHBoxLayout()
        name_price_layout.setSpacing(10)
        
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(lbl_name)
        name_col.addWidget(self.v_input_name)
        
        price_col = QVBoxLayout()
        price_col.setSpacing(4)
        price_col.addWidget(lbl_price)
        price_col.addWidget(self.v_input_price)
        
        name_price_layout.addLayout(name_col)
        name_price_layout.addLayout(price_col)
        
        form_layout.addLayout(name_price_layout)
        form_layout.addStretch()
        
        scroll.setWidget(form_container)
        v_right_layout.addWidget(scroll)
        
        # Action Buttons Panel
        btn_panel = QVBoxLayout()
        btn_panel.setSpacing(styles.s(6))
        
        self.btn_v_add = QPushButton("추가 / 저장")
        self.btn_v_add.setStyleSheet(MODERN_BTN_GREEN)
        self.btn_v_add.setFixedHeight(styles.s(45))
        self.btn_v_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_v_add.clicked.connect(self.save_voucher)
        btn_panel.addWidget(self.btn_v_add)
        
        self.btn_v_print = QPushButton("상품권 이미지 보기")
        self.btn_v_print.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_v_print.setFixedHeight(styles.s(36))
        self.btn_v_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_v_print.clicked.connect(self.print_voucher_image)
        btn_panel.addWidget(self.btn_v_print)
        
        manage_btn_layout = QHBoxLayout()
        manage_btn_layout.setSpacing(6)
        
        self.btn_v_delete = QPushButton("선택 삭제")
        self.btn_v_delete.setStyleSheet(MODERN_BTN_RED)
        self.btn_v_delete.setFixedHeight(styles.s(36))
        self.btn_v_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_v_delete.clicked.connect(self.delete_voucher)
        
        self.btn_v_clear = QPushButton("초기화")
        self.btn_v_clear.setStyleSheet(MODERN_BTN_GRAY)
        self.btn_v_clear.setFixedHeight(styles.s(36))
        self.btn_v_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_v_clear.clicked.connect(self.clear_v_form)
        
        manage_btn_layout.addWidget(self.btn_v_delete)
        manage_btn_layout.addWidget(self.btn_v_clear)
        btn_panel.addLayout(manage_btn_layout)
        
        v_right_layout.addLayout(btn_panel)

    def populate_target_products(self):
        self.v_combo_target_prod.blockSignals(True)
        self.v_combo_target_prod.clear()
        self.v_combo_target_prod.addItem("--- 교환 대상 상품 선택 ---", None)
        
        products = self.product_manager.get_all_products()
        for barcode, p in products.items():
            self.v_combo_target_prod.addItem(f"{p['name']} ({p['price']:,}원)", barcode)
        self.v_combo_target_prod.blockSignals(False)

    def on_target_product_changed(self, index):
        barcode = self.v_combo_target_prod.currentData()
        if barcode:
            product = self.product_manager.get_product(barcode)
            if product:
                self.v_input_name.setText(f"모바일){product['name']}교환권")
                self.v_input_price.setText(str(product['price']))

    def load_voucher_data(self):
        # Populate target product list
        self.populate_target_products()
        
        vouchers = self.product_manager.get_all_vouchers()
        self.v_table.setRowCount(len(vouchers))
        
        row = 0
        for barcode, data in vouchers.items():
            self.v_table.setItem(row, 0, QTableWidgetItem(barcode))
            self.v_table.setItem(row, 1, QTableWidgetItem(data["name"]))
            
            target_barcode = data["product_barcode"]
            target_product = self.product_manager.get_product(target_barcode)
            target_name = target_product["name"] if target_product else f"미기록 ({target_barcode})"
            
            self.v_table.setItem(row, 2, QTableWidgetItem(target_name))
            self.v_table.setItem(row, 3, QTableWidgetItem(f"{data['price']:,}"))
            
            self.v_table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.v_table.item(row, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            row += 1

    def on_v_table_click(self, row, col):
        self.v_table.selectRow(row)
        barcode = self.v_table.item(row, 0).text()
        voucher = self.product_manager.get_voucher(barcode)
        
        if voucher:
            self.current_editing_v_barcode = barcode
            self.v_input_barcode.setText(barcode)
            self.v_input_name.setText(voucher["name"])
            self.v_input_price.setText(str(voucher["price"]))
            
            target_bc = voucher["product_barcode"]
            idx = self.v_combo_target_prod.findData(target_bc)
            if idx >= 0:
                self.v_combo_target_prod.setCurrentIndex(idx)

    def filter_vouchers(self):
        search_text = self.v_input_search.text().strip().lower()
        for row in range(self.v_table.rowCount()):
            barcode_item = self.v_table.item(row, 0)
            name_item = self.v_table.item(row, 1)
            
            barcode = barcode_item.text().lower() if barcode_item else ""
            name = name_item.text().lower() if name_item else ""
            
            if search_text in barcode or search_text in name:
                self.v_table.setRowHidden(row, False)
            else:
                self.v_table.setRowHidden(row, True)

    def update_v_barcode_counter(self):
        length = len(self.v_input_barcode.text())
        self.v_lbl_barcode_counter.setText(f"({length} / 13)")
        if length == 13:
            self.v_lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: #10B981; font-weight: bold;")
        else:
            self.v_lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; font-weight: bold;")

    def clear_v_form(self):
        self.current_editing_v_barcode = None
        self.v_input_barcode.setText("9900000000")
        self.v_input_barcode.setFocus()
        self.v_input_barcode.setCursorPosition(10)
        self.v_combo_target_prod.setCurrentIndex(0)
        self.v_input_name.clear()
        self.v_input_price.clear()
        self.v_table.clearSelection()
        self.update_v_barcode_counter()

    def save_voucher(self):
        barcode = self.v_input_barcode.text().strip()
        name = self.v_input_name.text().strip()
        price_str = self.v_input_price.text().strip()
        target_barcode = self.v_combo_target_prod.currentData()
        
        if not name or not price_str or not target_barcode:
            self.show_alert("경고", "교환 대상 상품과 상품권 이름을 채워주세요.", 'warning')
            return
            
        # Auto generate barcode if empty, default prefix, or invalid
        if not barcode or barcode == "9900000000" or len(barcode) != 13 or not barcode.isdigit():
            import random
            existing_vouchers = self.product_manager.get_all_vouchers()
            while True:
                rand_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
                barcode = f"99{rand_part}"
                if barcode not in existing_vouchers:
                    break
            
        try:
            price = int(price_str.replace(",", ""))
        except ValueError:
            self.show_alert("경고", "금액은 숫자여야 합니다.", 'warning')
            return
            
        # Save
        self.product_manager.add_voucher(barcode, target_barcode, name, price)
        self.load_voucher_data()
        self.clear_v_form()
        self.show_alert("완료", f"상품권 정보가 저장되었습니다.\n바코드: {barcode}", 'info')

    def delete_voucher(self):
        current_row = self.v_table.currentRow()
        if current_row < 0:
            self.show_alert("경고", "삭제할 상품권을 선택해주세요.", 'warning')
            return
            
        barcode = self.v_table.item(current_row, 0).text()
        if self.show_alert("삭제 확인", f"상품권 [{barcode}]\n삭제하시겠습니까?", 'question'):
            self.product_manager.delete_voucher(barcode)
            self.load_voucher_data()
            self.clear_v_form()

    def print_voucher_image(self):
        import os
        import base64
        
        # 1. Determine which voucher to display
        barcode = self.v_input_barcode.text().strip()
        if not barcode or barcode == "9900000000":
            # If not typing, check if one is selected in the table
            current_row = self.v_table.currentRow()
            if current_row >= 0:
                barcode = self.v_table.item(current_row, 0).text()
            else:
                self.show_alert("경고", "이미지를 출력할 상품권을 선택하거나 정보를 입력해주세요.", 'warning')
                return
                
        # Get voucher details
        voucher = self.product_manager.get_voucher(barcode)
        if not voucher:
            self.show_alert("경고", "저장된 상품권 정보를 찾을 수 없습니다.\n먼저 상품권을 저장해주세요.", 'warning')
            return
            
        voucher_name = voucher["name"]
        voucher_price = voucher["price"]
        target_barcode = voucher["product_barcode"]
        
        # Get target product details
        target_product = self.product_manager.get_product(target_barcode)
        if target_product:
            product_name = target_product["name"]
            product_category = target_product.get("category", "etc")
        else:
            product_name = voucher_name
            product_category = "etc"
            
        # 2. Get product image (if exists) or fallback emoji
        image_html = ""
        import sys
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        image_path = None
        for ext in ["png", "jpg", "jpeg", "webp"]:
            p = os.path.join(os.path.abspath("."), "photo", f"{target_barcode}.{ext}")
            if os.path.exists(p):
                image_path = p
                break
                
        if not image_path:
            for ext in ["png", "jpg", "jpeg"]:
                p = os.path.join(base_path, "assets", f"{target_barcode}.{ext}")
                if os.path.exists(p):
                    image_path = p
                    break
                
        if os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    img_data = f.read()
                img_b64 = base64.b64encode(img_data).decode("utf-8")
                ext = "jpg" if image_path.endswith(".jpg") else "png"
                img_src = f"data:image/{ext};base64,{img_b64}"
                image_html = f'<img src="{img_src}" height="110" style="display: block;" />'
            except Exception as e:
                image_html = ""
                
        if not image_html:
            # Fallback category emojis
            CATEGORY_EMOJIS = {
                "snack": "🍪",
                "drink": "🥤",
                "candy": "🍭",
                "jelly": "🍬",
                "water": "🥛",
                "etc": "🎁",
                "핫바": "🍢",
                "식사류": "🍱",
                "면류": "🍜"
            }
            emoji = CATEGORY_EMOJIS.get(product_category, "🎁")
            image_html = f'<div style="font-size: 64pt; line-height: 120px; text-align: center;">{emoji}</div>'
            
        # 3. Generate barcode image base64
        barcode_img_src = self.receipt_manager.generate_barcode_base64(barcode)
        
        # Format barcode text with spaces (e.g. 9900 0123 4567 8)
        spaced_barcode = " ".join([barcode[i:i+4] for i in range(0, len(barcode), 4)])
        
        # 4. Construct coupon HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Malgun Gothic', 'Dotum', sans-serif;
                    background-color: #FAFAFA;
                    margin: 0;
                    padding: 10px;
                }}
                .card-container {{
                    width: 320px;
                    background-color: #ffffff;
                    border: 1px solid #E0E0E0;
                    border-radius: 12px;
                    margin: 0 auto;
                }}
                .card-header {{
                    background: #FF7A50;
                    padding: 25px 0;
                    border-top-left-radius: 11px;
                    border-top-right-radius: 11px;
                    text-align: center;
                }}
                .image-box {{
                    width: 140px;
                    height: 140px;
                    background-color: #ffffff;
                    border-radius: 12px;
                    margin: 0 auto;
                }}
                .card-body {{
                    padding: 20px;
                    text-align: center;
                    background-color: #FAFAFA;
                    border-bottom-left-radius: 11px;
                    border-bottom-right-radius: 11px;
                }}
                .brand-name {{
                    font-size: 11pt;
                    color: #888888;
                    font-weight: bold;
                    letter-spacing: 1.5px;
                    margin-bottom: 5px;
                }}
                .product-name {{
                    font-size: 15pt;
                    font-weight: bold;
                    color: #222222;
                    margin-bottom: 15px;
                    line-height: 1.3;
                }}
                .pay-banner {{
                    width: 85%;
                    border-top: 1px solid #E0E0E0;
                    border-bottom: 1px solid #E0E0E0;
                    margin: 10px auto 20px auto;
                    padding: 8px 0;
                    font-size: 9.5pt;
                    color: #757575;
                    font-weight: 500;
                }}
                .pay-dot {{
                    color: #37474F;
                    font-weight: bold;
                }}
                .barcode-box {{
                    background-color: #ffffff;
                    border: 1px solid #EBEBEB;
                    border-radius: 6px;
                    padding: 12px 10px;
                    display: inline-block;
                    margin-bottom: 10px;
                }}
                .barcode-number-row {{
                    margin-top: 5px;
                }}
                .barcode-num {{
                    font-size: 13pt;
                    font-weight: bold;
                    color: #333333;
                    letter-spacing: 1.5px;
                    font-family: 'Courier New', Courier, monospace;
                    vertical-align: middle;
                }}
                .copy-lbl {{
                    font-size: 8pt;
                    color: #9E9E9E;
                    border: 1px solid #D0D0D0;
                    border-radius: 3px;
                    padding: 2px 5px;
                    margin-left: 6px;
                    background-color: #FFFFFF;
                    vertical-align: middle;
                    font-weight: normal;
                }}
            </style>
        </head>
        <body>
            <div class="card-container">
                <div class="card-header">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" style="width: 140px; height: 140px; background-color: #ffffff; border-radius: 12px;">
                        <tr>
                            <td align="center" valign="middle" style="height: 140px; width: 140px;">
                                {image_html}
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="card-body">
                    <div class="brand-name">CU</div>
                    <div class="product-name">{product_name}</div>
                    
                    <div class="pay-banner">
                        <span class="pay-dot">●</span> pay 카카오페이로 추가결제
                    </div>
                    
                    <div class="barcode-box">
                        <img src="{barcode_img_src}" width="220" height="60" />
                    </div>
                    
                    <div class="barcode-number-row">
                        <span class="barcode-num">{spaced_barcode}</span>
                        <span class="copy-lbl">번호복사</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 5. Open dialog using ReceiptPreviewDialog with a custom title
        from ui_components import ReceiptPreviewDialog
        dialog = ReceiptPreviewDialog(html, self, title="모바일 상품권 확인", height=780)
        dialog.exec()
