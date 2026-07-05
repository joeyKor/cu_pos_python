import sys
import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QWidget, QLineEdit,
                             QGraphicsDropShadowEffect, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QColor, QFont
import styles
from ui_components import CustomMessageDialog
from firebase_manager import FirebaseManager


class MobilePaymentWorker(QThread):
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


class MobilePaymentDialog(QDialog):
    def __init__(self, total_amount, firebase_mgr=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(styles.s(540), styles.s(370))
        
        self.total_amount = total_amount
        self.firebase_mgr = firebase_mgr if firebase_mgr else FirebaseManager()
        self.is_processing = False
        
        # Main dialog layout (adds 10px margin around container for shadow)
        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.setContentsMargins(10, 10, 10, 10)
        
        # Main Container
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border-radius: {styles.s(8)}px;
                border: 1px solid #B0BEC5;
            }}
        """)
        main_dialog_layout.addWidget(self.container)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        # Layout inside the container
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Header
        self.create_header()
        
        # 2. Content Layout
        self.create_content()
        
        # 3. Footer
        self.create_footer()
        
        # Connect signals
        self.txt_account.returnPressed.connect(self.on_submit_payment)
        self.txt_account.textChanged.connect(self.on_account_text_changed)
        
        # Set focus
        self.txt_account.setFocus()
        
    def create_header(self):
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: #7E57C2; /* Purple header */
            border-top-left-radius: {styles.s(7)}px;
            border-top-right-radius: {styles.s(7)}px;
            border: none;
            border-bottom: 1px solid #CFD8DC;
        """)
        header.setFixedHeight(styles.s(55))
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        
        title = QLabel("모바일 결제 (DU머니 QR/바코드)")
        title.setStyleSheet(f"color: white; font-weight: bold; font-size: 14pt; font-family: '{styles.FONT_FAMILY}';")
        
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(styles.s(30), styles.s(30))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
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
        self.btn_close.clicked.connect(self.reject)
        
        hbox.addWidget(title)
        hbox.addStretch()
        hbox.addWidget(self.btn_close)
        
        self.layout.addWidget(header)
        
    def create_content(self):
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(f"background-color: {styles.WHITE}; border: none;")
        
        vbox = QVBoxLayout(self.content_widget)
        vbox.setContentsMargins(styles.s(25), styles.s(20), styles.s(25), styles.s(15))
        vbox.setSpacing(styles.s(15))
        
        # Amount Card
        amount_card = QFrame()
        amount_card.setStyleSheet(f"""
            QFrame {{
                background-color: #F8F9FA;
                border-radius: {styles.s(6)}px;
                border: 1px solid #CFD8DC;
            }}
        """)
        amt_lyt = QHBoxLayout(amount_card)
        amt_lyt.setContentsMargins(styles.s(20), styles.s(12), styles.s(20), styles.s(12))
        
        lbl_amt_title = QLabel("결제 대상 금액")
        lbl_amt_title.setStyleSheet(f"font-size: 11pt; color: #555555; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        
        self.lbl_amt_value = QLabel(f"{int(self.total_amount):,} 원")
        self.lbl_amt_value.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: #7E57C2; font-family: '{styles.FONT_FAMILY}'; border: none; background: transparent;")
        self.lbl_amt_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        amt_lyt.addWidget(lbl_amt_title)
        amt_lyt.addStretch()
        amt_lyt.addWidget(self.lbl_amt_value)
        vbox.addWidget(amount_card)
        
        # Account Input Area
        input_vbox = QVBoxLayout()
        input_vbox.setSpacing(styles.s(6))
        
        lbl_acc_title = QLabel("결제 코드 입력 / 스캔")
        lbl_acc_title.setStyleSheet(f"font-size: 10.5pt; font-weight: bold; color: #333333; font-family: '{styles.FONT_FAMILY}';")
        
        self.txt_account = QLineEdit()
        self.txt_account.setPlaceholderText("바코드를 스캔하거나 결제 코드를 입력해 주세요.")
        self.txt_account.setFixedHeight(styles.s(45))
        self.txt_account.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #B0BEC5;
                border-radius: {styles.s(4)}px;
                padding-left: {styles.s(12)}px;
                font-size: 12pt;
                font-family: '{styles.FONT_FAMILY}';
                background-color: {styles.WHITE};
                color: #212121;
            }}
            QLineEdit:focus {{
                border: 1.5px solid #7E57C2;
                background-color: #FDFBFF;
            }}
        """)
        
        input_vbox.addWidget(lbl_acc_title)
        input_vbox.addWidget(self.txt_account)
        vbox.addLayout(input_vbox)
        
        # Status Label / Connection state
        status_hbox = QHBoxLayout()
        self.lbl_status = QLabel("스캔 시 자동으로 승인이 진행됩니다.")
        self.lbl_status.setStyleSheet(f"font-size: 9pt; color: #666666; font-family: '{styles.FONT_FAMILY}';")
        
        self.lbl_db_mode = QLabel("🟢 연결 완료")
        self.lbl_db_mode.setStyleSheet(f"color: #2E8B57; font-weight: bold; font-size: 9pt; font-family: '{styles.FONT_FAMILY}';")
        self.lbl_db_mode.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        status_hbox.addWidget(self.lbl_status)
        status_hbox.addWidget(self.lbl_db_mode)
        vbox.addLayout(status_hbox)
        
        self.layout.addWidget(self.content_widget)
        
    def create_footer(self):
        self.footer_widget = QFrame()
        self.footer_widget.setStyleSheet(f"""
            background-color: {styles.GRAY_BG};
            border-bottom-left-radius: {styles.s(7)}px;
            border-bottom-right-radius: {styles.s(7)}px;
            border-top: 1px solid {styles.BORDER_COLOR};
            border-left: none; border-right: none; border-bottom: none;
        """)
        self.footer_widget.setFixedHeight(styles.s(70))
        hbox = QHBoxLayout(self.footer_widget)
        hbox.setContentsMargins(styles.s(20), 0, styles.s(20), 0)
        hbox.setSpacing(styles.s(10))
        
        btn_cancel = QPushButton("결제 취소")
        btn_cancel.setFixedHeight(styles.s(45))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.CANCEL_RED};
                color: {styles.WHITE};
                border: none;
                border-radius: {styles.s(6)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:pressed {{
                background-color: #D32F2F;
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_pay = QPushButton("결제 승인")
        self.btn_pay.setFixedHeight(styles.s(45))
        self.btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pay.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.ACCENT_GREEN};
                color: {styles.WHITE};
                border: none;
                border-radius: {styles.s(6)}px;
                font-family: '{styles.FONT_FAMILY}';
                font-size: {styles.fs(13)};
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:pressed {{
                background-color: {styles.DARK_GREEN};
            }}
        """)
        self.btn_pay.clicked.connect(self.on_submit_payment)
        
        hbox.addWidget(btn_cancel)
        hbox.addWidget(self.btn_pay)
        
        self.layout.addWidget(self.footer_widget)
        
    def on_account_text_changed(self, text):
        for kor_prefix in ["ㅔ묘", "ㅖ묘", "ㅔ됴", "ㅖ됴"]:
            if text.startswith(kor_prefix):
                text = "pay" + text[len(kor_prefix):]
                self.txt_account.blockSignals(True)
                self.txt_account.setText(text)
                self.txt_account.blockSignals(False)
                break
                
        # If it reaches 16 characters and starts with pay, auto submit
        if len(text) >= 16 and text.startswith("pay"):
            QTimer.singleShot(150, self.on_submit_payment)
            
    def on_submit_payment(self):
        if getattr(self, "is_processing", False):
            return
            
        account_num = self.txt_account.text().strip()
        for kor_prefix in ["ㅔ묘", "ㅖ묘", "ㅔ됴", "ㅖ됴"]:
            if account_num.startswith(kor_prefix):
                account_num = "pay" + account_num[len(kor_prefix):]
                self.txt_account.setText(account_num)
                break
                
        if not account_num:
            self.lbl_status.setText("⚠️ 결제 코드를 입력해 주세요.")
            self.lbl_status.setStyleSheet("color: red; font-size: 8.5pt; font-family: 'Malgun Gothic';")
            self.txt_account.setFocus()
            return
            
        is_qr = account_num.startswith("pay")
        if is_qr:
            account_num = account_num[3:]
            self.txt_account.setText(account_num)
            
        self.is_processing = True
        self.lbl_status.setText("⏳ 결제 처리 진행 중...")
        self.lbl_status.setStyleSheet("color: #483D8B; font-weight: bold; font-size: 8.5pt; font-family: 'Malgun Gothic';")
        self.btn_pay.setEnabled(False)
        self.txt_account.setEnabled(False)
        if hasattr(self, 'btn_close'):
            self.btn_close.setEnabled(False)
        
        store_name = "DU순천점"
        store_info_path = os.path.join(os.path.abspath("."), "json", "store_info.json")
        if os.path.exists(store_info_path):
            try:
                with open(store_info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                    store_name = info.get("store_name", "DU순천점")
            except Exception:
                pass
                
        self.show_progress_ui()
        
        self.payment_worker = MobilePaymentWorker(
            self.firebase_mgr,
            account_num,
            self.total_amount,
            store_name
        )
        self.payment_worker.finished_signal.connect(self.on_payment_finished)
        self.payment_worker.start()
        
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_payment_progress)
        self.progress_timer.start(15)  # 1.5 seconds duration total
        
    def show_progress_ui(self):
        self.content_widget.hide()
        self.footer_widget.hide()
        if hasattr(self, 'btn_close'):
            self.btn_close.hide()
            
        self.progress_widget = QFrame()
        self.progress_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.WHITE};
                border: none;
                border-bottom-left-radius: {styles.s(12)}px;
                border-bottom-right-radius: {styles.s(12)}px;
            }}
        """)
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(styles.s(30), styles.s(35), styles.s(30), styles.s(35))
        progress_layout.setSpacing(styles.s(15))
        progress_layout.addStretch()
        
        # Title Label
        self.lbl_progress_title = QLabel("결제가 진행 중입니다")
        self.lbl_progress_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_progress_title.setStyleSheet(f"font-size: 15pt; font-weight: bold; color: {styles.DARK_PURPLE}; font-family: '{styles.FONT_FAMILY}';")
        progress_layout.addWidget(self.lbl_progress_title)
        
        # Subtitle
        self.lbl_progress_sub = QLabel("잠시만 기다려 주세요...")
        self.lbl_progress_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_progress_sub.setStyleSheet(f"font-size: 9.5pt; color: #666666; font-family: '{styles.FONT_FAMILY}';")
        progress_layout.addWidget(self.lbl_progress_sub)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(styles.s(12))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {styles.BORDER_COLOR};
                border-radius: {styles.s(6)}px;
                background-color: #F0F0F0;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                stop:0 {styles.PRIMARY_PURPLE}, 
                                                stop:1 {styles.DARK_PURPLE});
                border-radius: {styles.s(6)}px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Detail / Status Label
        self.lbl_progress_detail = QLabel("결제 승인 요청 중...")
        self.lbl_progress_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_progress_detail.setStyleSheet(f"font-size: 9pt; color: #7B68EE; font-weight: bold; font-family: '{styles.FONT_FAMILY}';")
        progress_layout.addWidget(self.lbl_progress_detail)
        
        progress_layout.addStretch()
        self.layout.addWidget(self.progress_widget)
        
        self.worker_finished = False
        self.worker_success = False
        self.worker_message = ""
        self.worker_balance = 0.0
        self.progress_step = 0
        
    def on_payment_finished(self, success, message, balance):
        self.worker_success = success
        self.worker_message = message
        self.worker_balance = balance
        self.worker_finished = True
        
    def update_payment_progress(self):
        self.progress_step += 1
        
        # Cap at 99 if worker has not finished yet
        if self.progress_step >= 99 and not self.worker_finished:
            self.progress_step = 99
            self.lbl_progress_detail.setText("서버 응답 대기 중...")
            
        self.progress_bar.setValue(self.progress_step)
        
        if self.progress_step < 50:
            if not self.worker_finished or self.worker_success:
                self.lbl_progress_detail.setText("결제 승인 요청 중...")
        elif self.progress_step < 99:
            if not self.worker_finished or self.worker_success:
                self.lbl_progress_detail.setText("결제 완료 처리 중...")
                
        if self.progress_step >= 100 and self.worker_finished:
            self.progress_timer.stop()
            if self.worker_success:
                self.final_account_number = self.payment_worker.account_number
                self.final_balance_after = self.worker_balance
                self.final_message = self.worker_message
                self.accept()
            else:
                self.restore_input_ui(self.worker_message)
                
    def restore_input_ui(self, error_message):
        if hasattr(self, 'progress_widget') and self.progress_widget:
            self.layout.removeWidget(self.progress_widget)
            self.progress_widget.deleteLater()
            self.progress_widget = None
            
        self.content_widget.show()
        self.footer_widget.show()
        if hasattr(self, 'btn_close'):
            self.btn_close.show()
            self.btn_close.setEnabled(True)
            
        self.btn_pay.setEnabled(True)
        self.txt_account.setEnabled(True)
        self.lbl_status.setText(f"❌ {error_message}")
        self.lbl_status.setStyleSheet("color: red; font-weight: bold; font-size: 8.5pt; font-family: 'Malgun Gothic';")
        self.txt_account.clear()
        self.txt_account.setFocus()
        
        self.is_processing = False
        
    def reject(self):
        if getattr(self, "is_processing", False):
            return
        if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
            return
        super().reject()
        
    def get_payment_details(self):
        return {
            "account_number": getattr(self, "final_account_number", ""),
            "balance_after": getattr(self, "final_balance_after", 0.0),
            "amount": self.total_amount
        }
