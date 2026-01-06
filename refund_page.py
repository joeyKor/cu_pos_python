import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPalette, QBrush, QPixmap
import styles

class RefundPage(QWidget):
    backRequested = pyqtSignal()
    barcodeScanned = pyqtSignal(str)
    receiptInquiryRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #F8F9FA;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header (Dark bar)
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("background-color: #2D3E50;")
        header_layout = QHBoxLayout(header_frame)
        
        lbl_title = QLabel("영수증 환불")
        lbl_title.setStyleSheet("color: white; font-size: 20pt; font-weight: bold;")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_frame)

        # 2. Middle Section
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(40)

        # Left Panel (Receipt Refund)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)

        lbl_instruct = QLabel("영수증의 바코드를 스캔하여\n환불을 하실 수 있습니다.")
        lbl_instruct.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_instruct.setStyleSheet("font-size: 18pt; font-weight: bold; color: #333;")
        left_panel.addWidget(lbl_instruct)

        # Single Receipt Image Display
        self.receipt_label = QLabel()
        img_path = r"C:\Users\joy\.gemini\antigravity\brain\292b5aaf-c0ae-439d-8ae2-8654b22aaa7c\cu_thermal_receipt_graphic_clean_1767624732528.png"
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            # Scale to fit nicely while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(380, 550, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.receipt_label.setPixmap(scaled_pixmap)
        else:
            self.receipt_label.setText("영수증 이미지를 불러올 수 없습니다.")
            self.receipt_label.setStyleSheet("color: #999; font-size: 14pt;")
        
        self.receipt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.receipt_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Barcode Input Area
        input_container = QFrame()
        input_container.setStyleSheet("background-color: #E9ECEF; border-radius: 10px; border: 1px solid #DEE2E6;")
        input_container.setFixedHeight(110)
        in_lyt = QVBoxLayout(input_container)
        
        lbl_in_title = QLabel("> 바코드 스캔")
        lbl_in_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2D3E50; border: none; background: transparent;")
        in_lyt.addWidget(lbl_in_title)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setFixedHeight(50)
        self.barcode_input.setStyleSheet("background-color: #F8D7DA; border: 1px solid #CCC; font-size: 18pt; padding-left: 10px; border-radius: 0px;")
        self.barcode_input.returnPressed.connect(self.on_barcode_return)
        self.barcode_input.textChanged.connect(self.on_barcode_text_changed)
        in_lyt.addWidget(self.barcode_input)
        
        left_panel.addWidget(input_container)
        content_layout.addLayout(left_panel, stretch=4)

        # Right Panel (Policy)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        lbl_policy_title = QLabel("환불 정책 변경")
        lbl_policy_title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #333;")
        right_panel.addWidget(lbl_policy_title)

        policy_box = QFrame()
        policy_box.setStyleSheet("background-color: #D1D5DB; border-radius: 10px;")
        p_lyt = QVBoxLayout(policy_box)
        p_lyt.setContentsMargins(20, 20, 20, 20)
        
        policy_text = (
            "• 정부 방침에 의해 교환/환불은 <span style='color: #D32F2F;'>30일 이내만 가능</span>하며, "
            "<span style='color: #D32F2F;'>영수증이 없으면 불가</span>합니다.<br><br>"
            "• 영수증이 없는 경우는, [영수증 조회] 버튼 선택하여 영수증 출력하여<br>  환불 바랍니다."
        )
        lbl_policy = QLabel(policy_text)
        lbl_policy.setWordWrap(True)
        lbl_policy.setStyleSheet("font-size: 14pt; color: #333; line-height: 1.5; background: transparent;")
        p_lyt.addWidget(lbl_policy)
        p_lyt.addStretch()
        
        right_panel.addWidget(policy_box)
        right_panel.addStretch()
        
        content_layout.addLayout(right_panel, stretch=6)
        main_layout.addWidget(content_widget, stretch=1)

        # 3. Bottom Navigation
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(80)
        bottom_frame.setStyleSheet("background-color: #D1D5DB; border-top: 1px solid #CCC;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(20, 10, 20, 10)
        
        btn_back = QPushButton("◀  이전 [CLEAR]")
        btn_back.setFixedSize(200, 60)
        btn_back.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 14pt; border-radius: 5px;")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.backRequested.emit)
        bottom_layout.addWidget(btn_back)
        
        bottom_layout.addStretch()
        
        btn_style = "background-color: #2D3E50; color: white; font-weight: bold; font-size: 14pt; border-radius: 5px; padding: 0 20px;"
        
        btn_bottle = QPushButton("공병/폴리백 환불")
        btn_bottle.setFixedHeight(60)
        btn_bottle.setStyleSheet(btn_style)
        
        btn_cig = QPushButton("담배교환")
        btn_cig.setFixedHeight(60)
        btn_cig.setStyleSheet(btn_style)
        
        btn_receipt = QPushButton("영수증 조회")
        btn_receipt.setFixedHeight(60)
        btn_receipt.setStyleSheet(btn_style)
        btn_receipt.clicked.connect(self.receiptInquiryRequested.emit)
        
        bottom_layout.addWidget(btn_bottle)
        bottom_layout.addWidget(btn_cig)
        bottom_layout.addWidget(btn_receipt)
        
        main_layout.addWidget(bottom_frame)

    def on_barcode_return(self):
        barcode = self.barcode_input.text().strip()
        if barcode:
            self.barcodeScanned.emit(barcode)
            self.barcode_input.clear()

    def on_barcode_text_changed(self, text):
        if len(text) >= 16:
            self.barcodeScanned.emit(text.strip())
            self.barcode_input.clear()
            self.barcode_input.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.barcode_input.setFocus()
