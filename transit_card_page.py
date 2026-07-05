import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGridLayout, 
                             QStackedWidget)
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


class TransitCardPage(QWidget):
    backRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        
        self.lbl_title = QLabel("교통카드 서비스")
        self.lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("통합조회 > 교통카드")
        lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #7B68EE; font-weight: bold;")
        header_layout.addWidget(lbl_breadcrumb)
        main_layout.addWidget(header_frame)
 
        # 2. Main Content Area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
 
        # --- Left Column: Instructions Panel ---
        left_frame = QFrame()
        left_frame.setStyleSheet("QFrame { background-color: #202D3D; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)
        
        lbl_caution_title = QLabel("⚠️ 교통카드 이용 안내")
        lbl_caution_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background: transparent; border: none;")
        left_layout.addWidget(lbl_caution_title)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #2D3E50; max-height: 1px; border: none;")
        left_layout.addWidget(divider)
        
        bullets = [
            "• T-money, Cashbee 등 전국호환 교통카드의 충전 및 잔액 환불이 가능합니다.",
            "• 교통카드 충전은 오직 현금으로만 거래 가능합니다. (신용카드 충전 불가)",
            "• 잔액 환불 시 대행 수수료 500원이 정상 차감되어 지급됩니다.",
            "• 카드를 단말기 서명패드(동글)의 교통카드 인식 영역에 올바르게 접촉해 주십시오."
        ]
        
        for bullet in bullets:
            lbl_bullet = QLabel(bullet)
            lbl_bullet.setWordWrap(True)
            lbl_bullet.setStyleSheet("font-size: 12pt; color: #E0E0E0; background: transparent; border: none; line-height: 1.4;")
            left_layout.addWidget(lbl_bullet)
            
        left_layout.addStretch()
        
        lbl_warning_footer = QLabel("충전 및 환불 완료 처리 전까지 절대로 단말기에서 카드를 제거하지 마십시오.")
        lbl_warning_footer.setWordWrap(True)
        lbl_warning_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_warning_footer.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: #FF8A65;
            background-color: #2C1F2D;
            border: 1px solid #FF8A65;
            border-radius: 5px;
            padding: 12px;
        """)
        left_layout.addWidget(lbl_warning_footer)
        
        content_layout.addWidget(left_frame, stretch=35)
  
        # --- Right Column: Search Form / Pages ---
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #DEE2E6; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        
        self.stack = QStackedWidget()
        
        # Build menu, charge, and refund sub-widgets
        self.init_menu_screen()
        self.init_charge_screen()
        self.init_refund_screen()
        
        self.stack.addWidget(self.menu_widget)
        self.stack.addWidget(self.charge_widget)
        self.stack.addWidget(self.refund_widget)
        
        right_layout.addWidget(self.stack)
        content_layout.addWidget(right_frame, stretch=65)
        
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
        self.btn_back.clicked.connect(self.handle_back_action)
        bottom_layout.addWidget(self.btn_back)
        bottom_layout.addStretch()
        
        main_layout.addWidget(bottom_frame)
        
        # Set default screen
        self.show_menu()
        
    def handle_back_action(self):
        # If we are on charge or refund screens, go back to menu first
        if self.stack.currentIndex() != 0:
            self.show_menu()
        else:
            self.backRequested.emit()
            
    def show_menu(self):
        self.lbl_title.setText("교통카드 서비스")
        self.stack.setCurrentIndex(0)
        
    def show_charge(self):
        self.lbl_title.setText("교통카드 서비스 - 충전")
        self.txt_charge_amt.clear()
        self.lbl_tag_status.setText("접촉 상태 대기 중...")
        self.stack.setCurrentIndex(1)
        self.txt_charge_amt.setFocus()
        
    def show_refund(self):
        self.lbl_title.setText("교통카드 - 환불")
        self.lbl_tag_status_r.setText("카드 확인 대기 중...")
        self.stack.setCurrentIndex(2)
        
    def init_menu_screen(self):
        self.menu_widget = QWidget()
        layout = QVBoxLayout(self.menu_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)
        
        lbl_guide = QLabel("원하시는 서비스를 선택하세요")
        lbl_guide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_guide.setStyleSheet("font-size: 16pt; font-weight: bold; color: #374151;")
        layout.addWidget(lbl_guide)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(25)
        
        # Large Charge Button
        self.btn_goto_charge = QPushButton()
        self.btn_goto_charge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_goto_charge.setFixedHeight(styles.s(220))
        self.btn_goto_charge.setStyleSheet("""
            QPushButton {
                background-color: #EDE9FE;
                border: 2px solid #C4B5FD;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #DDD6FE;
                border-color: #A78BFA;
            }
        """)
        c_layout = QVBoxLayout(self.btn_goto_charge)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.setSpacing(15)
        
        lbl_c_icon = QLabel("⚡")
        lbl_c_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_icon.setStyleSheet("font-size: 40pt; background: transparent;")
        
        lbl_c_title = QLabel("교통카드 충전")
        lbl_c_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #4C1D95; background: transparent;")
        
        lbl_c_desc = QLabel("현금을 투입하고\n카드를 충전합니다")
        lbl_c_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_desc.setStyleSheet("font-size: 11pt; color: #6D28D9; background: transparent;")
        
        c_layout.addWidget(lbl_c_icon)
        c_layout.addWidget(lbl_c_title)
        c_layout.addWidget(lbl_c_desc)
        self.btn_goto_charge.clicked.connect(self.show_charge)
        
        # Large Refund Button
        self.btn_goto_refund = QPushButton()
        self.btn_goto_refund.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_goto_refund.setFixedHeight(styles.s(220))
        self.btn_goto_refund.setStyleSheet("""
            QPushButton {
                background-color: #FEF3C7;
                border: 2px solid #FDE68A;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #FDE68A;
                border-color: #FCD34D;
            }
        """)
        r_layout = QVBoxLayout(self.btn_goto_refund)
        r_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_layout.setSpacing(15)
        
        lbl_r_icon = QLabel("🪙")
        lbl_r_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_icon.setStyleSheet("font-size: 40pt; background: transparent;")
        
        lbl_r_title = QLabel("교통카드 환불")
        lbl_r_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #78350F; background: transparent;")
        
        lbl_r_desc = QLabel("카드 잔액을 차감하고\n현금으로 환불합니다")
        lbl_r_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_desc.setStyleSheet("font-size: 11pt; color: #92400E; background: transparent;")
        
        r_layout.addWidget(lbl_r_icon)
        r_layout.addWidget(lbl_r_title)
        r_layout.addWidget(lbl_r_desc)
        self.btn_goto_refund.clicked.connect(self.show_refund)
        
        btn_layout.addWidget(self.btn_goto_charge)
        btn_layout.addWidget(self.btn_goto_refund)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
    def init_charge_screen(self):
        self.charge_widget = QWidget()
        layout = QVBoxLayout(self.charge_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Grid input
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setColumnStretch(1, 1)
        
        grid.addWidget(BadgeLabel(1, "충전 금액"), 0, 0)
        
        self.txt_charge_amt = QLineEdit()
        self.txt_charge_amt.setPlaceholderText("충전할 금액 입력 (예: 10,000)")
        self.txt_charge_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_charge_amt.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 10px;
                padding-right: 15px;
                font-size: 16pt;
                font-weight: bold;
                min-height: 45px;
            }}
            QLineEdit:focus {{
                border: 2px solid #7B68EE;
            }}
        """)
        grid.addWidget(self.txt_charge_amt, 0, 1)
        layout.addLayout(grid)
        
        # Preset buttons
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(10)
        presets = [("1천원", 1000), ("3천원", 3000), ("5천원", 5000), ("1만원", 10000), ("3만원", 30000), ("5만원", 50000)]
        for label, val in presets:
            btn = QPushButton(label)
            btn.setFixedHeight(styles.s(50))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8F9FA;
                    color: #4B5563;
                    font-size: 12pt;
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
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=val: self.add_charge_amt(v))
            presets_layout.addWidget(btn)
        layout.addLayout(presets_layout)
        
        layout.addSpacing(10)
        
        # Tag card indicator
        tag_card = QFrame()
        tag_card.setFixedHeight(120)
        tag_card.setStyleSheet("""
            QFrame {
                background-color: #F5F3FF;
                border: 2px dashed #A78BFA;
                border-radius: 8px;
            }
        """)
        tag_lyt = QVBoxLayout(tag_card)
        tag_lyt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag_lyt.setSpacing(8)
        
        lbl_tag_main = QLabel("💳 카드를 단말기에 접촉하세요")
        lbl_tag_main.setStyleSheet("font-size: 14pt; font-weight: bold; color: #6D28D9; border: none; background: transparent;")
        lbl_tag_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_tag_status = QLabel("접촉 상태 대기 중...")
        self.lbl_tag_status.setStyleSheet("font-size: 11pt; color: #8B5CF6; border: none; background: transparent;")
        self.lbl_tag_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tag_lyt.addWidget(lbl_tag_main)
        tag_lyt.addWidget(self.lbl_tag_status)
        layout.addWidget(tag_card)
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.btn_charge_confirm = QPushButton("충전 완료")
        self.btn_charge_confirm.setFixedHeight(styles.s(55))
        self.btn_charge_confirm.setFixedWidth(styles.s(200))
        self.btn_charge_confirm.setStyleSheet("""
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
        self.btn_charge_confirm.clicked.connect(self.process_charge)
        
        self.btn_charge_cancel = QPushButton("취소")
        self.btn_charge_cancel.setFixedHeight(styles.s(55))
        self.btn_charge_cancel.setFixedWidth(styles.s(120))
        self.btn_charge_cancel.setStyleSheet("""
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
        self.btn_charge_cancel.clicked.connect(self.show_menu)
        
        btn_row.addStretch()
        btn_row.addWidget(self.btn_charge_confirm)
        btn_row.addWidget(self.btn_charge_cancel)
        layout.addLayout(btn_row)
        layout.addStretch()
        
    def init_refund_screen(self):
        self.refund_widget = QWidget()
        layout = QVBoxLayout(self.refund_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Form grid layout for refund
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setColumnStretch(1, 1)
        
        LBL_STYLE = "font-size: 12pt; font-weight: bold; color: #333;"
        INPUT_STYLE = """
            QLineEdit {
                background-color: #E5E7EB;
                color: #374151;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-right: 15px;
                font-size: 14pt;
                font-weight: bold;
                min-height: 40px;
            }
        """
        
        # 1. 환불가능잔액
        lbl_avail = QLabel("환불 가능 잔액")
        lbl_avail.setStyleSheet(LBL_STYLE)
        self.txt_avail_amt = QLineEdit("18,500 원")
        self.txt_avail_amt.setReadOnly(True)
        self.txt_avail_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_avail_amt.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(lbl_avail, 0, 0)
        form_layout.addWidget(self.txt_avail_amt, 0, 1)
        
        # 2. 환불수수료
        lbl_fee = QLabel("환불 대행 수수료")
        lbl_fee.setStyleSheet(LBL_STYLE)
        self.txt_fee = QLineEdit("500 원")
        self.txt_fee.setReadOnly(True)
        self.txt_fee.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_fee.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(lbl_fee, 1, 0)
        form_layout.addWidget(self.txt_fee, 1, 1)
        
        # 3. 실 지급액
        lbl_net = QLabel("실 지급 금액")
        lbl_net.setStyleSheet(LBL_STYLE)
        self.txt_net_amt = QLineEdit("18,000 원")
        self.txt_net_amt.setReadOnly(True)
        self.txt_net_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_net_amt.setStyleSheet(INPUT_STYLE + "QLineEdit { background-color: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; }")
        form_layout.addWidget(lbl_net, 2, 0)
        form_layout.addWidget(self.txt_net_amt, 2, 1)
        
        layout.addLayout(form_layout)
        
        # Tag card indicator for refund
        tag_card_r = QFrame()
        tag_card_r.setFixedHeight(120)
        tag_card_r.setStyleSheet("""
            QFrame {
                background-color: #FFFDF2;
                border: 2px dashed #FCD34D;
                border-radius: 8px;
            }
        """)
        tag_lyt_r = QVBoxLayout(tag_card_r)
        tag_lyt_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag_lyt_r.setSpacing(8)
        
        lbl_tag_main_r = QLabel("💳 카드를 단말기에 접촉하세요")
        lbl_tag_main_r.setStyleSheet("font-size: 14pt; font-weight: bold; color: #B45309; border: none; background: transparent;")
        lbl_tag_main_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_tag_status_r = QLabel("카드 확인 대기 중...")
        self.lbl_tag_status_r.setStyleSheet("font-size: 11pt; color: #D97706; border: none; background: transparent;")
        self.lbl_tag_status_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tag_lyt_r.addWidget(lbl_tag_main_r)
        tag_lyt_r.addWidget(self.lbl_tag_status_r)
        layout.addWidget(tag_card_r)
        
        # Buttons for refund
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.btn_refund_confirm = QPushButton("환불 완료")
        self.btn_refund_confirm.setFixedHeight(styles.s(55))
        self.btn_refund_confirm.setFixedWidth(styles.s(200))
        self.btn_refund_confirm.setStyleSheet("""
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
        self.btn_refund_confirm.clicked.connect(self.process_refund)
        
        self.btn_refund_cancel = QPushButton("취소")
        self.btn_refund_cancel.setFixedHeight(styles.s(55))
        self.btn_refund_cancel.setFixedWidth(styles.s(120))
        self.btn_refund_cancel.setStyleSheet("""
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
        self.btn_refund_cancel.clicked.connect(self.show_menu)
        
        btn_row.addStretch()
        btn_row.addWidget(self.btn_refund_confirm)
        btn_row.addWidget(self.btn_refund_cancel)
        layout.addLayout(btn_row)
        layout.addStretch()
        
    def add_charge_amt(self, amt):
        text = self.txt_charge_amt.text().replace(",", "")
        curr = int(text) if text.isdigit() else 0
        new_val = curr + amt
        self.txt_charge_amt.setText(f"{new_val:,}")
        
    def process_charge(self):
        text = self.txt_charge_amt.text().replace(",", "")
        if not text.isdigit() or int(text) <= 0:
            CustomMessageDialog("오류", "올바른 충전 금액을 입력해주세요.", 'warning', self).exec()
            self.txt_charge_amt.setFocus()
            return
            
        amt = int(text)
        self.lbl_tag_status.setText("⏳ 충전 승인 요청 중...")
        
        QTimer.singleShot(1500, lambda: self.complete_charge(amt))
        
    def complete_charge(self, amt):
        self.lbl_tag_status.setText("✅ 충전 완료!")
        CustomMessageDialog("성공", f"교통카드에 {amt:,}원이 성공적으로 충전되었습니다.", 'info', self).exec()
        self.handle_back_action()
        
    def process_refund(self):
        self.lbl_tag_status_r.setText("⏳ 환불 승인 요청 중...")
        QTimer.singleShot(1500, self.complete_refund)
        
    def complete_refund(self):
        self.lbl_tag_status_r.setText("✅ 환불 완료!")
        CustomMessageDialog("성공", "교통카드 잔액 18,500원(수수료 500원 차감)이 환불되었습니다.\n현금 18,000원을 지급해 주세요.", 'info', self).exec()
        self.handle_back_action()
