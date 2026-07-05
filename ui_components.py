from PyQt6.QtWidgets import (QPushButton, QLabel, QFrame, QVBoxLayout, QDialog, 
                             QHBoxLayout, QSpinBox, QGraphicsDropShadowEffect, QLineEdit, QTextBrowser,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QDateEdit, QComboBox,
                             QWidget, QGridLayout, QProgressBar)
from PyQt6.QtCore import Qt, QDate, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QFont
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import os
import sys
import styles
import time
import random

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ActionButton(QPushButton):
    def __init__(self, text, style_sheet, icon_char=None, parent=None):
        super().__init__("", parent)
        self.setStyleSheet(style_sheet)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)
        
        self.original_icon_char = icon_char
        if icon_char:
            self.icon_label = QLabel(icon_char)
            self.icon_label.setFixedSize(36, 36) # Slightly larger icon container
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.icon_label.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); border-radius: 18px; color: white; border: 1px solid white; font-size: 14pt; font-weight: bold;")
            layout.addWidget(self.icon_label)
        else:
            self.icon_label = None
        
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet(f"color: white; font-weight: bold; border: none; background: transparent; font-size: {styles.FONT_SIZE_LARGE}; font-family: '{styles.FONT_FAMILY}';")
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label, 1)
        
        # Add a small spacer at the end to balance the icon's presence if it exists
        if icon_char:
            layout.addSpacing(10)
        
        # Make the button textually recognizable for accessibility or simple lookups
        self.setObjectName(text)
        self.is_checked = False

    def set_checked(self, checked):
        if not hasattr(self, 'icon_label') or not self.icon_label:
            return

        self.is_checked = checked
        if checked:
            self.icon_label.setText("✔")
            self.icon_label.setStyleSheet("background-color: #FBC02D; border-radius: 18px; color: #333; border: 1px solid #FBC02D; font-size: 16pt; font-weight: bold;")
        else:
            self.icon_label.setText(self.original_icon_char if self.original_icon_char else "")
            self.icon_label.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); border-radius: 18px; color: white; border: 1px solid white; font-size: 14pt; font-weight: bold;")

    def setText(self, text):
        super().setText("") # Always keep native QPushButton text empty
        if hasattr(self, 'text_label') and self.text_label:
            self.text_label.setText(text)
        self.setObjectName(text)

class StatusLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(styles.LABEL_HEADER_STYLE)

class SummaryFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.TOTAL_AREA_STYLE)

class EditItemDialog(QDialog):
    def __init__(self, barcode, product, current_qty, product_manager, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(850), styles.s(550))
        
        self.barcode = barcode
        self.product = product
        self.product_manager = product_manager
        self.delete_clicked = False
        self.current_qty = current_qty
        self.input_qty_str = str(current_qty)
        
        self.init_ui()
        
    def init_ui(self):
        # Background Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(830), styles.s(530))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: #2E3A59;
                border-radius: {styles.s(16)}px;
                border: 2px solid #1E293B;
            }}
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 6)
        self.container.setGraphicsEffect(shadow)
        
        main_layout = QHBoxLayout(self.container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # ========================================================
        # LEFT PANEL: 상품별 행사정보
        # ========================================================
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background-color: #F1F5F9; border-radius: 12px; border: none; }")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 20)
        left_layout.setSpacing(15)
        
        # Left Title Bar
        left_title_bar = QFrame()
        left_title_bar.setFixedHeight(50)
        left_title_bar.setStyleSheet("QFrame { background-color: #3C5087; border-top-left-radius: 12px; border-top-right-radius: 12px; border: none; }")
        left_title_layout = QHBoxLayout(left_title_bar)
        left_title_layout.setContentsMargins(15, 0, 15, 0)
        
        lbl_left_title = QLabel("상품별 행사정보")
        lbl_left_title.setStyleSheet(f"color: white; font-size: {styles.fs(14)}; font-weight: bold; font-family: '{styles.FONT_FAMILY}';")
        left_title_layout.addWidget(lbl_left_title)
        left_title_layout.addStretch()
        
        btn_close_x = QPushButton("✕")
        btn_close_x.setFixedSize(30, 30)
        btn_close_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_x.setStyleSheet("QPushButton { color: white; font-size: 14pt; border: none; background: transparent; } QPushButton:hover { color: #FF8A80; }")
        btn_close_x.clicked.connect(self.reject)
        left_title_layout.addWidget(btn_close_x)
        
        left_layout.addWidget(left_title_bar)
        
        # Left Content Frame
        left_content = QFrame()
        left_content.setStyleSheet("QFrame { background: transparent; border: none; }")
        left_content_layout = QVBoxLayout(left_content)
        left_content_layout.setContentsMargins(20, 10, 20, 10)
        left_content_layout.setSpacing(20)
        
        # Info sections styling helper
        def create_info_section(title, content_text):
            sec_layout = QVBoxLayout()
            sec_layout.setSpacing(5)
            
            lbl_sec_title = QLabel(f"◎ {title}")
            lbl_sec_title.setStyleSheet(f"font-size: {styles.fs(12.5)}; font-weight: bold; color: #1E293B; font-family: '{styles.FONT_FAMILY}';")
            
            lbl_sec_content = QLabel(content_text)
            lbl_sec_content.setWordWrap(True)
            lbl_sec_content.setStyleSheet(f"font-size: {styles.fs(11.5)}; color: #475569; font-family: '{styles.FONT_FAMILY}'; padding-left: 10px;")
            
            sec_layout.addWidget(lbl_sec_title)
            sec_layout.addWidget(lbl_sec_content)
            return sec_layout
            
        # Get Promo Names / Desc
        promo_type = self.product.get("promo_type", 0)
        promo_name = "-"
        promo_desc = "-"
        if promo_type == 1:
            promo_name = "1+1 행사"
            promo_desc = "1개 구매 시 1개 증정"
        elif promo_type == 2:
            promo_name = "2+1 행사"
            promo_desc = "2개 구매 시 1개 증정"
            
        # Fetch related products
        related_names = []
        if promo_type in [1, 2]:
            for bc, p_data in self.product_manager.get_all_products().items():
                if bc != self.barcode:
                    if p_data.get("category") == self.product.get("category") and p_data.get("promo_type") == promo_type:
                        related_names.append(p_data["name"])
        related_text = ", ".join(related_names[:3]) if related_names else "-"
        
        left_content_layout.addLayout(create_info_section("상품명", f"- {self.barcode} *{self.product['name']}"))
        left_content_layout.addLayout(create_info_section("행사명", f"- {promo_name}"))
        left_content_layout.addLayout(create_info_section("행사설명", f"- {promo_desc}"))
        left_content_layout.addLayout(create_info_section("연관상품", f"- {related_text}"))
        left_content_layout.addStretch()
        
        left_layout.addWidget(left_content, stretch=1)
        
        # ========================================================
        # RIGHT PANEL: 키패드 및 수량 제어
        # ========================================================
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background-color: #2E3A59; border-radius: 12px; border: none; }")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(12)
        
        # Qty Display Area
        self.qty_display_frame = QFrame()
        self.qty_display_frame.setFixedHeight(75)
        self.qty_display_frame.setStyleSheet("""
            QFrame {
                background-color: #2563EB;
                border-radius: 8px;
                border: 2px solid #3B82F6;
            }
        """)
        display_layout = QHBoxLayout(self.qty_display_frame)
        display_layout.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_qty_display = QLabel(self.input_qty_str)
        self.lbl_qty_display.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.lbl_qty_display.setStyleSheet(f"color: white; font-size: 28pt; font-weight: bold; font-family: '{styles.FONT_FAMILY}';")
        display_layout.addWidget(self.lbl_qty_display)
        
        right_layout.addWidget(self.qty_display_frame)
        
        # Action Control Buttons Row (수량변경, 등록취소)
        ctrl_btn_layout = QHBoxLayout()
        ctrl_btn_layout.setSpacing(8)
        
        btn_update = QPushButton("수량변경")
        btn_update.setFixedHeight(50)
        btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update.setStyleSheet(f"""
            QPushButton {{
                background-color: #4B5563;
                color: white;
                font-size: {styles.fs(13)};
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #374151; }}
        """)
        btn_update.clicked.connect(self.apply_qty)
        
        btn_delete = QPushButton("등록취소")
        btn_delete.setFixedHeight(50)
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: #4B5563;
                color: white;
                font-size: {styles.fs(13)};
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #991B1B; }}
        """)
        btn_delete.clicked.connect(self.delete_item)
        
        ctrl_btn_layout.addWidget(btn_update, stretch=1)
        ctrl_btn_layout.addWidget(btn_delete, stretch=1)
        right_layout.addLayout(ctrl_btn_layout)
        
        # Keypad Grid Layout (1-9, 0, BKSP)
        keypad_grid = QGridLayout()
        keypad_grid.setSpacing(8)
        
        keypad_buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("0", 3, 0), ("⬅ BKSP", 3, 1, 1, 2)
        ]
        
        for item in keypad_buttons:
            text = item[0]
            row = item[1]
            col = item[2]
            rowspan = item[3] if len(item) > 3 else 1
            colspan = item[4] if len(item) > 4 else 1
            
            btn = QPushButton(text)
            btn.setFixedHeight(styles.s(55))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #374151;
                    color: white;
                    font-size: {styles.fs(15)};
                    font-weight: bold;
                    border-radius: 6px;
                    border: none;
                }}
                QPushButton:hover {{ background-color: #4B5563; }}
                QPushButton:pressed {{ background-color: #1F2937; }}
            """)
            
            if text.isdigit():
                btn.clicked.connect(lambda checked, t=text: self.key_pressed(t))
            else:
                btn.clicked.connect(self.backspace_pressed)
                
            keypad_grid.addWidget(btn, row, col, rowspan, colspan)
            
        right_layout.addLayout(keypad_grid)
        
        # Bottom Close Button
        btn_cancel = QPushButton("닫기 [CLEAR]")
        btn_cancel.setFixedHeight(50)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #1F2937;
                color: white;
                font-size: {styles.fs(12.5)};
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #111827; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        right_layout.addWidget(btn_cancel)
        
        # Assemble panels into Main layout
        main_layout.addWidget(left_panel, stretch=55)
        main_layout.addWidget(right_panel, stretch=45)
        
    def key_pressed(self, num_char):
        if self.input_qty_str == "0" or self.input_qty_str == "1" and len(self.input_qty_str) == 1:
            self.input_qty_str = num_char
        else:
            if len(self.input_qty_str) < 3: # Limit to 3 digits (up to 999)
                self.input_qty_str += num_char
        self.update_display()
        
    def backspace_pressed(self):
        if len(self.input_qty_str) > 1:
            self.input_qty_str = self.input_qty_str[:-1]
        else:
            self.input_qty_str = "1"
        self.update_display()
        
    def update_display(self):
        self.lbl_qty_display.setText(self.input_qty_str)
        
    def apply_qty(self):
        try:
            val = int(self.input_qty_str)
            if val < 1:
                val = 1
        except ValueError:
            val = 1
        self.current_qty = val
        self.accept()
        
    def delete_item(self):
        self.delete_clicked = True
        self.accept()
        
    def get_new_qty(self):
        return self.current_qty

