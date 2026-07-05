from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QWidget, QLineEdit, QGridLayout,
                             QGraphicsDropShadowEffect, QButtonGroup)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from ui_components import CustomMessageDialog

import styles

try:
    from smartcard.System import readers
    from smartcard.Exceptions import NoCardException, CardConnectionException
    SMARTCARD_AVAILABLE = True
except ImportError:
    SMARTCARD_AVAILABLE = False

class CreditCardPaymentDialog(QDialog):
    def __init__(self, total_amount, firebase_mgr=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(680), styles.s(520))
        
        self.total_amount = total_amount
        self.firebase_mgr = firebase_mgr
        if self.firebase_mgr is None:
            try:
                from firebase_manager import FirebaseManager
                self.firebase_mgr = FirebaseManager()
            except Exception:
                self.firebase_mgr = None
        self.is_auto_processing = False
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(660), styles.s(500))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: #ECEFF1;
                border: 2px solid #10355C;
                border-radius: 0px;
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
        self.txt_card_num.textChanged.connect(self.on_card_num_changed)
        self.txt_card_num.returnPressed.connect(self.process_payment)
        
        # Smart Card Reader States
        self.last_card_state = "DISCONNECTED"
        self.active_reader = None
        self.connection = None
        
        self.card_timer = QTimer(self)
        self.card_timer.timeout.connect(self.check_card_loop)
        if SMARTCARD_AVAILABLE:
            self.card_timer.start(800)
            self.lbl_card_status.setText("● 리더기 감지 중...")
            self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #F59E0B; font-family: 'Malgun Gothic';")
        else:
            self.lbl_card_status.setText("● 스마트카드 모듈 미설치")
            self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #EF4444; font-family: 'Malgun Gothic';")

    def create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            background-color: #10355C;
            border-radius: 0px;
            border: none;
        """)
        header.setFixedHeight(styles.s(50))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        title = QLabel("신용카드")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 14pt; font-family: 'Malgun Gothic';")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(styles.s(30), styles.s(30))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                font-weight: bold;
                border: none;
                font-size: 13pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(title)
        hbox.addStretch()
        hbox.addWidget(btn_close)
        
        self.layout.addWidget(header)

        # Tab sub-header row
        tab_bar = QFrame()
        tab_bar.setFixedHeight(styles.s(45))
        tab_bar.setStyleSheet("""
            background-color: #E5EBF2;
            border-bottom: 1px solid #B4C4D4;
            border-radius: 0px;
        """)
        tab_lyt = QHBoxLayout(tab_bar)
        tab_lyt.setContentsMargins(styles.s(20), styles.s(5), styles.s(20), styles.s(5))
        tab_lyt.setSpacing(styles.s(8))
        
        btn_reg = QPushButton("등록")
        btn_reg.setFixedSize(styles.s(80), styles.s(30))
        btn_reg.setStyleSheet("""
            QPushButton {
                background-color: #1C3E68;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #1C3E68;
                border-radius: 2px;
            }
        """)
        
        btn_help = QPushButton("도움말")
        btn_help.setFixedSize(styles.s(80), styles.s(30))
        btn_help.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #374151;
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #B4C4D4;
                border-radius: 2px;
            }
        """)
        
        tab_lyt.addWidget(btn_reg)
        tab_lyt.addWidget(btn_help)
        tab_lyt.addStretch()
        
        btn_globe = QPushButton("🌐")
        btn_globe.setFixedSize(styles.s(32), styles.s(32))
        btn_globe.setStyleSheet("QPushButton { background: transparent; font-size: 14pt; border: none; }")
        
        btn_speaker = QPushButton("🔊")
        btn_speaker.setFixedSize(styles.s(32), styles.s(32))
        btn_speaker.setStyleSheet("QPushButton { background: transparent; font-size: 14pt; border: none; }")
        
        tab_lyt.addWidget(btn_globe)
        tab_lyt.addWidget(btn_speaker)
        
        self.layout.addWidget(tab_bar)

        
    def create_content(self):
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #ECEFF1; border: none;")
        vbox = QVBoxLayout(content_widget)
        vbox.setContentsMargins(styles.s(20), styles.s(15), styles.s(20), styles.s(10))
        vbox.setSpacing(styles.s(10))
        
        lbl_style = """
            background-color: #D8E3EC;
            color: #10355C;
            font-weight: bold;
            font-size: 10pt;
            font-family: 'Malgun Gothic';
            border: 1px solid #B4C4D4;
            padding: 6px;
        """
        
        input_style = """
            QLineEdit {
                background-color: white;
                color: black;
                font-size: 10pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #B4C4D4;
                border-radius: 0px;
                padding: 5px;
            }
            QLineEdit:read-only {
                background-color: #E6EAEF;
                color: #777777;
            }
            QLineEdit:focus {
                border: 2px solid #1C3E68;
                background-color: #FFFDE7;
            }
        """
        
        val_lbl_style = """
            background-color: white;
            color: black;
            font-size: 10pt;
            font-family: 'Malgun Gothic';
            border: 1px solid #B4C4D4;
            padding: 6px;
        """

        # 1. 카드정보
        card_title = QLabel("카드정보")
        card_title.setStyleSheet("color: #10355C; font-weight: bold; font-size: 11pt; font-family: 'Malgun Gothic'; background: transparent;")
        vbox.addWidget(card_title)
        
        card_grid = QGridLayout()
        card_grid.setSpacing(0)
        card_grid.setColumnStretch(1, 1)
        
        # 카드사명
        lbl_name = QLabel("카드사명")
        lbl_name.setStyleSheet(lbl_style)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_card_name = QLineEdit()
        self.txt_card_name.setReadOnly(True)
        self.txt_card_name.setPlaceholderText("카드 스캔 시 자동 인식")
        self.txt_card_name.setStyleSheet(input_style)
        card_grid.addWidget(lbl_name, 0, 0)
        card_grid.addWidget(self.txt_card_name, 0, 1)
        
        # 카드번호
        lbl_num = QLabel("카드 번호")
        lbl_num.setStyleSheet(lbl_style)
        lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_card_num = QLineEdit()
        self.txt_card_num.setPlaceholderText("스캔하거나 카드 번호를 입력하세요")
        self.txt_card_num.setMaxLength(20)
        self.txt_card_num.setStyleSheet(input_style + "QLineEdit { background-color: #EAF7EA; }")
        card_grid.addWidget(lbl_num, 1, 0)
        card_grid.addWidget(self.txt_card_num, 1, 1)
        
        vbox.addLayout(card_grid)
        vbox.addSpacing(styles.s(10))
        
        # 2. 결제정보
        pay_title = QLabel("결제정보")
        pay_title.setStyleSheet("color: #10355C; font-weight: bold; font-size: 11pt; font-family: 'Malgun Gothic'; background: transparent;")
        vbox.addWidget(pay_title)
        
        pay_grid = QGridLayout()
        pay_grid.setSpacing(0)
        pay_grid.setColumnStretch(1, 1)
        pay_grid.setColumnStretch(3, 1)
        
        # 결제대상금액
        lbl_target_amt = QLabel("결제대상금액")
        lbl_target_amt.setStyleSheet(lbl_style)
        lbl_target_amt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_target_val = QLabel(f"{self.total_amount:,}")
        self.lbl_target_val.setStyleSheet(val_lbl_style)
        self.lbl_target_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        pay_grid.addWidget(lbl_target_amt, 0, 0)
        pay_grid.addWidget(self.lbl_target_val, 0, 1)
        
        # 결제할금액
        lbl_pay_amt = QLabel("결제할 금액")
        lbl_pay_amt.setStyleSheet(lbl_style)
        lbl_pay_amt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.txt_pay_amt = QLineEdit(f"{self.total_amount}")
        self.txt_pay_amt.setStyleSheet(input_style)
        self.txt_pay_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        pay_grid.addWidget(lbl_pay_amt, 0, 2)
        pay_grid.addWidget(self.txt_pay_amt, 0, 3)
        
        # 할부개월
        lbl_install = QLabel("할부개월")
        lbl_install.setStyleSheet(lbl_style)
        lbl_install.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        install_cell = QFrame()
        install_cell.setStyleSheet("background-color: white; border: 1px solid #B4C4D4; border-radius: 0px;")
        cell_lyt = QHBoxLayout(install_cell)
        cell_lyt.setContentsMargins(styles.s(5), styles.s(2), styles.s(5), styles.s(2))
        cell_lyt.setSpacing(styles.s(10))
        
        self.txt_install = QLineEdit()
        self.txt_install.setPlaceholderText("0")
        self.txt_install.setFixedWidth(styles.s(80))
        self.txt_install.setStyleSheet("border: 1px solid #CCCCCC; padding: 3px; font-size: 10pt; font-family: 'Malgun Gothic';")
        
        lbl_hint = QLabel("* 일시불 : [반복/입력]")
        lbl_hint.setStyleSheet("font-size: 9pt; color: #555555; font-family: 'Malgun Gothic'; font-weight: bold;")
        
        cell_lyt.addWidget(self.txt_install)
        cell_lyt.addWidget(lbl_hint)
        cell_lyt.addStretch()
        
        pay_grid.addWidget(lbl_install, 1, 0)
        pay_grid.addWidget(install_cell, 1, 1, 1, 3)
        
        # 비밀번호
        lbl_pw = QLabel("비밀번호")
        lbl_pw.setStyleSheet(lbl_style)
        lbl_pw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.txt_pw = QLineEdit()
        self.txt_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pw.setPlaceholderText("카드 비밀번호 앞 2자리")
        self.txt_pw.setStyleSheet(input_style)
        
        pay_grid.addWidget(lbl_pw, 2, 0)
        pay_grid.addWidget(self.txt_pw, 2, 1, 1, 3)
        
        # IC카드 상태
        lbl_status = QLabel("IC카드 상태")
        lbl_status.setStyleSheet(lbl_style)
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_card_status = QLabel("● 리더기 확인 중...")
        self.lbl_card_status.setStyleSheet("background-color: white; color: #F59E0B; font-weight: bold; font-size: 10pt; font-family: 'Malgun Gothic'; border: 1px solid #B4C4D4; padding: 6px;")
        
        pay_grid.addWidget(lbl_status, 3, 0)
        pay_grid.addWidget(self.lbl_card_status, 3, 1, 1, 3)
        
        vbox.addLayout(pay_grid)
        vbox.addStretch()
        
        self.layout.addWidget(content_widget)

    def create_footer(self):
        footer = QFrame()
        footer.setStyleSheet("""
            background-color: #ECEFF1;
            border-top: 1px solid #B4C4D4;
            border-radius: 0px;
        """)
        footer.setFixedHeight(styles.s(60))
        
        hbox = QHBoxLayout(footer)
        hbox.setContentsMargins(styles.s(20), styles.s(10), styles.s(20), styles.s(10))
        hbox.setSpacing(styles.s(15))
        hbox.addStretch()
        
        btn_close = QPushButton("닫기 [CLEAR]")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedHeight(styles.s(38))
        btn_close.setFixedWidth(styles.s(130))
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #10355C;
                color: white;
                font-weight: bold;
                border-radius: 0px;
                font-size: 11pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #10355C;
            }
            QPushButton:hover { background-color: #1C3E68; }
        """)
        btn_close.clicked.connect(self.reject)
        
        self.btn_confirm = QPushButton("확인")
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setFixedHeight(styles.s(38))
        self.btn_confirm.setFixedWidth(styles.s(110))
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #10355C;
                color: white;
                font-weight: bold;
                border-radius: 0px;
                font-size: 11pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #10355C;
            }
            QPushButton:hover { background-color: #1C3E68; }
        """)
        self.btn_confirm.clicked.connect(self.process_payment)
        
        hbox.addWidget(btn_close)
        hbox.addWidget(self.btn_confirm)
        
        self.layout.addWidget(footer)


    def process_payment(self):
        card_num = self.txt_card_num.text().strip()
        pay_amt_txt = self.txt_pay_amt.text().replace(",", "")
        
        cleaned_num = card_num.replace("-", "")
        if not cleaned_num.isdigit() or not (11 <= len(cleaned_num) <= 16):
            CustomMessageDialog("오류", "올바른 계좌/카드번호를 입력해주세요.", 'warning', self).exec()
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

        self.start_card_transaction(card_num, amt)

    def on_card_num_changed(self, text):
        cleaned = text.replace("-", "")
        is_card_or_full = len(cleaned) in (12, 16) or getattr(self, 'is_card_reading', False)
        if is_card_or_full and cleaned.isdigit() and not self.is_auto_processing:
            self.start_auto_payment()

    def start_auto_payment(self):
        card_num = self.txt_card_num.text().strip()
        pay_amt_txt = self.txt_pay_amt.text().replace(",", "")
        cleaned_num = card_num.replace("-", "")
        if cleaned_num.isdigit() and (11 <= len(cleaned_num) <= 16) and pay_amt_txt.isdigit():
            self.is_auto_processing = True
            self.start_card_transaction(card_num, int(pay_amt_txt))

    def start_card_transaction(self, card_num, amount):
        self.show_approval_overlay(
            'processing',
            '💳 결제 승인 요청',
            '결제 승인 중입니다.\n카드를 빼지 마세요.',
            f'전송 금액: {amount:,}원',
            '⏳ 카드사 서버와 통신 중...'
        )
        self.btn_confirm.setEnabled(False)
        QTimer.singleShot(2000, lambda: self.execute_firebase_payment(card_num, amount))

    def execute_firebase_payment(self, card_num, amount):
        if not self.firebase_mgr:
            self.show_approval_overlay(
                'success',
                '✅ 결제 승인 완료',
                '결제가 정상적으로 완료되었습니다. (오프라인 모드)',
                f'승인 금액: {amount:,}원',
                '카드 및 영수증을 확인해 주세요.'
            )
            self.final_balance_after = 0.0
            QTimer.singleShot(1500, self.accept)
            return

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

        success, message, balance = self.firebase_mgr.process_payment(
            account_number=card_num,
            pin_input="",
            amount=amount,
            store_name=store_name,
            bypass_pin=True
        )

        if success:
            self.final_balance_after = balance
            self.show_approval_overlay(
                'success',
                '✅ 결제 승인 완료',
                '결제가 성공적으로 처리되었습니다.',
                f'승인 금액: {amount:,}원 | 남은 잔액: {int(balance):,}원',
                '카드 및 영수증을 확인해 주세요.'
            )
            QTimer.singleShot(1500, self.accept)
        else:
            self.btn_confirm.setEnabled(True)
            self.is_auto_processing = False
            self.show_approval_overlay(
                'error',
                '❌ 결제 승인 실패',
                '결제 승인 오류가 발생했습니다.',
                f'사유: {message}',
                '확인 버튼을 눌러 이전 화면으로 돌아갑니다.'
            )

    def get_card_number(self):
        return self.txt_card_num.text().strip()
        
    def get_payment_amount(self):
        return int(self.txt_pay_amt.text().replace(",", ""))

    def accept(self):
        self.card_timer.stop()
        super().accept()

    def reject(self):
        self.card_timer.stop()
        super().reject()

    def closeEvent(self, event):
        self.card_timer.stop()
        super().closeEvent(event)

    def check_card_loop(self):
        if not SMARTCARD_AVAILABLE:
            return
        try:
            rs = readers()
            if not rs:
                self.lbl_card_status.setText("● 카드 리더기 연결 안 됨")
                self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #EF4444; font-family: 'Malgun Gothic';")
                self.set_disconnected_state()
            else:
                self.active_reader = rs[0]
                self.auto_read_card()
        except Exception:
            self.lbl_card_status.setText("● 리더기 확인 중 오류")
            self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #EF4444; font-family: 'Malgun Gothic';")
            self.set_disconnected_state()

    def set_disconnected_state(self):
        self.last_card_state = "DISCONNECTED"
        self.connection = None

    def auto_read_card(self):
        if not self.active_reader:
            return
            
        if self.connection is not None and self.last_card_state == "READY":
            try:
                # Fast presence check
                read_cmd = [0xFF, 0xB0, 0x00, 0x00, 0x01]
                self.connection.transmit(read_cmd)
                return
            except Exception:
                self.lbl_card_status.setText("● 카드를 삽입해주세요")
                self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #3B82F6; font-family: 'Malgun Gothic';")
                self.set_disconnected_state()
                return

        try:
            conn = self.active_reader.createConnection()
            connected = False
            for protocol in [1, 2, 3]:
                try:
                    conn.connect(protocol)
                    connected = True
                    break
                except Exception:
                    continue
            
            if not connected:
                conn.connect()
                
            self.connection = conn
            
            if self.last_card_state != "READY":
                self.lbl_card_status.setText("● 카드 읽는 중...")
                self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #F59E0B; font-family: 'Malgun Gothic';")
                from PyQt6.QtWidgets import QApplication
                QApplication.processEvents()
                
                card_number = self.read_card_number_sequence()
                if card_number:
                    digits_only = "".join([c for c in card_number if c.isdigit()])
                    if len(digits_only) > 16:
                        digits_only = digits_only[:16]
                    
                    if digits_only:
                        self.is_card_reading = True
                        self.txt_card_num.setText(digits_only)
                        self.is_card_reading = False
                        self.txt_card_name.setText("IC 카드")
                        self.lbl_card_status.setText("● 카드 인식 성공")
                        self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #10B981; font-family: 'Malgun Gothic';")
                        self.last_card_state = "READY"
                    else:
                        self.lbl_card_status.setText("● 인식 실패 (데이터 없음)")
                        self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #EF4444; font-family: 'Malgun Gothic';")
                        self.last_card_state = "READY"
                else:
                    self.lbl_card_status.setText("● 인식 실패 (다시 시도)")
                    self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #EF4444; font-family: 'Malgun Gothic';")
                    self.last_card_state = "READY"
                    
        except NoCardException:
            self.lbl_card_status.setText("● 카드를 삽입해주세요")
            self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #3B82F6; font-family: 'Malgun Gothic';")
            self.set_disconnected_state()
        except CardConnectionException:
            self.lbl_card_status.setText("● 카드 인식 오류")
            self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #EF4444; font-family: 'Malgun Gothic';")
            self.last_card_state = "DISCONNECTED"
        except Exception:
            self.lbl_card_status.setText("● 카드 감지 중 오류")
            self.lbl_card_status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #EF4444; font-family: 'Malgun Gothic';")
            self.set_disconnected_state()

    def read_card_number_sequence(self):
        if not self.connection:
            return None
        try:
            # 1. Initialize SLE4442 card
            init_cmd = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
            self.connection.transmit(init_cmd)
            
            # 2. Read 20 bytes from address 0x00
            read_cmd = [0xFF, 0xB0, 0x00, 0x00, 0x14]
            data, sw1, sw2 = self.connection.transmit(read_cmd)
            
            if sw1 == 0x90 and sw2 == 0x00:
                decoded = "".join([chr(x) for x in data if 32 <= x <= 126])
                return decoded.strip()
        except Exception:
            pass
        return None

    def show_approval_overlay(self, status_type, title, main_msg, sub_msg, status_msg):
        # Remove old overlay if exists
        if hasattr(self, 'approval_overlay') and self.approval_overlay is not None:
            try:
                self.approval_overlay.deleteLater()
            except Exception:
                pass
            self.approval_overlay = None
            
        self.approval_overlay = QFrame(self.container)
        self.approval_overlay.setGeometry(0, styles.s(95), styles.s(660), styles.s(405))
        self.approval_overlay.setStyleSheet("background-color: white; border-top: 1px solid #B4C4D4; border-radius: 0px; border: none;")
        
        layout = QVBoxLayout(self.approval_overlay)
        layout.setContentsMargins(styles.s(40), styles.s(45), styles.s(40), styles.s(45))
        layout.setSpacing(styles.s(15))
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        if status_type == 'success':
            title_color = "#10B981"
        elif status_type == 'error':
            title_color = "#EF4444"
        else:
            title_color = styles.PRIMARY_PURPLE
        title_label.setStyleSheet(f"font-size: {styles.fs(18)}; font-weight: bold; color: {title_color}; font-family: 'Malgun Gothic';")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {title_color}; height: 2px;")
        line.setFixedHeight(2)
        
        msg_main = QLabel(main_msg)
        msg_main.setStyleSheet(f"font-size: {styles.fs(20)}; font-weight: bold; color: #1F2937; font-family: 'Malgun Gothic';")
        msg_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_main.setWordWrap(True)
        
        msg_sub = QLabel(sub_msg)
        msg_sub.setStyleSheet(f"font-size: {styles.fs(12)}; color: #6B7280; font-family: 'Malgun Gothic';")
        msg_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_sub.setWordWrap(True)
        
        msg_status = QLabel(status_msg)
        msg_status.setStyleSheet(f"font-size: {styles.fs(12)}; color: {title_color}; font-weight: bold; font-family: 'Malgun Gothic';")
        msg_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(line)
        layout.addStretch()
        layout.addWidget(msg_main)
        layout.addWidget(msg_sub)
        layout.addStretch()
        layout.addWidget(msg_status)
        
        if status_type == 'error':
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(styles.s(15))
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn_retry = QPushButton("다시 시도")
            btn_retry.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_retry.setFixedHeight(styles.s(38))
            btn_retry.setFixedWidth(styles.s(110))
            btn_retry.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.PRIMARY_PURPLE};
                    color: white;
                    font-weight: bold;
                    border-radius: {styles.s(5)}px;
                    font-size: {styles.fs(11)};
                    border: none;
                }}
                QPushButton:hover {{ background-color: #6D28D9; }}
            """)
            btn_retry.clicked.connect(self.hide_approval_overlay)
            
            btn_cancel = QPushButton("결제 취소")
            btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_cancel.setFixedHeight(styles.s(38))
            btn_cancel.setFixedWidth(styles.s(110))
            btn_cancel.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: #4B5563;
                    font-weight: bold;
                    border: 1px solid #D1D5DB;
                    border-radius: {styles.s(5)}px;
                    font-size: {styles.fs(11)};
                }}
                QPushButton:hover {{ background-color: #F3F4F6; }}
            """)
            btn_cancel.clicked.connect(self.reject)
            
            btn_layout.addWidget(btn_retry)
            btn_layout.addWidget(btn_cancel)
            layout.addLayout(btn_layout)
            
        self.approval_overlay.show()
        self.approval_overlay.raise_()

    def hide_approval_overlay(self):
        if hasattr(self, 'approval_overlay') and self.approval_overlay is not None:
            try:
                self.approval_overlay.deleteLater()
            except Exception:
                pass
            self.approval_overlay = None




class CashPaymentDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(760), styles.s(530))
        
        self.total_amount = total_amount
        self.received_amount = 0
        
        # Main dialog layout (adds 10px margin around container for shadow)
        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.setContentsMargins(10, 10, 10, 10)
        
        # Main Container
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(10)}px;
                border: 1px solid #757575;
            }}
        """)
        main_dialog_layout.addWidget(self.container)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header / Title Bar
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #4E5154; 
            border-top-left-radius: {styles.s(9)}px;
            border-top-right-radius: {styles.s(9)}px;
            border: none;
            border-bottom: 1px solid #757575;
        """)
        header.setFixedHeight(styles.s(60))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(25), 0, styles.s(25), 0)
        
        title = QLabel("현금결제")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 16pt; font-family: 'Malgun Gothic';")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(styles.s(36), styles.s(36))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                font-weight: bold;
                border: none;
                font-size: 15pt;
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
        layout.addWidget(header)
        
        # Content Widget
        content = QWidget()
        content.setStyleSheet("background-color: white; border: none;")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(styles.s(30), styles.s(25), styles.s(30), styles.s(20))
        vbox.setSpacing(styles.s(20))
        
        # Total Amount Row
        total_section = QWidget()
        total_section.setStyleSheet("background: transparent; border: none;")
        total_section_layout = QHBoxLayout(total_section)
        total_section_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_total_title = QLabel("합계")
        lbl_total_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #212121; font-family: 'Malgun Gothic';")
        
        right_info_widget = QWidget()
        right_info_layout = QVBoxLayout(right_info_widget)
        right_info_layout.setContentsMargins(0, 0, 0, 0)
        right_info_layout.setSpacing(styles.s(6))
        
        # Globe & Speaker Row
        icon_row = QHBoxLayout()
        icon_row.setContentsMargins(0, 0, 0, 0)
        icon_row.setSpacing(styles.s(8))
        icon_row.addStretch()
        
        btn_globe = QPushButton("🌐")
        btn_globe.setFixedSize(styles.s(34), styles.s(34))
        btn_globe.setStyleSheet("""
            QPushButton {
                background-color: #ECEFF1;
                border: 1px solid #CFD8DC;
                border-radius: 17px;
                color: #546E7A;
                font-size: 13pt;
            }
        """)
        
        btn_speaker = QPushButton("🔊")
        btn_speaker.setFixedSize(styles.s(34), styles.s(34))
        btn_speaker.setStyleSheet("""
            QPushButton {
                background-color: #ECEFF1;
                border: 1px solid #CFD8DC;
                border-radius: 17px;
                color: #546E7A;
                font-size: 13pt;
            }
        """)
        
        icon_row.addWidget(btn_globe)
        icon_row.addWidget(btn_speaker)
        
        lbl_total_val = QLabel()
        lbl_total_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_total_val.setText(f"<span style='color: #D32F2F; font-size: 28pt; font-weight: bold;'>{self.total_amount:,}</span> <span style='color: #212121; font-size: 20pt; font-weight: bold;'>원 입니다.</span>")
        
        right_info_layout.addLayout(icon_row)
        right_info_layout.addWidget(lbl_total_val)
        
        total_section_layout.addWidget(lbl_total_title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        total_section_layout.addWidget(right_info_widget)
        
        vbox.addWidget(total_section)
        
        # Horizontal Separator line 1
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("background-color: #E0E0E0; max-height: 1px; border: none;")
        vbox.addWidget(line1)
        
        # Input Container Row (Gray background frame)
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: #ECEFF1;
                border: 1px solid #CFD8DC;
                border-radius: 6px;
            }
        """)
        input_container_layout = QHBoxLayout(input_container)
        input_container_layout.setContentsMargins(styles.s(20), styles.s(12), styles.s(20), styles.s(12))
        input_container_layout.setSpacing(styles.s(20))
        
        lbl_pay = QLabel("▶ 결제금액")
        lbl_pay.setStyleSheet("font-size: 15pt; font-weight: bold; color: #37474F; border: none; background: transparent; font-family: 'Malgun Gothic';")
        
        self.txt_received = QLineEdit()
        self.txt_received.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_received.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FFFDE7; /* Light yellow background */
                color: #212121;
                border: 1px solid #B0BEC5; 
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(24)}; 
                font-weight: bold;
                padding: {styles.s(8)}px {styles.s(15)}px;
                font-family: '{styles.FONT_FAMILY}';
            }}
            QLineEdit:focus {{
                border: 1px solid #78909C;
            }}
        """)
        
        input_container_layout.addWidget(lbl_pay)
        input_container_layout.addWidget(self.txt_received, stretch=1)
        vbox.addWidget(input_container)
        
        # Preset Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(styles.s(12))
        
        presets = [("천원", 1000), ("오천원", 5000), ("만원", 10000), ("오만원", 50000)]
        for text, val in presets:
            btn = QPushButton(text)
            btn.setFixedHeight(styles.s(55))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #F5F7FA;
                    border: 1px solid #CFD8DC;
                    border-radius: {styles.s(4)}px;
                    font-size: {styles.fs(15)};
                    font-weight: bold;
                    color: #37474F;
                    font-family: '{styles.FONT_FAMILY}';
                }}
                QPushButton:hover {{
                    background-color: #ECEFF1;
                }}
                QPushButton:pressed {{
                    background-color: #CFD8DC;
                }}
            """)
            btn.clicked.connect(lambda checked, v=val: self.add_amount(v))
            btn_layout.addWidget(btn)
            
        vbox.addLayout(btn_layout)
        vbox.addStretch()
        
        # Horizontal Separator line 2
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: #E0E0E0; max-height: 1px; border: none;")
        vbox.addWidget(line2)
        
        # Bottom Confirm Row
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addStretch()
        
        btn_confirm = QPushButton("확인")
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.setFixedSize(styles.s(140), styles.s(45))
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: #4E5154;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(15)};
                border: none;
            }}
            QPushButton:hover {{
                background-color: #3C3F41;
            }}
            QPushButton:pressed {{
                background-color: #2E3032;
            }}
        """)
        btn_confirm.clicked.connect(self.process_payment)
        bottom_layout.addWidget(btn_confirm)
        vbox.addLayout(bottom_layout)
        
        layout.addWidget(content)
        
        # Default value setup
        self.txt_received.setText(f"{self.total_amount}")
        self.txt_received.selectAll()
        self.txt_received.setFocus()
        
    def add_amount(self, amount):
        current_text = self.txt_received.text().replace(",", "")
        current_val = int(current_text) if current_text.isdigit() else 0
        new_val = current_val + amount
        self.txt_received.setText(f"{new_val:,}")
        
    def process_payment(self):
        txt = self.txt_received.text().replace(",", "")
        if not txt.isdigit() or int(txt) <= 0:
            CustomMessageDialog("오류", "올바른 금액을 입력해주세요.", 'warning', self).exec()
            self.txt_received.clear()
            self.txt_received.setFocus()
            return

        received = int(txt)
        self.received_amount = received
        self.accept()


