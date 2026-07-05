import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QSpacerItem, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPixmap, QFont, QIcon
import styles

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PostPaymentPage(QWidget):
    backRequested = pyqtSignal()
    previousTransactionRequested = pyqtSignal()
    barcodeScanned = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Base Style
        self.setStyleSheet("background-color: white;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(styles.s(0), styles.s(0), styles.s(0), styles.s(0))
        main_layout.setSpacing(0)

        # Main Body (Split Left and Right)
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(styles.s(40), styles.s(40), styles.s(40), styles.s(40))
        body_layout.setSpacing(styles.s(50))

        # --- LEFT: Receipt Illustration ---
        self.receipt_label = QLabel()
        asset_path = resource_path(os.path.join("assets", "cu_receipt_scan_illustration.png"))
        if os.path.exists(asset_path):
            pix = QPixmap(asset_path).scaled(styles.s(500), styles.s(500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.receipt_label.setPixmap(pix)
        else:
            self.receipt_label.setText("📄\n[영수증 스캔 이미지]")
            self.receipt_label.setStyleSheet(f"font-size: {styles.fs(30)}; border: 2px solid #E0E0E0; padding: 20px; border-radius: 10px; color: #999;")
        
        self.receipt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(self.receipt_label, stretch=1)

        # --- RIGHT: Instructions & Button ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(styles.s(20))
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header Text
        title_label = QLabel("결제 후, 할인 또는 적립, 현금영수증을 할 수 있습니다.\n영수증의 바코드를 스캔하여 주십시오.")
        title_label.setStyleSheet(f"font-size: {styles.fs(22)}; font-weight: bold; color: #5C6BC0; line-height: 1.4;")
        right_layout.addWidget(title_label)
        
        # Divider Line
        line = QFrame()
        line.setFixedHeight(styles.s(2))
        line.setStyleSheet("background-color: #E0E0E0; border: none;") # Solid line as per image
        right_layout.addWidget(line)
        
        # Bullet Points
        info_layout = QVBoxLayout()
        info_layout.setSpacing(styles.s(10))
        
        bullet1 = QLabel("※ 직전거래는 [직전거래] 버튼을 선택하시면 됩니다.")
        bullet1.setStyleSheet(f"font-size: {styles.fs(18)}; color: #E53935; font-weight: bold;")
        info_layout.addWidget(bullet1)
        
        bullet2 = QLabel("※ 결제 후 적립/현금영수증은 중복 적용이 불가합니다.")
        bullet2.setStyleSheet(f"font-size: {styles.fs(18)}; color: #E53935; font-weight: bold;")
        info_layout.addWidget(bullet2)
        
        right_layout.addLayout(info_layout)
        right_layout.addSpacing(styles.s(30))

        # Action Button (More like a rectangle in info)
        self.btn_prev_tx = QPushButton("직전거래")
        self.btn_prev_tx.setFixedSize(styles.s(250), styles.s(80))
        self.btn_prev_tx.setStyleSheet(f"""
            QPushButton {{
                background-color: #2D3E50;
                color: white;
                font-size: {styles.fs(24)};
                font-weight: bold;
                border-radius: {styles.s(6)}px;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #1A2836;
            }}
        """)
        self.btn_prev_tx.clicked.connect(self.previousTransactionRequested.emit)
        right_layout.addWidget(self.btn_prev_tx)
        
        right_layout.addStretch()
        
        body_layout.addWidget(right_panel, stretch=1)
        main_layout.addWidget(body_widget, stretch=1)

        # 3. Bottom Bar
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(styles.s(80))
        bottom_bar.setStyleSheet("background-color: #E8EAF6; border-top: 1px solid #D1D9E6;")
        
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(styles.s(40), 0, styles.s(40), 0)
        
        icon_label = QLabel("❯") 
        icon_label.setStyleSheet(f"font-size: {styles.fs(22)}; color: #5C6BC0; font-weight: bold;")
        bottom_layout.addWidget(icon_label)
        
        lbl_scan = QLabel("바코드 스캔")
        lbl_scan.setStyleSheet(f"font-size: {styles.fs(20)}; font-weight: bold; color: #333; margin-left: 10px;")
        bottom_layout.addWidget(lbl_scan)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("바코드를 스캔하세요")
        self.barcode_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #D1D9E6;
                border: none;
                border-radius: 4px;
                padding: {styles.s(10)}px;
                font-size: {styles.fs(20)};
                color: #333;
                margin-left: 20px;
            }}
        """)
        self.barcode_input.returnPressed.connect(self.on_barcode_return)
        self.barcode_input.textChanged.connect(self.on_barcode_changed)
        bottom_layout.addWidget(self.barcode_input, stretch=1)
        
        # Close Button
        btn_back = QPushButton("닫기")
        btn_back.setFixedSize(styles.s(100), styles.s(50))
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: #9E9E9E;
                color: white;
                font-size: {styles.fs(16)};
                font-weight: bold;
                border-radius: 4px;
                border: none;
                margin-left: 10px;
            }}
            QPushButton:hover {{ background-color: #757575; }}
        """)
        btn_back.clicked.connect(self.backRequested.emit)
        bottom_layout.addWidget(btn_back)
        
        main_layout.addWidget(bottom_bar)

    def on_barcode_changed(self, text):
        if len(text.strip()) == 16:
            self.on_barcode_return()

    def on_barcode_return(self):
        barcode = self.barcode_input.text().strip()
        if barcode:
            self.barcode_input.clear()
            self.barcodeScanned.emit(barcode)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.backRequested.emit()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.barcode_input.setFocus()

