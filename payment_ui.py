from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QWidget, QLineEdit, QGridLayout,
                             QTabWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from ui_components import CustomMessageDialog

import styles

class CreditCardPaymentDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 500)
        
        self.total_amount = total_amount
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 580, 480)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border: none;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        # Layout
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Header
        self.create_header()
        
        # 2. Content (Tabs + Form)
        self.create_content()
        
        # 3. Footer
        self.create_footer()
        
        # Set Focus to Card Number
        self.txt_card_num.setFocus()
        
    def create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            background-color: #5c6bc0; /* Indigo shade matching image */
            border: none;
        """)
        header.setFixedHeight(40)
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("신용카드")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 11pt;")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { color: white; background: transparent; font-weight: bold; border: none; font-size: 12pt; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(title)
        hbox.addStretch()
        hbox.addWidget(btn_close)
        
        self.layout.addWidget(header)
        
    def create_content(self):
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {styles.GRAY_BG};")
        vbox = QVBoxLayout(content_widget)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(10)
        
        # Tabs - Only "Register" button remains as a pseudo-tab
        tabs = QWidget()
        tabs.setFixedHeight(40)
        tabs_layout = QHBoxLayout(tabs)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(2)
        
        btn_register = QPushButton("등록")
        btn_register.setCheckable(True)
        btn_register.setChecked(True)
        btn_register.setFixedSize(100, 35)
        # Active tab style
        btn_register.setStyleSheet("""
            QPushButton {
                background-color: #5C6BC0; 
                color: white; 
                font-weight: bold;
                border: none;
                font-size: 10pt;
            }
        """)
        
        tabs_layout.addWidget(btn_register)
        tabs_layout.addStretch()
        
        vbox.addWidget(tabs)
        
        # == Form Area ==
        vbox.addWidget(self.create_section_label("카드정보"))
        
        card_info_frame = QFrame()
        card_info_frame.setStyleSheet("background-color: #E8EAF6; border: none;") 
        card_grid = QGridLayout(card_info_frame)
        card_grid.setContentsMargins(0, 0, 0, 0)
        card_grid.setSpacing(1) # Gap for grid lines
        
        # Styles for labels and values
        lbl_style = "background-color: #9FA8DA; padding: 10px; font-weight: bold; color: black;"
        input_green_style = "background-color: #C8E6C9; border: 1px solid #A5D6A7; padding: 2px;" # Light green input
        
        # Row 1: Card Name
        card_grid.addWidget(self.create_label("카드사명", lbl_style), 0, 0)
        self.txt_card_name = QLineEdit()
        self.txt_card_name.setReadOnly(True) 
        self.txt_card_name.setStyleSheet("background-color: #E0E0E0; border: none;") # Grayed out
        card_grid.addWidget(self.txt_cell(self.txt_card_name), 0, 1)
        
        # Row 2: Card Number
        card_grid.addWidget(self.create_label("카드번호", lbl_style), 1, 0)
        self.txt_card_num = QLineEdit()
        self.txt_card_num.setPlaceholderText("숫자 12자리 입력")
        self.txt_card_num.setMaxLength(12)
        self.txt_card_num.setStyleSheet(input_green_style)
        card_grid.addWidget(self.txt_cell(self.txt_card_num), 1, 1)
        
        card_grid.setColumnStretch(1, 1)
        vbox.addWidget(card_info_frame)
        
        # 2. Payment Info Section
        vbox.addWidget(self.create_section_label("결제정보"))
        
        pay_info_frame = QFrame()
        pay_info_frame.setStyleSheet("background-color: #E8EAF6; border: none;")
        pay_grid = QGridLayout(pay_info_frame)
        pay_grid.setContentsMargins(0, 0, 0, 0)
        pay_grid.setSpacing(1)
        
        # Row 1: Total Amount | Payment Amount
        pay_grid.addWidget(self.create_label("결제대상금액", lbl_style), 0, 0)
        
        self.lbl_total = QLabel(f"{self.total_amount:,}")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_total.setStyleSheet("background-color: white; padding: 10px; font-weight: bold; color: black;")
        pay_grid.addWidget(self.lbl_total, 0, 1)
        
        pay_grid.addWidget(self.create_label("결제할금액", lbl_style.replace("#9FA8DA", "#7986CB")), 0, 2) # Slightly darker
        self.txt_pay_amt = QLineEdit(f"{self.total_amount}")
        self.txt_pay_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_pay_amt.setStyleSheet("background-color: white; padding: 5px; font-weight: bold; color: black;")
        pay_grid.addWidget(self.txt_cell(self.txt_pay_amt), 0, 3)
        
        # Row 2: Installments
        pay_grid.addWidget(self.create_label("할부개월", lbl_style), 1, 0)
        
        install_widget = QWidget()
        install_widget.setStyleSheet("background-color: white;")
        install_layout = QHBoxLayout(install_widget)
        install_layout.setContentsMargins(5, 5, 5, 5)
        
        self.txt_install = QLineEdit()
        self.txt_install.setFixedSize(100, 30)
        self.txt_install.setStyleSheet("border: 1px solid #BDBDBD;")
        
        lbl_install_hint = QLabel("* 일시불 : [반복/입력]")
        lbl_install_hint.setStyleSheet("color: #616161; margin-left: 10px;")
        
        install_layout.addWidget(self.txt_install)
        install_layout.addWidget(lbl_install_hint)
        install_layout.addStretch()
        
        pay_grid.addWidget(install_widget, 1, 1, 1, 3) # Span 3 cols
        
        # Row 3: Password
        pay_grid.addWidget(self.create_label("비밀번호", lbl_style), 2, 0)
        self.txt_pw = QLineEdit()
        self.txt_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pw.setStyleSheet("background-color: white; border: none;") # Or styled
        pay_grid.addWidget(self.txt_cell(self.txt_pw), 2, 1, 1, 3)
        
        # Column sizing
        pay_grid.setColumnStretch(1, 1)
        pay_grid.setColumnStretch(3, 1)
        
        vbox.addWidget(pay_info_frame)
        
        # Spacer
        vbox.addStretch()
        
        # Status Bar look-alike (empty gray box)
        status_bar = QLabel("")
        status_bar.setFixedHeight(40)
        status_bar.setStyleSheet("background-color: #CFD8DC; border: none;")
        vbox.addWidget(status_bar)
        
        self.layout.addWidget(content_widget)
        
    def create_footer(self):
        footer = QFrame()
        footer.setStyleSheet("background-color: #E0E0E0;")
        footer.setFixedHeight(60)
        
        hbox = QHBoxLayout(footer)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addStretch()
        
        btn_close = QPushButton("닫기 [CLEAR]")
        btn_close.setFixedSize(120, 40)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { background-color: #455A64; color: white; font-weight: bold; border-radius: 4px; font-size: 14pt; }
            QPushButton:hover { background-color: #37474F; }
        """)
        btn_close.clicked.connect(self.reject)
        
        btn_confirm = QPushButton("확인")
        btn_confirm.setFixedSize(100, 40)
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.setStyleSheet("""
            QPushButton { background-color: #424242; color: white; font-weight: bold; border-radius: 4px; font-size: 14pt; }
            QPushButton:hover { background-color: #212121; }
        """)
        btn_confirm.clicked.connect(self.process_payment)
        
        hbox.addWidget(btn_close)
        hbox.addWidget(btn_confirm)
        
        self.layout.addWidget(footer)

    def create_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: bold; color: #546E7A; margin-top: 5px;")
        return lbl
        
    def create_label(self, text, style):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(style)
        lbl.setFixedWidth(120)
        return lbl
        
    def txt_cell(self, widget):
        # Wrap widget in a frame for white bg if needed, or just return widget
        # The grid handling will put it in the cell. 
        # Check if we need a container to fill the cell background white
        container = QWidget()
        container.setStyleSheet("background-color: white;")
        l = QVBoxLayout(container)
        l.setContentsMargins(0,0,0,0)
        l.addWidget(widget)
        return container

    def process_payment(self):
        card_num = self.txt_card_num.text().strip()
        pay_amt_txt = self.txt_pay_amt.text().replace(",", "")
        
        if not card_num.isdigit() or len(card_num) != 12:
            CustomMessageDialog("오류", "카드번호 12자리를 올바르게 입력해주세요.", 'warning', self).exec()
            self.txt_card_num.setFocus()
            return

        if not pay_amt_txt.isdigit() or int(pay_amt_txt) <= 0:
            CustomMessageDialog("오류", "올바른 결제 금액을 입력해주세요.", 'warning', self).exec()
            self.txt_pay_amt.setFocus()
            return
            
        amt = int(pay_amt_txt)
        if amt > self.total_amount:
            CustomMessageDialog("오류", "결제 금액이 대상 금액보다 큽니다.", 'warning', self).exec()
            self.txt_pay_amt.setFocus()
            return

        self.accept()

    def get_card_number(self):
        return self.txt_card_num.text().strip()
        
    def get_payment_amount(self):
        return int(self.txt_pay_amt.text().replace(",", ""))

class CashPaymentDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 500)
        
        self.total_amount = total_amount
        self.received_amount = 0
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 580, 480)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border: 1px solid #9E9E9E;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            background-color: #546E7A; 
            border: none;
        """)
        header.setFixedHeight(40)
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("현금결제")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 11pt;")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { color: white; background: transparent; font-weight: bold; border: none; font-size: 12pt; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(title)
        hbox.addStretch()
        hbox.addWidget(btn_close)
        layout.addWidget(header)
        
        # Content
        content = QWidget()
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(20)
        
        # Total Msg
        lbl_msg = QLabel(f"합계        <span style='color: red; font-size: 24pt;'>{self.total_amount:,}</span> 원 입니다.")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_msg.setStyleSheet("font-size: 20pt; font-weight: bold; color: black;")
        vbox.addWidget(lbl_msg)
        
        vbox.addSpacing(10)
        
        # Input Area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #ECEFF1; border-radius: 5px;")
        input_layout = QHBoxLayout(input_frame)
        
        lbl_pay = QLabel("▶ 결제금액")
        lbl_pay.setStyleSheet("font-size: 14pt; font-weight: bold; color: #546E7A;")
        
        self.txt_received = QLineEdit()
        self.txt_received.setAlignment(Qt.AlignmentFlag.AlignRight)
        # Yellow background for input as in image
        self.txt_received.setStyleSheet("""
            QLineEdit {
                background-color: #FFF9C4; 
                color: black;
                border: 1px solid #BDBDBD; 
                font-size: 20pt; 
                font-weight: bold;
                padding: 10px;
            }
        """)
        # Focus input
        self.txt_received.setFocus()
        
        input_layout.addWidget(lbl_pay)
        input_layout.addWidget(self.txt_received)
        
        vbox.addWidget(input_frame)
        
        # Preset Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        presets = [("천원", 1000), ("오천원", 5000), ("만원", 10000), ("오만원", 50000)]
        for text, val in presets:
            btn = QPushButton(text)
            btn.setFixedHeight(60)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.WHITE};
                    border: 1px solid #BDBDBD;
                    border-radius: 5px;
                    font-size: 14pt;
                    font-weight: bold;
                    color: {styles.TEXT_COLOR};
                }}
                QPushButton:hover {{ background-color: #F5F5F5; }}
                QPushButton:pressed {{ background-color: #E0E0E0; }}
            """)
            btn.clicked.connect(lambda checked, v=val: self.add_amount(v))
            btn_layout.addWidget(btn)
            
        vbox.addLayout(btn_layout)
        vbox.addStretch()
        
        layout.addWidget(content)
        
        # Footer
        footer = QFrame()
        footer.setStyleSheet("background-color: #E0E0E0;")
        footer.setFixedHeight(60)
        
        hbox_foot = QHBoxLayout(footer)
        hbox_foot.setContentsMargins(10, 10, 10, 10)
        hbox_foot.addStretch()
        
        btn_close_f = QPushButton("닫기 [CLEAR]")
        btn_close_f.setFixedSize(120, 40)
        btn_close_f.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_f.setStyleSheet("""
            QPushButton { background-color: #455A64; color: white; font-weight: bold; border-radius: 4px; font-size: 14pt; }
            QPushButton:hover { background-color: #37474F; }
        """)
        btn_close_f.clicked.connect(self.reject)
        
        btn_confirm_f = QPushButton("확인")
        btn_confirm_f.setFixedSize(100, 40)
        btn_confirm_f.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm_f.setStyleSheet("""
            QPushButton { background-color: #424242; color: white; font-weight: bold; border-radius: 4px; font-size: 14pt; }
            QPushButton:hover { background-color: #212121; }
        """)
        btn_confirm_f.clicked.connect(self.process_payment)
        
        hbox_foot.addWidget(btn_close_f)
        hbox_foot.addWidget(btn_confirm_f)
        
        layout.addWidget(footer)
        
    def add_amount(self, amount):
        current_text = self.txt_received.text().replace(",", "")
        current_val = int(current_text) if current_text.isdigit() else 0
        new_val = current_val + amount
        self.txt_received.setText(f"{new_val}")
        
    def process_payment(self):
        txt = self.txt_received.text().replace(",", "")
        if not txt.isdigit() or int(txt) <= 0:
            CustomMessageDialog("오류", "올바른 금액을 입력해주세요.", 'warning', self).exec()
            self.txt_received.clear()
            self.txt_received.setFocus()
            return

        received = int(txt)
        # We now allow partial payments (received < self.total_amount)
        # The logic in main.py will handle tracking total paid amount
             
        self.received_amount = received
        self.accept()


