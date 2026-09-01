import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGridLayout, 
                             QStackedWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont
import styles
from ui_components import CustomMessageDialog
from transit_card_manager import TransitCardManager

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


class TransitCardVisualWidget(QFrame):
    """실물 교통카드(T-Money/RFID) 형태의 시각적 카드 위젯"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(styles.s(160))
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E1B4B, stop:0.5 #312E81, stop:1 #4C1D95);
                border-radius: {styles.s(14)}px;
                border: 2px solid #818CF8;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(styles.s(22), styles.s(16), styles.s(22), styles.s(16))
        layout.setSpacing(styles.s(8))
        
        # Top Row: Brand / Type & Contactless Icon
        top_row = QHBoxLayout()
        self.lbl_card_type = QLabel("Tmoney")
        self.lbl_card_type.setStyleSheet("color: #E0E7FF; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        
        lbl_nfc = QLabel("💳  ))))")
        lbl_nfc.setStyleSheet("color: #FCD34D; font-size: 13pt; font-weight: bold; background: transparent; border: none;")
        
        top_row.addWidget(self.lbl_card_type)
        top_row.addStretch()
        top_row.addWidget(lbl_nfc)
        layout.addLayout(top_row)
        
        # Center Row: Card Title/Desc
        self.lbl_card_id = QLabel("카드를 단말기/스캐너에 접촉하세요")
        self.lbl_card_id.setStyleSheet("color: #A5B4FC; font-size: 13pt; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(self.lbl_card_id)
        
        layout.addStretch()
        
        # Bottom Row: Balance display
        bottom_row = QHBoxLayout()
        lbl_bal_title = QLabel("현재 잔액")
        lbl_bal_title.setStyleSheet("color: #C7D2FE; font-size: 11pt; background: transparent; border: none;")
        
        self.lbl_balance = QLabel("0 원")
        self.lbl_balance.setStyleSheet("color: #34D399; font-size: 18pt; font-weight: bold; background: transparent; border: none;")
        
        bottom_row.addWidget(lbl_bal_title)
        bottom_row.addStretch()
        bottom_row.addWidget(self.lbl_balance)
        layout.addLayout(bottom_row)

    def set_card_data(self, card_data):
        if card_data:
            bal = int(card_data.get("balance", 0))
            self.lbl_card_type.setText("Tmoney")
            self.lbl_card_id.setText("Tmoney 스마트 교통카드")
            self.lbl_card_id.setStyleSheet("color: #FFFFFF; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
            self.lbl_balance.setText(f"{bal:,} 원")
        else:
            self.lbl_card_type.setText("Tmoney")
            self.lbl_card_id.setText("카드를 단말기/스캐너에 접촉하세요")
            self.lbl_card_id.setStyleSheet("color: #A5B4FC; font-size: 13pt; font-weight: bold; background: transparent; border: none;")
            self.lbl_balance.setText("0 원")


class TransitCardPage(QWidget):
    backRequested = pyqtSignal()
    
    def __init__(self, transit_card_manager=None, transaction_manager=None, parent=None):
        super().__init__(parent)
        self.tm = transit_card_manager or TransitCardManager()
        self.transaction_manager = transaction_manager
        self.current_card = None
        self.init_ui()
 
    def init_ui(self):
        self.setStyleSheet("background-color: #F8F9FA;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
 
        # 1. Header Frame
        header_frame = QFrame()
        header_frame.setFixedHeight(styles.s(80))
        header_frame.setStyleSheet("background-color: white; border-bottom: 2px solid #DEE2E6;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(styles.s(30), 0, styles.s(30), 0)
        
        self.lbl_title = QLabel("교통카드 서비스")
        self.lbl_title.setStyleSheet(f"font-size: {styles.fs(22)}; font-weight: bold; color: #333;")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        
        self.lbl_breadcrumb = QLabel("통합조회 > 교통카드")
        self.lbl_breadcrumb.setStyleSheet(f"font-size: {styles.fs(13)}; color: #7B68EE; font-weight: bold;")
        header_layout.addWidget(self.lbl_breadcrumb)
        main_layout.addWidget(header_frame)
 
        # 2. Main Content Area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(styles.s(20), styles.s(20), styles.s(20), styles.s(20))
        content_layout.setSpacing(styles.s(20))
 
        # --- Left Column: Instructions Panel ---
        left_frame = QFrame()
        left_frame.setStyleSheet("QFrame { background-color: #202D3D; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(styles.s(25), styles.s(25), styles.s(25), styles.s(25))
        left_layout.setSpacing(styles.s(15))
        
        lbl_caution_title = QLabel("⚠️ 교통카드 이용 안내")
        lbl_caution_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background: transparent; border: none;")
        left_layout.addWidget(lbl_caution_title)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #2D3E50; max-height: 1px; border: none;")
        left_layout.addWidget(divider)
        
        bullets = [
            "• T-money, Cashbee, RailPlus 등 전국호환 교통카드의 충전, 잔액 조회 및 환불이 가능합니다.",
            "• 스캐너 장치로 카드를 스캔하거나 단말기 접촉 시 실시간 잔액이 즉시 조회됩니다.",
            "• 교통카드 충전은 현금 결제로 안전하게 진행됩니다.",
            "• 잔액 환불 시 대행 수수료 500원이 정상 차감되어 현금 지급됩니다."
        ]
        
        for bullet in bullets:
            lbl_bullet = QLabel(bullet)
            lbl_bullet.setWordWrap(True)
            lbl_bullet.setStyleSheet("font-size: 11pt; color: #E0E0E0; background: transparent; border: none; line-height: 1.4;")
            left_layout.addWidget(lbl_bullet)
            
        left_layout.addStretch()
        
        lbl_warning_footer = QLabel("충전 및 환불 완료 처리 전까지 절대로 단말기에서 카드를 제거하지 마십시오.")
        lbl_warning_footer.setWordWrap(True)
        lbl_warning_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_warning_footer.setStyleSheet("""
            font-size: 11pt;
            font-weight: bold;
            color: #FF8A65;
            background-color: #2C1F2D;
            border: 1px solid #FF8A65;
            border-radius: 5px;
            padding: 10px;
        """)
        left_layout.addWidget(lbl_warning_footer)
        
        content_layout.addWidget(left_frame, stretch=35)
  
        # --- Right Column: Search Form / Pages ---
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #DEE2E6; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(styles.s(20), styles.s(20), styles.s(20), styles.s(20))
        right_layout.setSpacing(styles.s(15))
        
        self.stack = QStackedWidget()
        
        # Build sub-screens
        self.init_menu_screen()
        self.init_charge_screen()
        self.init_refund_screen()
        self.init_inquiry_screen()
        
        self.stack.addWidget(self.menu_widget)      # Index 0
        self.stack.addWidget(self.charge_widget)    # Index 1
        self.stack.addWidget(self.refund_widget)    # Index 2
        self.stack.addWidget(self.inquiry_widget)   # Index 3
        
        right_layout.addWidget(self.stack)
        content_layout.addWidget(right_frame, stretch=65)
        
        main_layout.addWidget(content_widget, stretch=1)
 
        # 3. Bottom Navigation
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(styles.s(80))
        bottom_frame.setStyleSheet("background-color: #CAD2D9; border-top: 1px solid #CCC;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(styles.s(30), styles.s(10), styles.s(30), styles.s(10))
        bottom_layout.setSpacing(styles.s(20))
        
        self.btn_back = QPushButton("◀  이전 [CLEAR]")
        self.btn_back.setFixedSize(styles.s(220), styles.s(55))
        self.btn_back.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 14pt; border-radius: 5px;")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.handle_back_action)
        bottom_layout.addWidget(self.btn_back)
        bottom_layout.addStretch()
        
        main_layout.addWidget(bottom_frame)
        
        # Set default screen
        self.show_menu()
        
    def handle_back_action(self):
        # If we are on sub-screens, go back to menu first
        if self.stack.currentIndex() != 0:
            self.show_menu()
        else:
            self.backRequested.emit()
            
    def show_menu(self):
        self.lbl_title.setText("교통카드 서비스")
        self.lbl_breadcrumb.setText("통합조회 > 교통카드")
        self.stack.setCurrentIndex(0)
        self.current_card = None
        
    def show_charge(self, card_id=None):
        self.lbl_title.setText("교통카드 서비스 - 충전")
        self.lbl_breadcrumb.setText("교통카드 > 충전")
        self.txt_charge_amt.clear()
        self.txt_scan_card_c.clear()
        self.card_visual_c.set_card_data(None)
        self.lbl_calc_current.setText("0 원")
        self.lbl_calc_charge.setText("+ 0 원")
        self.lbl_calc_total.setText("0 원")
        self.lbl_tag_status_c.setText("카드를 스캐너로 스캔하거나 접촉하세요")
        self.stack.setCurrentIndex(1)
        
        if card_id:
            self.process_card_scanned(card_id, "charge")
        QTimer.singleShot(50, self.txt_scan_card_c.setFocus)
        
    def show_refund(self, card_id=None):
        self.lbl_title.setText("교통카드 서비스 - 환불")
        self.lbl_breadcrumb.setText("교통카드 > 환불")
        self.txt_scan_card_r.clear()
        self.card_visual_r.set_card_data(None)
        self.txt_avail_amt.setText("0 원")
        self.txt_fee.setText("500 원")
        self.txt_net_amt.setText("0 원")
        self.lbl_tag_status_r.setText("환불할 카드를 스캐너로 스캔하세요")
        self.stack.setCurrentIndex(2)
        
        if card_id:
            self.process_card_scanned(card_id, "refund")
        QTimer.singleShot(50, self.txt_scan_card_r.setFocus)

    def show_inquiry(self, card_id=None):
        self.lbl_title.setText("교통카드 - 잔액 및 거래내역 조회")
        self.lbl_breadcrumb.setText("통합조회 > 교통카드잔액조회")
        self.txt_scan_card_i.clear()
        self.card_visual_i.set_card_data(None)
        self.table_history.setRowCount(0)
        self.lbl_tag_status_i.setText("조회할 카드를 스캐너로 스캔하세요")
        self.stack.setCurrentIndex(3)
        
        if card_id:
            self.process_card_scanned(card_id, "inquiry")
        QTimer.singleShot(50, self.txt_scan_card_i.setFocus)

    # --- Scanner Input Handler ---
    def process_card_scanned(self, raw_input, mode=None):
        raw_text = raw_input.strip() if raw_input else ""
        cid = self.tm.normalize_id(raw_text)
        
        curr_idx = self.stack.currentIndex()
        if not cid:
            # If scan input was empty and Return was pressed in Charge screen:
            if curr_idx == 1 or mode == "charge":
                text = self.txt_charge_amt.text().replace(",", "")
                if self.current_card and text.isdigit() and int(text) > 0:
                    self.process_charge()
                else:
                    self.txt_scan_card_c.setFocus()
            elif curr_idx == 2 or mode == "refund":
                if self.current_card:
                    self.process_refund()
                else:
                    self.txt_scan_card_r.setFocus()
            return
            
        card = self.tm.get_or_create_card(cid)
        self.current_card = card
        
        if mode == "charge" or curr_idx == 1:
            self.txt_scan_card_c.clear()
            self.card_visual_c.set_card_data(card)
            self.lbl_tag_status_c.setText("✅ Tmoney 카드 인식 완료")
            self.update_charge_calc()
            self.txt_scan_card_c.setFocus()
        elif mode == "refund" or curr_idx == 2:
            self.txt_scan_card_r.clear()
            self.card_visual_r.set_card_data(card)
            bal = int(card.get("balance", 0))
            fee = 500 if bal >= 500 else 0
            net = max(0, bal - fee)
            self.txt_avail_amt.setText(f"{bal:,} 원")
            self.txt_fee.setText(f"{fee:,} 원")
            self.txt_net_amt.setText(f"{net:,} 원")
            self.lbl_tag_status_r.setText("✅ Tmoney 카드 인식 완료")
            self.txt_scan_card_r.setFocus()
        elif mode == "inquiry" or curr_idx == 3:
            self.txt_scan_card_i.clear()
            self.card_visual_i.set_card_data(card)
            self.lbl_tag_status_i.setText("✅ Tmoney 카드 인식 완료")
            self.load_card_history_table(cid)
            self.txt_scan_card_i.setFocus()
        elif curr_idx == 0:
            # On Menu screen, scan automatically takes user to charge screen
            self.show_charge(cid)

    def load_card_history_table(self, card_id):
        history = self.tm.get_card_history(card_id)
        self.table_history.setRowCount(0)
        
        for row_idx, record in enumerate(history):
            self.table_history.insertRow(row_idx)
            
            ts = record.get("timestamp", "")
            tx_type = record.get("type", "")
            amt = record.get("amount", 0)
            bal_after = record.get("balance_after", 0)
            memo = record.get("memo", "")
            
            amt_str = f"+{amt:,}원" if amt > 0 else f"{amt:,}원"
            
            items = [
                QTableWidgetItem(ts),
                QTableWidgetItem(tx_type),
                QTableWidgetItem(amt_str),
                QTableWidgetItem(f"{bal_after:,}원"),
                QTableWidgetItem(memo)
            ]
            
            # Alignments & Colors
            items[0].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            items[1].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            items[2].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            items[3].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            items[4].setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            if tx_type == "충전":
                items[1].setForeground(QColor("#10B981"))
                items[2].setForeground(QColor("#10B981"))
            elif tx_type == "환불":
                items[1].setForeground(QColor("#F59E0B"))
                items[2].setForeground(QColor("#F59E0B"))
            else: # 결제
                items[1].setForeground(QColor("#EF4444"))
                items[2].setForeground(QColor("#EF4444"))
                
            for col_idx, item in enumerate(items):
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table_history.setItem(row_idx, col_idx, item)

    def init_menu_screen(self):
        self.menu_widget = QWidget()
        layout = QVBoxLayout(self.menu_widget)
        layout.setContentsMargins(styles.s(30), styles.s(30), styles.s(30), styles.s(30))
        layout.setSpacing(styles.s(25))
        
        lbl_guide = QLabel("원하시는 교통카드 서비스를 선택하거나 카드를 스캔하세요")
        lbl_guide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_guide.setStyleSheet(f"font-size: {styles.fs(16)}; font-weight: bold; color: #374151; border: none; background: transparent;")
        layout.addWidget(lbl_guide)
        
        layout.addStretch(1)
        
        # Three action cards in horizontal row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(styles.s(20))
        
        # 1. Large Charge Button
        self.btn_goto_charge = QPushButton()
        self.btn_goto_charge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_goto_charge.setFixedHeight(styles.s(220))
        self.btn_goto_charge.setStyleSheet(f"""
            QPushButton {{
                background-color: #EDE9FE;
                border: 2px solid #C4B5FD;
                border-radius: {styles.s(16)}px;
            }}
            QPushButton:hover {{
                background-color: #DDD6FE;
                border: 2px solid #A78BFA;
            }}
        """)
        c_layout = QVBoxLayout(self.btn_goto_charge)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.setSpacing(styles.s(10))
        
        lbl_c_icon = QLabel("⚡")
        lbl_c_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_icon.setStyleSheet(f"font-size: {styles.fs(36)}; background: transparent; border: none;")
        
        lbl_c_title = QLabel("교통카드 충전")
        lbl_c_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_title.setStyleSheet(f"font-size: {styles.fs(17)}; font-weight: bold; color: #4C1D95; background: transparent; border: none;")
        
        lbl_c_desc = QLabel("현금으로 카드를\n즉시 충전합니다")
        lbl_c_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_desc.setStyleSheet(f"font-size: {styles.fs(11)}; color: #6D28D9; background: transparent; border: none;")
        
        c_layout.addWidget(lbl_c_icon)
        c_layout.addWidget(lbl_c_title)
        c_layout.addWidget(lbl_c_desc)
        self.btn_goto_charge.clicked.connect(lambda: self.show_charge())
        
        # 2. Large Refund Button
        self.btn_goto_refund = QPushButton()
        self.btn_goto_refund.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_goto_refund.setFixedHeight(styles.s(220))
        self.btn_goto_refund.setStyleSheet(f"""
            QPushButton {{
                background-color: #FEF3C7;
                border: 2px solid #FDE68A;
                border-radius: {styles.s(16)}px;
            }}
            QPushButton:hover {{
                background-color: #FDE68A;
                border: 2px solid #FCD34D;
            }}
        """)
        r_layout = QVBoxLayout(self.btn_goto_refund)
        r_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_layout.setSpacing(styles.s(10))
        
        lbl_r_icon = QLabel("🪙")
        lbl_r_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_icon.setStyleSheet(f"font-size: {styles.fs(36)}; background: transparent; border: none;")
        
        lbl_r_title = QLabel("교통카드 환불")
        lbl_r_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_title.setStyleSheet(f"font-size: {styles.fs(17)}; font-weight: bold; color: #78350F; background: transparent; border: none;")
        
        lbl_r_desc = QLabel("카드 잔액을 정산하여\n현금으로 환불합니다")
        lbl_r_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_desc.setStyleSheet(f"font-size: {styles.fs(11)}; color: #92400E; background: transparent; border: none;")
        
        r_layout.addWidget(lbl_r_icon)
        r_layout.addWidget(lbl_r_title)
        r_layout.addWidget(lbl_r_desc)
        self.btn_goto_refund.clicked.connect(lambda: self.show_refund())
        
        # 3. Large Inquiry Button
        self.btn_goto_inquiry = QPushButton()
        self.btn_goto_inquiry.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_goto_inquiry.setFixedHeight(styles.s(220))
        self.btn_goto_inquiry.setStyleSheet(f"""
            QPushButton {{
                background-color: #E0F2FE;
                border: 2px solid #BAE6FD;
                border-radius: {styles.s(16)}px;
            }}
            QPushButton:hover {{
                background-color: #BAE6FD;
                border: 2px solid #7DD3FC;
            }}
        """)
        i_layout = QVBoxLayout(self.btn_goto_inquiry)
        i_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        i_layout.setSpacing(styles.s(10))
        
        lbl_i_icon = QLabel("🔍")
        lbl_i_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_i_icon.setStyleSheet(f"font-size: {styles.fs(36)}; background: transparent; border: none;")
        
        lbl_i_title = QLabel("잔액 및 내역 조회")
        lbl_i_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_i_title.setStyleSheet(f"font-size: {styles.fs(17)}; font-weight: bold; color: #075985; background: transparent; border: none;")
        
        lbl_i_desc = QLabel("카드 잔액 및 최근\n이용 내역을 조회합니다")
        lbl_i_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_i_desc.setStyleSheet(f"font-size: {styles.fs(11)}; color: #0284C7; background: transparent; border: none;")
        
        i_layout.addWidget(lbl_i_icon)
        i_layout.addWidget(lbl_i_title)
        i_layout.addWidget(lbl_i_desc)
        self.btn_goto_inquiry.clicked.connect(lambda: self.show_inquiry())
        
        btn_layout.addWidget(self.btn_goto_charge, stretch=1)
        btn_layout.addWidget(self.btn_goto_refund, stretch=1)
        btn_layout.addWidget(self.btn_goto_inquiry, stretch=1)
        
        layout.addLayout(btn_layout)
        layout.addStretch(1)

    def init_charge_screen(self):
        self.charge_widget = QWidget()
        layout = QVBoxLayout(self.charge_widget)
        layout.setContentsMargins(styles.s(10), styles.s(10), styles.s(10), styles.s(10))
        layout.setSpacing(styles.s(12))
        
        # 1. Scanner & Visual Card section
        top_box = QHBoxLayout()
        top_box.setSpacing(styles.s(15))
        
        # Left: Scanner input
        scan_panel = QFrame()
        scan_panel.setStyleSheet("background-color: #F3F4F6; border: 1px solid #E5E7EB; border-radius: 8px;")
        scan_lyt = QVBoxLayout(scan_panel)
        scan_lyt.setContentsMargins(styles.s(12), styles.s(12), styles.s(12), styles.s(12))
        scan_lyt.setSpacing(styles.s(8))
        
        lbl_scan_guide = QLabel("🔍 카드 스캔 (RFID / 리더기 입력)")
        lbl_scan_guide.setStyleSheet("font-size: 11pt; font-weight: bold; color: #4B5563;")
        scan_lyt.addWidget(lbl_scan_guide)
        
        self.txt_scan_card_c = QLineEdit()
        self.txt_scan_card_c.setPlaceholderText("스캐너로 카드를 인식하세요")
        self.txt_scan_card_c.setFixedHeight(styles.s(45))
        self.txt_scan_card_c.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: white;
                selection-background-color: white;
                selection-color: white;
                border: 2px solid #7B68EE;
                border-radius: 6px;
                padding-left: 10px;
                font-size: 13pt;
            }
        """)
        self.txt_scan_card_c.returnPressed.connect(lambda: self.process_card_scanned(self.txt_scan_card_c.text(), "charge"))
        scan_lyt.addWidget(self.txt_scan_card_c)
        
        self.lbl_tag_status_c = QLabel("카드를 스캐너로 스캔하거나 접촉하세요")
        self.lbl_tag_status_c.setStyleSheet("font-size: 10pt; color: #6D28D9; font-weight: bold;")
        scan_lyt.addWidget(self.lbl_tag_status_c)
        scan_lyt.addStretch()
        
        # Right: Visual Card Frame
        self.card_visual_c = TransitCardVisualWidget()
        
        top_box.addWidget(scan_panel, stretch=5)
        top_box.addWidget(self.card_visual_c, stretch=5)
        layout.addLayout(top_box)
        
        # 2. Charge Amount Input & Presets
        charge_box = QFrame()
        charge_box.setStyleSheet("background-color: #FAFAFA; border: 1px solid #E5E7EB; border-radius: 8px;")
        c_lyt = QVBoxLayout(charge_box)
        c_lyt.setContentsMargins(styles.s(15), styles.s(12), styles.s(15), styles.s(12))
        c_lyt.setSpacing(styles.s(10))
        
        row_amt = QHBoxLayout()
        row_amt.addWidget(BadgeLabel(1, "충전할 금액"))
        
        self.txt_charge_amt = QLineEdit()
        self.txt_charge_amt.setPlaceholderText("충전할 금액 (예: 10,000)")
        self.txt_charge_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_charge_amt.setFixedHeight(styles.s(45))
        self.txt_charge_amt.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #111827;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding-right: 15px;
                font-size: 16pt;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #7B68EE;
            }
        """)
        self.txt_charge_amt.textChanged.connect(self.update_charge_calc)
        self.txt_charge_amt.returnPressed.connect(self.process_charge)
        row_amt.addWidget(self.txt_charge_amt, stretch=1)
        c_lyt.addLayout(row_amt)
        
        # Preset buttons
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(styles.s(8))
        presets = [("1천원", 1000), ("3천원", 3000), ("5천원", 5000), ("1만원", 10000), ("3만원", 30000), ("5만원", 50000), ("10만원", 100000)]
        for label, val in presets:
            btn = QPushButton(f"+{label}")
            btn.setFixedHeight(styles.s(45))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F3F4F6;
                    color: #374151;
                    font-size: 11pt;
                    font-weight: bold;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #EDE9FE;
                    border: 1px solid #A78BFA;
                    color: #5B21B6;
                }
            """)
            btn.clicked.connect(lambda checked, v=val: self.add_charge_amt(v))
            presets_layout.addWidget(btn)
            
        btn_clr = QPushButton("정정")
        btn_clr.setFixedHeight(styles.s(45))
        btn_clr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clr.setStyleSheet("background-color: #FEE2E2; color: #B91C1C; font-size: 11pt; font-weight: bold; border: 1px solid #FCA5A5; border-radius: 6px;")
        btn_clr.clicked.connect(self.clear_charge_amt)
        presets_layout.addWidget(btn_clr)
        
        c_lyt.addLayout(presets_layout)
        layout.addWidget(charge_box)
        
        # 3. Live Balance Preview Summary Bar
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 8px;")
        sum_lyt = QHBoxLayout(summary_frame)
        sum_lyt.setContentsMargins(styles.s(15), styles.s(10), styles.s(15), styles.s(10))
        
        self.lbl_calc_current = QLabel("현재 잔액: 0 원")
        self.lbl_calc_current.setStyleSheet("font-size: 12pt; color: #4F46E5; font-weight: bold;")
        
        lbl_plus = QLabel("+")
        lbl_plus.setStyleSheet("font-size: 14pt; color: #6B7280; font-weight: bold;")
        
        self.lbl_calc_charge = QLabel("충전 금액: 0 원")
        self.lbl_calc_charge.setStyleSheet("font-size: 12pt; color: #059669; font-weight: bold;")
        
        lbl_eq = QLabel("=")
        lbl_eq.setStyleSheet("font-size: 14pt; color: #6B7280; font-weight: bold;")
        
        self.lbl_calc_total = QLabel("충전 후 잔액: 0 원")
        self.lbl_calc_total.setStyleSheet("font-size: 14pt; color: #1E1B4B; font-weight: bold;")
        
        sum_lyt.addWidget(self.lbl_calc_current)
        sum_lyt.addStretch()
        sum_lyt.addWidget(lbl_plus)
        sum_lyt.addStretch()
        sum_lyt.addWidget(self.lbl_calc_charge)
        sum_lyt.addStretch()
        sum_lyt.addWidget(lbl_eq)
        sum_lyt.addStretch()
        sum_lyt.addWidget(self.lbl_calc_total)
        layout.addWidget(summary_frame)
        
        # 4. Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(styles.s(12))
        
        self.btn_charge_confirm = QPushButton("충전 완료 [ENTER]")
        self.btn_charge_confirm.setFixedHeight(styles.s(55))
        self.btn_charge_confirm.setFixedWidth(styles.s(220))
        self.btn_charge_confirm.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 6px;
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
                border-radius: 6px;
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

    def add_charge_amt(self, amt):
        digits = "".join(c for c in self.txt_charge_amt.text() if c.isdigit())
        curr = int(digits) if digits else 0
        new_val = curr + amt
        self.txt_charge_amt.setText(f"{new_val:,}")
        self.update_charge_calc()
        QTimer.singleShot(10, self.txt_scan_card_c.setFocus)

    def clear_charge_amt(self):
        self.txt_charge_amt.clear()
        self.update_charge_calc()
        QTimer.singleShot(10, self.txt_scan_card_c.setFocus)

    def update_charge_calc(self):
        curr_bal = int(self.current_card.get("balance", 0)) if self.current_card else 0
        digits = "".join(c for c in self.txt_charge_amt.text() if c.isdigit())
        charge_amt = int(digits) if digits else 0
        total_bal = curr_bal + charge_amt
        
        self.lbl_calc_current.setText(f"현재: {curr_bal:,}원")
        self.lbl_calc_charge.setText(f"+ 충전: {charge_amt:,}원")
        self.lbl_calc_total.setText(f"충전 후: {total_bal:,}원")

    def process_charge(self):
        if not self.current_card:
            raw_scan = self.txt_scan_card_c.text().strip()
            if raw_scan:
                self.process_card_scanned(raw_scan, "charge")
            else:
                CustomMessageDialog("알림", "충전할 카드를 먼저 스캔하거나 접촉해 주세요.", 'warning', self).exec()
                self.txt_scan_card_c.setFocus()
                return

        digits = "".join(c for c in self.txt_charge_amt.text() if c.isdigit())
        if not digits or int(digits) <= 0:
            CustomMessageDialog("오류", "올바른 충전 금액을 선택하거나 입력해주세요.", 'warning', self).exec()
            self.txt_scan_card_c.setFocus()
            return
            
        amt = int(digits)
        cid = self.current_card.get("card_id")
        
        success, new_bal, msg, tx = self.tm.recharge_card(cid, amt, payment_method="현금")
        if success:
            self.current_card = self.tm.get_card(cid)
            self.card_visual_c.set_card_data(self.current_card)
            self.update_charge_calc()
            
            # Message
            CustomMessageDialog("충전 완료", 
                                f"Tmoney 교통카드 충전이 성공적으로 완료되었습니다.\n\n"
                                f"• 카드 종류: Tmoney\n"
                                f"• 충전 금액: {amt:,} 원\n"
                                f"• 이전 잔액: {tx['balance_before']:,} 원\n"
                                f"• 충전 후 잔액: {new_bal:,} 원", 
                                'info', self).exec()
            self.txt_charge_amt.clear()
            self.show_menu()
        else:
            CustomMessageDialog("충전 실패", msg, 'warning', self).exec()
            self.txt_scan_card_c.setFocus()

    def init_refund_screen(self):
        self.refund_widget = QWidget()
        layout = QVBoxLayout(self.refund_widget)
        layout.setContentsMargins(styles.s(10), styles.s(10), styles.s(10), styles.s(10))
        layout.setSpacing(styles.s(12))
        
        # 1. Scanner & Visual Card for refund
        top_box = QHBoxLayout()
        top_box.setSpacing(styles.s(15))
        
        scan_panel = QFrame()
        scan_panel.setStyleSheet("background-color: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px;")
        scan_lyt = QVBoxLayout(scan_panel)
        scan_lyt.setContentsMargins(styles.s(12), styles.s(12), styles.s(12), styles.s(12))
        scan_lyt.setSpacing(styles.s(8))
        
        lbl_scan_guide = QLabel("🔍 환불 카드 스캔 (RFID / 리더기 입력)")
        lbl_scan_guide.setStyleSheet("font-size: 11pt; font-weight: bold; color: #92400E;")
        scan_lyt.addWidget(lbl_scan_guide)
        
        self.txt_scan_card_r = QLineEdit()
        self.txt_scan_card_r.setPlaceholderText("스캐너로 카드를 인식하세요")
        self.txt_scan_card_r.setFixedHeight(styles.s(45))
        self.txt_scan_card_r.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: white;
                selection-background-color: white;
                selection-color: white;
                border: 2px solid #F59E0B;
                border-radius: 6px;
                padding-left: 10px;
                font-size: 13pt;
            }
        """)
        self.txt_scan_card_r.returnPressed.connect(lambda: self.process_card_scanned(self.txt_scan_card_r.text(), "refund"))
        scan_lyt.addWidget(self.txt_scan_card_r)
        
        self.lbl_tag_status_r = QLabel("환불할 카드를 스캐너로 스캔하세요")
        self.lbl_tag_status_r.setStyleSheet("font-size: 10pt; color: #B45309; font-weight: bold;")
        scan_lyt.addWidget(self.lbl_tag_status_r)
        scan_lyt.addStretch()
        
        self.card_visual_r = TransitCardVisualWidget()
        
        top_box.addWidget(scan_panel, stretch=5)
        top_box.addWidget(self.card_visual_r, stretch=5)
        layout.addLayout(top_box)
        
        # 2. Refund calculation form
        form_layout = QGridLayout()
        form_layout.setSpacing(styles.s(15))
        form_layout.setColumnStretch(1, 1)
        
        LBL_STYLE = "font-size: 12pt; font-weight: bold; color: #333;"
        INPUT_STYLE = """
            QLineEdit {
                background-color: #F3F4F6;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding-right: 15px;
                font-size: 14pt;
                font-weight: bold;
                min-height: 40px;
            }
        """
        
        lbl_avail = QLabel("환불 가능 잔액")
        lbl_avail.setStyleSheet(LBL_STYLE)
        self.txt_avail_amt = QLineEdit("0 원")
        self.txt_avail_amt.setReadOnly(True)
        self.txt_avail_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_avail_amt.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(lbl_avail, 0, 0)
        form_layout.addWidget(self.txt_avail_amt, 0, 1)
        
        lbl_fee = QLabel("환불 대행 수수료")
        lbl_fee.setStyleSheet(LBL_STYLE)
        self.txt_fee = QLineEdit("500 원")
        self.txt_fee.setReadOnly(True)
        self.txt_fee.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_fee.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(lbl_fee, 1, 0)
        form_layout.addWidget(self.txt_fee, 1, 1)
        
        lbl_net = QLabel("실 현금 지급액")
        lbl_net.setStyleSheet(LBL_STYLE)
        self.txt_net_amt = QLineEdit("0 원")
        self.txt_net_amt.setReadOnly(True)
        self.txt_net_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_net_amt.setStyleSheet(INPUT_STYLE + "QLineEdit { background-color: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; font-size: 16pt; }")
        form_layout.addWidget(lbl_net, 2, 0)
        form_layout.addWidget(self.txt_net_amt, 2, 1)
        
        layout.addLayout(form_layout)
        
        # 3. Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(styles.s(12))
        
        self.btn_refund_confirm = QPushButton("환불 완료")
        self.btn_refund_confirm.setFixedHeight(styles.s(55))
        self.btn_refund_confirm.setFixedWidth(styles.s(220))
        self.btn_refund_confirm.setStyleSheet("""
            QPushButton {
                background-color: #D97706;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #B45309;
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
                border-radius: 6px;
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

    def process_refund(self):
        if not self.current_card:
            raw_scan = self.txt_scan_card_r.text().strip()
            if raw_scan:
                self.process_card_scanned(raw_scan, "refund")
            else:
                CustomMessageDialog("알림", "환불할 카드를 먼저 스캔하세요.", 'warning', self).exec()
                self.txt_scan_card_r.setFocus()
                return

        cid = self.current_card.get("card_id")
        bal = int(self.current_card.get("balance", 0))
        
        if bal <= 0:
            CustomMessageDialog("환불 불가", "카드에 남아있는 잔액이 없습니다 (0원).", 'warning', self).exec()
            return

        if bal < 500:
            CustomMessageDialog("환불 불가", f"카드 잔액({bal:,}원)이 수수료(500원)보다 적어 환불할 수 없습니다.", 'warning', self).exec()
            return

        success, refund_net, fee, msg, tx = self.tm.refund_card(cid, fee=500)
        if success:
            self.current_card = self.tm.get_card(cid)
            self.card_visual_r.set_card_data(self.current_card)
            self.txt_avail_amt.setText("0 원")
            self.txt_net_amt.setText("0 원")
            
            CustomMessageDialog("환불 완료",
                                f"Tmoney 교통카드 환불이 완료되었습니다.\n\n"
                                f"• 카드 종류: Tmoney\n"
                                f"• 환불 잔액: {bal:,} 원\n"
                                f"• 수수료 차감: {fee:,} 원\n"
                                f"• 고객 실지급액: {refund_net:,} 원\n\n"
                                f"고객에게 현금 {refund_net:,}원을 지급해 주세요.",
                                'info', self).exec()
            self.show_menu()
        else:
            CustomMessageDialog("환불 오류", msg, 'warning', self).exec()

    def init_inquiry_screen(self):
        self.inquiry_widget = QWidget()
        layout = QVBoxLayout(self.inquiry_widget)
        layout.setContentsMargins(styles.s(10), styles.s(10), styles.s(10), styles.s(10))
        layout.setSpacing(styles.s(12))
        
        # 1. Scanner & Visual Card
        top_box = QHBoxLayout()
        top_box.setSpacing(styles.s(15))
        
        scan_panel = QFrame()
        scan_panel.setStyleSheet("background-color: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 8px;")
        scan_lyt = QVBoxLayout(scan_panel)
        scan_lyt.setContentsMargins(styles.s(12), styles.s(12), styles.s(12), styles.s(12))
        scan_lyt.setSpacing(styles.s(8))
        
        lbl_scan_guide = QLabel("🔍 조회 카드 스캔 (RFID / 리더기 입력)")
        lbl_scan_guide.setStyleSheet("font-size: 11pt; font-weight: bold; color: #0369A1;")
        scan_lyt.addWidget(lbl_scan_guide)
        
        self.txt_scan_card_i = QLineEdit()
        self.txt_scan_card_i.setPlaceholderText("스캐너로 카드를 인식하세요")
        self.txt_scan_card_i.setFixedHeight(styles.s(45))
        self.txt_scan_card_i.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: white;
                selection-background-color: white;
                selection-color: white;
                border: 2px solid #0284C7;
                border-radius: 6px;
                padding-left: 10px;
                font-size: 13pt;
            }
        """)
        self.txt_scan_card_i.returnPressed.connect(lambda: self.process_card_scanned(self.txt_scan_card_i.text(), "inquiry"))
        scan_lyt.addWidget(self.txt_scan_card_i)
        
        self.lbl_tag_status_i = QLabel("조회할 카드를 스캐너로 스캔하세요")
        self.lbl_tag_status_i.setStyleSheet("font-size: 10pt; color: #0284C7; font-weight: bold;")
        scan_lyt.addWidget(self.lbl_tag_status_i)
        scan_lyt.addStretch()
        
        self.card_visual_i = TransitCardVisualWidget()
        
        top_box.addWidget(scan_panel, stretch=5)
        top_box.addWidget(self.card_visual_i, stretch=5)
        layout.addLayout(top_box)
        
        # 2. History Table
        lbl_tbl = QLabel("📊 최근 거래 내역 (충전 / 결제 / 환불)")
        lbl_tbl.setStyleSheet("font-size: 12pt; font-weight: bold; color: #374151;")
        layout.addWidget(lbl_tbl)
        
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels(["일시", "구분", "변동 금액", "거래 후 잔액", "내역 / 비고"])
        self.table_history.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_history.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_history.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_history.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                gridline-color: #F3F4F6;
                font-size: 11pt;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #4B5563;
                font-weight: bold;
                font-size: 11pt;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
            }
        """)
        layout.addWidget(self.table_history, stretch=1)
        
        # 3. Action Buttons
        btn_row = QHBoxLayout()
        self.btn_inquiry_charge = QPushButton("⚡ 이 카드로 바로 충전하기")
        self.btn_inquiry_charge.setFixedHeight(styles.s(50))
        self.btn_inquiry_charge.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 6px;
                padding-left: 20px;
                padding-right: 20px;
            }
            QPushButton:hover {
                background-color: #6D28D9;
            }
        """)
        self.btn_inquiry_charge.clicked.connect(self.go_charge_from_inquiry)
        
        btn_row.addStretch()
        btn_row.addWidget(self.btn_inquiry_charge)
        layout.addLayout(btn_row)

    def go_charge_from_inquiry(self):
        cid = self.current_card.get("card_id") if self.current_card else None
        self.show_charge(cid)