class PostPaymentOptionDialog(QDialog):
    def __init__(self, tx_data, parent=None):
        super().__init__(parent)
        self.tx_data = tx_data
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(styles.s(1250), styles.s(700))
        self.setStyleSheet("background-color: #F8F9FA; border: none;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Header
        header = QFrame()
        header.setFixedHeight(styles.s(60))
        header.setStyleSheet("background-color: #2D3E50; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(styles.s(20), 0, styles.s(10), 0)
        
        lbl_title = QLabel("결제 후, 할인/적립/현금영수증 선택")
        lbl_title.setStyleSheet(f"color: white; font-size: {styles.fs(20)}; font-weight: bold;")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        btn_close_x = QPushButton("✕")
        btn_close_x.setFixedSize(styles.s(40), styles.s(40))
        btn_close_x.setStyleSheet("color: white; font-size: 24px; background: transparent; border: none;")
        btn_close_x.clicked.connect(self.reject)
        header_layout.addWidget(btn_close_x)
        
        layout.addWidget(header)

        # 2. Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(styles.s(30), styles.s(30), styles.s(30), styles.s(40))
        body_layout.setSpacing(styles.s(20))

        # Instructions
        instr_label = QLabel(
            "고객번호로 발급된 현금영수증은 영수증 환불로 진행해주세요.\n"
            "결제 후 적립/현금영수증은 중복 적용이 불가합니다.\n"
            "(결제 후, 할인)은 환불이 이루어집니다. 할인을 하시고, 다시 결제해 주십시오."
        )
        instr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instr_label.setStyleSheet(f"font-size: {styles.fs(16)}; color: #333; font-weight: 500; line-height: 1.5;")
        body_layout.addWidget(instr_label)

        # Buttons Row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(styles.s(50), 0, styles.s(50), 0)
        btn_row.setSpacing(styles.s(40))
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def create_option_button(text, icon_symbol, color="#2D3E50"):
            btn = QPushButton()
            btn.setFixedSize(styles.s(320), styles.s(350))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: none;
                    border-radius: {styles.s(12)}px;
                }}
                QPushButton:hover {{ 
                    background-color: #FAFAFA; 
                    border: 2px solid {color}; 
                }}
                QPushButton:pressed {{
                    background-color: #ECEFF1;
                }}
            """)
            
            btn_lyt = QVBoxLayout(btn)
            btn_lyt.setContentsMargins(styles.s(20), styles.s(30), styles.s(20), styles.s(30))
            btn_lyt.setSpacing(styles.s(15))
            
            # Icon using Emoji or Symbol
            icon_lbl = QLabel(icon_symbol)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(f"font-size: {styles.fs(80)}; color: {color}; background: transparent;")
            btn_lyt.addWidget(icon_lbl)
            
            # Text label
            text_lbl = QLabel(text)
            text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_lbl.setStyleSheet(f"font-size: {styles.fs(22)}; font-weight: bold; color: #2C3E50; background: transparent;")
            btn_lyt.addWidget(text_lbl)
            
            return btn

        # Map to symbols: 💳 (Discount/Cards), 💎 (Points), 📄 (Receipt)
        self.btn_discount = create_option_button("제휴할인", "💳")
        self.btn_points = create_option_button("포인트 적립", "💎")
        self.btn_receipt = create_option_button("현금영수증", "📄", "#5C6BC0")
        self.btn_receipt.clicked.connect(self.handle_receipt_clicked)

        btn_row.addWidget(self.btn_discount)
        btn_row.addWidget(self.btn_points)
        btn_row.addWidget(self.btn_receipt)
        
        body_layout.addStretch()
        body_layout.addLayout(btn_row)
        body_layout.addStretch()
        
        # Bottom Close Button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        btn_close = QPushButton("닫기[CLEAR]")
        btn_close.setFixedSize(styles.s(200), styles.s(55))
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: #546E7A;
                color: white;
                font-size: {styles.fs(18)};
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #455A64; }}
        """)
        btn_close.clicked.connect(self.reject)
        bottom_layout.addWidget(btn_close)
        
        body_layout.addLayout(bottom_layout)
        
        layout.addWidget(body)

    def handle_receipt_clicked(self):
        payments = self.tx_data.get("payments", [])
        cash_amt = 0
        if payments:
            for p in payments:
                if p.get("method") == "Cash":
                    cash_amt += p.get("amount", 0)
        else:
            if self.tx_data.get("payment_method") == "Cash":
                cash_amt = self.tx_data.get("total_amt", 0)
                
        if cash_amt <= 0:
            from ui_components import CustomMessageDialog
            CustomMessageDialog("발급 불가", "현금으로 결제한 금액이 없습니다.\n현금 결제건만 현금영수증 발급이 가능합니다.", 'warning', self).exec()
            return
            
        from payment_ui import CashReceiptDialog
        dialog = CashReceiptDialog(cash_amt, cash_amt, self)
        if dialog.exec():
            if dialog.receipt_issued and dialog.receipt_id:
                tx_barcode = self.tx_data.get("tx_barcode")
                if tx_barcode and self.parent():
                    self.parent().transaction_manager.update_cash_receipt(tx_barcode, dialog.receipt_id)
                from ui_components import CustomMessageDialog
                CustomMessageDialog("발급 완료", f"현금영수증이 발급되었습니다.\n승인번호: {dialog.receipt_id}", 'info', self).exec()
                self.accept()

    def mousePressEvent(self, event):
        # Allow dragging if needed, or just let it be
        super().mousePressEvent(event)