# (Old duplicate CashReceiptDialog class removed. New customized version is defined at the bottom of the file.)


class TransitCardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(520), styles.s(450))
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(500), styles.s(430))
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(15)}px;
                border: 1px solid {styles.BORDER_COLOR};
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
        
        # 2. Content Stack Widget
        from PyQt6.QtWidgets import QStackedWidget
        self.stack = QStackedWidget()
        
        self.init_main_menu()
        self.init_charge_screen()
        self.init_refund_screen()
        
        self.stack.addWidget(self.menu_widget)
        self.stack.addWidget(self.charge_widget)
        self.stack.addWidget(self.refund_widget)
        
        self.layout.addWidget(self.stack)
        
        # Default index
        self.stack.setCurrentIndex(0)
        
    def create_header(self):
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #8A79B6; /* Service Purple Theme */
            border-top-left-radius: {styles.s(15)}px;
            border-top-right-radius: {styles.s(15)}px;
            border: none;
        """)
        header.setFixedHeight(styles.s(55))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        self.lbl_title = QLabel("교통카드 서비스")
        self.lbl_title.setStyleSheet("color: white; font-weight: bold; font-size: 14pt; font-family: 'Malgun Gothic';")
        
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
                border-radius: 15px;
            }
        """)
        btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(self.lbl_title)
        hbox.addStretch()
        hbox.addWidget(btn_close)
        
        self.layout.addWidget(header)
        
    def init_main_menu(self):
        self.menu_widget = QWidget()
        lyt = QVBoxLayout(self.menu_widget)
        lyt.setContentsMargins(styles.s(25), styles.s(30), styles.s(25), styles.s(30))
        lyt.setSpacing(styles.s(20))
        
        # Guide Label
        lbl_guide = QLabel("원하시는 서비스를 선택하세요")
        lbl_guide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_guide.setStyleSheet(f"font-size: {styles.fs(14)}; font-weight: bold; color: #374151; font-family: '{styles.FONT_FAMILY}';")
        lyt.addWidget(lbl_guide)
        
        # Grid for two large buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(styles.s(15))
        
        # 1. Charge Button
        self.btn_goto_charge = QPushButton()
        self.btn_goto_charge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_goto_charge.setFixedHeight(styles.s(180))
        self.btn_goto_charge.setStyleSheet(f"""
            QPushButton {{
                background-color: #EDE9FE;
                border: 2px solid #C4B5FD;
                border-radius: {styles.s(12)}px;
            }}
            QPushButton:hover {{
                background-color: #DDD6FE;
                border: 2px solid #A78BFA;
            }}
        """)
        c_layout = QVBoxLayout(self.btn_goto_charge)
        c_layout.setContentsMargins(styles.s(15), styles.s(20), styles.s(15), styles.s(20))
        c_layout.setSpacing(styles.s(10))
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_c_icon = QLabel("⚡")
        lbl_c_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_icon.setStyleSheet(f"font-size: {styles.fs(36)}; background: transparent; border: none;")
        
        lbl_c_title = QLabel("교통카드 충전")
        lbl_c_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_title.setStyleSheet(f"font-size: {styles.fs(16)}; font-weight: bold; color: #4C1D95; background: transparent; border: none;")
        
        lbl_c_desc = QLabel("현금을 투입하고\n카드를 충전합니다")
        lbl_c_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_desc.setStyleSheet(f"font-size: {styles.fs(11)}; color: #6D28D9; background: transparent; border: none;")
        
        c_layout.addWidget(lbl_c_icon)
        c_layout.addWidget(lbl_c_title)
        c_layout.addWidget(lbl_c_desc)
        self.btn_goto_charge.clicked.connect(self.show_charge)
        
        # 2. Refund Button
        self.btn_goto_refund = QPushButton()
        self.btn_goto_refund.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_goto_refund.setFixedHeight(styles.s(180))
        self.btn_goto_refund.setStyleSheet(f"""
            QPushButton {{
                background-color: #FEF3C7;
                border: 2px solid #FDE68A;
                border-radius: {styles.s(12)}px;
            }}
            QPushButton:hover {{
                background-color: #FDE68A;
                border: 2px solid #FCD34D;
            }}
        """)
        r_layout = QVBoxLayout(self.btn_goto_refund)
        r_layout.setContentsMargins(styles.s(15), styles.s(20), styles.s(15), styles.s(20))
        r_layout.setSpacing(styles.s(10))
        r_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_r_icon = QLabel("🪙")
        lbl_r_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_icon.setStyleSheet(f"font-size: {styles.fs(36)}; background: transparent; border: none;")
        
        lbl_r_title = QLabel("교통카드 환불")
        lbl_r_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_title.setStyleSheet(f"font-size: {styles.fs(16)}; font-weight: bold; color: #78350F; background: transparent; border: none;")
        
        lbl_r_desc = QLabel("카드 잔액을 차감하고\n현금으로 환불합니다")
        lbl_r_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_desc.setStyleSheet(f"font-size: {styles.fs(11)}; color: #92400E; background: transparent; border: none;")
        
        r_layout.addWidget(lbl_r_icon)
        r_layout.addWidget(lbl_r_title)
        r_layout.addWidget(lbl_r_desc)
        self.btn_goto_refund.clicked.connect(self.show_refund)
        
        btn_layout.addWidget(self.btn_goto_charge)
        btn_layout.addWidget(self.btn_goto_refund)
        lyt.addLayout(btn_layout)
        lyt.addStretch()
        
    def init_charge_screen(self):
        self.charge_widget = QWidget()
        lyt = QVBoxLayout(self.charge_widget)
        lyt.setContentsMargins(styles.s(25), styles.s(15), styles.s(25), styles.s(15))
        lyt.setSpacing(styles.s(12))
        
        # Header Row (Back button & title)
        hdr_row = QHBoxLayout()
        btn_back = QPushButton("◀ 메뉴로")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #4B5563;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(4)}px;
                font-weight: bold;
                padding: {styles.s(4)}px {styles.s(10)}px;
                font-size: {styles.fs(10)};
            }}
            QPushButton:hover {{ background-color: #F3F4F6; }}
        """)
        btn_back.clicked.connect(self.show_menu)
        hdr_row.addWidget(btn_back)
        hdr_row.addStretch()
        
        lbl_c_title = QLabel("충전 금액 등록")
        lbl_c_title.setStyleSheet(f"font-size: {styles.fs(12)}; font-weight: bold; color: #4C1D95; font-family: '{styles.FONT_FAMILY}';")
        hdr_row.addWidget(lbl_c_title)
        lyt.addLayout(hdr_row)
        
        # Input Field for Amount
        INPUT_QSS = f"""
            QLineEdit {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                padding: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(15)};
                color: {styles.TEXT_COLOR};
                font-weight: bold;
            }}
            QLineEdit:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
            }}
        """
        
        self.txt_charge_amt = QLineEdit()
        self.txt_charge_amt.setPlaceholderText("충전할 금액 입력 (원)")
        self.txt_charge_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_charge_amt.setStyleSheet(INPUT_QSS)
        lyt.addWidget(self.txt_charge_amt)
        
        # Preset buttons for charge
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(styles.s(6))
        presets = [("천원", 1000), ("오천원", 5000), ("만원", 10000), ("오만원", 50000)]
        for text, val in presets:
            btn = QPushButton(text)
            btn.setFixedHeight(styles.s(38))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 1px solid #D1D5DB;
                    border-radius: {styles.s(6)}px;
                    font-size: {styles.fs(11)};
                    font-weight: bold;
                    color: #4B5563;
                }}
                QPushButton:hover {{ background-color: #F3F4F6; }}
            """)
            btn.clicked.connect(lambda checked, v=val: self.add_charge_amt(v))
            preset_layout.addWidget(btn)
        lyt.addLayout(preset_layout)
        
        # Tag Card Visual Guide
        tag_card = QFrame()
        tag_card.setStyleSheet(f"""
            QFrame {{
                background-color: #F5F3FF;
                border: 1px dashed #A78BFA;
                border-radius: {styles.s(8)}px;
            }}
        """)
        tag_lyt = QVBoxLayout(tag_card)
        tag_lyt.setContentsMargins(styles.s(15), styles.s(12), styles.s(15), styles.s(12))
        tag_lyt.setSpacing(styles.s(4))
        
        lbl_tag_main = QLabel("💳 카드를 단말기에 접촉하세요")
        lbl_tag_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tag_main.setStyleSheet(f"font-size: {styles.fs(13)}; font-weight: bold; color: #6D28D9; border: none; background: transparent;")
        
        self.lbl_tag_status = QLabel("접촉 상태 대기 중...")
        self.lbl_tag_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tag_status.setStyleSheet(f"font-size: {styles.fs(10)}; color: #8B5CF6; border: none; background: transparent;")
        
        tag_lyt.addWidget(lbl_tag_main)
        tag_lyt.addWidget(self.lbl_tag_status)
        lyt.addWidget(tag_card)
        
        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(styles.s(10))
        
        btn_confirm = QPushButton("충전 완료")
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.setFixedHeight(styles.s(42))
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(6)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        btn_confirm.clicked.connect(self.process_charge)
        
        btn_cancel = QPushButton("취소")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedHeight(styles.s(42))
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #4B5563;
                font-weight: bold;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                font-size: {styles.fs(12)};
            }}
            QPushButton:hover {{ background-color: #F3F4F6; }}
        """)
        btn_cancel.clicked.connect(self.show_menu)
        
        btn_row.addWidget(btn_confirm, stretch=2)
        btn_row.addWidget(btn_cancel, stretch=1)
        lyt.addLayout(btn_row)
        
    def init_refund_screen(self):
        self.refund_widget = QWidget()
        lyt = QVBoxLayout(self.refund_widget)
        lyt.setContentsMargins(styles.s(25), styles.s(15), styles.s(25), styles.s(15))
        lyt.setSpacing(styles.s(12))
        
        # Header Row
        hdr_row = QHBoxLayout()
        btn_back = QPushButton("◀ 메뉴로")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #4B5563;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(4)}px;
                font-weight: bold;
                padding: {styles.s(4)}px {styles.s(10)}px;
                font-size: {styles.fs(10)};
            }}
            QPushButton:hover {{ background-color: #F3F4F6; }}
        """)
        btn_back.clicked.connect(self.show_menu)
        hdr_row.addWidget(btn_back)
        hdr_row.addStretch()
        
        lbl_r_title = QLabel("잔액 환불 등록")
        lbl_r_title.setStyleSheet(f"font-size: {styles.fs(12)}; font-weight: bold; color: #92400E; font-family: '{styles.FONT_FAMILY}';")
        hdr_row.addWidget(lbl_r_title)
        lyt.addLayout(hdr_row)
        
        # Refund Detail Grid
        INPUT_QSS = f"""
            QLineEdit {{
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                padding: {styles.s(8)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                color: {styles.TEXT_COLOR};
                font-weight: bold;
            }}
            QLineEdit:focus {{
                border: 2px solid {styles.PRIMARY_PURPLE};
                background-color: white;
            }}
        """
        
        form_layout = QGridLayout()
        form_layout.setSpacing(styles.s(10))
        form_layout.setColumnStretch(1, 1)
        
        LBL_QSS = f"font-size: {styles.fs(11)}; color: #374151; font-weight: bold; font-family: '{styles.FONT_FAMILY}';"
        
        # 환불가능금액
        lbl_avail = QLabel("환불 가능 잔액")
        lbl_avail.setStyleSheet(LBL_QSS)
        self.txt_avail_amt = QLineEdit("18,500")
        self.txt_avail_amt.setReadOnly(True)
        self.txt_avail_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_avail_amt.setStyleSheet(INPUT_QSS + "QLineEdit { background-color: #E5E7EB; color: #4B5563; }")
        
        form_layout.addWidget(lbl_avail, 0, 0)
        form_layout.addWidget(self.txt_avail_amt, 0, 1)
        
        # 환불수수료
        lbl_fee = QLabel("환불 수수료")
        lbl_fee.setStyleSheet(LBL_QSS)
        self.txt_fee = QLineEdit("500")
        self.txt_fee.setReadOnly(True)
        self.txt_fee.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_fee.setStyleSheet(INPUT_QSS + "QLineEdit { background-color: #E5E7EB; color: #4B5563; }")
        
        form_layout.addWidget(lbl_fee, 1, 0)
        form_layout.addWidget(self.txt_fee, 1, 1)
        
        # 실지급액
        lbl_net = QLabel("실 지급액")
        lbl_net.setStyleSheet(LBL_QSS)
        self.txt_net_amt = QLineEdit("18,000")
        self.txt_net_amt.setReadOnly(True)
        self.txt_net_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_net_amt.setStyleSheet(INPUT_QSS + "QLineEdit { background-color: #FEF3C7; color: #B45309; }")
        
        form_layout.addWidget(lbl_net, 2, 0)
        form_layout.addWidget(self.txt_net_amt, 2, 1)
        
        lyt.addLayout(form_layout)
        
        # Tag Card Visual Guide
        tag_card = QFrame()
        tag_card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFDF2;
                border: 1px dashed #FCD34D;
                border-radius: {styles.s(8)}px;
            }}
        """)
        tag_lyt = QVBoxLayout(tag_card)
        tag_lyt.setContentsMargins(styles.s(15), styles.s(12), styles.s(15), styles.s(12))
        tag_lyt.setSpacing(styles.s(4))
        
        lbl_tag_main = QLabel("💳 카드를 단말기에 접촉하세요")
        lbl_tag_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tag_main.setStyleSheet(f"font-size: {styles.fs(13)}; font-weight: bold; color: #B45309; border: none; background: transparent;")
        
        self.lbl_tag_status_r = QLabel("카드 확인 대기 중...")
        self.lbl_tag_status_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tag_status_r.setStyleSheet(f"font-size: {styles.fs(10)}; color: #D97706; border: none; background: transparent;")
        
        tag_lyt.addWidget(lbl_tag_main)
        tag_lyt.addWidget(self.lbl_tag_status_r)
        lyt.addWidget(tag_card)
        
        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(styles.s(10))
        
        btn_confirm = QPushButton("환불 완료")
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.setFixedHeight(styles.s(42))
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(6)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        btn_confirm.clicked.connect(self.process_refund)
        
        btn_cancel = QPushButton("취소")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedHeight(styles.s(42))
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #4B5563;
                font-weight: bold;
                border: 1px solid #D1D5DB;
                border-radius: {styles.s(6)}px;
                font-size: {styles.fs(12)};
            }}
            QPushButton:hover {{ background-color: #F3F4F6; }}
        """)
        btn_cancel.clicked.connect(self.show_menu)
        
        btn_row.addWidget(btn_confirm, stretch=2)
        btn_row.addWidget(btn_cancel, stretch=1)
        lyt.addLayout(btn_row)
        
    def show_menu(self):
        self.lbl_title.setText("교통카드 서비스")
        self.stack.setCurrentIndex(0)
        
    def show_charge(self):
        self.lbl_title.setText("교통카드 - 충전")
        self.txt_charge_amt.clear()
        self.lbl_tag_status.setText("접촉 상태 대기 중...")
        self.stack.setCurrentIndex(1)
        self.txt_charge_amt.setFocus()
        
    def show_refund(self):
        self.lbl_title.setText("교통카드 - 환불")
        self.lbl_tag_status_r.setText("카드 확인 대기 중...")
        self.stack.setCurrentIndex(2)
        
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
        self.accept()
        
    def process_refund(self):
        self.lbl_tag_status_r.setText("⏳ 환불 승인 요청 중...")
        QTimer.singleShot(1500, self.complete_refund)
        
    def complete_refund(self):
        self.lbl_tag_status_r.setText("✅ 환불 완료!")
        CustomMessageDialog("성공", "교통카드 잔액 18,500원(수수료 500원 차감)이 환불되었습니다.\n현금 18,000원을 지급해 주세요.", 'info', self).exec()
        self.accept()