class CashReceiptDialog(QDialog):
    def __init__(self, total_amount, received_amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(700, 650)
        
        self.total_amount = total_amount
        self.received_amount = received_amount
        self.change_amount = received_amount - total_amount
        
        self.issue_receipt = False
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 680, 630)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border: 1px solid #9E9E9E;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            background-color: #546E7A; 
            border: none;
        """)
        header.setFixedHeight(40)
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("현금영수증")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 11pt; border: none;")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { color: white; background: transparent; font-weight: bold; border: none; font-size: 12pt; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(title)
        hbox.addStretch()
        hbox.addWidget(btn_close)
        layout.addWidget(header)
        
        # Content
        content = QWidget()
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(15)
        
        # Tabs for Payment / Help (just visual from image)
        tabs_bar = QHBoxLayout()
        tabs_bar.setSpacing(0)
        
        t1 = QLabel("결제")
        t1.setFixedSize(100, 40)
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1.setStyleSheet("background-color: #546E7A; color: white; font-weight: bold; font-size: 12pt; border: none;")
        
        t2 = QLabel("도움말")
        t2.setFixedSize(100, 40)
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setStyleSheet("background-color: #E0E0E0; color: black; border: 1px solid #BDBDBD; font-size: 12pt;")
        
        tabs_bar.addWidget(t1)
        tabs_bar.addWidget(t2)
        tabs_bar.addStretch()
        vbox.addLayout(tabs_bar)
        
        # Message
        msg = QLabel(f"<span style='color: red; font-size: 20pt; font-weight: bold;'>{self.received_amount:,}</span> <span style='font-size: 20pt; font-weight: bold; color: black;'>원 받았습니다. 현금영수증 필요하세요?</span>")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("border: none;")
        vbox.addWidget(msg)
        
        vbox.addSpacing(10)
        
        # Type Tabs (Personal/Corporate)
        type_layout = QHBoxLayout()
        type_layout.setSpacing(0)
        
        btn_personal = QPushButton("개인")
        btn_personal.setFixedSize(100, 40)
        btn_personal.setStyleSheet("background-color: #9575CD; color: white; font-weight: bold; font-size: 12pt; border: none;")
        
        btn_corp = QPushButton("법인")
        btn_corp.setFixedSize(100, 40)
        btn_corp.setStyleSheet("background-color: #9E9E9E; color: white; font-weight: bold; font-size: 12pt; border: none;")
        
        type_layout.addWidget(btn_personal)
        type_layout.addWidget(btn_corp)
        type_layout.addStretch()
        vbox.addLayout(type_layout)
        
        # ID Input
        id_frame = QFrame()
        id_frame.setStyleSheet("background-color: #E8EAF6; border: 1px solid #C5CAE9;")
        id_grid = QGridLayout(id_frame)
        id_grid.setContentsMargins(0, 0, 0, 0)
        id_grid.setSpacing(0) # Removed spacing to avoid grid lines
        
        id_grid.addWidget(self.create_cell_label("발급구분"), 0, 0)
        id_grid.addWidget(self.create_cell_val("개인소득공제용"), 0, 1)
        
        id_grid.addWidget(self.create_cell_label("신분확인번호"), 1, 0)
        
        input_container = QWidget()
        input_container.setStyleSheet("background-color: white;")
        ic_layout = QHBoxLayout(input_container)
        ic_layout.setContentsMargins(5, 5, 5, 5)
        
        self.txt_id = QLineEdit()
        self.txt_id.setStyleSheet("background-color: #FFF9C4; color: black; border: 1px solid #BDBDBD; font-size: 14pt; padding: 2px;")
        
        btn_manual = QPushButton("고객직접입력 (동글입력)")
        btn_manual.setStyleSheet("background-color: #455A64; color: white; font-weight: bold; padding: 5px;")
        
        ic_layout.addWidget(self.txt_id)
        ic_layout.addWidget(btn_manual)
        
        id_grid.addWidget(input_container, 1, 1)
        id_grid.setColumnStretch(1, 1)
        
        vbox.addWidget(id_frame)
        
        # Yes/No Buttons
        yn_layout = QHBoxLayout()
        
        btn_no = QPushButton("아니오 (자동발급)")
        btn_no.setFixedSize(180, 50)
        btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_no.setStyleSheet("background-color: #455A64; color: white; font-size: 12pt; font-weight: bold; border-radius: 5px;")
        btn_no.clicked.connect(self.accept) # Proceed without receipt
        
        btn_yes = QPushButton("예 (발급하기)")
        btn_yes.setFixedSize(180, 50)
        btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_yes.setStyleSheet("background-color: #455A64; color: white; font-size: 12pt; font-weight: bold; border-radius: 5px;")
        btn_yes.clicked.connect(self.issue_and_accept)
        
        yn_layout.addStretch()
        yn_layout.addWidget(btn_no)
        yn_layout.addWidget(btn_yes)
        vbox.addLayout(yn_layout)

        
        # Summary Footer
        summary_frame = QFrame()
        summary_frame.setFixedHeight(120)
        summary_frame.setStyleSheet("border-top: 2px solid #BDBDBD;")
        sum_layout = QHBoxLayout(summary_frame)
        
        # Left: received method
        l_layout = QVBoxLayout()
        l_label = QLabel("현금")
        l_label.setStyleSheet("font-size: 14pt; color: #616161;")
        l_amt = QLabel(f"{self.received_amount:,}원")
        l_amt.setStyleSheet("font-size: 14pt; color: #616161;")
        l_layout.addWidget(l_label)
        l_layout.addWidget(l_amt)
        l_layout.addStretch()
        
        sum_layout.addLayout(l_layout)
        sum_layout.addStretch()
        
        # Right: Breakdown
        r_grid = QGridLayout()
        r_grid.setVerticalSpacing(5)
        r_grid.setHorizontalSpacing(20)
        
        lbl_tot_title = QLabel("총 금액")
        lbl_tot_title.setStyleSheet("color: black; font-size: 12pt; border: none;")
        r_grid.addWidget(lbl_tot_title, 0, 0)
        
        lbl_tot = QLabel(f"{self.total_amount:,} 원")
        lbl_tot.setStyleSheet("font-size: 24pt; font-weight: bold; color: black; border: none;")
        r_grid.addWidget(lbl_tot, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
        lbl_pd_title = QLabel("결제한 금액")
        lbl_pd_title.setStyleSheet("color: black; font-size: 12pt; border: none;")
        r_grid.addWidget(lbl_pd_title, 1, 0)
        
        lbl_pd = QLabel(f"{self.received_amount:,} 원")
        lbl_pd.setStyleSheet("font-size: 14pt; font-weight: bold; color: black; border: none;")
        r_grid.addWidget(lbl_pd, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
        lbl_chg_title = QLabel("거스름돈")
        lbl_chg_title.setStyleSheet("color: black; font-size: 12pt; border: none;")
        r_grid.addWidget(lbl_chg_title, 2, 0)
        
        lbl_chg = QLabel(f"{self.change_amount:,} 원")
        lbl_chg.setStyleSheet("font-size: 18pt; font-weight: bold; color: #E53935; border: none;")
        r_grid.addWidget(lbl_chg, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
        sum_layout.addLayout(r_grid)
        
        vbox.addWidget(summary_frame)
        
        layout.addWidget(content)

    def create_cell_label(self, text):
        l = QLabel(text)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setStyleSheet("background-color: #E8EAF6; font-weight: bold; color: #5C6BC0; padding: 10px;")
        l.setFixedWidth(120)
        return l
        
    def create_cell_val(self, text):
        l = QLabel(text)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        l.setStyleSheet("background-color: white; padding: 10px; font-weight: bold;")
        return l

    def issue_and_accept(self):
        self.issue_receipt = True
        self.accept()
        
    def get_receipt_id(self):
        return self.txt_id.text().strip()
