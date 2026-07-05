import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
import styles
from ui_components import CustomMessageDialog

class BadgeLabel(QWidget):
    def __init__(self, number, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        if number:
            self.badge = QLabel(str(number))
            self.badge.setFixedSize(24, 24)
            self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.badge.setStyleSheet("background-color: #7B68EE; color: white; border-radius: 12px; font-weight: bold; font-size: 10pt; border: none;")
            layout.addWidget(self.badge)
        else:
            self.spacer = QWidget()
            self.spacer.setFixedSize(24, 24)
            layout.addWidget(self.spacer)
            
        self.label = QLabel(text)
        self.label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333333; border: none; background: transparent;")
        layout.addWidget(self.label)
        layout.addStretch()

class ChangeAccumulationPage(QWidget):
    backRequested = pyqtSignal()
    accumulationCompleted = pyqtSignal(int)
    
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
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
        
        self.lbl_title = QLabel("잔돈적립")
        self.lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("서비스 > 잔돈적립")
        lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #7B68EE; font-weight: bold;")
        header_layout.addWidget(lbl_breadcrumb)
        main_layout.addWidget(header_frame)
        
        # 2. Main Content Area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # --- Left Column: Guide & Safe Balance Sync ---
        left_frame = QFrame()
        left_frame.setStyleSheet("QFrame { background-color: #202D3D; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)
        
        lbl_caution_title = QLabel("🪙 잔돈적립 서비스 안내")
        lbl_caution_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background: transparent; border: none;")
        left_layout.addWidget(lbl_caution_title)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #2D3E50; max-height: 1px; border: none;")
        left_layout.addWidget(divider)
        
        bullets = [
            "• 고객 거래 중 발생한 현금 잔돈을 회원카드 또는 교통카드에 적립해 드리는 서비스입니다.",
            "• 적립을 완료하면, 거스름돈이 고객에게 지급되지 않고 금고에 보관되는 잔돈 보유량과 자동 동기화되어 금고 잔액이 가산됩니다."
        ]
        
        for bullet in bullets:
            lbl_bullet = QLabel(bullet)
            lbl_bullet.setWordWrap(True)
            lbl_bullet.setStyleSheet("font-size: 11pt; color: #E0E0E0; background: transparent; border: none; line-height: 1.4;")
            left_layout.addWidget(lbl_bullet)
            
        left_layout.addSpacing(15)
        
        # Sync safe balance cards
        self.safe_card = QFrame()
        self.safe_card.setStyleSheet("QFrame { background-color: #2C3E50; border-radius: 6px; }")
        safe_card_lyt = QVBoxLayout(self.safe_card)
        safe_card_lyt.setContentsMargins(15, 15, 15, 15)
        safe_card_lyt.setSpacing(10)
        
        self.lbl_current_safe = QLabel("현재 금고 보관 금액: 0 원")
        self.lbl_current_safe.setStyleSheet("font-size: 11pt; font-weight: bold; color: #94A3B8; background: transparent;")
        
        self.lbl_expected_safe = QLabel("적립 후 금고 금액: 0 원")
        self.lbl_expected_safe.setStyleSheet("font-size: 12pt; font-weight: bold; color: #8BC34A; background: transparent;")
        
        safe_card_lyt.addWidget(self.lbl_current_safe)
        safe_card_lyt.addWidget(self.lbl_expected_safe)
        left_layout.addWidget(self.safe_card)
        
        left_layout.addStretch()
        content_layout.addWidget(left_frame, stretch=35)
        
        # --- Right Column: Accumulation form ---
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #DEE2E6; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setColumnStretch(1, 1)
        
        grid.addWidget(BadgeLabel(1, "적립할 잔돈 금액"), 0, 0)
        
        self.txt_accum_amt = QLineEdit()
        self.txt_accum_amt.setPlaceholderText("적립할 금액 입력 (예: 1,700)")
        self.txt_accum_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_accum_amt.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 10px;
                padding-right: 15px;
                font-size: 16pt;
                font-weight: bold;
                min-height: 45px;
            }
            QLineEdit:focus {
                border: 2px solid #7B68EE;
            }
        """)
        self.txt_accum_amt.textChanged.connect(self.on_amount_changed)
        grid.addWidget(self.txt_accum_amt, 0, 1)
        right_layout.addLayout(grid)
        
        # Preset buttons for quick accumulation
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(10)
        presets = [("100원", 100), ("500원", 500), ("1천원", 1000), ("5천원", 5000), ("1만원", 10000)]
        for label, val in presets:
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8F9FA;
                    color: #4B5563;
                    font-size: 11pt;
                    font-weight: bold;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #E5E7EB;
                }
                QPushButton:pressed {
                    background-color: #7B68EE;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, v=val: self.add_accum_amt(v))
            presets_layout.addWidget(btn)
        right_layout.addLayout(presets_layout)
        
        right_layout.addSpacing(10)
        
        # Tag card indicator
        tag_card = QFrame()
        tag_card.setFixedHeight(120)
        tag_card.setStyleSheet("""
            QFrame {
                background-color: #EEF2F6;
                border: 2px dashed #94A3B8;
                border-radius: 8px;
            }
        """)
        tag_lyt = QVBoxLayout(tag_card)
        tag_lyt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag_lyt.setSpacing(8)
        
        lbl_tag_main = QLabel("💳 적립할 카드를 단말기에 접촉하세요")
        lbl_tag_main.setStyleSheet("font-size: 14pt; font-weight: bold; color: #1E293B; border: none; background: transparent;")
        lbl_tag_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_tag_status = QLabel("접촉 상태 대기 중...")
        self.lbl_tag_status.setStyleSheet("font-size: 11pt; color: #475569; border: none; background: transparent;")
        self.lbl_tag_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tag_lyt.addWidget(lbl_tag_main)
        tag_lyt.addWidget(self.lbl_tag_status)
        right_layout.addWidget(tag_card)
        
        # Confirmation buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.btn_confirm = QPushButton("적립 완료")
        self.btn_confirm.setFixedHeight(55)
        self.btn_confirm.setFixedWidth(200)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_confirm.clicked.connect(self.process_accumulation)
        
        self.btn_cancel = QPushButton("취소")
        self.btn_cancel.setFixedHeight(55)
        self.btn_cancel.setFixedWidth(120)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        self.btn_cancel.clicked.connect(self.backRequested.emit)
        
        btn_row.addStretch()
        btn_row.addWidget(self.btn_confirm)
        btn_row.addWidget(self.btn_cancel)
        right_layout.addLayout(btn_row)
        right_layout.addStretch()
        
        content_layout.addWidget(right_frame, stretch=65)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # 3. Bottom Navigation Frame
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(100)
        bottom_frame.setStyleSheet("background-color: #CAD2D9; border-top: 1px solid #CCC;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(30, 10, 30, 10)
        
        self.btn_back = QPushButton("◀  이전 [CLEAR]")
        self.btn_back.setFixedSize(220, 65)
        self.btn_back.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 15pt; border-radius: 5px;")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.backRequested.emit)
        
        bottom_layout.addWidget(self.btn_back)
        bottom_layout.addStretch()
        main_layout.addWidget(bottom_frame)
        
        # Initial Safe sync
        self.refresh_safe_balance()
        
    def refresh_safe_balance(self):
        base_safe_amt = self.transaction_manager.get_base_safe_amt()
        cash_total = self.transaction_manager.get_cash_total()
        self.current_safe_total = base_safe_amt + cash_total
        
        self.lbl_current_safe.setText(f"현재 금고 보관 금액: {self.current_safe_total:,} 원")
        self.on_amount_changed(self.txt_accum_amt.text())
        
    def add_accum_amt(self, amt):
        text = self.txt_accum_amt.text().replace(",", "")
        curr = int(text) if text.isdigit() else 0
        new_val = curr + amt
        self.txt_accum_amt.setText(f"{new_val:,}")
        
    def on_amount_changed(self, text):
        clean_text = text.replace(",", "")
        amount = int(clean_text) if clean_text.isdigit() else 0
        
        expected_total = self.current_safe_total + amount
        self.lbl_expected_safe.setText(f"적립 후 금고 금액: {expected_total:,} 원")
        
        if clean_text.isdigit() and amount > 0:
            self.txt_accum_amt.blockSignals(True)
            self.txt_accum_amt.setText(f"{amount:,}")
            self.txt_accum_amt.blockSignals(False)
            
    def process_accumulation(self):
        text = self.txt_accum_amt.text().replace(",", "")
        if not text.isdigit() or int(text) <= 0:
            CustomMessageDialog("오류", "올바른 적립 금액을 입력해 주세요.", 'warning', self).exec()
            self.txt_accum_amt.setFocus()
            return
            
        amt = int(text)
        self.lbl_tag_status.setText("⏳ 적립 승인 요청 중...")
        
        QTimer.singleShot(1500, lambda: self.complete_accumulation(amt))
        
    def complete_accumulation(self, amt):
        self.lbl_tag_status.setText("✅ 적립 완료!")
        self.accumulationCompleted.emit(amt)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.txt_accum_amt.clear()
        self.lbl_tag_status.setText("접촉 상태 대기 중...")
        self.refresh_safe_balance()
        self.txt_accum_amt.setFocus()
