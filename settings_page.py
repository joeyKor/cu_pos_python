from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QPushButton, 
                             QHeaderView, QWidget, QComboBox, QAbstractItemView, QFrame, QScrollArea, QCheckBox, QTabWidget, QApplication, QGridLayout, QGraphicsDropShadowEffect, QRadioButton)
import os
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QColor
import styles
from product_manager import ProductManager, CATEGORIES
from ui_components import CustomMessageDialog
from cash_drawer_manager import cash_drawer

class ProductRegistrationDialog(QDialog):
    """
    신규 상품 등록 및 상품 정보 수정을 위한 모던 커스텀 팝업 다이얼로그
    """
    def __init__(self, product_manager, editing_barcode=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(680), styles.s(740))
        
        self.product_manager = product_manager
        self.editing_barcode = editing_barcode # None for new, barcode string for edit
        self.selected_image_path = None
        self.image_deleted = False
        self.created_barcode = None
        self.is_manual_barcode = False
        
        self.init_ui()
        
        if self.editing_barcode:
            self.load_product_data()
        else:
            self.generate_new_barcode()

    def init_ui(self):
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
                padding: {styles.s(8)}px;
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

        # Container Frame
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(660), styles.s(720))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(16)}px;
                border: 1px solid #E5E7EB;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 90))
        shadow.setOffset(0, 6)
        self.container.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Header Bar
        header_bar = QFrame()
        header_bar.setFixedHeight(styles.s(58))
        header_bar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {styles.PRIMARY_PURPLE}, stop:1 #4F46E5);
                border-top-left-radius: {styles.s(16)}px;
                border-top-right-radius: {styles.s(16)}px;
                border-bottom: none;
            }}
        """)
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(20, 0, 15, 0)
        
        title_text = "✏️ 상품 정보 수정" if self.editing_barcode else "✨ 새 상품 등록"
        self.lbl_title = QLabel(title_text)
        self.lbl_title.setStyleSheet(f"font-size: {styles.fs(16)}; font-weight: bold; color: white; border: none; background: transparent; font-family: '{styles.FONT_FAMILY}';")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(styles.s(32), styles.s(32))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 15pt;
                font-weight: bold;
                border: none;
                background: transparent;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        btn_close.clicked.connect(self.reject)
        header_layout.addWidget(btn_close)
        
        main_layout.addWidget(header_bar)
        
        # 2. Form Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(styles.s(24), styles.s(20), styles.s(24), styles.s(20))
        content_layout.setSpacing(styles.s(14))
        
        grid = QGridLayout()
        grid.setSpacing(styles.s(10))
        grid.setContentsMargins(0, 0, 0, 0)
        
        # 1) Barcode & Buttons
        barcode_hdr = QHBoxLayout()
        barcode_hdr.setSpacing(8)
        self.lbl_barcode_title = QLabel("바코드")
        self.lbl_barcode_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        self.lbl_barcode_counter = QLabel("(13 / 13)")
        self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: #10B981; font-weight: bold; border: none; background: transparent;")
        barcode_hdr.addWidget(self.lbl_barcode_title)
        barcode_hdr.addWidget(self.lbl_barcode_counter)
        barcode_hdr.addStretch()
        
        self.btn_manual_toggle = QPushButton("✏️ 직접 입력")
        self.btn_manual_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_manual_toggle.setFixedHeight(styles.s(30))
        self.btn_manual_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: #FEF3C7;
                color: #B45309;
                border: 1px solid #FCD34D;
                border-radius: {styles.s(4)}px;
                padding: 0px {styles.s(12)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11.5)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FDE68A;
            }}
        """)
        self.btn_manual_toggle.clicked.connect(self.toggle_manual_barcode)
        barcode_hdr.addWidget(self.btn_manual_toggle)
        
        self.btn_regen_bc = QPushButton("🔄 자동생성")
        self.btn_regen_bc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_regen_bc.setFixedHeight(styles.s(30))
        self.btn_regen_bc.setStyleSheet(f"""
            QPushButton {{
                background-color: #EEF2FF;
                color: {styles.PRIMARY_PURPLE};
                border: 1px solid #C7D2FE;
                border-radius: {styles.s(4)}px;
                padding: 0px {styles.s(12)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11.5)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E0E7FF;
            }}
        """)
        self.btn_regen_bc.clicked.connect(self.generate_new_barcode)
        barcode_hdr.addWidget(self.btn_regen_bc)
        
        self.check_quick = QCheckBox("단축 등록 (0/5)")
        self.check_quick.setStyleSheet(MODERN_CHECKBOX_STYLE)
        self.check_quick.clicked.connect(self.on_check_quick_clicked)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setReadOnly(True)
        self.input_barcode.setStyleSheet(MODERN_INPUT_STYLE.replace("#F9FAFB", "#F3F4F6"))
        self.input_barcode.textChanged.connect(self.update_barcode_counter)
        
        grid.addLayout(barcode_hdr, 0, 0)
        grid.addWidget(self.check_quick, 0, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.input_barcode, 1, 0, 1, 2)
        
        # 2) Product Name
        lbl_name = QLabel("상품명 *")
        lbl_name.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("상품명을 입력하세요")
        self.input_name.setStyleSheet(MODERN_INPUT_STYLE)
        grid.addWidget(lbl_name, 2, 0, 1, 2)
        grid.addWidget(self.input_name, 3, 0, 1, 2)
        
        # 3) Price & Stock
        lbl_price = QLabel("단가 (원) *")
        lbl_price.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("예: 2,000")
        self.input_price.setStyleSheet(MODERN_INPUT_STYLE)
        
        lbl_stock = QLabel("초기 재고 수량 *")
        lbl_stock.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        self.input_stock = QLineEdit()
        self.input_stock.setText("10")
        self.input_stock.setStyleSheet(MODERN_INPUT_STYLE)
        
        grid.addWidget(lbl_price, 4, 0)
        grid.addWidget(self.input_price, 5, 0)
        grid.addWidget(lbl_stock, 4, 1)
        grid.addWidget(self.input_stock, 5, 1)
        
        # 4) Promo & Category
        lbl_promo = QLabel("행사 종류")
        lbl_promo.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        self.combo_promo = QComboBox()
        self.combo_promo.addItems(["없음", "1+1", "2+1"])
        self.combo_promo.setStyleSheet(MODERN_COMBO_STYLE)
        
        lbl_cat = QLabel("분류")
        lbl_cat.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        self.combo_category = QComboBox()
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.setEditable(True)
        self.combo_category.setStyleSheet(MODERN_COMBO_STYLE)
        
        grid.addWidget(lbl_promo, 6, 0)
        grid.addWidget(self.combo_promo, 7, 0)
        grid.addWidget(lbl_cat, 6, 1)
        grid.addWidget(self.combo_category, 7, 1)
        
        content_layout.addLayout(grid)
        
        # 5) Image Selection
        lbl_img = QLabel("상품 이미지")
        lbl_img.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-top: 4px; border: none; background: transparent;")
        content_layout.addWidget(lbl_img)
        
        img_row = QHBoxLayout()
        img_row.setSpacing(12)
        
        self.lbl_image_preview = QLabel("이미지 없음")
        self.lbl_image_preview.setFixedSize(styles.s(75), styles.s(75))
        self.lbl_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image_preview.setStyleSheet("""
            QLabel {
                border: 1px dashed #CBD5E1;
                border-radius: 8px;
                background-color: #F8FAFC;
                color: #94A3B8;
                font-weight: bold;
                font-size: 9pt;
            }
        """)
        
        img_btn_layout = QVBoxLayout()
        img_btn_layout.setSpacing(6)
        
        btn_find_img = QPushButton("📁 이미지 찾기")
        btn_find_img.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_find_img.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.PRIMARY_PURPLE};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: {styles.fs(12)};
                padding: 6px 14px;
            }}
            QPushButton:hover {{
                background-color: #6366F1;
            }}
        """)
        btn_find_img.clicked.connect(self.select_image)
        
        btn_del_img = QPushButton("이미지 삭제")
        btn_del_img.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del_img.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #4B5563;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
            }
        """)
        btn_del_img.clicked.connect(self.clear_image)
        
        img_btn_layout.addWidget(btn_find_img)
        img_btn_layout.addWidget(btn_del_img)
        
        img_row.addWidget(self.lbl_image_preview)
        img_row.addLayout(img_btn_layout)
        img_row.addStretch()
        content_layout.addLayout(img_row)
        
        content_layout.addStretch()
        
        # Bottom Buttons
        btn_action_layout = QHBoxLayout()
        btn_action_layout.setSpacing(10)
        
        save_btn_text = "💾 변경사항 저장" if self.editing_barcode else "✨ 상품 등록 완료"
        self.btn_save = QPushButton(save_btn_text)
        self.btn_save.setFixedHeight(styles.s(46))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {styles.fs(14)};
                font-weight: bold;
                font-family: '{styles.FONT_FAMILY}';
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)
        self.btn_save.clicked.connect(self.save_new_product)
        
        btn_cancel = QPushButton("취소")
        btn_cancel.setFixedHeight(styles.s(46))
        btn_cancel.setFixedWidth(styles.s(100))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #4B5563;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_action_layout.addWidget(btn_cancel)
        btn_action_layout.addWidget(self.btn_save, stretch=1)
        content_layout.addLayout(btn_action_layout)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # Set focus to product name initially
        self.input_name.setFocus()
        self.update_quick_checkbox_text()

    def update_quick_checkbox_text(self):
        count = self.product_manager.get_quick_items_count()
        self.check_quick.setText(f"단축 등록 ({count}/5)")

    def on_check_quick_clicked(self, checked):
        if checked:
            count = self.product_manager.get_quick_items_count()
            was_quick = False
            if self.editing_barcode:
                p = self.product_manager.get_product(self.editing_barcode)
                if p and p.get("is_quick", False):
                    was_quick = True
            if not was_quick and count >= 5:
                self.check_quick.setChecked(False)
                self.show_alert("알림", "단축 등록은 메인 화면에 표시되는 최대 5개까지만 등록할 수 있습니다.\n기존 등록된 단축 상품(★)을 먼저 해제해 주세요.", 'warning')
        self.update_quick_checkbox_text()

    def toggle_manual_barcode(self):
        self.is_manual_barcode = not self.is_manual_barcode
        if self.is_manual_barcode:
            self.input_barcode.setReadOnly(False)
            self.input_barcode.setStyleSheet(f"""
                QLineEdit {{
                    background-color: white;
                    border: 2px solid {styles.PRIMARY_PURPLE};
                    border-radius: {styles.s(6)}px;
                    padding: {styles.s(10)}px;
                    font-family: '{styles.FONT_FAMILY}';
                    font-size: {styles.fs(13)};
                    color: {styles.TEXT_COLOR};
                }}
            """)
            self.lbl_barcode_title.setText("바코드 (직접 입력)")
            self.btn_manual_toggle.setText("🔒 자동 생성 모드")
            self.btn_manual_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #E0E7FF;
                    color: #4338CA;
                    border: 1px solid #C7D2FE;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #C7D2FE;
                }
            """)
            self.input_barcode.setFocus()
            self.input_barcode.selectAll()
        else:
            self.input_barcode.setReadOnly(True)
            self.input_barcode.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #F3F4F6;
                    border: 1px solid #D1D5DB;
                    border-radius: {styles.s(6)}px;
                    padding: {styles.s(10)}px;
                    font-family: '{styles.FONT_FAMILY}';
                    font-size: {styles.fs(13)};
                    color: {styles.TEXT_COLOR};
                }}
            """)
            self.lbl_barcode_title.setText("바코드 (자동 생성)")
            self.btn_manual_toggle.setText("✏️ 직접 입력")
            self.btn_manual_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #FEF3C7;
                    color: #B45309;
                    border: 1px solid #FCD34D;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FDE68A;
                }
            """)
            if not self.input_barcode.text().strip():
                self.generate_new_barcode()

    def update_barcode_counter(self):
        length = len(self.input_barcode.text().strip())
        self.lbl_barcode_counter.setText(f"({length} / 13)")
        if length == 13:
            self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: #10B981; font-weight: bold; border: none; background: transparent;")
        else:
            self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; font-weight: bold; border: none; background: transparent;")

    def generate_new_barcode(self):
        import random
        existing_products = self.product_manager.get_all_products()
        while True:
            rand_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
            barcode = f"88{rand_part}"
            if barcode not in existing_products:
                break
        self.input_barcode.setText(barcode)
        if self.is_manual_barcode:
            self.toggle_manual_barcode()

    def load_product_data(self):
        product = self.product_manager.get_product(self.editing_barcode)
        if not product:
            return
            
        self.input_barcode.setText(self.editing_barcode)
        self.input_name.setText(product.get("name", ""))
        self.input_price.setText(str(product.get("price", "")))
        self.input_stock.setText(str(product.get("stock", 10)))
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
        self.update_quick_checkbox_text()
        
        # Load image preview
        existing_path = self.get_existing_image_path(self.editing_barcode)
        if existing_path:
            pixmap = QPixmap(existing_path)
            if not pixmap.isNull():
                self.lbl_image_preview.setPixmap(
                    pixmap.scaled(styles.s(75), styles.s(75), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )

    def get_existing_image_path(self, barcode):
        if not barcode:
            return None
        for ext in ["png", "jpg", "jpeg", "webp"]:
            path = f"photo/{barcode}.{ext}"
            if os.path.exists(path):
                return path
        return None

    def select_image(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "이미지 파일 (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self.selected_image_path = file_path
            self.image_deleted = False
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.lbl_image_preview.setPixmap(
                    pixmap.scaled(styles.s(75), styles.s(75), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )

    def clear_image(self):
        self.selected_image_path = None
        self.image_deleted = True
        self.lbl_image_preview.clear()
        self.lbl_image_preview.setText("이미지 없음")

    def show_alert(self, title, message, type='info'):
        dialog = CustomMessageDialog(title, message, type, self)
        dialog.exec()
        return dialog.result_value

    def save_new_product(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        price_str = self.input_price.text().strip()
        stock_str = self.input_stock.text().strip()
        promo_type = self.combo_promo.currentIndex()
        category = self.combo_category.currentText().strip()
        is_quick = self.check_quick.isChecked()

        if not name:
            self.show_alert("경고", "상품명을 입력해주세요.", 'warning')
            self.input_name.setFocus()
            return
            
        if is_quick:
            was_quick = False
            if self.editing_barcode:
                p = self.product_manager.get_product(self.editing_barcode)
                if p and p.get("is_quick", False):
                    was_quick = True
            if not was_quick and self.product_manager.get_quick_items_count() >= 5:
                self.show_alert("경고", "단축 상품은 메인 화면에 표시되는 최대 5개까지만 등록할 수 있습니다.\n기존 등록된 상품(★)을 먼저 해제해 주세요.", 'warning')
                return
            
        if not price_str:
            self.show_alert("경고", "단가를 입력해주세요.", 'warning')
            self.input_price.setFocus()
            return

        if not stock_str:
            self.show_alert("경고", "재고 수량을 입력해주세요.", 'warning')
            self.input_stock.setFocus()
            return

        try:
            price = int(price_str.replace(",", ""))
            stock = int(stock_str.replace(",", ""))
        except ValueError:
            self.show_alert("경고", "단가와 재고는 숫자여야 합니다.", 'warning')
            return

        if not barcode or len(barcode) != 13 or not barcode.isdigit():
            self.show_alert("경고", "올바른 바코드가 아닙니다.", 'warning')
            return

        existing_product = self.product_manager.get_product(barcode)
        
        if self.editing_barcode:
            # Editing existing item
            if self.editing_barcode != barcode:
                # Barcode changed
                if existing_product:
                    msg = f"바코드 [{barcode}]는 이미 등록된 상품입니다.\n기존 상품: {existing_product['name']}\n\n이 상품 정보를 현재 입력하신 정보로 변경하시겠습니까?"
                    if self.show_alert("중복 확인", msg, 'question'):
                        self.product_manager.delete_product(self.editing_barcode)
                        self.product_manager.add_product(barcode, name, price, category, stock, promo_type, is_quick)
                    else:
                        return
                else:
                    self.product_manager.update_product_key(self.editing_barcode, barcode, name, price, category, stock, promo_type, is_quick)
            else:
                self.product_manager.add_product(barcode, name, price, category, stock, promo_type, is_quick)
        else:
            # Adding new item
            if existing_product:
                msg = f"바코드 [{barcode}]는 이미 등록된 상품입니다.\n기존 상품: {existing_product['name']}\n\n이 상품 정보를 덮어쓰시겠습니까?"
                if not self.show_alert("중복 확인", msg, 'question'):
                    return
            self.product_manager.add_product(barcode, name, price, category, stock, promo_type, is_quick)

        # Image processing
        if self.image_deleted:
            existing_p = self.get_existing_image_path(barcode)
            if existing_p:
                try:
                    os.remove(existing_p)
                except Exception as e:
                    print(f"Error removing image: {e}")
        elif self.selected_image_path:
            for ext in ["png", "jpg", "jpeg", "webp"]:
                p = f"photo/{barcode}.{ext}"
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except:
                        pass
            try:
                os.makedirs("photo", exist_ok=True)
                ext = self.selected_image_path.split(".")[-1]
                import shutil
                shutil.copy(self.selected_image_path, f"photo/{barcode}.{ext}")
            except Exception as e:
                print(f"Error copying image: {e}")
        elif self.editing_barcode and self.editing_barcode != barcode:
            old_img = self.get_existing_image_path(self.editing_barcode)
            if old_img:
                ext = old_img.split(".")[-1]
                new_img = f"photo/{barcode}.{ext}"
                try:
                    os.makedirs("photo", exist_ok=True)
                    if os.path.exists(new_img):
                        os.remove(new_img)
                    import shutil
                    shutil.move(old_img, new_img)
                except Exception as e:
                    print(f"Error moving image: {e}")

        self.created_barcode = barcode
        success_msg = f"상품 '{name}' 정보가\n성공적으로 수정되었습니다!" if self.editing_barcode else f"신규 상품 '{name}'이(가)\n성공적으로 등록되었습니다!"
        self.show_alert("성공", success_msg, 'info')
        self.accept()


class SettingsPage(QWidget):
    backRequested = pyqtSignal()
    drawerTestResult = pyqtSignal(bool, str)

    def __init__(self, product_manager, receipt_manager, parent=None):
        super().__init__(parent)
        self.product_manager: ProductManager = product_manager
        self.receipt_manager = receipt_manager
        self.drawerTestResult.connect(self.on_drawer_test_finished)
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
        self.product_tab_layout.setSpacing(15)
        
        self.create_left_panel()
        self.create_product_action_panel()
        
        self.product_tab_layout.addWidget(self.left_card, stretch=1)
        self.product_tab_layout.addWidget(self.product_action_card)
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
        
        # Tab 3: System Settings
        self.system_tab = QWidget()
        self.system_tab_layout = QVBoxLayout(self.system_tab)
        self.system_tab_layout.setContentsMargins(30, 30, 30, 30)
        self.system_tab_layout.setSpacing(20)
        
        # Screen Mode Group
        mode_card = QFrame()
        mode_card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }}
        """)
        card_lyt = QVBoxLayout(mode_card)
        card_lyt.setContentsMargins(25, 25, 25, 25)
        card_lyt.setSpacing(15)
        
        lbl_mode_title = QLabel("화면 모드 설정")
        lbl_mode_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1E293B; border: none;")
        card_lyt.addWidget(lbl_mode_title)
        
        lbl_mode_desc = QLabel("POS 화면 표시 모드를 선택할 수 있습니다. 전체화면 모드 또는 창 화면 모드로 전환합니다.")
        lbl_mode_desc.setStyleSheet("font-size: 11pt; color: #64748B; border: none;")
        card_lyt.addWidget(lbl_mode_desc)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)
        
        self.btn_fullscreen = QPushButton("🖥️ 전체화면 모드")
        self.btn_fullscreen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fullscreen.setFixedHeight(50)
        self.btn_fullscreen.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.PRIMARY_PURPLE};
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #6D28D9; }}
        """)
        self.btn_fullscreen.clicked.connect(self.set_fullscreen)
        
        self.btn_windowed = QPushButton("🪟 창 화면 모드")
        self.btn_windowed.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_windowed.setFixedHeight(50)
        self.btn_windowed.setStyleSheet(f"""
            QPushButton {{
                background-color: #F1F5F9;
                color: #334155;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 8px;
                border: 1px solid #CBD5E1;
            }}
            QPushButton:hover {{ background-color: #E2E8F0; }}
        """)
        self.btn_windowed.clicked.connect(self.set_windowed)
        
        btn_row.addWidget(self.btn_fullscreen, stretch=1)
        btn_row.addWidget(self.btn_windowed, stretch=1)
        card_lyt.addLayout(btn_row)
        
        self.system_tab_layout.addWidget(mode_card)
        
        # Cash Drawer Settings Group
        self.drawer_card = self.create_drawer_settings_card()
        self.system_tab_layout.addWidget(self.drawer_card)
        
        self.system_tab_layout.addStretch()
        
        self.tab_widget.addTab(self.system_tab, "시스템 설정")
        
        self.content_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.content_widget, stretch=1)
        
        # 3. Bottom Navigation
        self.create_bottom_nav()
        
        # Load Data
        self.load_data()
        self.clear_form()
        self.load_voucher_data()
        self.clear_v_form()
        self.set_mode("products")

    def create_header(self):
        header_frame = QFrame()
        header_frame.setMinimumHeight(60)
        header_frame.setStyleSheet("background-color: white; border-bottom: 2px solid #DEE2E6;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        self.lbl_header_title = QLabel("상품 관리")
        self.lbl_header_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(self.lbl_header_title)
        
        header_layout.addStretch()
        
        self.lbl_breadcrumb = QLabel("홈 > 상품관리")
        self.lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #777;")
        header_layout.addWidget(self.lbl_breadcrumb)
        self.main_layout.addWidget(header_frame)

    def set_mode(self, mode="products"):
        self.mode = mode
        if mode == "system":
            self.lbl_header_title.setText("시스템 설정")
            self.lbl_breadcrumb.setText("설정 > 시스템 설정")
            self.tab_widget.setTabVisible(0, False)
            self.tab_widget.setTabVisible(1, False)
            self.tab_widget.setTabVisible(2, True)
            self.tab_widget.setCurrentWidget(self.system_tab)
        else: # "products"
            self.lbl_header_title.setText("상품 관리")
            self.lbl_breadcrumb.setText("홈 > 상품관리")
            self.tab_widget.setTabVisible(0, True)
            self.tab_widget.setTabVisible(1, True)
            self.tab_widget.setTabVisible(2, False)
            self.tab_widget.setCurrentWidget(self.product_tab)

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
        header_row.setSpacing(10)
        
        lbl_title = QLabel("상품 목록")
        lbl_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        header_row.addWidget(lbl_title)
        
        header_row.addStretch()
        
        # Modern Search Input
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔍 상품명 또는 바코드 검색...")
        self.input_search.setFixedWidth(styles.s(280))
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
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(styles.s(45))
        self.table.cellClicked.connect(self.on_table_click)
        self.table.cellDoubleClicked.connect(self.on_table_double_click)
        
        left_layout.addWidget(self.table)

    def create_product_action_panel(self):
        # Right action card frame with vertical buttons
        self.product_action_card = QFrame()
        self.product_action_card.setObjectName("product_action_card")
        self.product_action_card.setFixedWidth(styles.s(260))
        self.product_action_card.setStyleSheet("""
            QFrame#product_action_card {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        action_layout = QVBoxLayout(self.product_action_card)
        action_layout.setContentsMargins(styles.s(12), styles.s(18), styles.s(12), styles.s(18))
        action_layout.setSpacing(styles.s(10))
        
        lbl_action_title = QLabel("상품 관리 메뉴")
        lbl_action_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        lbl_action_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_layout.addWidget(lbl_action_title)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("border: none; background-color: #E5E7EB; height: 1px;")
        action_layout.addWidget(line)
        
        # 1. New Product Button
        self.btn_open_add_dialog = QPushButton("✨ 새 상품 추가")
        self.btn_open_add_dialog.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_add_dialog.setFixedHeight(styles.s(44))
        self.btn_open_add_dialog.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.PRIMARY_PURPLE};
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(4)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #6366F1; }}
            QPushButton:pressed {{ background-color: {styles.DARK_PURPLE}; }}
        """)
        self.btn_open_add_dialog.clicked.connect(self.open_new_product_dialog)
        action_layout.addWidget(self.btn_open_add_dialog)
        
        # Row 1: Edit & Delete Selected Buttons
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(styles.s(8))
        
        self.btn_edit_selected = QPushButton("✏️ 선택 수정")
        self.btn_edit_selected.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_selected.setFixedHeight(styles.s(42))
        self.btn_edit_selected.setStyleSheet(f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(2)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11.5)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #059669; }}
            QPushButton:pressed {{ background-color: #047857; }}
        """)
        self.btn_edit_selected.clicked.connect(self.edit_selected_product)
        row1_layout.addWidget(self.btn_edit_selected)
        
        self.btn_delete_selected = QPushButton("🗑️ 선택 삭제")
        self.btn_delete_selected.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete_selected.setFixedHeight(styles.s(42))
        self.btn_delete_selected.setStyleSheet(f"""
            QPushButton {{
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(2)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11.5)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #DC2626; }}
            QPushButton:pressed {{ background-color: #B91C1C; }}
        """)
        self.btn_delete_selected.clicked.connect(self.delete_selected_product)
        row1_layout.addWidget(self.btn_delete_selected)
        action_layout.addLayout(row1_layout)
        
        # Row 2: Print Barcodes (Selected / All)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(styles.s(8))
        
        self.btn_print_barcode = QPushButton("🖨️ 바코드 선택")
        self.btn_print_barcode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print_barcode.setFixedHeight(styles.s(40))
        self.btn_print_barcode.setStyleSheet(f"""
            QPushButton {{
                background-color: #F1F5F9;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(2)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #E2E8F0; color: #0F172A; }}
            QPushButton:pressed {{ background-color: #CBD5E1; }}
        """)
        self.btn_print_barcode.clicked.connect(self.print_selected_barcode)
        row2_layout.addWidget(self.btn_print_barcode)
        
        self.btn_print_all = QPushButton("📋 바코드 전체")
        self.btn_print_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print_all.setFixedHeight(styles.s(40))
        self.btn_print_all.setStyleSheet(f"""
            QPushButton {{
                background-color: #F1F5F9;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(2)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #E2E8F0; color: #0F172A; }}
            QPushButton:pressed {{ background-color: #CBD5E1; }}
        """)
        self.btn_print_all.clicked.connect(self.print_all_barcodes)
        row2_layout.addWidget(self.btn_print_all)
        action_layout.addLayout(row2_layout)
        
        # Section Divider for POP Shelf Labels
        line_pop = QFrame()
        line_pop.setFrameShape(QFrame.Shape.HLine)
        line_pop.setStyleSheet("border: none; background-color: #E2E8F0; height: 1px; margin: 4px 0;")
        action_layout.addWidget(line_pop)
        
        lbl_pop_title = QLabel("🏷️ 매장 진열대 가격표 (POP)")
        lbl_pop_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; font-weight: bold; color: #475569; background: transparent;")
        lbl_pop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_layout.addWidget(lbl_pop_title)
        
        # Row 3: POP Selected & Promo
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(styles.s(8))
        
        self.btn_pop_selected = QPushButton("🏷️ 선택 POP")
        self.btn_pop_selected.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pop_selected.setFixedHeight(styles.s(42))
        self.btn_pop_selected.setStyleSheet(f"""
            QPushButton {{
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(2)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11.5)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
            QPushButton:pressed {{ background-color: #1E40AF; }}
        """)
        self.btn_pop_selected.clicked.connect(self.print_selected_pop)
        row3_layout.addWidget(self.btn_pop_selected)
        
        self.btn_pop_promo = QPushButton("🔥 행사 POP")
        self.btn_pop_promo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pop_promo.setFixedHeight(styles.s(42))
        self.btn_pop_promo.setStyleSheet(f"""
            QPushButton {{
                background-color: #EA580C;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(2)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11.5)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #C2410C; }}
            QPushButton:pressed {{ background-color: #9A3412; }}
        """)
        self.btn_pop_promo.clicked.connect(self.print_promo_pop)
        row3_layout.addWidget(self.btn_pop_promo)
        action_layout.addLayout(row3_layout)
        
        # Row 4: POP All
        self.btn_pop_all = QPushButton("📋 전체 진열대 POP 출력")
        self.btn_pop_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pop_all.setFixedHeight(styles.s(42))
        self.btn_pop_all.setStyleSheet(f"""
            QPushButton {{
                background-color: #0D9488;
                color: white;
                border: none;
                border-radius: {styles.s(8)}px;
                padding: 0px {styles.s(4)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(12)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
            QPushButton:pressed {{ background-color: #115E59; }}
        """)
        self.btn_pop_all.clicked.connect(self.print_all_pop)
        action_layout.addWidget(self.btn_pop_all)
        
        action_layout.addStretch()

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
        
        # Title of the form & [새 상품 추가] Button
        form_header_layout = QHBoxLayout()
        form_header_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_form = QLabel("상품 정보 입력")
        lbl_form.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR}; border: none; background: transparent;")
        form_header_layout.addWidget(lbl_form)
        form_header_layout.addStretch()
        
        self.btn_open_add_dialog = QPushButton("✨ 새 상품 추가")
        self.btn_open_add_dialog.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_add_dialog.setFixedHeight(styles.s(32))
        self.btn_open_add_dialog.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.PRIMARY_PURPLE};
                color: white;
                border: none;
                border-radius: {styles.s(6)}px;
                padding: 0px {styles.s(12)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(12)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #6366F1;
            }}
            QPushButton:pressed {{
                background-color: {styles.DARK_PURPLE};
            }}
        """)
        self.btn_open_add_dialog.clicked.connect(self.open_new_product_dialog)
        form_header_layout.addWidget(self.btn_open_add_dialog)
        
        right_layout.addLayout(form_header_layout)
        
        # Scroll Area for the form fields
        scroll = QScrollArea()
        # Set widget resizable to false or compact and remove scroll margins to prevent unnecessary scrolling
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; } QWidget { background-color: transparent; }")
        scroll.verticalScrollBar().setStyleSheet(styles.SCROLLBAR_STYLE)
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(styles.s(8))
        form_layout.setContentsMargins(0, 0, 5, 0)
        
        # Grid layout for compact side-by-side elements
        grid = QGridLayout()
        grid.setSpacing(styles.s(8))
        grid.setContentsMargins(0, 0, 0, 0)
        
        # 1. Barcode & Quick Checkbox in a row
        barcode_header_layout = QHBoxLayout()
        lbl_barcode = QLabel("바코드")
        lbl_barcode.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.lbl_barcode_counter = QLabel("(0 / 13)")
        self.lbl_barcode_counter.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: {styles.PRIMARY_PURPLE}; font-weight: bold;")
        barcode_header_layout.addWidget(lbl_barcode)
        barcode_header_layout.addWidget(self.lbl_barcode_counter)
        barcode_header_layout.addStretch()
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setReadOnly(True)
        self.input_barcode.setPlaceholderText("상품 추가/저장 시 바코드가 자동 생성됩니다")
        self.input_barcode.setStyleSheet(MODERN_INPUT_STYLE.replace("#F9FAFB", "#F3F4F6")) # Darker gray background for read-only
        self.input_barcode.textChanged.connect(self.update_barcode_counter)
        
        self.check_quick = QCheckBox("단축 등록")
        self.check_quick.setStyleSheet(MODERN_CHECKBOX_STYLE)
        self.check_quick.clicked.connect(self.on_panel_check_quick_clicked)
        
        # Add to grid: Barcode (Row 0, Col 0, span 1), Checkbox (Row 0, Col 1, span 1)
        grid.addLayout(barcode_header_layout, 0, 0)
        grid.addWidget(self.check_quick, 0, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        grid.addWidget(self.input_barcode, 1, 0, 1, 2)
        
        # 2. Product Name (Row 2, 3)
        lbl_name = QLabel("상품명")
        lbl_name.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.input_name = QLineEdit()
        self.input_name.setStyleSheet(MODERN_INPUT_STYLE)
        self.input_name.setPlaceholderText("상품명을 입력하세요")
        grid.addWidget(lbl_name, 2, 0, 1, 2)
        grid.addWidget(self.input_name, 3, 0, 1, 2)
        
        # 3. Price & Stock (Row 4, 5)
        lbl_price = QLabel("단가 (원)")
        lbl_price.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.input_price = QLineEdit()
        self.input_price.setStyleSheet(MODERN_INPUT_STYLE)
        self.input_price.setPlaceholderText("예: 2,000")
        
        lbl_stock = QLabel("재고 수량")
        lbl_stock.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.input_stock = QLineEdit()
        self.input_stock.setStyleSheet(MODERN_INPUT_STYLE)
        self.input_stock.setPlaceholderText("예: 100")
        
        grid.addWidget(lbl_price, 4, 0)
        grid.addWidget(self.input_price, 5, 0)
        grid.addWidget(lbl_stock, 4, 1)
        grid.addWidget(self.input_stock, 5, 1)
        
        # 4. Promo & Category (Row 6, 7)
        lbl_promo = QLabel("행사 종류")
        lbl_promo.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.combo_promo = QComboBox()
        self.combo_promo.addItems(["없음", "1+1", "2+1"])
        self.combo_promo.setStyleSheet(MODERN_COMBO_STYLE)
        
        lbl_cat = QLabel("분류")
        lbl_cat.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        self.combo_category = QComboBox()
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.setEditable(True)
        self.combo_category.setStyleSheet(MODERN_COMBO_STYLE)
        
        grid.addWidget(lbl_promo, 6, 0)
        grid.addWidget(self.combo_promo, 7, 0)
        grid.addWidget(lbl_cat, 6, 1)
        grid.addWidget(self.combo_category, 7, 1)
        
        form_layout.addLayout(grid)
        
        # 5. Product Image Layout (More compact, side-by-side)
        lbl_img_section = QLabel("상품 이미지")
        lbl_img_section.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-top: 2px;")
        form_layout.addWidget(lbl_img_section)
        
        img_row_layout = QHBoxLayout()
        img_row_layout.setSpacing(10)
        
        self.lbl_image_preview = QLabel("이미지 없음")
        self.lbl_image_preview.setFixedSize(styles.s(80), styles.s(80))
        self.lbl_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image_preview.setStyleSheet("""
            QLabel {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: #F9FAFB;
                color: #6B7280;
                font-weight: bold;
                font-size: 9pt;
            }
        """)
        
        img_btn_layout = QVBoxLayout()
        img_btn_layout.setSpacing(4)
        
        self.btn_select_image = QPushButton("이미지 찾기")
        self.btn_select_image.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_select_image.setFixedHeight(styles.s(32))
        self.btn_select_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_image.clicked.connect(self.select_product_image)
        
        self.btn_clear_image = QPushButton("이미지 삭제")
        self.btn_clear_image.setStyleSheet(MODERN_BTN_GRAY)
        self.btn_clear_image.setFixedHeight(styles.s(32))
        self.btn_clear_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_image.clicked.connect(self.clear_product_image)
        
        img_btn_layout.addWidget(self.btn_select_image)
        img_btn_layout.addWidget(self.btn_clear_image)
        
        img_row_layout.addWidget(self.lbl_image_preview)
        img_row_layout.addLayout(img_btn_layout)
        img_row_layout.addStretch()
        form_layout.addLayout(img_row_layout)
        
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
        
        # Barcode & POP printing group
        print_group = QFrame()
        print_group.setStyleSheet("QFrame { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; } QLabel { border: none; background: transparent; }")
        print_layout = QVBoxLayout(print_group)
        print_layout.setContentsMargins(8, 8, 8, 8)
        print_layout.setSpacing(5)
        
        lbl_print_title = QLabel("🏷️ 바코드 & 진열대 가격표(POP) 출력")
        lbl_print_title.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; font-weight: bold; color: #334155; background: transparent;")
        print_layout.addWidget(lbl_print_title)
        
        # Row 1: Barcode label printing
        barcode_btn_layout = QHBoxLayout()
        barcode_btn_layout.setSpacing(6)
        
        self.btn_print_selected = QPushButton("바코드 선택")
        self.btn_print_selected.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_print_selected.setFixedHeight(styles.s(34))
        self.btn_print_selected.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print_selected.clicked.connect(self.print_selected_barcode)
        
        self.btn_print_all = QPushButton("바코드 전체")
        self.btn_print_all.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_print_all.setFixedHeight(styles.s(34))
        self.btn_print_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print_all.clicked.connect(self.print_all_barcodes)
        
        barcode_btn_layout.addWidget(self.btn_print_selected)
        barcode_btn_layout.addWidget(self.btn_print_all)
        print_layout.addLayout(barcode_btn_layout)
        
        # Row 2: POP Price tags (Selected & Promo)
        MODERN_BTN_BLUE = f"""
            QPushButton {{
                background-color: #2563EB;
                color: white;
                font-size: {styles.fs(10.5)};
                font-weight: bold;
                border-radius: {styles.s(6)}px;
                border: none;
                font-family: '{styles.FONT_FAMILY}';
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
        """
        MODERN_BTN_ORANGE = f"""
            QPushButton {{
                background-color: #EA580C;
                color: white;
                font-size: {styles.fs(10.5)};
                font-weight: bold;
                border-radius: {styles.s(6)}px;
                border: none;
                font-family: '{styles.FONT_FAMILY}';
            }}
            QPushButton:hover {{ background-color: #C2410C; }}
        """
        MODERN_BTN_TEAL = f"""
            QPushButton {{
                background-color: #0D9488;
                color: white;
                font-size: {styles.fs(10.5)};
                font-weight: bold;
                border-radius: {styles.s(6)}px;
                border: none;
                font-family: '{styles.FONT_FAMILY}';
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
        """
        
        pop_btn_layout = QHBoxLayout()
        pop_btn_layout.setSpacing(6)
        
        self.btn_pop_selected = QPushButton("선택 가격표 POP")
        self.btn_pop_selected.setStyleSheet(MODERN_BTN_BLUE)
        self.btn_pop_selected.setFixedHeight(styles.s(34))
        self.btn_pop_selected.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pop_selected.clicked.connect(self.print_selected_pop)
        
        self.btn_pop_promo = QPushButton("🔥 행사상품 POP")
        self.btn_pop_promo.setStyleSheet(MODERN_BTN_ORANGE)
        self.btn_pop_promo.setFixedHeight(styles.s(34))
        self.btn_pop_promo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pop_promo.clicked.connect(self.print_promo_pop)
        
        pop_btn_layout.addWidget(self.btn_pop_selected)
        pop_btn_layout.addWidget(self.btn_pop_promo)
        print_layout.addLayout(pop_btn_layout)
        
        # Row 3: All products POP
        self.btn_pop_all = QPushButton("📋 전체 진열대 가격표(POP) 출력")
        self.btn_pop_all.setStyleSheet(MODERN_BTN_TEAL)
        self.btn_pop_all.setFixedHeight(styles.s(34))
        self.btn_pop_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pop_all.clicked.connect(self.print_all_pop)
        print_layout.addWidget(self.btn_pop_all)
        
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
        
        # 단축 등록 개수 헤더 표시 (최대 5개)
        quick_cnt = self.product_manager.get_quick_items_count()
        self.table.setHorizontalHeaderItem(6, QTableWidgetItem(f"단축 ({quick_cnt}/5)"))
        if hasattr(self, 'check_quick'):
            self.check_quick.setText(f"단축 등록 ({quick_cnt}/5)")
        
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
            quick_item = QTableWidgetItem(quick_text)
            if is_quick:
                quick_item.setForeground(QColor("#7C3AED"))
            self.table.setItem(row, 6, quick_item)
            
            # Alignments
            self.table.item(row, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 6).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            
            row += 1
            
        if hasattr(self, 'v_table'):
            self.load_voucher_data()

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

    def on_table_click(self, row, col):
        self.table.selectRow(row)
        # 6번 열(단축) 클릭 시 1클릭으로 바로 토글
        if col == 6:
            barcode_item = self.table.item(row, 0)
            if barcode_item:
                barcode = barcode_item.text().strip()
                product = self.product_manager.get_product(barcode)
                if product:
                    is_currently_quick = product.get("is_quick", False)
                    if is_currently_quick:
                        self.product_manager.set_quick_item(barcode, False)
                        self.load_data()
                        self.table.selectRow(row)
                    else:
                        if self.product_manager.get_quick_items_count() >= 5:
                            CustomMessageDialog(
                                "단축 등록 제한", 
                                "단축 상품은 메인 화면에 최대 5개까지만 등록할 수 있습니다.\n기존 등록된 단축 상품(★)을 먼저 해제해 주세요.", 
                                'warning', 
                                self
                            ).exec()
                        else:
                            self.product_manager.set_quick_item(barcode, True)
                            self.load_data()
                            self.table.selectRow(row)

    def on_table_double_click(self, row, col):
        self.edit_selected_product()

    def edit_selected_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            self.show_alert("경고", "수정할 상품을 선택해주세요.", 'warning')
            return
            
        barcode = self.table.item(current_row, 0).text()
        dialog = ProductRegistrationDialog(self.product_manager, editing_barcode=barcode, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            target_bc = dialog.created_barcode or barcode
            for r in range(self.table.rowCount()):
                bc_item = self.table.item(r, 0)
                if bc_item and bc_item.text() == target_bc:
                    self.table.selectRow(r)
                    break

    def delete_selected_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            self.show_alert("경고", "삭제할 상품을 선택해주세요.", 'warning')
            return
            
        barcode = self.table.item(current_row, 0).text()
        name = self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else barcode
        
        if self.show_alert("삭제 확인", f"상품 '{name}' (바코드: {barcode})\n정말 삭제하시겠습니까?", 'question'):
            self.product_manager.delete_product(barcode)
            
            # Delete image
            existing_path = self.get_existing_image_path(barcode)
            if existing_path:
                try:
                    os.remove(existing_path)
                except Exception as e:
                    print(f"Error deleting image on product delete: {e}")
                    
            self.load_data()
            self.show_alert("삭제 완료", f"상품 '{name}'이(가) 삭제되었습니다.", 'info')

    def open_new_product_dialog(self):
        dialog = ProductRegistrationDialog(self.product_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            # Select newly added product in the table if available
            if dialog.created_barcode:
                for row in range(self.table.rowCount()):
                    bc_item = self.table.item(row, 0)
                    if bc_item and bc_item.text() == dialog.created_barcode:
                        self.table.selectRow(row)
                        break

    def clear_form(self):
        self.current_editing_barcode = None # Reset
        if hasattr(self, 'input_barcode'):
            self.input_barcode.setText("8801000000")
            self.input_name.clear()
            self.input_price.clear()
            self.input_stock.setText("10")
            self.combo_promo.setCurrentIndex(0)
            self.combo_category.setCurrentIndex(0)
            self.check_quick.setChecked(False)
            self.update_barcode_counter()
            self.selected_image_path = None
            self.image_deleted = False
            self.update_image_preview()
        self.table.clearSelection()

    def show_alert(self, title, message, type='info'):
        dialog = CustomMessageDialog(title, message, type, self)
        dialog.exec()
        return dialog.result_value

    def on_panel_check_quick_clicked(self, checked):
        if checked:
            count = self.product_manager.get_quick_items_count()
            was_quick = False
            if hasattr(self, 'current_editing_barcode') and self.current_editing_barcode:
                p = self.product_manager.get_product(self.current_editing_barcode)
                if p and p.get("is_quick", False):
                    was_quick = True
            if not was_quick and count >= 5:
                self.check_quick.setChecked(False)
                self.show_alert("알림", "단축 상품은 메인 화면에 최대 5개까지만 등록할 수 있습니다.\n기존 등록된 상품(★)을 먼저 해제해 주세요.", 'warning')

    def save_product(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        price_str = self.input_price.text().strip()
        stock_str = self.input_stock.text().strip()
        promo_type = self.combo_promo.currentIndex()
        category = self.combo_category.currentText().strip()
        is_quick = self.check_quick.isChecked()
        
        if is_quick:
            was_quick = False
            if hasattr(self, 'current_editing_barcode') and self.current_editing_barcode:
                p = self.product_manager.get_product(self.current_editing_barcode)
                if p and p.get("is_quick", False):
                    was_quick = True
            if not was_quick and self.product_manager.get_quick_items_count() >= 5:
                self.show_alert("경고", "단축 상품은 최대 5개까지만 등록할 수 있습니다.\n기존 등록된 상품(★)을 먼저 해제해 주세요.", 'warning')
                return

        # Auto generate general product barcode starting with 88 (Korean retail standard code prefix) if not editing
        if not self.current_editing_barcode:
            import random
            existing_products = self.product_manager.get_all_products()
            while True:
                rand_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
                barcode = f"88{rand_part}"
                if barcode not in existing_products:
                    break
                    
        if not name or not price_str or not stock_str:
            self.show_alert("경고", "모든 필드를 입력해주세요.", 'warning')
            return
            
        # Validation: 13 digits numeric
        if not barcode or len(barcode) != 13 or not barcode.isdigit():
            self.show_alert("경고", "바코드가 올바르게 생성되지 않았습니다. 다시 시도해 주세요.", 'warning')
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
                        self.product_manager.add_product(barcode, name, price, category, stock, promo_type, is_quick)
                    else:
                        return
                else:
                    # Normal rename (barcode changed to a new unique one)
                    self.product_manager.update_product_key(self.current_editing_barcode, barcode, name, price, category, stock, promo_type, is_quick)
            else:
                # Barcode didn't change, just update details
                self.product_manager.add_product(barcode, name, price, category, stock, promo_type, is_quick)
        else:
            # Scenario 2: Adding a completely new product (or duplicate on enter)
            if existing_product:
                msg = f"바코드 [{barcode}]는 이미 등록된 상품입니다.\n기존 상품: {existing_product['name']}\n\n이 상품 정보를 현재 입력하신 정보로 변경하시겠습니까?"
                if self.show_alert("중복 확인", msg, 'question'):
                    self.product_manager.add_product(barcode, name, price, category, stock, promo_type, is_quick)
                else:
                    return
            else:
                # Normal new addition
                self.product_manager.add_product(barcode, name, price, category, stock, promo_type, is_quick)

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
        barcode = ""
        name = ""
        price = 0
        
        current_row = self.table.currentRow()
        if current_row >= 0:
            barcode = self.table.item(current_row, 0).text()
            name = self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else ""
            price_str = self.table.item(current_row, 2).text().replace(",", "") if self.table.item(current_row, 2) else "0"
            try:
                price = int(price_str)
            except:
                price = 0
        elif hasattr(self, 'input_barcode'):
            barcode = self.input_barcode.text().strip()
            name = self.input_name.text().strip()
            try:
                price = int(self.input_price.text().strip().replace(",", ""))
            except:
                price = 0
        
        if not barcode or not name:
            self.show_alert("경고", "출력할 상품을 목록에서 선택해주세요.", 'warning')
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

    def generate_pop_label_html(self, products_list, title="매장 진열대 가격표(POP)"):
        cards_html = ""
        for p in products_list:
            barcode = p.get("barcode", "")
            name = p.get("name", "")
            price = p.get("price", 0)
            category = p.get("category", "일반")
            promo_type = p.get("promo_type", 0)
            
            barcode_img = self.receipt_manager.generate_barcode_base64(barcode)
            spaced_barcode = " ".join([barcode[i:i+4] for i in range(0, len(barcode), 4)])
            
            if promo_type == 1:
                badge_html = '<td align="right" style="background:#EF4444; color:white; font-size:12pt; font-weight:bold; padding:4px 10px; border-radius:4px;">1 + 1</td>'
                unit_price = round(price / 2)
                calc_html = f'''
                <tr>
                    <td colspan="2" style="background-color: #FEF2F2; border: 1px dashed #EF4444; padding: 6px; text-align: center; color: #DC2626; font-size: 10pt; font-weight: bold;">
                        ★ 1+1 행사 혜택! 개당 <b style="font-size:11pt;">{unit_price:,}원</b>
                    </td>
                </tr>
                '''
                border_color = "#EF4444"
            elif promo_type == 2:
                badge_html = '<td align="right" style="background:#F59E0B; color:white; font-size:12pt; font-weight:bold; padding:4px 10px; border-radius:4px;">2 + 1</td>'
                unit_price = round((price * 2) / 3)
                calc_html = f'''
                <tr>
                    <td colspan="2" style="background-color: #FFFBEB; border: 1px dashed #F59E0B; padding: 6px; text-align: center; color: #D97706; font-size: 10pt; font-weight: bold;">
                        ★ 2+1 행사 혜택! 개당 <b style="font-size:11pt;">{unit_price:,}원</b>
                    </td>
                </tr>
                '''
                border_color = "#F59E0B"
            else:
                badge_html = f'<td align="right" style="background:#EEF2FF; color:#4F46E5; border:1px solid #C7D2FE; font-size:10pt; font-weight:bold; padding:3px 8px; border-radius:4px;">{category}</td>'
                calc_html = '''
                <tr>
                    <td colspan="2" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 5px; text-align: center; color: #64748B; font-size: 9.5pt;">
                        DU 편의점 엄선 추천 상품
                    </td>
                </tr>
                '''
                border_color = "#94A3B8"
                
            card = f'''
            <table align="center" width="340" cellpadding="8" cellspacing="0" style="border: 2px solid {border_color}; background-color: #FFFFFF; margin: 10px auto; font-family: 'Malgun Gothic', sans-serif;">
                <!-- Header row -->
                <tr>
                    <td align="left" style="vertical-align: middle;">
                        <span style="background-color: #1E293B; color: #FFFFFF; font-size: 9.5pt; font-weight: bold; padding: 3px 6px;">DU 편의점</span>
                        <span style="color: #64748B; font-size: 9.5pt; font-weight: bold; margin-left: 6px;">{category}</span>
                    </td>
                    {badge_html}
                </tr>
                
                <!-- Product Name -->
                <tr>
                    <td colspan="2" style="font-size: 14pt; font-weight: bold; color: #111827; padding-top: 6px; padding-bottom: 4px;">
                        {name}
                    </td>
                </tr>
                
                <!-- Price -->
                <tr>
                    <td colspan="2" align="right" style="border-bottom: 2px solid #F1F5F9; padding-bottom: 6px;">
                        <span style="font-size: 10pt; color: #64748B; font-weight: bold; margin-right: 8px;">판매가</span>
                        <span style="font-size: 22pt; font-weight: bold; color: #0F172A;">{price:,}</span>
                        <span style="font-size: 13pt; font-weight: bold; color: #0F172A;">원</span>
                    </td>
                </tr>
                
                <!-- Benefit Calculation -->
                {calc_html}
                
                <!-- Barcode -->
                <tr>
                    <td colspan="2" align="center" style="padding-top: 8px;">
                        <img src="{barcode_img}" height="38" /><br>
                        <span style="font-size: 9pt; color: #475569; font-weight: bold; letter-spacing: 2px;">{spaced_barcode}</span>
                    </td>
                </tr>
            </table>
            
            <div style="text-align: center; color: #94A3B8; font-size: 8pt; margin: 6px 0 12px 0;">
                - - - - - - - - - - - - - - - ✂ 절취선 - - - - - - - - - - - - - - -
            </div>
            '''
            cards_html += card
            
        html = f'''
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 8px;
                    background-color: #F8FAFC;
                    font-family: 'Malgun Gothic', 'Dotum', sans-serif;
                }}
            </style>
        </head>
        <body>
            <div style="text-align: center; margin-bottom: 8px;">
                <span style="font-size: 11pt; font-weight: bold; color: #334155;">🏷️ {title} (총 {len(products_list)}건)</span>
            </div>
            {cards_html}
        </body>
        </html>
        '''
        return html

    def get_selected_product_info(self):
        barcode = ""
        current_row = self.table.currentRow()
        if current_row >= 0:
            item = self.table.item(current_row, 0)
            if item:
                barcode = item.text().strip()
        if not barcode and hasattr(self, 'input_barcode'):
            barcode = self.input_barcode.text().strip()
            
        if barcode:
            p = self.product_manager.get_product(barcode)
            if p:
                return {
                    "barcode": barcode,
                    "name": p.get("name", ""),
                    "price": p.get("price", 0),
                    "category": p.get("category", "일반"),
                    "promo_type": p.get("promo_type", 0)
                }
        return None

    def print_selected_pop(self):
        p = self.get_selected_product_info()
        if not p:
            self.show_alert("경고", "진열대 가격표(POP)를 출력할 상품을 목록에서 선택해주세요.", 'warning')
            return
            
        html = self.generate_pop_label_html([p], title=f"{p['name']} 진열대 가격표(POP)")
        from ui_components import ReceiptPreviewDialog
        dialog = ReceiptPreviewDialog(html, self, title="선택 상품 진열대 가격표(POP)", height=780)
        dialog.exec()

    def print_promo_pop(self):
        products = self.product_manager.get_all_products()
        promo_items = []
        for barcode, data in products.items():
            ptype = data.get("promo_type", 0)
            if ptype in (1, 2):
                promo_items.append({
                    "barcode": barcode,
                    "name": data.get("name", ""),
                    "price": data.get("price", 0),
                    "category": data.get("category", "일반"),
                    "promo_type": ptype
                })
                
        if not promo_items:
            self.show_alert("알림", "등록된 행사 상품(1+1 또는 2+1)이 없습니다.", 'info')
            return
            
        html = self.generate_pop_label_html(promo_items, title="행사상품(1+1/2+1) 진열대 가격표(POP)")
        from ui_components import ReceiptPreviewDialog
        dialog = ReceiptPreviewDialog(html, self, title="행사상품(1+1/2+1) 진열대 가격표(POP)", height=780)
        dialog.exec()

    def print_all_pop(self):
        products = self.product_manager.get_all_products()
        if not products:
            self.show_alert("알림", "등록된 상품이 없습니다.", 'info')
            return
            
        all_items = []
        for barcode, data in products.items():
            all_items.append({
                "barcode": barcode,
                "name": data.get("name", ""),
                "price": data.get("price", 0),
                "category": data.get("category", "일반"),
                "promo_type": data.get("promo_type", 0)
            })
            
        html = self.generate_pop_label_html(all_items, title="전체 진열대 가격표(POP)")
        from ui_components import ReceiptPreviewDialog
        dialog = ReceiptPreviewDialog(html, self, title="전체 진열대 가격표(POP)", height=780)
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
        self.v_table.setColumnCount(6)
        self.v_table.setHorizontalHeaderLabels(["상품권 바코드", "상품권 이름", "유형", "교환 대상 상품", "잔액 / 액면가", "상태"])
        
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
        self.v_table.setColumnWidth(0, styles.s(130)) # Barcode
        self.v_table.setColumnWidth(1, styles.s(160)) # Name
        self.v_table.setColumnWidth(2, styles.s(85))  # Type
        self.v_table.setColumnWidth(3, styles.s(130)) # Target
        self.v_table.setColumnWidth(4, styles.s(110)) # Balance / Price
        self.v_table.setColumnWidth(5, styles.s(75))  # Status
        
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
        
        # Row 0: Voucher Type Selection (물품 교환권 vs 금액형 상품권)
        type_box = QVBoxLayout()
        type_box.setSpacing(styles.s(6))
        lbl_type = QLabel("상품권 유형 선택")
        lbl_type.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};")
        type_box.addWidget(lbl_type)
        
        type_btn_layout = QHBoxLayout()
        type_btn_layout.setSpacing(styles.s(8))
        
        self.btn_v_type_item = QPushButton("🏷️  물품 교환권")
        self.btn_v_type_amount = QPushButton("💳  금액형 상품권")
        
        self.btn_v_type_item.setFixedHeight(styles.s(44))
        self.btn_v_type_amount.setFixedHeight(styles.s(44))
        self.btn_v_type_item.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_v_type_amount.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_v_type_item.clicked.connect(lambda: self.switch_voucher_type("item", reset_fields=True))
        self.btn_v_type_amount.clicked.connect(lambda: self.switch_voucher_type("amount", reset_fields=True))
        
        type_btn_layout.addWidget(self.btn_v_type_item)
        type_btn_layout.addWidget(self.btn_v_type_amount)
        type_box.addLayout(type_btn_layout)
        form_layout.addLayout(type_box)
        
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
        self.v_input_barcode.setReadOnly(True)
        self.v_input_barcode.setPlaceholderText("상품권 생성 시 자동으로 부여됩니다")
        self.v_input_barcode.setStyleSheet(MODERN_INPUT_STYLE.replace("#F9FAFB", "#F3F4F6"))
        self.v_input_barcode.textChanged.connect(self.update_v_barcode_counter)
        
        # Target Product Dropdown (물품 교환권용)
        self.lbl_v_target = QLabel("교환 대상 상품")
        self.lbl_v_target.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR}; margin-top: {styles.s(5)}px;")
        self.v_combo_target_prod = QComboBox()
        self.v_combo_target_prod.setStyleSheet(MODERN_COMBO_STYLE)
        self.v_combo_target_prod.currentIndexChanged.connect(self.on_target_product_changed)
        
        # Quick Amount Buttons (금액형 상품권용)
        self.v_quick_amt_widget = QWidget()
        quick_amt_layout = QVBoxLayout(self.v_quick_amt_widget)
        quick_amt_layout.setContentsMargins(0, 0, 0, 0)
        quick_amt_layout.setSpacing(4)
        lbl_quick_hint = QLabel("빠른 금액 선택")
        lbl_quick_hint.setStyleSheet(f"font-size: {styles.FONT_SIZE_SMALL}; color: #6B7280; font-weight: bold;")
        quick_amt_layout.addWidget(lbl_quick_hint)
        
        btn_amt_row = QHBoxLayout()
        btn_amt_row.setSpacing(6)
        for amt in [3000, 5000, 10000, 30000, 50000]:
            btn = QPushButton(f"{amt:,}원")
            btn.setFixedHeight(styles.s(32))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #EEF2FF;
                    border: 1px solid #C7D2FE;
                    color: #4338CA;
                    font-size: 10pt;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #E0E7FF;
                }
            """)
            btn.clicked.connect(lambda checked, a=amt: self.set_quick_amount(a))
            btn_amt_row.addWidget(btn)
        quick_amt_layout.addLayout(btn_amt_row)
        self.v_quick_amt_widget.hide() # Hidden by default (item exchange checked)
        
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
        self.v_input_price.setPlaceholderText("예: 5,000")
        
        form_layout.addLayout(barcode_header_layout)
        form_layout.addWidget(self.v_input_barcode)
        
        form_layout.addWidget(self.lbl_v_target)
        form_layout.addWidget(self.v_combo_target_prod)
        form_layout.addWidget(self.v_quick_amt_widget)
        
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
        
        action_btn_layout = QHBoxLayout()
        action_btn_layout.setSpacing(6)

        self.btn_v_print = QPushButton("상품권 이미지 보기")
        self.btn_v_print.setStyleSheet(MODERN_BTN_PURPLE)
        self.btn_v_print.setFixedHeight(styles.s(36))
        self.btn_v_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_v_print.clicked.connect(self.print_voucher_image)
        action_btn_layout.addWidget(self.btn_v_print)

        MODERN_BTN_COCOA = f"""
            QPushButton {{
                background-color: #FEE500;
                color: #3C1E1E;
                border: none;
                border-radius: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FADA0A;
            }}
            QPushButton:pressed {{
                background-color: #E6C800;
            }}
        """
        self.btn_v_cocoa = QPushButton("☕ 코코아톡 전송")
        self.btn_v_cocoa.setStyleSheet(MODERN_BTN_COCOA)
        self.btn_v_cocoa.setFixedHeight(styles.s(36))
        self.btn_v_cocoa.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_v_cocoa.clicked.connect(self.send_voucher_cocoatalk)
        action_btn_layout.addWidget(self.btn_v_cocoa)

        btn_panel.addLayout(action_btn_layout)
        
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
        
        # Initialize default type UI
        self.current_v_type = "item"
        self.switch_voucher_type("item", reset_fields=False)

    def switch_voucher_type(self, v_type, reset_fields=True):
        """상품권 유형(물품 교환권 vs 금액형 상품권) 전환 및 UI/필드 갱신"""
        self.current_v_type = v_type
        
        # 눈에 확 띄는 버튼 스타일 (활성: 선명한 브랜드 컬러 + 흰색 볼드 텍스트 / 비활성: 부드러운 회색 + 테두리)
        active_item_style = (
            "QPushButton {"
            "  background-color: #7C3AED;"
            "  color: #FFFFFF;"
            f"  font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold;"
            f"  border-radius: {styles.s(8)}px;"
            "  border: 2px solid #5B21B6;"
            "  padding: 6px 12px;"
            "}"
            "QPushButton:hover { background-color: #6D28D9; }"
        )
        inactive_item_style = (
            "QPushButton {"
            "  background-color: #F3F4F6;"
            "  color: #4B5563;"
            f"  font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: 600;"
            f"  border-radius: {styles.s(8)}px;"
            "  border: 1.5px solid #D1D5DB;"
            "  padding: 6px 12px;"
            "}"
            "QPushButton:hover { background-color: #EDE9FE; color: #7C3AED; border-color: #C4B5FD; }"
        )
        
        active_amount_style = (
            "QPushButton {"
            "  background-color: #2563EB;"
            "  color: #FFFFFF;"
            f"  font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold;"
            f"  border-radius: {styles.s(8)}px;"
            "  border: 2px solid #1D4ED8;"
            "  padding: 6px 12px;"
            "}"
            "QPushButton:hover { background-color: #1D4ED8; }"
        )
        inactive_amount_style = (
            "QPushButton {"
            "  background-color: #F3F4F6;"
            "  color: #4B5563;"
            f"  font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: 600;"
            f"  border-radius: {styles.s(8)}px;"
            "  border: 1.5px solid #D1D5DB;"
            "  padding: 6px 12px;"
            "}"
            "QPushButton:hover { background-color: #DBEAFE; color: #2563EB; border-color: #93C5FD; }"
        )
        
        if v_type == "item":
            self.btn_v_type_item.setStyleSheet(active_item_style)
            self.btn_v_type_amount.setStyleSheet(inactive_amount_style)
            self.lbl_v_target.setVisible(True)
            self.v_combo_target_prod.setVisible(True)
            self.v_quick_amt_widget.setVisible(False)
        else:
            self.btn_v_type_item.setStyleSheet(inactive_item_style)
            self.btn_v_type_amount.setStyleSheet(active_amount_style)
            self.lbl_v_target.setVisible(False)
            self.v_combo_target_prod.setVisible(False)
            self.v_quick_amt_widget.setVisible(True)
            
        if reset_fields:
            self.current_editing_v_barcode = None
            self.v_input_name.clear()
            self.v_input_price.clear()
            self.v_combo_target_prod.setCurrentIndex(0)
            self.v_input_barcode.clear()
            self.update_v_barcode_counter()
            self.v_table.clearSelection()

    def set_quick_amount(self, amt):
        self.v_input_price.setText(str(amt))
        self.v_input_name.setText(f"모바일)금액권 {amt:,}원")
        if not self.current_editing_v_barcode:
            import random
            existing_vouchers = self.product_manager.get_all_vouchers()
            while True:
                rand_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
                barcode = f"99{rand_part}"
                if barcode not in existing_vouchers:
                    break
            self.v_input_barcode.setText(barcode)
            self.update_v_barcode_counter()

    def populate_target_products(self):
        self.v_combo_target_prod.blockSignals(True)
        self.v_combo_target_prod.clear()
        self.v_combo_target_prod.addItem("--- 교환 대상 상품 선택 ---", None)
        
        products = self.product_manager.get_all_products()
        for barcode, p in products.items():
            self.v_combo_target_prod.addItem(f"{p['name']} ({p['price']:,}원)", barcode)
        self.v_combo_target_prod.blockSignals(False)

    def on_target_product_changed(self, index):
        if getattr(self, "current_v_type", "item") != "item":
            return
        barcode = self.v_combo_target_prod.currentData()
        if barcode:
            product = self.product_manager.get_product(barcode)
            if product:
                self.v_input_name.setText(f"모바일){product['name']}교환권")
                self.v_input_price.setText(str(product['price']))
                
                # Auto-generate barcode if not editing an existing voucher
                if not self.current_editing_v_barcode:
                    import random
                    existing_vouchers = self.product_manager.get_all_vouchers()
                    while True:
                        # Generate 11 random digits to append to '99'
                        rand_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
                        generated_bc = f"99{rand_part}"
                        if generated_bc not in existing_vouchers:
                            break
                    self.v_input_barcode.setText(generated_bc)
                    self.update_v_barcode_counter()

    def load_voucher_data(self):
        # Populate target product list
        self.populate_target_products()
        
        vouchers = self.product_manager.get_all_vouchers()
        self.v_table.setRowCount(len(vouchers))
        
        row = 0
        for barcode, data in vouchers.items():
            self.v_table.setItem(row, 0, QTableWidgetItem(barcode))
            self.v_table.setItem(row, 1, QTableWidgetItem(data.get("name", "상품권")))
            
            v_type = data.get("voucher_type", "item" if data.get("product_barcode") else "amount")
            v_type_str = "물품교환" if v_type == "item" else "금액권"
            self.v_table.setItem(row, 2, QTableWidgetItem(v_type_str))
            
            target_barcode = data.get("product_barcode", "")
            if v_type == "item" and target_barcode:
                target_product = self.product_manager.get_product(target_barcode)
                target_name = target_product["name"] if target_product else f"미기록 ({target_barcode})"
            else:
                target_name = "-"
            self.v_table.setItem(row, 3, QTableWidgetItem(target_name))
            
            price = data.get("price", 0)
            balance = data.get("balance", price)
            status = data.get("status", "unused")
            
            if status == "used" or balance <= 0:
                status_text = "사용완료"
            elif balance < price:
                status_text = "잔액남음"
            else:
                status_text = "미사용"
                
            val_text = f"{balance:,} / {price:,}" if v_type == "amount" else f"{price:,}"
            self.v_table.setItem(row, 4, QTableWidgetItem(val_text))
            self.v_table.setItem(row, 5, QTableWidgetItem(status_text))
            
            self.v_table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.v_table.item(row, 2).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.v_table.item(row, 4).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.v_table.item(row, 5).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            
            # Apply styling colors for type and status
            if v_type == "amount":
                self.v_table.item(row, 2).setForeground(QColor("#1D4ED8")) # Indigo/Blue
            else:
                self.v_table.item(row, 2).setForeground(QColor("#7C3AED")) # Purple
                
            if status_text == "사용완료":
                self.v_table.item(row, 5).setForeground(QColor("#D32F2F")) # Red
            elif status_text == "잔액남음":
                self.v_table.item(row, 5).setForeground(QColor("#0284C7")) # Sky Blue
            else:
                self.v_table.item(row, 5).setForeground(QColor("#388E3C")) # Green
            
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
            
            v_type = voucher.get("voucher_type", "item" if voucher.get("product_barcode") else "amount")
            self.switch_voucher_type(v_type, reset_fields=False)
            if v_type == "item":
                target_bc = voucher.get("product_barcode", "")
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
        self.switch_voucher_type("item", reset_fields=True)

    def save_voucher(self):
        barcode = self.v_input_barcode.text().strip()
        name = self.v_input_name.text().strip()
        price_str = self.v_input_price.text().strip()
        is_item = (getattr(self, "current_v_type", "item") == "item")
        v_type = self.current_v_type
        target_barcode = self.v_combo_target_prod.currentData() if is_item else ""
        
        if is_item and not target_barcode:
            self.show_alert("경고", "교환 대상 상품을 선택해주세요.", 'warning')
            return
            
        if not name or not price_str:
            self.show_alert("경고", "상품권 이름과 금액을 입력해주세요.", 'warning')
            return
            
        try:
            price = int(price_str.replace(",", ""))
            if price <= 0:
                raise ValueError
        except ValueError:
            self.show_alert("경고", "금액은 0보다 큰 숫자여야 합니다.", 'warning')
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
            
        # Save
        self.product_manager.add_voucher(
            barcode=barcode,
            product_barcode=target_barcode,
            name=name,
            price=price,
            status="unused",
            voucher_type=v_type,
            balance=price
        )
        self.load_voucher_data()
        self.clear_v_form()
        self.show_alert("완료", f"[{'물품교환권' if is_item else '금액형상품권'}] 저장되었습니다.\n바코드: {barcode}", 'info')

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
                
        if image_path and os.path.exists(image_path):
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
                    width: 350px;
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
                    padding: 20px 15px;
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
                    width: 90%;
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
                    border: 1.5px solid #E2E8F0;
                    border-radius: 8px;
                    padding: 14px 10px;
                    display: block;
                    width: 92%;
                    margin: 0 auto 12px auto;
                    box-sizing: border-box;
                    text-align: center;
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
                    <div class="brand-name">DU</div>
                    <div class="product-name">{product_name}</div>
                    
                    <div class="pay-banner">
                        <span class="pay-dot">●</span> pay 카카오페이로 추가결제
                    </div>
                    
                    <div class="barcode-box">
                        <img src="{barcode_img_src}" style="width: 100%; max-width: 295px; height: 80px; display: block; margin: 0 auto;" />
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

    def send_voucher_cocoatalk(self):
        barcode = self.v_input_barcode.text().strip()
        if not barcode or barcode == "9900000000":
            current_row = self.v_table.currentRow()
            if current_row >= 0:
                barcode = self.v_table.item(current_row, 0).text()
            else:
                self.show_alert("경고", "코코아톡으로 전송할 상품권을 선택하거나 정보를 입력해주세요.", 'warning')
                return

        voucher = self.product_manager.get_voucher(barcode)
        if not voucher:
            self.show_alert("경고", "저장된 상품권 정보를 찾을 수 없습니다.\n먼저 상품권을 저장해주세요.", 'warning')
            return

        target_barcode = voucher.get("product_barcode", "")
        target_product = self.product_manager.get_product(target_barcode)

        from cocoatalk_sender import CocoaTalkVoucherDialog
        dialog = CocoaTalkVoucherDialog(barcode, voucher, target_product, self.receipt_manager, self)
        dialog.exec()

    def set_fullscreen(self):
        win = self.window()
        if win:
            win.showFullScreen()
            CustomMessageDialog("화면 설정", "전체화면 모드로 전환되었습니다.", 'info', self).exec()

    def set_windowed(self):
        win = self.window()
        if win:
            win.showNormal()
            # Set to standard POS window size
            win.resize(styles.s(1024), styles.s(768))
            # Center it on screen
            screen = QApplication.primaryScreen().geometry()
            size = win.geometry()
            win.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
            CustomMessageDialog("화면 설정", "창 화면 모드로 전환되었습니다.", 'info', self).exec()

    def create_drawer_settings_card(self):
        drawer_card = QFrame()
        drawer_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        d_lyt = QVBoxLayout(drawer_card)
        d_lyt.setContentsMargins(25, 25, 25, 25)
        d_lyt.setSpacing(15)

        lbl_drawer_title = QLabel("💰 금전문함(돈통/금고) 설정")
        lbl_drawer_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1E293B; border: none;")
        d_lyt.addWidget(lbl_drawer_title)

        lbl_drawer_desc = QLabel("현금 결제 시 자동으로 금고(돈통)가 열리도록 연동합니다. COM 포트 및 연결 방식을 설정하고 직접 열기 테스트를 할 수 있습니다.")
        lbl_drawer_desc.setStyleSheet("font-size: 11pt; color: #64748B; border: none;")
        d_lyt.addWidget(lbl_drawer_desc)

        # Mode Selection
        mode_box = QHBoxLayout()
        mode_box.setSpacing(20)
        
        self.rb_drawer_serial = QRadioButton("USB / 시리얼 오픈기 (추천)")
        self.rb_drawer_serial.setStyleSheet("font-size: 11pt; font-weight: bold; color: #334155; border: none;")
        self.rb_drawer_printer = QRadioButton("영수증 프린터 방식")
        self.rb_drawer_printer.setStyleSheet("font-size: 11pt; font-weight: bold; color: #334155; border: none;")
        
        cfg = cash_drawer.config
        current_mode = cfg.get("mode", "serial")
        if current_mode == "printer":
            self.rb_drawer_printer.setChecked(True)
        else:
            self.rb_drawer_serial.setChecked(True)
            
        self.rb_drawer_serial.toggled.connect(self.on_drawer_mode_changed)
        self.rb_drawer_printer.toggled.connect(self.on_drawer_mode_changed)
        
        mode_box.addWidget(self.rb_drawer_serial)
        mode_box.addWidget(self.rb_drawer_printer)
        mode_box.addStretch()
        d_lyt.addLayout(mode_box)

        # Device Selection Row
        dev_row = QHBoxLayout()
        dev_row.setSpacing(10)
        
        self.lbl_device_title = QLabel("COM 포트:")
        self.lbl_device_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #334155; min-width: 80px; border: none;")
        
        self.cb_drawer_device = QComboBox()
        self.cb_drawer_device.setFixedHeight(40)
        self.cb_drawer_device.setStyleSheet(f"""
            QComboBox {{
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11pt;
                font-weight: bold;
                color: #1E293B;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid #CBD5E1;
                selection-background-color: {styles.PRIMARY_PURPLE};
                selection-color: white;
                color: #1E293B;
            }}
        """)
        
        btn_refresh_dev = QPushButton("🔄 새로고침")
        btn_refresh_dev.setFixedSize(110, 40)
        btn_refresh_dev.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh_dev.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                font-size: 10pt;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        btn_refresh_dev.clicked.connect(self.refresh_drawer_devices)
        
        dev_row.addWidget(self.lbl_device_title)
        dev_row.addWidget(self.cb_drawer_device, stretch=1)
        dev_row.addWidget(btn_refresh_dev)
        d_lyt.addLayout(dev_row)

        # Options Checkboxes
        opt_row = QHBoxLayout()
        opt_row.setSpacing(25)
        
        self.chk_drawer_auto = QCheckBox("현금 결제 시 금고 자동 열림")
        self.chk_drawer_auto.setChecked(cfg.get("auto_open", True))
        self.chk_drawer_auto.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {styles.PRIMARY_PURPLE}; border: none;")
        
        self.chk_drawer_sound = QCheckBox("열림 효과음 재생")
        self.chk_drawer_sound.setChecked(cfg.get("sound_enabled", True))
        self.chk_drawer_sound.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {styles.PRIMARY_PURPLE}; border: none;")
        
        opt_row.addWidget(self.chk_drawer_auto)
        opt_row.addWidget(self.chk_drawer_sound)
        opt_row.addStretch()
        d_lyt.addLayout(opt_row)

        # Test and Save Action Buttons Row
        action_row = QHBoxLayout()
        action_row.setSpacing(15)
        
        btn_test_open = QPushButton("🔓 금전문함 열기 테스트")
        btn_test_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_test_open.setFixedHeight(48)
        btn_test_open.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #1D4ED8; }
            QPushButton:pressed { background-color: #1E40AF; }
        """)
        btn_test_open.clicked.connect(self.test_open_drawer)
        
        btn_save_drawer = QPushButton("💾 설정 저장")
        btn_save_drawer.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_drawer.setFixedHeight(48)
        btn_save_drawer.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.PRIMARY_PURPLE};
                color: white;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: #6D28D9; }}
        """)
        btn_save_drawer.clicked.connect(self.save_drawer_settings)
        
        self.lbl_drawer_status = QLabel("")
        self.lbl_drawer_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #16A34A; border: none;")
        
        action_row.addWidget(btn_test_open)
        action_row.addWidget(btn_save_drawer)
        action_row.addWidget(self.lbl_drawer_status, stretch=1)
        d_lyt.addLayout(action_row)

        self.refresh_drawer_devices()
        return drawer_card

    def on_drawer_mode_changed(self):
        self.refresh_drawer_devices()

    def refresh_drawer_devices(self):
        is_serial = self.rb_drawer_serial.isChecked()
        self.cb_drawer_device.clear()
        
        cfg = cash_drawer.config
        if is_serial:
            self.lbl_device_title.setText("COM 포트:")
            ports = cash_drawer.get_available_ports()
            if ports:
                self.cb_drawer_device.addItems(ports)
                saved_port = cfg.get("port", "COM6")
                matched = False
                for i, p in enumerate(ports):
                    if p.startswith(saved_port):
                        self.cb_drawer_device.setCurrentIndex(i)
                        matched = True
                        break
                if not matched and ports:
                    self.cb_drawer_device.setCurrentIndex(0)
            else:
                self.cb_drawer_device.addItem("연결된 COM 포트 없음")
        else:
            self.lbl_device_title.setText("프린터:")
            printers = cash_drawer.get_available_printers()
            if printers:
                self.cb_drawer_device.addItems(printers)
                saved_pr = cfg.get("printer_name", "")
                if saved_pr in printers:
                    self.cb_drawer_device.setCurrentText(saved_pr)
                elif printers:
                    self.cb_drawer_device.setCurrentIndex(0)
            else:
                self.cb_drawer_device.addItem("설치된 프린터 없음")

    def save_drawer_settings(self):
        is_serial = self.rb_drawer_serial.isChecked()
        mode = "serial" if is_serial else "printer"
        selected = self.cb_drawer_device.currentText()
        
        updates = {
            "mode": mode,
            "auto_open": self.chk_drawer_auto.isChecked(),
            "sound_enabled": self.chk_drawer_sound.isChecked()
        }
        if is_serial:
            if selected and not selected.startswith("연결된"):
                updates["port"] = selected.split()[0]
        else:
            if selected and not selected.startswith("설치된"):
                updates["printer_name"] = selected
                
        cash_drawer.save_config(updates)
        self.lbl_drawer_status.setText("설정이 저장되었습니다.")
        QTimer.singleShot(3000, lambda: self.lbl_drawer_status.setText(""))
        CustomMessageDialog("설정 완료", "금전문함(돈통) 설정이 성공적으로 저장되었습니다.", 'info', self).exec()

    def test_open_drawer(self):
        self.lbl_drawer_status.setText("신호 전송 중...")
        cash_drawer.open_drawer_async(callback=self.drawerTestResult.emit)

    def on_drawer_test_finished(self, success, msg):
        if success:
            self.lbl_drawer_status.setText(f"열림 완료: {msg}")
            CustomMessageDialog("열림 성공", f"금전문함(돈통)에 신호가 성공적으로 전송되었습니다.\n({msg})", 'info', self).exec()
        else:
            self.lbl_drawer_status.setText(f"오류: {msg}")
            CustomMessageDialog("열림 실패", f"금전문함 신호 전송에 실패했습니다.\n오류: {msg}", 'warning', self).exec()
        QTimer.singleShot(4000, lambda: self.lbl_drawer_status.setText(""))