class PromotionDialog(QDialog):
    def __init__(self, title, message, promo_type, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.promo_type = promo_type # 1 for 1+1, 2 for 2+1
        self.init_ui(title, message)
        
    def init_ui(self, title, message):
        self.setFixedSize(styles.s(500), styles.s(300))
        # Theme color based on promo type
        color = "#F44336" if self.promo_type == 1 else "#FF9800" # Red for 1+1, Orange for 2+1
        self.setStyleSheet(f"background-color: white; border: 4px solid {color}; border-radius: 20px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon/Label
        promo_text = "1 + 1" if self.promo_type == 1 else "2 + 1"
        lbl_promo = QLabel(promo_text)
        lbl_promo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_promo.setStyleSheet(f"font-size: {styles.fs(48)}; font-weight: bold; color: {color}; border: none;")
        layout.addWidget(lbl_promo)
        
        # Message
        lbl_msg = QLabel(message)
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_msg.setStyleSheet(f"font-size: {styles.fs(20)}; font-weight: bold; color: #333; border: none;")
        lbl_msg.setWordWrap(True)
        layout.addWidget(lbl_msg)
        
        layout.addStretch()
        
        # Close Button
        btn_close = QPushButton("확인")
        btn_close.setFixedHeight(styles.s(60))
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: {styles.fs(20)};
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }}
            QPushButton:hover {{ background-color: {color}CC; }}
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