class CashReceiptDialog(QDialog):
    def __init__(self, target_amount, received_amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(680), styles.s(520))
        
        self.target_amount = target_amount
        self.received_amount = received_amount
        self.change_amount = max(0, received_amount - target_amount)
        self.receipt_issued = False
        self.receipt_id = ""
        
        import os
        audio_path = os.path.abspath(os.path.join("assets", "audio", "현금.mp3"))
        if os.path.exists(audio_path):
            from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
            from PyQt6.QtCore import QUrl
            self.player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.player.setAudioOutput(self.audio_output)
            self.player.setSource(QUrl.fromLocalFile(audio_path))
            self.player.play()
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(styles.s(10), styles.s(10), styles.s(660), styles.s(500))
        self.container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #30353A;
                border-radius: 0px;
            }
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
        
        # 2. Content
        self.create_content()
        
        # 3. Footer
        self.create_footer()
        
        # Set focus to phone number input
        self.txt_identifier.setFocus()

    def create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            background-color: #30353A;
            border-radius: 0px;
            border: none;
        """)
        header.setFixedHeight(styles.s(50))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        title = QLabel("현금영수증")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 14pt; font-family: 'Malgun Gothic';")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(styles.s(30), styles.s(30))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                font-weight: bold;
                border: none;
                font-size: 13pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(title)
        hbox.addStretch()
        hbox.addWidget(btn_close)
        self.layout.addWidget(header)

        # Tab sub-header row
        tab_bar = QFrame()
        tab_bar.setFixedHeight(styles.s(45))
        tab_bar.setStyleSheet("""
            background-color: #F4F6F8;
            border-bottom: 1px solid #D1D5DB;
            border-radius: 0px;
        """)
        tab_lyt = QHBoxLayout(tab_bar)
        tab_lyt.setContentsMargins(styles.s(20), styles.s(5), styles.s(20), styles.s(5))
        tab_lyt.setSpacing(styles.s(8))
        
        btn_pay_tab = QPushButton("결제")
        btn_pay_tab.setFixedSize(styles.s(80), styles.s(30))
        btn_pay_tab.setStyleSheet("""
            QPushButton {
                background-color: #30353A;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #30353A;
                border-radius: 2px;
            }
        """)
        
        btn_help_tab = QPushButton("도움말")
        btn_help_tab.setFixedSize(styles.s(80), styles.s(30))
        btn_help_tab.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #374151;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #D1D5DB;
                border-radius: 2px;
            }
        """)
        
        tab_lyt.addWidget(btn_pay_tab)
        tab_lyt.addWidget(btn_help_tab)
        tab_lyt.addStretch()
        
        btn_globe = QPushButton("🌐")
        btn_globe.setFixedSize(styles.s(32), styles.s(32))
        btn_globe.setStyleSheet("QPushButton { background: transparent; font-size: 14pt; border: none; }")
        
        tab_lyt.addWidget(btn_globe)
        self.layout.addWidget(tab_bar)

    def create_content(self):
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white; border: none;")
        vbox = QVBoxLayout(content_widget)
        vbox.setContentsMargins(styles.s(25), styles.s(20), styles.s(25), styles.s(15))
        vbox.setSpacing(styles.s(15))
        
        lbl_msg = QLabel(f'<span style="color:#D32F2F; font-size:16pt; font-weight:bold;">{self.received_amount:,}</span>'
                         f'<span style="color:#333333; font-size:15pt; font-weight:bold;"> 원 받았습니다. 현금영수증 필요하세요?</span>')
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_msg.setStyleSheet("background: transparent;")
        vbox.addWidget(lbl_msg)
        vbox.addSpacing(styles.s(5))
        
        tab_widget = QFrame()
        tab_widget.setStyleSheet("background: transparent; border: none;")
        tab_lyt = QHBoxLayout(tab_widget)
        tab_lyt.setContentsMargins(0, 0, 0, 0)
        tab_lyt.setSpacing(0)
        
        self.btn_type_personal = QPushButton("개인")
        self.btn_type_personal.setFixedSize(styles.s(70), styles.s(30))
        self.btn_type_personal.setCheckable(True)
        self.btn_type_personal.setChecked(True)
        
        self.btn_type_corp = QPushButton("법인")
        self.btn_type_corp.setFixedSize(styles.s(70), styles.s(30))
        self.btn_type_corp.setCheckable(True)
        
        self.type_grp = QButtonGroup(self)
        self.type_grp.addButton(self.btn_type_personal, 1)
        self.type_grp.addButton(self.btn_type_corp, 2)
        self.type_grp.buttonClicked.connect(self.on_type_changed)
        
        self.update_type_button_styles()
        
        tab_lyt.addWidget(self.btn_type_personal)
        tab_lyt.addWidget(self.btn_type_corp)
        tab_lyt.addStretch()
        
        vbox.addWidget(tab_widget)
        
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setColumnStretch(1, 1)
        
        lbl_style = """
            background-color: #ECEFF1;
            color: #374151;
            font-weight: bold;
            font-size: 10pt;
            font-family: 'Malgun Gothic';
            border: 1px solid #B4C4D4;
            padding: 8px;
        """
        
        val_lbl_style = """
            background-color: white;
            color: black;
            font-size: 10pt;
            font-family: 'Malgun Gothic';
            border: 1px solid #B4C4D4;
            padding: 8px;
        """
        
        lbl_class = QLabel("발급구분")
        lbl_class.setStyleSheet(lbl_style)
        lbl_class.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_class_val = QLabel("개인소득공제용")
        self.lbl_class_val.setStyleSheet(val_lbl_style)
        self.lbl_class_val.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        grid.addWidget(lbl_class, 0, 0)
        grid.addWidget(self.lbl_class_val, 0, 1)
        
        lbl_ident = QLabel("신분확인번호")
        lbl_ident.setStyleSheet(lbl_style)
        lbl_ident.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ident_cell = QFrame()
        ident_cell.setStyleSheet("background-color: white; border: 1px solid #B4C4D4; border-radius: 0px;")
        cell_lyt = QHBoxLayout(ident_cell)
        cell_lyt.setContentsMargins(styles.s(5), styles.s(3), styles.s(5), styles.s(3))
        cell_lyt.setSpacing(styles.s(8))
        
        self.txt_identifier = QLineEdit()
        self.txt_identifier.setText("010-")
        self.txt_identifier.setPlaceholderText("휴대폰번호 또는 카드번호 입력")
        self.txt_identifier.setStyleSheet("border: 1px solid #B4C4D4; padding: 4px; font-size: 11pt; font-family: 'Malgun Gothic'; background-color: #FFFDE7; color: black;")
        self.txt_identifier.textChanged.connect(self.on_identifier_text_changed)
        
        btn_dongle = QPushButton("고객직접입력 (동글입력)")
        btn_dongle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_dongle.setFixedHeight(styles.s(30))
        btn_dongle.setStyleSheet("""
            QPushButton {
                background-color: #4B5563;
                color: white;
                font-weight: bold;
                font-size: 9pt;
                font-family: 'Malgun Gothic';
                border: none;
                padding-left: 10px;
                padding-right: 10px;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        btn_dongle.clicked.connect(self.mock_dongle_input)
        
        cell_lyt.addWidget(self.txt_identifier, stretch=1)
        cell_lyt.addWidget(btn_dongle)
        
        grid.addWidget(lbl_ident, 1, 0)
        grid.addWidget(ident_cell, 1, 1)
        
        vbox.addLayout(grid)
        vbox.addSpacing(styles.s(10))
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self.btn_no = QPushButton("아니오 (자동발급)")
        self.btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_no.setFixedSize(styles.s(140), styles.s(38))
        self.btn_no.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #374151;
                border-radius: 2px;
            }
            QPushButton:hover { background-color: #1F2937; }
        """)
        self.btn_no.clicked.connect(self.process_no_receipt)
        
        self.btn_yes = QPushButton("예 (발급하기)")
        self.btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_yes.setFixedSize(styles.s(120), styles.s(38))
        self.btn_yes.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #374151;
                border-radius: 2px;
            }
            QPushButton:hover { background-color: #1F2937; }
        """)
        self.btn_yes.clicked.connect(self.process_yes_receipt)
        
        btn_row.addWidget(self.btn_no)
        btn_row.addWidget(self.btn_yes)
        vbox.addLayout(btn_row)
        
        vbox.addStretch()
        self.layout.addWidget(content_widget)

    def create_footer(self):
        footer = QFrame()
        footer.setStyleSheet("""
            background-color: white;
            border-top: 1px solid #B4C4D4;
            border-radius: 0px;
        """)
        footer.setFixedHeight(styles.s(110))
        
        hbox = QHBoxLayout(footer)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        
        left_box = QFrame()
        left_box.setStyleSheet("border: none; border-right: 1px solid #B4C4D4;")
        left_lyt = QVBoxLayout(left_box)
        left_lyt.setContentsMargins(styles.s(20), styles.s(15), styles.s(20), styles.s(15))
        
        left_row = QHBoxLayout()
        lbl_cash = QLabel("현금")
        lbl_cash.setStyleSheet("font-size: 11pt; font-family: 'Malgun Gothic'; font-weight: bold; color: black;")
        
        lbl_cash_val = QLabel(f"{self.received_amount:,}원")
        lbl_cash_val.setStyleSheet("font-size: 11pt; font-family: 'Malgun Gothic'; font-weight: bold; color: black;")
        lbl_cash_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        left_row.addWidget(lbl_cash)
        left_row.addWidget(lbl_cash_val)
        left_lyt.addLayout(left_row)
        left_lyt.addStretch()
        
        right_box = QFrame()
        right_box.setStyleSheet("border: none;")
        right_lyt = QVBoxLayout(right_box)
        right_lyt.setContentsMargins(styles.s(20), styles.s(8), styles.s(20), styles.s(8))
        right_lyt.setSpacing(styles.s(3))
        
        r1 = QHBoxLayout()
        l_tot = QLabel("총 금액")
        l_tot.setStyleSheet("font-size: 10pt; font-family: 'Malgun Gothic'; color: #555555;")
        v_tot = QLabel(f"{self.target_amount:,} 원")
        v_tot.setStyleSheet("font-size: 11pt; font-family: 'Malgun Gothic'; font-weight: bold; color: black;")
        v_tot.setAlignment(Qt.AlignmentFlag.AlignRight)
        r1.addWidget(l_tot)
        r1.addWidget(v_tot)
        
        r2 = QHBoxLayout()
        l_paid = QLabel("결제한 금액")
        l_paid.setStyleSheet("font-size: 10pt; font-family: 'Malgun Gothic'; color: #555555;")
        v_paid = QLabel(f"{self.received_amount:,} 원")
        v_paid.setStyleSheet("font-size: 11pt; font-family: 'Malgun Gothic'; font-weight: bold; color: black;")
        v_paid.setAlignment(Qt.AlignmentFlag.AlignRight)
        r2.addWidget(l_paid)
        r2.addWidget(v_paid)
        
        r3 = QHBoxLayout()
        l_chg = QLabel("거스름돈")
        l_chg.setStyleSheet("font-size: 11pt; font-family: 'Malgun Gothic'; font-weight: bold; color: black;")
        v_chg = QLabel(f"{self.change_amount:,} 원")
        v_chg.setStyleSheet("font-size: 14pt; font-family: 'Malgun Gothic'; font-weight: bold; color: #D32F2F;")
        v_chg.setAlignment(Qt.AlignmentFlag.AlignRight)
        r3.addWidget(l_chg)
        r3.addWidget(v_chg)
        
        right_lyt.addLayout(r1)
        right_lyt.addLayout(r2)
        right_lyt.addLayout(r3)
        
        hbox.addWidget(left_box, stretch=1)
        hbox.addWidget(right_box, stretch=1)
        self.layout.addWidget(footer)

    def on_type_changed(self, button):
        if button == self.btn_type_personal:
            self.lbl_class_val.setText("개인소득공제용")
        else:
            self.lbl_class_val.setText("지출증빙용")
        self.update_type_button_styles()

    def update_type_button_styles(self):
        active_style = """
            QPushButton {
                background-color: #8E24AA;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #8E24AA;
                border-radius: 0px;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: #D1D1D1;
                color: #475569;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'Malgun Gothic';
                border: 1px solid #CCCCCC;
                border-radius: 0px;
            }
        """
        self.btn_type_personal.setStyleSheet(active_style if self.btn_type_personal.isChecked() else inactive_style)
        self.btn_type_corp.setStyleSheet(active_style if self.btn_type_corp.isChecked() else inactive_style)

    def mock_dongle_input(self):
        self.txt_identifier.setText("010-1111-1234")

    def on_identifier_text_changed(self, text):
        self.txt_identifier.blockSignals(True)
        # Ensure the text always starts with '010-'
        if not text.startswith("010-"):
            digits = "".join(c for c in text if c.isdigit())
            if not digits.startswith("010"):
                digits = "010" + digits
            text = "010-" + digits[3:]
            
        remainder = "".join(c for c in text[4:] if c.isdigit())
        remainder = remainder[:8]
        
        formatted = "010-"
        if len(remainder) > 4:
            formatted += remainder[:4] + "-" + remainder[4:]
        else:
            formatted += remainder
            
        self.txt_identifier.setText(formatted)
        self.txt_identifier.blockSignals(False)

    def process_no_receipt(self):
        self.receipt_issued = False
        self.accept()

    def process_yes_receipt(self):
        import random
        identifier = self.txt_identifier.text().replace("-", "").strip()
        if not identifier.isdigit() or not (10 <= len(identifier) <= 16):
            CustomMessageDialog("오류", "올바른 휴대폰번호 또는 카드번호를 입력해주세요.", 'warning', self).exec()
            self.txt_identifier.setFocus()
            return
        
        self.receipt_issued = True
        self.receipt_id = f"CU-{random.randint(100000, 999999)}"
        self.accept()


class AffiliateDiscountDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(750), styles.s(610))
        
        self.total_amount = total_amount
        self.discount_amount = 0
        self.points_used = 0
        self.card_issuer = "T멤버십"
        self.card_number = ""
        
        # Main dialog layout (adds 10px margin around container for shadow)
        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.setContentsMargins(10, 10, 10, 10)
        
        # Main Container
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(8)}px;
                border: 1px solid #757575;
            }}
        """)
        main_dialog_layout.addWidget(self.container)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Header / Title Bar
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #4E5154; 
            border-top-left-radius: {styles.s(7)}px;
            border-top-right-radius: {styles.s(7)}px;
            border: none;
            border-bottom: 1px solid #757575;
        """)
        header.setFixedHeight(styles.s(50))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        title = QLabel("제휴할인 및 포인트 적립/사용")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 14pt; font-family: 'Malgun Gothic';")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(styles.s(30), styles.s(30))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                font-weight: bold;
                border: none;
                font-size: 13pt;
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
        layout.addWidget(header)
        
        # Content Widget
        content = QWidget()
        content.setStyleSheet("background-color: white; border: none;")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(styles.s(20), styles.s(15), styles.s(20), styles.s(15))
        vbox.setSpacing(styles.s(15))
        
        # Tabs Layout
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(0)
        
        self.btn_reg_tab = QPushButton("등록")
        self.btn_reg_tab.setFixedSize(styles.s(120), styles.s(35))
        self.btn_reg_tab.setStyleSheet("background-color: #3F51B5; color: white; font-weight: bold; border: 1px solid #3F51B5; border-bottom: none; font-size: 11pt; font-family: 'Malgun Gothic';")
        
        self.btn_help_tab = QPushButton("도움말")
        self.btn_help_tab.setFixedSize(styles.s(120), styles.s(35))
        self.btn_help_tab.setStyleSheet("background-color: #F5F5F5; color: #333; border: 1px solid #D3D3D3; border-bottom: 1px solid #3F51B5; font-size: 11pt; font-family: 'Malgun Gothic';")
        self.btn_help_tab.clicked.connect(self.show_help)
        
        tab_layout.addWidget(self.btn_reg_tab)
        tab_layout.addWidget(self.btn_help_tab)
        tab_layout.addStretch()
        vbox.addLayout(tab_layout)
        
        # Card Info Header
        info_header_layout = QHBoxLayout()
        lbl_card_info_title = QLabel("카드정보")
        lbl_card_info_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #37474F; font-family: 'Malgun Gothic';")
        
        lbl_card_info_sub = QLabel("* SKT 카드번호 수기입력시 카드번호 16자리 입력")
        lbl_card_info_sub.setStyleSheet("font-size: 9pt; color: #78909C; font-family: 'Malgun Gothic';")
        
        info_header_layout.addWidget(lbl_card_info_title)
        info_header_layout.addStretch()
        info_header_layout.addWidget(lbl_card_info_sub)
        vbox.addLayout(info_header_layout)
        
        # Card Info Table Grid
        card_table = QFrame()
        card_table.setStyleSheet("QFrame { border: 1px solid #CFD8DC; background-color: #ECEFF1; }")
        grid_card = QGridLayout(card_table)
        grid_card.setContentsMargins(0, 0, 0, 0)
        grid_card.setSpacing(1)
        
        lbl_issuer_label = QLabel("  카드사명")
        lbl_issuer_label.setFixedWidth(styles.s(150))
        lbl_issuer_label.setFixedHeight(styles.s(40))
        lbl_issuer_label.setStyleSheet("background-color: #ECEFF1; font-weight: bold; color: #37474F; font-size: 11pt; font-family: 'Malgun Gothic'; border: none;")
        
        from PyQt6.QtWidgets import QComboBox
        self.combo_issuer = QComboBox()
        self.combo_issuer.addItems(["T멤버십", "CU포인트", "OK캐시백"])
        self.combo_issuer.setFixedHeight(styles.s(38))
        self.combo_issuer.setStyleSheet("QComboBox { background-color: white; border: none; font-size: 11pt; padding-left: 10px; font-family: 'Malgun Gothic'; }")
        self.combo_issuer.currentTextChanged.connect(self.on_issuer_changed)
        
        grid_card.addWidget(lbl_issuer_label, 0, 0)
        grid_card.addWidget(self.combo_issuer, 0, 1)
        
        lbl_num_label = QLabel("  카드번호")
        lbl_num_label.setFixedWidth(styles.s(150))
        lbl_num_label.setFixedHeight(styles.s(40))
        lbl_num_label.setStyleSheet("background-color: #ECEFF1; font-weight: bold; color: #37474F; font-size: 11pt; font-family: 'Malgun Gothic'; border: none;")
        
        self.txt_card_number = QLineEdit()
        self.txt_card_number.setFixedHeight(styles.s(38))
        self.txt_card_number.setStyleSheet("QLineEdit { background-color: white; border: none; font-size: 12pt; padding-left: 10px; font-family: 'Malgun Gothic'; color: #212121; }")
        
        grid_card.addWidget(lbl_num_label, 1, 0)
        grid_card.addWidget(self.txt_card_number, 1, 1)
        
        vbox.addWidget(card_table)
        
        # Discount Info Header
        lbl_disc_title = QLabel("할인정보")
        lbl_disc_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #37474F; font-family: 'Malgun Gothic';")
        vbox.addWidget(lbl_disc_title)
        
        # Discount Info Table Grid
        disc_table = QFrame()
        disc_table.setStyleSheet("QFrame { border: 1px solid #CFD8DC; background-color: #ECEFF1; }")
        grid_disc = QGridLayout(disc_table)
        grid_disc.setContentsMargins(0, 0, 0, 0)
        grid_disc.setSpacing(1)
        
        lbl_target_label = QLabel("  할인대상금액")
        lbl_target_label.setFixedWidth(styles.s(150))
        lbl_target_label.setFixedHeight(styles.s(40))
        lbl_target_label.setStyleSheet("background-color: #ECEFF1; font-weight: bold; color: #37474F; font-size: 11pt; font-family: 'Malgun Gothic'; border: none;")
        
        lbl_target_val = QLabel(f"{total_amount:,}   ")
        lbl_target_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_target_val.setFixedHeight(styles.s(40))
        lbl_target_val.setStyleSheet("background-color: white; font-weight: bold; color: #212121; font-size: 12pt; font-family: 'Malgun Gothic'; border: none;")
        
        grid_disc.addWidget(lbl_target_label, 0, 0)
        grid_disc.addWidget(lbl_target_val, 0, 1)
        
        vbox.addWidget(disc_table)
        
        # Notice Label (Red)
        lbl_notice = QLabel(
            "2016년 6월 1일부터 SKT 멤버십 할인율이 변경됩니다.\n"
            "(VIP/골드 고객 1,000원 당 100원 할인), (실버고객 1,000원 당 50원 할인)"
        )
        lbl_notice.setStyleSheet("color: #EF5350; font-size: 9.5pt; font-weight: bold; font-family: 'Malgun Gothic';")
        vbox.addWidget(lbl_notice)
        
        vbox.addStretch()
        
        # Footer Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #E0E0E0; max-height: 1px; border: none;")
        vbox.addWidget(line)
        
        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(styles.s(10))
        
        # 1. OK캐시백 사용
        btn_ok_cash = QPushButton("OK캐시백 사용")
        btn_ok_cash.setFixedHeight(styles.s(45))
        btn_ok_cash.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok_cash.setStyleSheet(f"""
            QPushButton {{
                background-color: #78909C;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(12)};
                border: none;
                padding-left: 10px; padding-right: 10px;
            }}
            QPushButton:hover {{ background-color: #607D8B; }}
        """)
        btn_ok_cash.clicked.connect(self.process_ok_cashback)
        
        # 2. 휴대전화번호로 CU포인트조회
        btn_cu_phone = QPushButton("휴대전화번호로\nCU포인트 조회(등급)")
        btn_cu_phone.setFixedHeight(styles.s(45))
        btn_cu_phone.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cu_phone.setStyleSheet(f"""
            QPushButton {{
                background-color: #546E7A;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(11)};
                border: none;
                padding-left: 10px; padding-right: 10px;
            }}
            QPushButton:hover {{ background-color: #455A64; }}
        """)
        btn_cu_phone.clicked.connect(self.process_cu_phone_lookup)
        
        # 3. 닫기 [CLEAR]
        btn_clear = QPushButton("닫기 [CLEAR]")
        btn_clear.setFixedHeight(styles.s(45))
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: #455A64;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #37474F; }}
        """)
        btn_clear.clicked.connect(self.reject)
        
        # 4. 확인
        self.btn_confirm = QPushButton("확인")
        self.btn_confirm.setFixedHeight(styles.s(45))
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: #37474F;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #212121; }}
        """)
        self.btn_confirm.clicked.connect(self.process_confirm)
        
        bottom_layout.addWidget(btn_ok_cash, stretch=2)
        bottom_layout.addWidget(btn_cu_phone, stretch=2)
        bottom_layout.addWidget(btn_clear, stretch=2)
        bottom_layout.addWidget(self.btn_confirm, stretch=2)
        vbox.addLayout(bottom_layout)
        
        layout.addWidget(content)
        
    def on_issuer_changed(self, issuer):
        self.card_issuer = issuer
        
    def show_help(self):
        CustomMessageDialog(
            "제휴할인/적립 도움말",
            "1. T멤버십: 카드를 리딩하거나 카드번호 16자리를 입력하여 확인을 누르면 회원 등급(VIP/골드/실버)에 따라 할인이 적용됩니다.\n\n"
            "2. CU포인트: 포인트 카드를 스캔하거나 휴대전화번호 조회 버튼을 눌러 회원을 조회 및 적립/사용할 수 있습니다.\n\n"
            "3. OK캐시백: OK캐시백 사용 버튼을 통해 포인트를 조회하고 결제에 사용할 수 있습니다.",
            "info",
            self
        ).exec()
        
    def process_ok_cashback(self):
        self.combo_issuer.setCurrentText("OK캐시백")
        self.txt_card_number.setText("7690-****-****-****")
        CustomMessageDialog(
            "OK캐시백 조회 완료",
            "OK캐시백 카드가 조회되었습니다.\n\n· 가용 포인트: 5,000 P\n\n확인을 누르면 결제에 사용됩니다.",
            "info",
            self
        ).exec()
        
    def process_cu_phone_lookup(self):
        dialog = CuPointPhoneLookupDialog(self)
        if not dialog.exec():
            return
            
        phone = dialog.phone_number
        clean_phone = phone.replace("-", "").strip()
        
        # Exact points from user screenshot: 5443
        points = 5443
        
        self.combo_issuer.setCurrentText("CU포인트")
        self.txt_card_number.setText(phone.strip())
        
        # Show points usage confirm dialog
        confirm_dialog = CuPointUseConfirmDialog(points, self)
        confirm_dialog.exec()
        
        if confirm_dialog.use_points:
            use_amt = min(points, self.total_amount)
            self.points_used = use_amt
            self.discount_amount = use_amt
            
            CustomMessageDialog(
                "CU포인트 사용 완료",
                f"CU포인트 사용이 적용되었습니다.\n\n· 사용 포인트: {use_amt:,}원\n· 남은 결제금액: {(self.total_amount - use_amt):,}원",
                "info",
                self
            ).exec()
        else:
            self.points_used = 0
            self.discount_amount = 0
            accum_points = int(self.total_amount * 0.01)
            
            CustomMessageDialog(
                "CU포인트 적립 적용",
                f"결제 완료 시 CU포인트가 적립됩니다.\n\n· 적립 예정 포인트: {accum_points:,} P (1% 적립)",
                "info",
                self
            ).exec()
        
    def process_confirm(self):
        card_num = self.txt_card_number.text().strip()
        issuer = self.combo_issuer.currentText()
        
        if not card_num:
            CustomMessageDialog("오류", "카드번호 또는 휴대폰번호를 입력해주세요.", 'warning', self).exec()
            self.txt_card_number.setFocus()
            return
            
        self.card_issuer = issuer
        self.card_number = card_num
        
        if issuer == "T멤버십":
            # Prompt user to choose tier for SKT membership discount
            from PyQt6.QtWidgets import QInputDialog
            items = ["VIP / 골드 (1,000원당 100원 할인)", "실버 (1,000원당 50원 할인)"]
            item, ok = QInputDialog.getItem(
                self, 
                "T멤버십 등급 선택", 
                "회원 등급을 선택하세요:", 
                items, 
                0, 
                False
            )
            if not ok:
                return
                
            if "VIP" in item:
                self.discount_amount = (self.total_amount // 1000) * 100
                tier_name = "VIP / 골드"
            else:
                self.discount_amount = (self.total_amount // 1000) * 50
                tier_name = "실버"
                
            # Limit discount to total_amount
            self.discount_amount = min(self.discount_amount, self.total_amount)
            
            CustomMessageDialog(
                "T멤버십 적용 완료",
                f"T멤버십 할인이 적용되었습니다.\n\n· 등급: {tier_name}\n· 할인 금액: {self.discount_amount:,}원",
                "info",
                self
            ).exec()
            
        elif issuer == "OK캐시백":
            # Use 5,000 points or total_amount, whichever is less
            use_points = min(5000, self.total_amount)
            self.points_used = use_points
            self.discount_amount = use_points # Deduct it as discount
            CustomMessageDialog(
                "OK캐시백 적용 완료",
                f"OK캐시백 포인트 사용이 적용되었습니다.\n\n· 사용 포인트: {use_points:,} P",
                "info",
                self
            ).exec()
            
        elif issuer == "CU포인트":
            if self.points_used > 0:
                pass
            else:
                # Simple point accumulation alert
                accum_points = int(self.total_amount * 0.01)
                CustomMessageDialog(
                    "CU포인트 적립 적용",
                    f"결제 완료 시 CU포인트가 적립됩니다.\n\n· 적립 예정 포인트: {accum_points:,} P (1% 적립)",
                    "info",
                    self
                ).exec()
            
        self.accept()


class CuPointPhoneLookupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(540), styles.s(320))
        
        self.phone_number = ""
        
        # Main dialog layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Container
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(8)}px;
                border: 1px solid #757575;
            }}
        """)
        main_layout.addWidget(self.container)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Title Bar
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #4E5154; 
            border-top-left-radius: {styles.s(7)}px;
            border-top-right-radius: {styles.s(7)}px;
            border: none;
            border-bottom: 1px solid #757575;
        """)
        header.setFixedHeight(styles.s(50))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        title = QLabel("휴대전화번호로 CU포인트 조회")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 13pt; font-family: 'Malgun Gothic';")
        
        btn_close = QPushButton("X")
        btn_close.setFixedSize(styles.s(30), styles.s(30))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                font-weight: bold;
                border: none;
                font-size: 13pt;
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
        layout.addWidget(header)
        
        # Content
        content = QWidget()
        content.setStyleSheet("background-color: white; border: none;")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(styles.s(20), styles.s(25), styles.s(20), styles.s(20))
        vbox.setSpacing(styles.s(20))
        
        # Row layout (icon + label + input)
        row_frame = QFrame()
        row_frame.setStyleSheet("QFrame { border: 1px solid #CFD8DC; background-color: #ECEFF1; }")
        grid = QGridLayout(row_frame)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(1)
        
        # Label container with circular icon
        lbl_container = QWidget()
        lbl_container.setStyleSheet("background-color: #ECEFF1; border: none;")
        lbl_hbox = QHBoxLayout(lbl_container)
        lbl_hbox.setContentsMargins(styles.s(15), 0, styles.s(10), 0)
        lbl_hbox.setSpacing(styles.s(8))
        
        # Blue circle right arrow icon
        icon_lbl = QLabel("▶")
        icon_lbl.setFixedSize(styles.s(22), styles.s(22))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background-color: #1A237E; color: white; border-radius: 11px; font-size: 9pt; font-weight: bold;")
        
        lbl_text = QLabel("휴대전화번호 입력")
        lbl_text.setStyleSheet("font-weight: bold; color: #37474F; font-size: 11pt; font-family: 'Malgun Gothic';")
        
        lbl_hbox.addWidget(icon_lbl)
        lbl_hbox.addWidget(lbl_text)
        
        self.txt_phone = QLineEdit()
        self.txt_phone.setText("010-")
        self.txt_phone.setFixedHeight(styles.s(45))
        self.txt_phone.setStyleSheet("QLineEdit { background-color: white; border: none; font-size: 13pt; font-weight: bold; padding-left: 15px; font-family: 'Malgun Gothic'; color: #212121; }")
        self.txt_phone.setFocus()
        self.txt_phone.setCursorPosition(4)
        
        grid.addWidget(lbl_container, 0, 0)
        grid.addWidget(self.txt_phone, 0, 1)
        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 6)
        
        vbox.addWidget(row_frame)
        vbox.addStretch()
        
        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        btn_clear = QPushButton("닫기 [CLEAR]")
        btn_clear.setFixedSize(styles.s(130), styles.s(45))
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: #455A64;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #37474F; }}
        """)
        btn_clear.clicked.connect(self.reject)
        
        btn_confirm = QPushButton("확인")
        btn_confirm.setFixedSize(styles.s(130), styles.s(45))
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: #37474F;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #212121; }}
        """)
        btn_confirm.clicked.connect(self.process_confirm)
        
        bottom_layout.addWidget(btn_clear)
        bottom_layout.addWidget(btn_confirm)
        vbox.addLayout(bottom_layout)
        
        layout.addWidget(content)
        
    def process_confirm(self):
        val = self.txt_phone.text().strip()
        if not val or val == "010-":
            CustomMessageDialog("오류", "휴대전화번호를 입력해주세요.", 'warning', self).exec()
            self.txt_phone.setFocus()
            return
        
        self.phone_number = val
        self.accept()


class CuPointUseConfirmDialog(QDialog):
    def __init__(self, points, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(520), styles.s(260))
        
        self.use_points = False
        
        # Main dialog layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Container
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(8)}px;
                border: 1px solid #757575;
            }}
        """)
        main_layout.addWidget(self.container)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title Bar
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #4E5154; 
            border-top-left-radius: {styles.s(7)}px;
            border-top-right-radius: {styles.s(7)}px;
            border: none;
            border-bottom: 1px solid #757575;
        """)
        header.setFixedHeight(styles.s(50))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        title = QLabel("질의 메시지")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 13pt; font-family: 'Malgun Gothic';")
        
        hbox.addWidget(title)
        hbox.addStretch()
        layout.addWidget(header)
        
        # Content
        content = QWidget()
        content.setStyleSheet("background-color: white; border: none;")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(styles.s(20), styles.s(25), styles.s(20), styles.s(20))
        vbox.setSpacing(styles.s(15))
        
        # Msg Label
        msg = QLabel(
            f"고객님의 사용가능 CU멤버십 포인트는 {points:,}원 입니다.\n"
            "포인트 사용하시겠습니까?"
        )
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: #212121; font-size: 12pt; font-weight: bold; font-family: 'Malgun Gothic'; line-height: 150%;")
        vbox.addWidget(msg)
        
        vbox.addStretch()
        
        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        btn_accum = QPushButton("적립[CLEAR]")
        btn_accum.setFixedSize(styles.s(140), styles.s(45))
        btn_accum.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accum.setStyleSheet(f"""
            QPushButton {{
                background-color: #455A64;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #37474F; }}
        """)
        btn_accum.clicked.connect(self.process_accum)
        
        btn_use = QPushButton("사용[반복/입력]")
        btn_use.setFixedSize(styles.s(140), styles.s(45))
        btn_use.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_use.setStyleSheet(f"""
            QPushButton {{
                background-color: #37474F;
                color: white;
                font-weight: bold;
                border-radius: {styles.s(4)}px;
                font-size: {styles.fs(12)};
                border: none;
            }}
            QPushButton:hover {{ background-color: #212121; }}
        """)
        btn_use.clicked.connect(self.process_use)
        
        bottom_layout.addWidget(btn_accum)
        bottom_layout.addWidget(btn_use)
        vbox.addLayout(bottom_layout)
        
        layout.addWidget(content)
        
    def process_accum(self):
        self.use_points = False
        self.accept()
        
    def process_use(self):
        self.use_points = True
        self.accept()