class PromoAlertWithRelatedDialog(QDialog):
    def __init__(self, product, related_items, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.product = product
        self.related_items = related_items[:3] # Limit to top 3 for clean layout
        self.added_barcode = None
        self.init_ui()
        
    def init_ui(self):
        # Determine theme color
        promo_type = self.product.get("promo_type", 1)
        color = "#EF4444" if promo_type == 1 else "#F59E0B" # Red for 1+1, Orange for 2+1
        promo_name = "1 + 1" if promo_type == 1 else "2 + 1"
        
        self.setFixedSize(styles.s(550), styles.s(450))
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #FFFFFF;
                border: 4px solid {color};
                border-radius: 20px;
            }}
            QLabel {{
                color: #1F2937;
                background: transparent;
                border: none;
                font-family: '{styles.FONT_FAMILY}';
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # 1. Promotion Badge Header
        hdr_layout = QHBoxLayout()
        
        badge_lbl = QLabel(promo_name)
        badge_lbl.setFixedSize(styles.s(140), styles.s(60))
        badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_lbl.setStyleSheet(f"""
            background-color: {color};
            color: white;
            font-size: {styles.fs(24)};
            font-weight: bold;
            border-radius: 30px;
        """)
        hdr_layout.addWidget(badge_lbl)
        
        title_lbl = QLabel("행사 상품 스캔 안내")
        title_lbl.setStyleSheet(f"font-size: {styles.fs(18)}; font-weight: bold; color: {color};")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()
        
        layout.addLayout(hdr_layout)
        
        # 2. Main Product Info
        info_frame = QFrame()
        if promo_type == 1:
            info_frame.setStyleSheet("""
                QFrame {
                    background-color: #FEE2E2;
                    border: 1px solid #FECACA;
                    border-radius: 10px;
                }
            """)
        else:
            info_frame.setStyleSheet("""
                QFrame {
                    background-color: #FEF3C7;
                    border: 1px solid #FDE68A;
                    border-radius: 10px;
                }
            """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        msg_lbl = QLabel(f"📢 <b>{self.product['name']}</b>")
        msg_lbl.setStyleSheet(f"font-size: {styles.fs(13)}; color: #1F2937;")
        msg_lbl.setWordWrap(True)
        
        sub_msg = QLabel("행사 대상 상품이 스캔되었습니다. 덤 증정 혜택을 챙겨주세요!")
        sub_msg.setStyleSheet(f"font-size: {styles.fs(10)}; color: #4B5563;")
        
        info_layout.addWidget(msg_lbl)
        info_layout.addWidget(sub_msg)
        layout.addWidget(info_frame)
        
        # 3. Related Products Section
        lbl_related = QLabel("🔗 연관 행사 상품 (카테고리 내 동일 행사)")
        lbl_related.setStyleSheet(f"font-size: {styles.fs(11)}; font-weight: bold; color: #475569;")
        layout.addWidget(lbl_related)
        
        related_layout = QHBoxLayout()
        related_layout.setSpacing(10)
        
        if not self.related_items:
            empty_lbl = QLabel("동일 행사의 다른 연관 상품이 존재하지 않습니다.")
            empty_lbl.setStyleSheet(f"color: #9CA3AF; font-size: {styles.fs(10)}; font-style: italic;")
            related_layout.addWidget(empty_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            for item in self.related_items:
                card = QFrame()
                card.setStyleSheet("""
                    QFrame {
                        background-color: #F9FAFB;
                        border: 1px solid #E5E7EB;
                        border-radius: 8px;
                    }
                    QFrame:hover {
                        border: 1px solid #6366F1;
                        background-color: #EEF2F6;
                    }
                """)
                card_lyt = QVBoxLayout(card)
                card_lyt.setContentsMargins(8, 8, 8, 8)
                card_lyt.setSpacing(4)
                
                # Check if image exists in photo/ or assets/
                img_lbl = QLabel()
                img_lbl.setFixedSize(styles.s(70), styles.s(70))
                img_lbl.setStyleSheet("background-color: white; border: 1px solid #E5E7EB;")
                
                img_path = None
                for ext in ["png", "jpg", "jpeg", "webp"]:
                    p = os.path.join(os.path.abspath("."), "photo", f"{item['barcode']}.{ext}")
                    if os.path.exists(p):
                        img_path = p
                        break
                if not img_path:
                    # Fallback to default mascot
                    img_path = resource_path(os.path.join("assets", "image", "cu_mascot_fullbody_white_background_1767715363864.png"))
                    
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    img_lbl.setPixmap(pixmap.scaled(styles.s(70), styles.s(70), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                
                name_lbl = QLabel(item["name"])
                name_lbl.setStyleSheet(f"font-size: {styles.fs(9)}; font-weight: bold; max-height: {styles.s(30)}px;")
                name_lbl.setWordWrap(True)
                name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                price_lbl = QLabel(f"{item['price']:,}원")
                price_lbl.setStyleSheet(f"font-size: {styles.fs(8.5)}; color: #4B5563; font-weight: bold;")
                price_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                add_btn = QPushButton("선택 추가")
                add_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        font-size: {styles.fs(8.5)};
                        font-weight: bold;
                        border-radius: 4px;
                        border: none;
                        padding: 3px;
                    }}
                    QPushButton:hover {{ background-color: {color}CC; }}
                """)
                add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                add_btn.clicked.connect(lambda checked, bc=item["barcode"]: self.select_add_item(bc))
                
                card_lyt.addWidget(img_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
                card_lyt.addWidget(name_lbl)
                card_lyt.addWidget(price_lbl)
                card_lyt.addWidget(add_btn)
                
                related_layout.addWidget(card)
                
        layout.addLayout(related_layout)
        layout.addStretch()
        
        # 4. Confirm/Close
        btn_close = QPushButton("확인")
        btn_close.setFixedHeight(styles.s(45))
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: #374151;
                color: white;
                font-size: {styles.fs(12)};
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #4B5563; }}
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
    def select_add_item(self, barcode):
        self.added_barcode = barcode
        self.accept()

class CustomMessageDialog(QDialog):
    """
    A beautiful custom dialog to replace QMessageBox.
    types: 'info', 'warning', 'question'
    """
    def __init__(self, title, message, type='info', parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 320)
        
        self.result_value = False
        self.init_time = time.time()
        
        # Main Container with rounding and shadow
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 480, 300)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: 15px;
                border: 1px solid {styles.BORDER_COLOR};
            }}
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 20)
        
        # Header (Color coded by type)
        header_color = styles.PRIMARY_PURPLE
        if type == 'warning':
            header_color = "#FFA726" # Orange
        elif type == 'question':
            header_color = styles.ACCENT_GREEN
            
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {header_color};
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: white; font-size: 14pt; font-weight: bold; font-family: 'Malgun Gothic';")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(header)
        
        # Message Body
        msg_frame = QFrame()
        msg_frame.setStyleSheet("background-color: transparent; border: none;") # Transparent inside container
        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(f"color: {styles.TEXT_COLOR}; font-size: 12pt; font-family: 'Malgun Gothic';")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        msg_layout.addWidget(lbl_msg)
        layout.addWidget(msg_frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(20, 0, 20, 0)
        
        if type == 'question':
            btn_yes = QPushButton("예 (Yes)")
            btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_yes.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.ACCENT_GREEN};
                    color: white;
                    border-radius: 8px;
                    padding: 8px 20px;
                    font-size: 11pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {styles.DARK_GREEN}; }}
            """)
            btn_yes.clicked.connect(self.accept_dialog)
            
            btn_no = QPushButton("아니오 (No)")
            btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_no.setStyleSheet(f"""
                QPushButton {{
                    background-color: #BDBDBD;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 20px;
                    font-size: 11pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: #9E9E9E; }}
            """)
            btn_no.clicked.connect(self.reject_dialog)
            
            btn_layout.addStretch()
            btn_layout.addWidget(btn_yes)
            btn_layout.addWidget(btn_no)
            btn_layout.addStretch()
            
        else: # Info or Warning
            btn_ok = QPushButton("확인 (OK)")
            btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ok.setStyleSheet(f"""
                QPushButton {{
                    background-color: {header_color};
                    color: white;
                    border-radius: 8px;
                    padding: 8px 30px;
                    font-size: 11pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: #E0E0E0; }}
            """)
            btn_ok.clicked.connect(self.accept_dialog)
            
            btn_layout.addStretch()
            btn_layout.addWidget(btn_ok)
            btn_layout.addStretch()
            
        layout.addLayout(btn_layout)

    def accept_dialog(self):
        self.result_value = True
        self.accept()

    def reject_dialog(self):
        self.result_value = False
        self.reject()

class SafeBalanceEditDialog(QDialog):
    def __init__(self, current_amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Calculate maximum units for storage
        self.current_amount = current_amount
        # base change fund is 100,000 won
        self.max_units = max(0, (self.current_amount - 100000) // 10000)
        self.new_amount = self.current_amount
        
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(styles.s(550), styles.s(350))
        
        # Main Container
        self.container = QFrame(self)
        self.container.setObjectName("container_frame")
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(530), styles.s(330))
        self.container.setStyleSheet(f"""
            QFrame#container_frame {{
                background-color: #EEEEEE;
                border-radius: 6px;
                border: 1px solid #7F8C8D;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, styles.s(15))
        main_layout.setSpacing(styles.s(10))
        
        # 1. Header (Title Bar)
        header = QFrame()
        header.setObjectName("header_frame")
        header.setStyleSheet("""
            QFrame#header_frame {
                background-color: #2D2F3A;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border: none;
            }
        """)
        header.setFixedHeight(styles.s(45))
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(styles.s(15), 0, styles.s(15), 0)
        
        lbl_title = QLabel("금고보관")
        lbl_title.setStyleSheet(f"color: white; font-size: {styles.fs(13)}; font-weight: bold; font-family: '{styles.FONT_FAMILY}';")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        btn_close_x = QPushButton("✕")
        btn_close_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_x.setFixedSize(styles.s(30), styles.s(30))
        btn_close_x.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: #BDC3C7;
                font-size: {styles.fs(14)};
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #EF5350;
            }}
        """)
        btn_close_x.clicked.connect(self.reject)
        header_layout.addWidget(btn_close_x)
        
        main_layout.addWidget(header)
        
        # Content Layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(styles.s(20), styles.s(5), styles.s(20), styles.s(5))
        content_layout.setSpacing(styles.s(12))
        
        # 2. Hint Message
        lbl_hint = QLabel("당일 금고보관가능금액 이내에서 금고보관액을 입력하여 주십시오.")
        lbl_hint.setStyleSheet(f"color: #A0522D; font-size: {styles.fs(11)}; font-weight: bold; font-family: '{styles.FONT_FAMILY}';")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(lbl_hint)
        
        # 3. Grid Table
        grid_table = QGridLayout()
        grid_table.setSpacing(0)
        
        lbl_cash_title = QLabel("현재현금시재")
        lbl_cash_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl_cash_title.setStyleSheet(f"""
            background-color: #D6E0E6;
            color: #333333;
            font-family: '{styles.FONT_FAMILY}';
            font-size: {styles.fs(11)};
            font-weight: bold;
            border-top: 1px solid #BDC3C7;
            border-left: 1px solid #BDC3C7;
            border-bottom: 1px solid #BDC3C7;
            border-right: 1px solid #BDC3C7;
            padding: {styles.s(8)}px {styles.s(15)}px;
        """)
        
        lbl_cash_val = QLabel(f"{self.current_amount:,} 원")
        lbl_cash_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_cash_val.setStyleSheet(f"""
            background-color: #FFFFFF;
            color: #333333;
            font-family: '{styles.FONT_FAMILY}';
            font-size: {styles.fs(11)};
            font-weight: bold;
            border-top: 1px solid #BDC3C7;
            border-right: 1px solid #BDC3C7;
            border-bottom: 1px solid #BDC3C7;
            border-left: none;
            padding: {styles.s(8)}px {styles.s(15)}px;
        """)
        
        lbl_avail_title = QLabel("당일금고보관가능금액")
        lbl_avail_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl_avail_title.setStyleSheet(f"""
            background-color: #D6E0E6;
            color: #333333;
            font-family: '{styles.FONT_FAMILY}';
            font-size: {styles.fs(11)};
            font-weight: bold;
            border-left: 1px solid #BDC3C7;
            border-bottom: 1px solid #BDC3C7;
            border-right: 1px solid #BDC3C7;
            border-top: none;
            padding: {styles.s(8)}px {styles.s(15)}px;
        """)
        
        lbl_avail_val = QLabel(f"{self.max_units:,} 만원")
        lbl_avail_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_avail_val.setStyleSheet(f"""
            background-color: #FFFFFF;
            color: #333333;
            font-family: '{styles.FONT_FAMILY}';
            font-size: {styles.fs(11)};
            font-weight: bold;
            border-right: 1px solid #BDC3C7;
            border-bottom: 1px solid #BDC3C7;
            border-left: none;
            border-top: none;
            padding: {styles.s(8)}px {styles.s(15)}px;
        """)
        
        grid_table.addWidget(lbl_cash_title, 0, 0)
        grid_table.addWidget(lbl_cash_val, 0, 1)
        grid_table.addWidget(lbl_avail_title, 1, 0)
        grid_table.addWidget(lbl_avail_val, 1, 1)
        grid_table.setColumnStretch(0, 1)
        grid_table.setColumnStretch(1, 1)
        content_layout.addLayout(grid_table)
        
        content_layout.addSpacing(styles.s(5))
        
        # 4. Input Row
        input_row_layout = QHBoxLayout()
        input_row_layout.setSpacing(styles.s(8))
        input_row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Bullet Icon Widget
        lbl_bullet = QLabel("▶")
        lbl_bullet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_bullet.setFixedSize(styles.s(18), styles.s(18))
        lbl_bullet.setStyleSheet("""
            QLabel {
                background-color: #2D3748;
                color: white;
                border-radius: 9px;
                font-size: 7pt;
                font-weight: bold;
                border: none;
            }
        """)
        input_row_layout.addWidget(lbl_bullet)
        
        lbl_input_title = QLabel("금고보관액")
        lbl_input_title.setStyleSheet(f"font-family: '{styles.FONT_FAMILY}'; font-size: {styles.fs(11)}; font-weight: bold; color: #333;")
        input_row_layout.addWidget(lbl_input_title)
        
        input_row_layout.addSpacing(styles.s(10))
        
        # Input wrapper for QLineEdit and "만원"
        input_wrapper = QFrame()
        input_wrapper.setFixedHeight(styles.s(40))
        input_wrapper.setStyleSheet("QFrame { border: 1px solid #BDC3C7; background-color: white; border-radius: 2px; }")
        
        wrapper_layout = QHBoxLayout(input_wrapper)
        wrapper_layout.setContentsMargins(styles.s(5), 0, 0, 0)
        wrapper_layout.setSpacing(0)
        
        self.txt_amount = QLineEdit()
        self.txt_amount.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.txt_amount.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(12)};
                font-weight: bold;
                color: #333;
                padding-right: {styles.s(5)}px;
            }}
        """)
        wrapper_layout.addWidget(self.txt_amount)
        
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet("background-color: #BDC3C7; border: none;")
        wrapper_layout.addWidget(sep)
        
        lbl_unit = QLabel("만원")
        lbl_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_unit.setFixedWidth(styles.s(60))
        lbl_unit.setStyleSheet(f"""
            QLabel {{
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11)};
                font-weight: bold;
                color: #333;
                background-color: #F5F7FA;
                border-top-right-radius: 2px;
                border-bottom-right-radius: 2px;
                border: none;
            }}
        """)
        wrapper_layout.addWidget(lbl_unit)
        
        input_row_layout.addWidget(input_wrapper, stretch=1)
        content_layout.addLayout(input_row_layout)
        
        main_layout.addLayout(content_layout)
        
        main_layout.addStretch()
        
        # 5. Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(styles.s(10))
        btn_layout.setContentsMargins(0, 0, styles.s(20), 0)
        btn_layout.addStretch()
        
        # Style for confirmation and close buttons
        btn_style = f"""
            QPushButton {{
                background-color: #2D2F3A;
                color: white;
                border-radius: {styles.s(4)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11)};
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #4A4D5C;
            }}
            QPushButton:pressed {{
                background-color: #1A1B22;
            }}
        """
        
        btn_clear = QPushButton("닫기 [CLEAR]")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setFixedSize(styles.s(130), styles.s(40))
        btn_clear.setStyleSheet(btn_style)
        btn_clear.clicked.connect(self.process_clear)
        btn_layout.addWidget(btn_clear)
        
        btn_ok = QPushButton("확인")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setFixedSize(styles.s(130), styles.s(40))
        btn_ok.setStyleSheet(btn_style)
        btn_ok.clicked.connect(self.process_save)
        btn_layout.addWidget(btn_ok)
        
        main_layout.addLayout(btn_layout)
        
        # Auto-focus the input line edit
        self.txt_amount.setFocus()

    def process_clear(self):
        self.reject()

    def process_save(self):
        txt = self.txt_amount.text().strip()
        if not txt:
            CustomMessageDialog("오류", "보관할 금액을 입력해 주세요.", 'warning', self).exec()
            self.txt_amount.setFocus()
            return
            
        if not txt.isdigit():
            CustomMessageDialog("오류", "숫자만 입력해 주세요.", 'warning', self).exec()
            self.txt_amount.setFocus()
            return
            
        units = int(txt)
        if units <= 0:
            CustomMessageDialog("오류", "1 만원 이상 입력해 주세요.", 'warning', self).exec()
            self.txt_amount.setFocus()
            return
            
        if units > self.max_units:
            CustomMessageDialog("오류", f"보관 가능 금액({self.max_units} 만원)을 초과할 수 없습니다.", 'warning', self).exec()
            self.txt_amount.setFocus()
            return
            
        # Success! Calculate new drawer cash total
        self.new_amount = self.current_amount - (units * 10000)
        self.accept()

    def get_amount(self):
        return self.new_amount

class ReceiptPreviewDialog(QDialog):
    def __init__(self, html_content, parent=None, title="기 결제 영수증 확인", height=700):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, height)
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 430, height - 20)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: 15px;
                border: 1px solid {styles.BORDER_COLOR};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 20)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {styles.PRIMARY_PURPLE};
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; font-family: 'Malgun Gothic';")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Receipt View
        self.view = QTextBrowser()
        self.view.setHtml(html_content)
        self.view.setStyleSheet("border: none; background: white; margin: 10px;")
        layout.addWidget(self.view)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(30, 0, 30, 0)
        
        btn_print = QPushButton("출력")
        btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_print.setFixedHeight(50)
        btn_print.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.ACCENT_GREEN};
                color: white;
                border-radius: 10px;
                font-size: 14pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {styles.DARK_GREEN}; }}
        """)
        btn_print.clicked.connect(self.print_receipt)
        
        btn_close = QPushButton("닫기")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedHeight(50)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #BDBDBD;
                color: white;
                border-radius: 10px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #9E9E9E; }
        """)
        btn_close.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_print, stretch=2)
        btn_layout.addWidget(btn_close, stretch=1)
        layout.addLayout(btn_layout)

    def print_receipt(self):
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            
            # Open print dialog for the user to select printer
            dialog = QPrintDialog(printer, self)
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                self.view.print(printer)
                self.accept()
        except Exception as e:
            from ui_components import CustomMessageDialog
            CustomMessageDialog("출력 오류", f"프린터 초기화 중 오류가 발생했습니다.\n{str(e)}", 'warning', self).exec()

class StoreRegistrationDialog(QDialog):
    def __init__(self, store_info, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 620)
        
        self.store_info = store_info
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 480, 600)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: 15px;
                border: 1px solid {styles.BORDER_COLOR};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(10)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {styles.PRIMARY_PURPLE};
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        
        lbl_title = QLabel("점포 정보 등록 / 수정")
        lbl_title.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; font-family: 'Malgun Gothic';")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 10, 30, 10)
        content_layout.setSpacing(15)
        
        def add_input_row(label, value):
            v_box = QVBoxLayout()
            v_box.setSpacing(5)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: #666; font-size: 10pt; font-weight: bold;")
            v_box.addWidget(lbl)
            
            edit = QLineEdit(value)
            edit.setFixedHeight(40)
            edit.setStyleSheet(f"""
                QLineEdit {{
                    font-size: 11pt;
                    color: {styles.TEXT_COLOR};
                    border: 1px solid {styles.BORDER_COLOR};
                    border-radius: 5px;
                    padding-left: 10px;
                    background-color: #F9F9F9;
                }}
                QLineEdit:focus {{
                    border: 2px solid {styles.PRIMARY_PURPLE};
                    background-color: white;
                }}
            """)
            v_box.addWidget(edit)
            content_layout.addLayout(v_box)
            return edit

        self.edit_name = add_input_row("점포명 (Store Name)", store_info.get("store_name", ""))
        self.edit_biz = add_input_row("사업자등록번호 (Biz Num)", store_info.get("biz_num", ""))
        self.edit_addr = add_input_row("주소 (Address)", store_info.get("address", ""))
        self.edit_owner = add_input_row("대표자명 (Owner)", store_info.get("owner", ""))
        self.edit_tel = add_input_row("전화번호 (Tel)", store_info.get("tel", ""))
        
        # Beep Sound Setting Checkbox
        from PyQt6.QtWidgets import QCheckBox
        self.cb_beep = QCheckBox("버튼 클릭 기계음(\"삐\" 소리) 사용")
        self.cb_beep.setChecked(getattr(styles, "BEEP_ENABLED", True))
        self.cb_beep.setStyleSheet("""
            QCheckBox {
                font-size: 11pt;
                font-weight: bold;
                color: #374151;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        content_layout.addWidget(self.cb_beep)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(30, 0, 30, 0)
        
        btn_save = QPushButton("저장")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFixedHeight(50)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.ACCENT_GREEN};
                color: white;
                border-radius: 10px;
                font-size: 13pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {styles.DARK_GREEN}; }}
        """)
        btn_save.clicked.connect(self.process_save)
        
        btn_cancel = QPushButton("취소")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedHeight(50)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #BDBDBD;
                color: white;
                border-radius: 10px;
                font-size: 13pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #9E9E9E; }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save, stretch=2)
        btn_layout.addWidget(btn_cancel, stretch=1)
        layout.addLayout(btn_layout)

    def process_save(self):
        import styles
        styles.BEEP_ENABLED = self.cb_beep.isChecked()
        self.new_info = {
            "store_name": self.edit_name.text().strip(),
            "biz_num": self.edit_biz.text().strip(),
            "address": self.edit_addr.text().strip(),
            "owner": self.edit_owner.text().strip(),
            "tel": self.edit_tel.text().strip(),
            "beep_enabled": self.cb_beep.isChecked()
        }
        self.accept()

class ProductInquiryDialog(QDialog):
    def __init__(self, product_manager, sales_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(1000), styles.s(700))
        
        self.product_manager = product_manager
        self.sales_mode = sales_mode
        self.selected_barcode = None
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(980), styles.s(680))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(15)}px;
                border: 1px solid {styles.BORDER_COLOR};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        # Main Vertical Layout
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, styles.s(15))
        layout.setSpacing(styles.s(12))
        
        # 1. Header Frame
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {styles.PRIMARY_PURPLE};
            border-top-left-radius: {styles.s(15)}px;
            border-top-right-radius: {styles.s(15)}px;
            border: none;
        """)
        header.setFixedHeight(styles.s(55))
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        lbl_title = QLabel("상품 조회/등록")
        lbl_title.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; font-family: 'Malgun Gothic';")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("통합조회 > 상품 조회/등록")
        lbl_breadcrumb.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 11pt; font-weight: bold;")
        header_layout.addWidget(lbl_breadcrumb)
        
        layout.addWidget(header)
        
        # Styles for inputs
        EDITABLE_STYLE = f"""
            QLineEdit {{
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 10px;
                padding-right: 10px;
                font-size: {styles.fs(12)};
                min-height: {styles.s(38)}px;
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
                font-size: {styles.fs(12)};
                font-weight: bold;
                min-height: {styles.s(38)}px;
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
                font-size: {styles.fs(12)};
                font-weight: bold;
                min-height: {styles.s(38)}px;
            }}
        """
        
        LBL_STYLE = "font-size: 11pt; font-weight: bold; color: #475569;"
        
        # 2. Split Content (Left Form / Right Image & List)
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent; border: none;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        content_layout.setSpacing(25)
        
        # --- Left Column (Details Form) ---
        left_panel = QFrame()
        left_panel.setStyleSheet("background: transparent; border: none;")
        left_layout = QGridLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 바코드 (Search Input)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("바코드 번호를 스캔하거나 입력")
        self.txt_search.setStyleSheet(EDITABLE_STYLE)
        self.txt_search.textChanged.connect(self.on_search_changed)
        
        btn_search_name = QPushButton("상품명으로 조회")
        btn_search_name.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search_name.setFixedHeight(styles.s(38))
        btn_search_name.setStyleSheet(f"""
            QPushButton {{
                background-color: #2D3E50;
                color: white;
                font-size: 10pt;
                font-weight: bold;
                border-radius: 4px;
                padding-left: 15px;
                padding-right: 15px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #1F2B38; }}
        """)
        btn_search_name.clicked.connect(lambda: self.txt_search.setFocus())
        
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
        cat_box.setSpacing(6)
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
        self.txt_promo_info.setFixedHeight(styles.s(130))
        self.txt_promo_info.setStyleSheet(f"""
            QTextBrowser {{
                background-color: #E2E8F0;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 8px;
                font-size: {styles.fs(11)};
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
        self.lbl_product_image.setFixedSize(styles.s(160), styles.s(180))
        self.lbl_product_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_product_image.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 6px; background-color: white;")
        
        top_row.addWidget(self.lbl_product_image)
        
        # Products Search List Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["바코드", "상품명"])
        self.table.setFixedHeight(styles.s(180))
        
        TABLE_QSS = f"""
            QTableWidget {{
                background-color: white;
                color: #333333;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                gridline-color: #F3F4F6;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(11)};
                selection-background-color: #EDE9FE;
                selection-color: #1E1B4B;
            }}
            QHeaderView::section {{
                background-color: #F3F4F6;
                color: #4B5563;
                padding: 4px;
                border: none;
                font-weight: bold;
            }}
        """
        self.table.setStyleSheet(TABLE_QSS)
        self.table.verticalScrollBar().setStyleSheet(styles.SCROLLBAR_STYLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(styles.s(32))
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.table.doubleClicked.connect(self.process_selection)
        
        header = self.table.horizontalHeader()
        self.table.setColumnWidth(0, styles.s(120))
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        top_row.addWidget(self.table)
        right_layout_v.addLayout(top_row)
        
        # Bottom half: Additional Status Grid
        status_grid = QGridLayout()
        status_grid.setSpacing(10)
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
        
        layout.addWidget(content_widget, stretch=1)
        
        # 3. Bottom Action Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(styles.s(15))
        btn_layout.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        btn_action_text = "상품 추가" if self.sales_mode else "판매 등록"
        btn_action_color = "#10B981" if self.sales_mode else styles.PRIMARY_PURPLE
        btn_action_hover = "#059669" if self.sales_mode else "#6366F1"
        
        self.btn_select = QPushButton(btn_action_text)
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.setFixedHeight(styles.s(50))
        self.btn_select.setMinimumWidth(styles.s(200))
        self.btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_action_color};
                color: white;
                border-radius: {styles.s(6)}px;
                font-size: {styles.fs(13)};
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: {btn_action_hover}; }}
        """)
        self.btn_select.clicked.connect(self.process_selection)
        
        btn_close = QPushButton("닫기")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedHeight(styles.s(50))
        btn_close.setMinimumWidth(styles.s(120))
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: #F3F4F6;
                color: #4B5563;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                font-size: {styles.fs(13)};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #E5E7EB; color: #1F2937; }}
        """)
        btn_close.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        # Load products list to table
        self.load_data()
        
        # Focus on search input by default
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
            # Mascot placeholder
            img_path = resource_path(os.path.join("assets", "image", "cu_mascot_fullbody_white_background_1767715363864.png"))
            pixmap = QPixmap(img_path)
            self.lbl_product_image.setPixmap(pixmap.scaled(styles.s(160), styles.s(180), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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
        img_path = None
        for ext in ["png", "jpg", "jpeg", "webp"]:
            p = os.path.join(os.path.abspath("."), "photo", f"{barcode}.{ext}")
            if os.path.exists(p):
                img_path = p
                break
                
        if not img_path:
            for ext in ["png", "jpg", "jpeg"]:
                p = resource_path(os.path.join("assets", "image", f"{barcode}.{ext}"))
                if os.path.exists(p):
                    img_path = p
                    break
                    
        if not img_path:
            img_path = resource_path(os.path.join("assets", "image", "cu_mascot_fullbody_white_background_1767715363864.png"))
            
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.lbl_product_image.setPixmap(pixmap.scaled(styles.s(160), styles.s(180), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
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
            self.accept()
            
    def get_selected_barcode(self):
        return self.selected_barcode

class VoucherExchangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(500), styles.s(320))
        
        self.result_value = False
        
        # Main Container with rounding and shadow
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(480), styles.s(300))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: 15px;
                border: 1px solid {styles.BORDER_COLOR};
            }}
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, styles.s(20))
        layout.setSpacing(styles.s(15))
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #546E7A;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header.setFixedHeight(styles.s(50))
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        lbl_title = QLabel("질의 메시지")
        lbl_title.setStyleSheet("color: white; font-size: 14pt; font-weight: bold; font-family: 'Malgun Gothic';")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Close '✕' Button on Top Right (like in screenshot)
        btn_close_x = QPushButton("✕")
        btn_close_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_x.setFixedSize(styles.s(30), styles.s(30))
        btn_close_x.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover { color: #FFCDD2; }
        """)
        btn_close_x.clicked.connect(self.reject_dialog)
        header_layout.addWidget(btn_close_x, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        layout.addWidget(header)
        
        # Message Body
        msg_frame = QFrame()
        msg_frame.setStyleSheet("background-color: transparent; border: none;")
        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setContentsMargins(styles.s(20), styles.s(20), styles.s(20), styles.s(20))
        
        lbl_msg = QLabel("※ 다른 상품으로 교환하시겠습니까?\n동일 상품 교환이 불가능할 시 동일 가격 이상의 다른 상품으로 교환이 가능하며 차액은 추가 결제해주시면 됩니다.")
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(f"color: {styles.TEXT_COLOR}; font-size: 12pt; font-family: 'Malgun Gothic'; font-weight: bold;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        msg_layout.addWidget(lbl_msg)
        layout.addWidget(msg_frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(styles.s(15))
        btn_layout.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        # 아니오 [CLEAR] (left button)
        btn_no = QPushButton("아니오 [CLEAR]")
        btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_no.setFixedHeight(styles.s(45))
        btn_no.setStyleSheet(f"""
            QPushButton {{
                background-color: #2D2F3A;
                color: white;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                font-family: 'Malgun Gothic';
            }}
            QPushButton:hover {{ background-color: #4A4D5C; }}
        """)
        btn_no.clicked.connect(self.reject_dialog)
        
        # 예 [반복/입력] (right button)
        btn_yes = QPushButton("예 [반복/입력]")
        btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_yes.setFixedHeight(styles.s(45))
        btn_yes.setStyleSheet(f"""
            QPushButton {{
                background-color: #546E7A;
                color: white;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                font-family: 'Malgun Gothic';
            }}
            QPushButton:hover {{ background-color: #78909C; }}
        """)
        btn_yes.clicked.connect(self.accept_dialog)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_no, stretch=1)
        btn_layout.addWidget(btn_yes, stretch=1)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

    def accept_dialog(self):
        self.result_value = True
        self.accept()

    def reject_dialog(self):
        self.result_value = False
        self.reject()

class KeepingLookupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(650, 480)
        self.phone_number = ""
        self.result_value = False
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 630, 460)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: #E2E8F0;
                border-radius: 12px;
                border: 1px solid #CBD5E0;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        # Main Layout
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Title
        self.lbl_window_title = QLabel("[키핑쿠폰 발급 회원 조회]")
        self.lbl_window_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_window_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2D3748; border: none; background: transparent;")
        layout.addWidget(self.lbl_window_title)
        
        # Dark Main Box Frame
        dark_box = QFrame()
        dark_box.setStyleSheet("""
            QFrame {
                background-color: #4A5568;
                border-radius: 8px;
                border: none;
            }
        """)
        dark_layout = QHBoxLayout(dark_box)
        dark_layout.setContentsMargins(20, 20, 20, 20)
        dark_layout.setSpacing(20)
        
        # Left Illustration Area (QFrame or QLabel)
        img_label = QLabel()
        img_label.setFixedSize(160, 140)
        img_label.setStyleSheet("background-color: white; border-radius: 6px; border: none;")
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Let's try loading cu_receipt_scan_illustration or mascot image
        ill_path = resource_path(os.path.join("assets", "image", "cu_receipt_scan_illustration.png"))
        if os.path.exists(ill_path):
            pixmap = QPixmap(ill_path)
            # Scale to fit
            scaled_pixmap = pixmap.scaled(150, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(scaled_pixmap)
        else:
            img_label.setText("CU Scanner")
            img_label.setStyleSheet("background-color: #CBD5E0; color: #4A5568; font-weight: bold; border-radius: 6px; border: none;")
            
        dark_layout.addWidget(img_label)
        
        # Right Text Column
        right_column = QVBoxLayout()
        right_column.setSpacing(10)
        
        lbl_prompt = QLabel("고객님의 휴대폰 번호를<br><font color='#EF5350'>입력</font>해 주세요!")
        lbl_prompt.setTextFormat(Qt.TextFormat.RichText)
        lbl_prompt.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; border: none; background: transparent;")
        lbl_prompt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        right_column.addWidget(lbl_prompt)
        
        # PocketCU QR Info and KakaoTalk Info
        info_row = QHBoxLayout()
        info_row.setSpacing(10)
        
        # PocketCU Text
        lbl_pocketcu = QLabel(
            "<b>[포켓CU QR]</b><br>"
            "· 포인트 적립은 결제단계에서 포켓CU QR 한번 더 스캔!<br>"
            "· 포켓CU QR 간편결제시 결제+적립 한번에!"
        )
        lbl_pocketcu.setStyleSheet("font-size: 8.5pt; color: #E2E8F0; line-height: 1.3; border: none; background: transparent;")
        info_row.addWidget(lbl_pocketcu, stretch=7)
        
        # KakaoTalk box mockup
        kakao_box = QFrame()
        kakao_box.setStyleSheet("background-color: #FFEB3B; border-radius: 6px; border: none;")
        kakao_layout = QHBoxLayout(kakao_box)
        kakao_layout.setContentsMargins(6, 6, 6, 6)
        kakao_layout.setSpacing(5)
        
        lbl_talk_icon = QLabel("TALK")
        lbl_talk_icon.setStyleSheet("background-color: #372213; color: #FFEB3B; font-weight: bold; font-size: 8pt; border-radius: 3px; padding: 2px 4px; border: none;")
        lbl_talk_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_talk_text = QLabel("포켓CU 미설치<br>고객에게는<br>카카오톡 발송")
        lbl_talk_text.setStyleSheet("color: #372213; font-size: 7.5pt; font-weight: bold; line-height: 1.1; border: none; background: transparent;")
        
        kakao_layout.addWidget(lbl_talk_icon)
        kakao_layout.addWidget(lbl_talk_text)
        info_row.addWidget(kakao_box, stretch=3)
        
        right_column.addLayout(info_row)
        dark_layout.addLayout(right_column)
        
        layout.addWidget(dark_box)
        
        # Bottom Input Area Row
        input_row_bg = QFrame()
        input_row_bg.setStyleSheet("background-color: #CBD5E0; border-radius: 6px; border: none;")
        input_row_layout = QHBoxLayout(input_row_bg)
        input_row_layout.setContentsMargins(10, 8, 10, 8)
        input_row_layout.setSpacing(10)
        
        lbl_scan_indicator = QLabel("▶ 바코드스캔")
        lbl_scan_indicator.setStyleSheet("font-size: 11pt; font-weight: bold; color: #2D3748; border: none; background: transparent;")
        
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("휴대폰 번호를 입력하거나 포켓CU 바코드를 스캔하세요 (- 제외)")
        self.input_phone.setFixedHeight(36)
        self.input_phone.setStyleSheet("""
            QLineEdit {
                background-color: #FEEBC8; /* Light yellow */
                color: #2D3748;
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #DD6B20;
                border-radius: 4px;
                padding-left: 8px;
            }
            QLineEdit:focus {
                background-color: #FFFFFF;
                border: 2px solid #3182CE;
            }
        """)
        self.input_phone.returnPressed.connect(self.accept_dialog)
        
        input_row_layout.addWidget(lbl_scan_indicator)
        input_row_layout.addWidget(self.input_phone)
        layout.addWidget(input_row_bg)
        
        # Lower Button Panel
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_ok = QPushButton("확인 [ENTER]")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setFixedHeight(45)
        btn_ok.setFixedWidth(130)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_ok.clicked.connect(self.accept_dialog)
        btn_layout.addWidget(btn_ok)
        
        btn_close = QPushButton("닫기 [CLEAR]")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedHeight(45)
        btn_close.setFixedWidth(130)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: white;
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2D3748;
            }
        """)
        btn_close.clicked.connect(self.reject_dialog)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        # Auto focus input field
        self.input_phone.setFocus()

    def accept_dialog(self):
        text = self.input_phone.text().strip()
        clean_text = text.replace("-", "")
        if not clean_text:
            return
            
        if len(clean_text) < 10 or not clean_text.isdigit():
            from ui_components import CustomMessageDialog
            CustomMessageDialog("입력 오류", "올바른 휴대폰 번호를 입력해 주세요.\n(예: 01012345678)", 'warning', self).exec()
            return
            
        if len(clean_text) == 11:
            self.phone_number = f"{clean_text[0:3]}-{clean_text[3:7]}-{clean_text[7:11]}"
        elif len(clean_text) == 10:
            self.phone_number = f"{clean_text[0:3]}-{clean_text[3:6]}-{clean_text[6:10]}"
        else:
            self.phone_number = clean_text
            
        self.result_value = True
        self.accept()

    def reject_dialog(self):
        self.result_value = False
        self.reject()


class PaymentWorker(QThread):
    finished_signal = pyqtSignal(bool, str, float)
    
    def __init__(self, firebase_mgr, account_number, amount, store_name):
        super().__init__()
        self.firebase_mgr = firebase_mgr
        self.account_number = account_number
        self.amount = amount
        self.store_name = store_name
        
    def run(self):
        try:
            success, message, balance = self.firebase_mgr.process_payment(
                account_number=self.account_number,
                pin_input="",
                amount=self.amount,
                store_name=self.store_name,
                bypass_pin=True
            )
            self.finished_signal.emit(success, message, balance)
        except Exception as e:
            self.finished_signal.emit(False, str(e), 0.0)


class BarcodePaymentProgressDialog(QDialog):
    def __init__(self, firebase_mgr, account_number, amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(460), styles.s(200))
        
        self.firebase_mgr = firebase_mgr
        self.account_number = account_number
        self.amount = amount
        
        self.result_success = None
        self.result_message = ""
        self.result_balance = 0.0
        self.worker_finished = False
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(440), styles.s(180))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(12)}px;
                border: 1px solid {styles.BORDER_COLOR};
            }}
        """)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(styles.s(30), styles.s(25), styles.s(30), styles.s(25))
        layout.setSpacing(styles.s(10))
        
        layout.addStretch()
        
        # Title Label
        self.lbl_title = QLabel("결제가 진행 중입니다")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet(f"font-size: 15pt; font-weight: bold; color: {styles.DARK_PURPLE}; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        layout.addWidget(self.lbl_title)
        
        # Subtitle
        self.lbl_sub = QLabel("잠시만 기다려 주세요...")
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sub.setStyleSheet(f"font-size: 9.5pt; color: #666666; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        layout.addWidget(self.lbl_sub)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(styles.s(10))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {styles.BORDER_COLOR};
                border-radius: {styles.s(5)}px;
                background-color: #F0F0F0;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                stop:0 {styles.PRIMARY_PURPLE}, 
                                                stop:1 {styles.DARK_PURPLE});
                border-radius: {styles.s(5)}px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Detail / Status Label
        self.lbl_detail = QLabel("결제 승인 요청 중...")
        self.lbl_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_detail.setStyleSheet(f"font-size: 9pt; color: #7B68EE; font-weight: bold; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        layout.addWidget(self.lbl_detail)
        
        layout.addStretch()
        
        # Load store name from store_info.json or default to DU순천점
        store_name = "DU순천점"
        import os, json
        store_info_path = os.path.join(os.path.abspath("."), "json", "store_info.json")
        if os.path.exists(store_info_path):
            try:
                with open(store_info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                    store_name = info.get("store_name", "DU순천점")
            except Exception:
                pass
                
        # Start background worker thread
        self.worker = PaymentWorker(self.firebase_mgr, self.account_number, self.amount, store_name)
        self.worker.finished_signal.connect(self.on_payment_finished)
        self.worker.start()
        
        # Start QTimer for smooth progress bar updates
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_step = 0
        self.progress_timer.start(20)  # 20ms * 100 = 2.0 seconds duration
        
    def update_progress(self):
        self.progress_step += 1
        self.progress_bar.setValue(min(self.progress_step, 100))
        
        # Hold progress bar at 99% if worker hasn't finished yet
        if self.progress_step >= 99 and not self.worker_finished:
            self.progress_step = 99
            self.lbl_detail.setText("서버 응답 대기 중...")
            
        if self.progress_step >= 100 and self.worker_finished:
            self.progress_timer.stop()
            if self.result_success:
                self.accept()
            else:
                self.reject()
                
    def on_payment_finished(self, success, message, balance):
        self.result_success = success
        self.result_message = message
        self.result_balance = balance
        self.worker_finished = True
        
    def get_result(self):
        return self.result_success, self.result_message, self.result_balance


class RefundWorker(QThread):
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, transaction_manager, firebase_mgr, barcode, amount, pay_method, tx):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.firebase_mgr = firebase_mgr
        self.barcode = barcode
        self.amount = amount
        self.pay_method = pay_method
        self.tx = tx
        
    def run(self):
        try:
            # 1. Process Firebase refund if it's MobilePay
            if self.pay_method == "MobilePay":
                account_num = None
                payments = self.tx.get("payments", [])
                for p in payments:
                    if p.get("method") == "MobilePay":
                        account_num = p.get("details", {}).get("account_number")
                        break
                if not account_num:
                    account_num = self.tx.get("payment_details", {}).get("account_number")
                
                if account_num:
                    store_name = "DU순천점"
                    import os, json
                    store_info_path = os.path.join(os.path.abspath("."), "json", "store_info.json")
                    if os.path.exists(store_info_path):
                        try:
                            with open(store_info_path, "r", encoding="utf-8") as f:
                                info = json.load(f)
                                store_name = info.get("store_name", "DU순천점")
                        except Exception:
                            pass
                    
                    # Deposit the amount back using process_refund
                    success, msg, bal = self.firebase_mgr.process_refund(
                        account_number=account_num,
                        amount=float(self.amount),
                        store_name=store_name
                    )
                    if not success:
                        self.finished_signal.emit(False, f"모바일 결제 승인 취소 실패: {msg}")
                        return
            
            # 2. Mark as refunded in transaction manager
            result = self.transaction_manager.mark_as_refunded(self.barcode)
            if result == "Success":
                self.finished_signal.emit(True, "환불이 정상 완료되었습니다.")
            elif result == "AlreadyRefunded":
                self.finished_signal.emit(False, "이미 환불 처리된 영수증입니다.")
            elif result == "NotFound":
                self.finished_signal.emit(False, "해당 바코드의 영수증을 찾을 수 없습니다.")
            else:
                self.finished_signal.emit(False, "환불 처리 중 오류가 발생했습니다.")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class BarcodeRefundProgressDialog(QDialog):
    def __init__(self, transaction_manager, firebase_mgr, barcode, amount, pay_method, tx, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(460), styles.s(200))
        
        self.transaction_manager = transaction_manager
        self.firebase_mgr = firebase_mgr
        self.barcode = barcode
        self.amount = amount
        self.pay_method = pay_method
        self.tx = tx
        
        self.result_success = None
        self.result_message = ""
        self.worker_finished = False
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(440), styles.s(180))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(12)}px;
                border: 1px solid {styles.BORDER_COLOR};
            }}
        """)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(styles.s(30), styles.s(25), styles.s(30), styles.s(25))
        layout.setSpacing(styles.s(10))
        
        layout.addStretch()
        
        # Title Label
        self.lbl_title = QLabel("환불 처리가 진행 중입니다")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet(f"font-size: 15pt; font-weight: bold; color: {styles.DARK_PURPLE}; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        layout.addWidget(self.lbl_title)
        
        # Subtitle
        self.lbl_sub = QLabel("잠시만 기다려 주세요...")
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sub.setStyleSheet(f"font-size: 9.5pt; color: #666666; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        layout.addWidget(self.lbl_sub)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(styles.s(10))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {styles.BORDER_COLOR};
                border-radius: {styles.s(5)}px;
                background-color: #F0F0F0;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                stop:0 {styles.PRIMARY_PURPLE}, 
                                                stop:1 {styles.DARK_PURPLE});
                border-radius: {styles.s(5)}px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Detail / Status Label
        self.lbl_detail = QLabel("환불 처리 요청 중...")
        self.lbl_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_detail.setStyleSheet(f"font-size: 9pt; color: #7B68EE; font-weight: bold; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        layout.addWidget(self.lbl_detail)
        
        layout.addStretch()
        
        # Start background worker thread
        self.worker = RefundWorker(self.transaction_manager, self.firebase_mgr, self.barcode, self.amount, self.pay_method, self.tx)
        self.worker.finished_signal.connect(self.on_refund_finished)
        self.worker.start()
        
        # Start QTimer for smooth progress bar updates
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_step = 0
        self.progress_timer.start(15)  # 15ms * 100 = 1.5 seconds duration
        
    def update_progress(self):
        self.progress_step += 1
        self.progress_bar.setValue(min(self.progress_step, 100))
        
        # Hold progress bar at 99% if worker hasn't finished yet
        if self.progress_step >= 99 and not self.worker_finished:
            self.progress_step = 99
            self.lbl_detail.setText("서버 응답 대기 중...")
            
        if self.progress_step >= 100 and self.worker_finished:
            self.progress_timer.stop()
            if self.result_success:
                self.accept()
            else:
                self.reject()
                
    def on_refund_finished(self, success, message):
        self.result_success = success
        self.result_message = message
        self.worker_finished = True
        
    def get_result(self):
        return self.result_success, self.result_message


class QtySelectorWidget(QWidget):
    valueChanged = pyqtSignal(int)
    
    def __init__(self, max_value, start_value=0, parent=None):
        super().__init__(parent)
        self.max_value = max_value
        self.value = start_value
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(styles.s(5))
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_minus = QPushButton("-")
        self.btn_minus.setFixedSize(styles.s(30), styles.s(30))
        self.btn_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minus.setStyleSheet(f"""
            QPushButton {{
                background-color: #E2E8F0;
                color: #4A5568;
                border: 1px solid #CBD5E0;
                border-radius: {styles.s(4)}px;
                font-weight: bold;
                font-size: 14pt;
            }}
            QPushButton:hover {{
                background-color: #CBD5E0;
            }}
            QPushButton:disabled {{
                color: #CBD5E0;
                background-color: #F7FAFC;
            }}
        """)
        
        self.lbl_value = QLabel(str(self.value))
        self.lbl_value.setFixedWidth(styles.s(35))
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_value.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: #2D3748; border: none; background: transparent;")
        
        self.btn_plus = QPushButton("+")
        self.btn_plus.setFixedSize(styles.s(30), styles.s(30))
        self.btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_plus.setStyleSheet(f"""
            QPushButton {{
                background-color: #E2E8F0;
                color: #4A5568;
                border: 1px solid #CBD5E0;
                border-radius: {styles.s(4)}px;
                font-weight: bold;
                font-size: 14pt;
            }}
            QPushButton:hover {{
                background-color: #CBD5E0;
            }}
            QPushButton:disabled {{
                color: #CBD5E0;
                background-color: #F7FAFC;
            }}
        """)
        
        layout.addWidget(self.btn_minus)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.btn_plus)
        
        self.btn_minus.clicked.connect(self.decrease)
        self.btn_plus.clicked.connect(self.increase)
        self.update_buttons()
        
    def decrease(self):
        if self.value > 0:
            self.value -= 1
            self.lbl_value.setText(str(self.value))
            self.valueChanged.emit(self.value)
            self.update_buttons()
            
    def increase(self):
        if self.value < self.max_value:
            self.value += 1
            self.lbl_value.setText(str(self.value))
            self.valueChanged.emit(self.value)
            self.update_buttons()
            
    def update_buttons(self):
        self.btn_minus.setEnabled(self.value > 0)
        self.btn_plus.setEnabled(self.value < self.max_value)


class KeepingCouponIssueDialog(QDialog):
    def __init__(self, keepable_items, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.keepable_items = keepable_items
        self.result_quantities = {}
        self.result_value = False
        
        self.setFixedSize(styles.s(680), styles.s(550))
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(8)}px;
                border: 1px solid #B0BEC5;
            }}
        """)
        main_layout.addWidget(self.container)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.create_header()
        self.create_subheader()
        self.create_table()
        self.create_footer()
        
    def create_header(self):
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #512DA8;
            border-top-left-radius: {styles.s(7)}px;
            border-top-right-radius: {styles.s(7)}px;
            border: none;
        """)
        header.setFixedHeight(styles.s(50))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(15), 0, styles.s(15), 0)
        
        title = QLabel("키핑쿠폰 발급")
        title.setStyleSheet(f"color: white; font-weight: bold; font-size: 13.5pt; font-family: '{styles.FONT_FAMILY}';")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(styles.s(30), styles.s(30))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                font-weight: bold;
                border: none;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
        """)
        btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(title)
        hbox.addStretch()
        hbox.addWidget(btn_close)
        
        self.layout.addWidget(header)
        
    def create_subheader(self):
        subheader = QFrame()
        subheader.setStyleSheet(f"""
            background-color: #E2E8F0;
            border: none;
            border-bottom: 1px solid #CBD5E0;
        """)
        subheader.setFixedHeight(styles.s(45))
        hbox = QHBoxLayout(subheader)
        hbox.setContentsMargins(styles.s(15), 0, styles.s(15), 0)
        hbox.setSpacing(styles.s(10))
        
        lbl_reg = QLabel("등록")
        lbl_reg.setFixedSize(styles.s(55), styles.s(28))
        lbl_reg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_reg.setStyleSheet(f"""
            background-color: #4A5568;
            color: white;
            font-weight: bold;
            font-size: 10pt;
            border-radius: {styles.s(4)}px;
            font-family: '{styles.FONT_FAMILY}';
        """)
        
        lbl_guide = QLabel("• 키핑쿠폰 발급 수량을 조정해주세요.")
        lbl_guide.setStyleSheet(f"color: #4A5568; font-size: 10.5pt; font-weight: bold; font-family: '{styles.FONT_FAMILY}';")
        
        hbox.addWidget(lbl_reg)
        hbox.addWidget(lbl_guide)
        hbox.addStretch()
        
        self.layout.addWidget(subheader)
        
    def create_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setRowCount(len(self.keepable_items))
        self.table.setHorizontalHeaderLabels(["행사명", "상품명", "키핑 가능 수량", "발급수량"])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                color: #2D3748;
                border: none;
                gridline-color: #E2E8F0;
                font-family: '{styles.FONT_FAMILY}';
            }}
            QHeaderView::section {{
                background-color: #F8F9FA;
                color: #4A5568;
                font-weight: bold;
                font-size: 10pt;
                border: none;
                border-bottom: 2px solid #CBD5E0;
                height: {styles.s(38)}px;
            }}
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        
        self.table.setColumnWidth(0, styles.s(140))
        self.table.setColumnWidth(2, styles.s(110))
        self.table.setColumnWidth(3, styles.s(130))
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        from datetime import datetime
        current_ym = datetime.now().strftime("%y%m")
        
        for idx, (item, product, max_keepable) in enumerate(self.keepable_items):
            prod_name = product["name"]
            brand = prod_name.split(")")[0] + ")" if ")" in prod_name else ""
            if brand:
                simple_name = prod_name.replace(brand, "").strip()
            else:
                simple_name = prod_name
            simple_name = simple_name.split(" ")[0]
            
            event_name = f"{current_ym}{simple_name}"
            item_event = QTableWidgetItem(event_name)
            item_event.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_event = QFont(styles.FONT_FAMILY, 9)
            item_event.setFont(font_event)
            item_event.setForeground(QColor("#2D3748"))
            
            item_prod = QTableWidgetItem(prod_name)
            item_prod.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            font_prod = QFont(styles.FONT_FAMILY, 9)
            item_prod.setFont(font_prod)
            item_prod.setForeground(QColor("#2D3748"))
            
            item_max = QTableWidgetItem(str(max_keepable))
            item_max.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_max = QFont(styles.FONT_FAMILY, 10)
            font_max.setBold(True)
            item_max.setFont(font_max)
            item_max.setForeground(QColor("#2D3748"))
            
            self.table.setItem(idx, 0, item_event)
            self.table.setItem(idx, 1, item_prod)
            self.table.setItem(idx, 2, item_max)
            
            barcode = item["barcode"]
            self.result_quantities[barcode] = max_keepable
            
            selector = QtySelectorWidget(max_keepable, start_value=max_keepable)
            selector.valueChanged.connect(lambda val, bc=barcode: self.on_qty_changed(bc, val))
            
            self.table.setCellWidget(idx, 3, selector)
            self.table.setRowHeight(idx, styles.s(45))
            
        self.layout.addWidget(self.table, stretch=1)
        
    def on_qty_changed(self, barcode, val):
        self.result_quantities[barcode] = val
        
    def create_footer(self):
        footer_outer = QFrame()
        footer_outer.setStyleSheet(f"""
            background-color: #F8F9FA;
            border-top: 1px solid #E2E8F0;
            border-bottom-left-radius: {styles.s(7)}px;
            border-bottom-right-radius: {styles.s(7)}px;
            border-left: none; border-right: none; border-bottom: none;
        """)
        
        outer_layout = QVBoxLayout(footer_outer)
        outer_layout.setContentsMargins(styles.s(15), styles.s(10), styles.s(15), styles.s(15))
        outer_layout.setSpacing(styles.s(10))
        
        lbl_guidelines = QLabel(
            "※ 고객에게는 교차상품 중 선택하여 교환할 수 있는 멀티쿠폰이 발급됩니다.<br>"
            "※ 키핑쿠폰을 발급하는 대상 상품은 재고 변동이 없습니다.<br>"
            "※ 행사당 최소 상품 1개는 고객이 직접 수령하며, 나머지 상품은 키핑이 가능합니다.<br>"
            "   <font color='#7E57C2'><b>[꿀TIP]</b></font> 1+1 A행사 10개 스캔시 9개 / 2+1 B행사 9개 스캔시 8개 키핑 가능!<br>"
            "<font color='#EF5350'><b>⚠️ 포인트 적립 · 할인물품은 고객 문의 후 결제단계에서 진행하세요.</b></font>"
        )
        lbl_guidelines.setTextFormat(Qt.TextFormat.RichText)
        lbl_guidelines.setStyleSheet(f"font-size: 8.5pt; color: #555555; line-height: 1.4; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        outer_layout.addWidget(lbl_guidelines)
        
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(styles.s(15))
        
        illustration_box = QFrame()
        illustration_box.setStyleSheet("background-color: #ECEFF1; border-radius: 6px; border: 1px solid #CFD8DC;")
        illustration_layout = QHBoxLayout(illustration_box)
        illustration_layout.setContentsMargins(styles.s(8), styles.s(6), styles.s(8), styles.s(6))
        illustration_layout.setSpacing(styles.s(8))
        
        lbl_phone_icon = QLabel("📱")
        lbl_phone_icon.setStyleSheet("font-size: 20pt; border: none; background: transparent;")
        
        lbl_pocket_info = QLabel("포켓CU QR로 포인트 적립은<br>다음단계 한번 더, 총 2번 스캔")
        lbl_pocket_info.setStyleSheet(f"font-size: 8pt; font-weight: bold; color: #37474F; line-height: 1.2; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        
        illustration_layout.addWidget(lbl_phone_icon)
        illustration_layout.addWidget(lbl_pocket_info)
        bottom_row.addWidget(illustration_box)
        
        bottom_row.addStretch()
        
        btn_cancel = QPushButton("닫기 [CLEAR]")
        btn_cancel.setFixedSize(styles.s(130), styles.s(45))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #546E7A;
                color: {styles.WHITE};
                border: none;
                border-radius: {styles.s(4)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #455A64;
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_submit = QPushButton("발급")
        btn_submit.setFixedSize(styles.s(130), styles.s(45))
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.setStyleSheet(f"""
            QPushButton {{
                background-color: #5E35B1;
                color: {styles.WHITE};
                border: none;
                border-radius: {styles.s(4)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #4527A0;
            }}
        """)
        btn_submit.clicked.connect(self.on_submit)
        
        bottom_row.addWidget(btn_cancel)
        bottom_row.addWidget(btn_submit)
        
        outer_layout.addLayout(bottom_row)
        self.layout.addWidget(footer_outer)
        
    def on_submit(self):
        total_issued = sum(self.result_quantities.values())
        if total_issued <= 0:
            from ui_components import CustomMessageDialog
            CustomMessageDialog("알림", "발급할 수량이 0개입니다.\n수량을 조절하거나 닫기를 눌러주세요.", 'info', self).exec()
            return
            
        self.result_value = True
        self.accept()

def get_choseong(text):
    CHOSEONG = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    result = ""
    for char in text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            idx = (code - 0xAC00) // 588
            result += CHOSEONG[idx]
        else:
            result += char
    return result

def match_korean(query, name):
    query = query.strip().lower()
    name = name.strip().lower()
    if not query:
        return True
    if query in name:
        return True
    CHOSEONG = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    q_choseong = get_choseong(query)
    n_choseong = get_choseong(name)
    if q_choseong in n_choseong:
        for c in query:
            if c not in CHOSEONG:
                if c not in name:
                    return False
        return True
    return False

class ProductNameSearchDialog(QDialog):
    def __init__(self, product_manager, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(1020), styles.s(620))
        self.product_manager = product_manager
        self.selected_barcode = None
        self.init_ui()
        
    def init_ui(self):
        # Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(1000), styles.s(600))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: {styles.s(16)}px;
                border: 2px solid #E2E8F0;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 6)
        self.container.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Header Bar
        header_bar = QFrame()
        header_bar.setFixedHeight(55)
        header_bar.setStyleSheet("QFrame { background-color: #F8F9FA; border-top-left-radius: 14px; border-top-right-radius: 14px; border-bottom: 1px solid #E2E8F0; }")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        lbl_title = QLabel("상품명으로 조회/등록")
        lbl_title.setStyleSheet(f"font-size: {styles.fs(15)}; font-weight: bold; color: #1F2937; font-family: '{styles.FONT_FAMILY}';")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        lbl_path = QLabel("통합조회 > 상품 조회/등록 > 상품명으로 조회/등록")
        lbl_path.setStyleSheet(f"font-size: {styles.fs(10)}; font-weight: bold; color: #7B68EE; font-family: '{styles.FONT_FAMILY}';")
        header_layout.addWidget(lbl_path)
        
        main_layout.addWidget(header_bar)
        
        # 2. Content Area
        content_frame = QWidget()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Left Info Panel
        left_panel = QFrame()
        left_panel.setFixedWidth(styles.s(320))
        left_panel.setStyleSheet("QFrame { background-color: #2A3554; border-radius: 12px; }")
        left_lyt = QVBoxLayout(left_panel)
        left_lyt.setContentsMargins(20, 40, 20, 40)
        left_lyt.setSpacing(20)
        
        info_text = QLabel("새우깡을 검색 하시려면\n화상 키보드를 이용하여\n상품명 입력란에")
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: white; font-size: {styles.fs(11)}; font-family: '{styles.FONT_FAMILY}'; line-height: 1.5;")
        
        example_box = QLabel("새우깡, ㅅㅇㄲ, ㅅㅇ깡")
        example_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        example_box.setFixedHeight(45)
        example_box.setStyleSheet(f"""
            background-color: white;
            color: #1F2937;
            font-size: {styles.fs(11.5)};
            font-weight: bold;
            border-radius: 6px;
            font-family: '{styles.FONT_FAMILY}';
        """)
        
        footer_text = QLabel("등으로 입력 가능합니다.")
        footer_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_text.setStyleSheet(f"color: white; font-size: {styles.fs(11)}; font-family: '{styles.FONT_FAMILY}';")
        
        left_lyt.addWidget(info_text)
        left_lyt.addWidget(example_box)
        left_lyt.addWidget(footer_text)
        left_lyt.addStretch()
        
        content_layout.addWidget(left_panel)
        
        # Right Search & Table Panel
        right_panel = QWidget()
        right_lyt = QVBoxLayout(right_panel)
        right_lyt.setContentsMargins(0, 0, 0, 0)
        right_lyt.setSpacing(12)
        
        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        lbl_search_title = QLabel("◎ 상품명입력")
        lbl_search_title.setStyleSheet(f"font-size: {styles.fs(11.5)}; font-weight: bold; color: #1F2937; font-family: '{styles.FONT_FAMILY}';")
        search_layout.addWidget(lbl_search_title)
        
        self.txt_search_name = QLineEdit()
        self.txt_search_name.setPlaceholderText("검색할 상품명을 입력하세요...")
        self.txt_search_name.setStyleSheet("""
            QLineEdit {
                background-color: #E2F0D9;
                color: black;
                border: 1px solid #A8D08D;
                border-radius: 4px;
                padding-left: 10px;
                font-size: 12pt;
                font-weight: bold;
                min-height: 40px;
            }
            QLineEdit:focus {
                border: 2px solid #528A35;
            }
        """)
        self.txt_search_name.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.txt_search_name, stretch=1)
        
        lbl_status = QLabel("운영 ☑")
        lbl_status.setStyleSheet(f"font-size: {styles.fs(11)}; font-weight: bold; color: #4B5563; font-family: '{styles.FONT_FAMILY}';")
        search_layout.addWidget(lbl_status)
        
        right_lyt.addLayout(search_layout)
        
        # Table & Touch Scroll Buttons Row
        table_row_lyt = QHBoxLayout()
        table_row_lyt.setSpacing(10)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["상품명", "바코드", "금액"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                color: #333333;
                border: 1px solid #CBD5E1;
                gridline-color: #E2E8F0;
                font-family: '{styles.FONT_FAMILY}';
                font-size: 11pt;
            }}
            QHeaderView::section {{
                background-color: #F1F5F9;
                color: #475569;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                border-bottom: 2px solid #CBD5E1;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid #F1F5F9;
            }}
            QTableWidget::item:selected {{
                background-color: #3C5087;
                color: white;
            }}
        """)
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        table_row_lyt.addWidget(self.table, stretch=1)
        
        # Touch Scroll Navigation Bar
        scroll_btn_layout = QVBoxLayout()
        scroll_btn_layout.setSpacing(10)
        
        btn_scroll_up = QPushButton("▲")
        btn_scroll_up.setFixedSize(styles.s(50), styles.s(65))
        btn_scroll_up.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scroll_up.setStyleSheet("""
            QPushButton {
                background-color: #E5E7EB;
                color: #374151;
                font-size: 16pt;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid #D1D5DB;
            }
            QPushButton:hover { background-color: #D1D5DB; }
        """)
        btn_scroll_up.clicked.connect(self.scroll_up)
        
        btn_scroll_down = QPushButton("▼")
        btn_scroll_down.setFixedSize(styles.s(50), styles.s(65))
        btn_scroll_down.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scroll_down.setStyleSheet("""
            QPushButton {
                background-color: #E5E7EB;
                color: #374151;
                font-size: 16pt;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid #D1D5DB;
            }
            QPushButton:hover { background-color: #D1D5DB; }
        """)
        btn_scroll_down.clicked.connect(self.scroll_down)
        
        scroll_btn_layout.addWidget(btn_scroll_up)
        scroll_btn_layout.addStretch()
        scroll_btn_layout.addWidget(btn_scroll_down)
        
        table_row_lyt.addLayout(scroll_btn_layout)
        right_lyt.addLayout(table_row_lyt, stretch=1)
        
        # Bottom Buttons
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.setSpacing(10)
        
        btn_select = QPushButton("선택 (F12)")
        btn_select.setFixedHeight(45)
        btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                font-size: {styles.fs(12)};
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        btn_select.clicked.connect(self.confirm_selection)
        
        btn_cancel = QPushButton("닫기")
        btn_cancel.setFixedHeight(45)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #6B7280;
                color: white;
                font-size: {styles.fs(12)};
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #4B5563; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        bottom_btn_layout.addWidget(btn_select, stretch=2)
        bottom_btn_layout.addWidget(btn_cancel, stretch=1)
        right_lyt.addLayout(bottom_btn_layout)
        
        content_layout.addWidget(right_panel, stretch=1)
        main_layout.addWidget(content_frame, stretch=1)
        
        # Load all products initially
        self.load_all_products()
        self.txt_search_name.setFocus()
        
    def load_all_products(self):
        products = self.product_manager.get_all_products()
        self.table.setRowCount(len(products))
        
        row = 0
        for barcode, p_data in products.items():
            self.table.setItem(row, 0, QTableWidgetItem(p_data["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p_data['price']:,}원"))
            
            # Align
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            row += 1
            
        if self.table.rowCount() > 0:
            self.table.selectRow(0)
            
    def filter_products(self):
        query = self.txt_search_name.text().strip()
        first_visible_row = -1
        
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            name = name_item.text() if name_item else ""
            
            if match_korean(query, name):
                self.table.setRowHidden(row, False)
                if first_visible_row == -1:
                    first_visible_row = row
            else:
                self.table.setRowHidden(row, True)
                
        if first_visible_row != -1:
            self.table.selectRow(first_visible_row)
            
    def scroll_up(self):
        scrollbar = self.table.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() - scrollbar.singleStep() * 4)
        
    def scroll_down(self):
        scrollbar = self.table.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() + scrollbar.singleStep() * 4)
        
    def on_table_double_clicked(self, row, col):
        self.confirm_selection()
        
    def confirm_selection(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            barcode_item = self.table.item(current_row, 1)
            if barcode_item:
                self.selected_barcode = barcode_item.text()
                self.accept()
                return
        self.reject()
