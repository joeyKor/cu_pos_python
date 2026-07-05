import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QDateEdit, 
                             QGridLayout, QDialog, QAbstractSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QPixmap, QColor
import styles
from ui_components import CustomMessageDialog

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class BankCodeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("background-color: white; border: 2px solid #2D3E50; border-radius: 10px;")
        self.selected_code = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header
        lbl_title = QLabel("은행코드 조회")
        lbl_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2D3E50; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        # Grid of banks
        grid_widget = QWidget()
        grid_widget.setStyleSheet("border: none; background: transparent;")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        
        banks = [
            ("KB국민은행", "04"), ("신한은행", "88"), ("우리은행", "20"), ("하나은행", "81"),
            ("NH농협은행", "11"), ("IBK기업은행", "03"), ("우체국", "71"), ("새마을금고", "45"),
            ("신협", "48"), ("SC제일은행", "23"), ("산업은행", "02"), ("수협은행", "07"),
            ("대구은행", "31"), ("부산은행", "32"), ("광주은행", "34"), ("경남은행", "39")
        ]
        
        cols = 4
        for idx, (name, code) in enumerate(banks):
            row = idx // cols
            col = idx % cols
            
            btn = QPushButton(f"{name}\n({code})")
            btn.setFixedSize(100, 60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8F9FA;
                    color: #212529;
                    font-size: 10pt;
                    font-weight: bold;
                    border: 1px solid #DEE2E6;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #E9ECEF;
                    border-color: #CED4DA;
                }
                QPushButton:pressed {
                    background-color: #7B68EE;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, c=code: self.select_code(c))
            grid.addWidget(btn, row, col)
            
        layout.addWidget(grid_widget)
        
        # Cancel button
        btn_cancel = QPushButton("닫기")
        btn_cancel.setFixedHeight(45)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)
        
    def select_code(self, code):
        self.selected_code = code
        self.accept()
        
    def get_selected_code(self):
        return self.selected_code


class LargeCheckDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("background-color: white; border: 3px solid #7B68EE; border-radius: 12px;")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title bar
        title_layout = QHBoxLayout()
        lbl_title = QLabel("수표 상세 보기 (클릭하여 닫기)")
        lbl_title.setStyleSheet("font-size: 15pt; font-weight: bold; color: #2D3E50; border: none; background: transparent;")
        title_layout.addWidget(lbl_title)
        title_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                font-size: 14pt;
                font-weight: bold;
                color: #888888;
                border: none;
            }
            QPushButton:hover {
                color: #FF5252;
            }
        """)
        btn_close.clicked.connect(self.accept)
        title_layout.addWidget(btn_close)
        layout.addLayout(title_layout)
        
        # Image
        lbl_img = QLabel()
        img_path = resource_path(os.path.join("assets", "image", "check_specimen.png"))
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            lbl_img.setPixmap(pixmap.scaled(styles.s(960), styles.s(340), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_img.setText("[수표 조회 안내 이미지]")
            lbl_img.setStyleSheet("font-size: 14pt; color: #999; border: 1px dashed #CCC; background-color: #EEE; min-height: 180px; border-radius: 8px;")
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_img.mousePressEvent = lambda event: self.accept()
        lbl_img.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(lbl_img)


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


class CheckInquiryPage(QWidget):
    backRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
 
    def init_ui(self):
        self.setStyleSheet("background-color: #F8F9FA;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
 
        # 1. Header
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("background-color: white; border-bottom: 2px solid #DEE2E6;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        lbl_title = QLabel("수표조회")
        lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("통합조회 > 수표조회")
        lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #7B68EE; font-weight: bold;")
        header_layout.addWidget(lbl_breadcrumb)
        main_layout.addWidget(header_frame)
 
        # 2. Main Content
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
 
        # --- Left Column: Instructions Panel ---
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #202D3D;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)
        
        # Title
        lbl_caution_title = QLabel("⚠️ 주의사항")
        lbl_caution_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background: transparent; border: none;")
        left_layout.addWidget(lbl_caution_title)
        
        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #2D3E50; max-height: 1px; border: none;")
        left_layout.addWidget(divider)
        
        # Bullets
        lbl_bullet1 = QLabel("• 해당 은행의 조회 서비스가 마감 된 경우에는 수표조회가 되지 않을 수 있습니다.")
        lbl_bullet1.setWordWrap(True)
        lbl_bullet1.setStyleSheet("font-size: 12pt; color: #E0E0E0; background: transparent; border: none; line-height: 1.4;")
        left_layout.addWidget(lbl_bullet1)
        
        lbl_bullet2 = QLabel("• 농협 수표는 은행마감시간(23시 ~ 08시), 주말 및 휴일에는 조회되지 않습니다.")
        lbl_bullet2.setWordWrap(True)
        lbl_bullet2.setStyleSheet("font-size: 12pt; color: #FF8A65; font-weight: bold; background: transparent; border: none; line-height: 1.4;")
        left_layout.addWidget(lbl_bullet2)
        
        lbl_bullet3 = QLabel("• 은행코드를 모르는 경우 아래 [은행코드 조회] 버튼을 눌러 확인 후 입력 하시면 됩니다.")
        lbl_bullet3.setWordWrap(True)
        lbl_bullet3.setStyleSheet("font-size: 12pt; color: #E0E0E0; background: transparent; border: none; line-height: 1.4;")
        left_layout.addWidget(lbl_bullet3)
        
        left_layout.addSpacing(15)
        
        # ARS Section
        lbl_ars_title = QLabel("수표조회 불가시 대처 방법(ARS 이용)")
        lbl_ars_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: white; background: transparent; border: none;")
        left_layout.addWidget(lbl_ars_title)
        
        ars_frame = QFrame()
        ars_frame.setStyleSheet("background-color: #16202C; border-radius: 8px; border: 1px solid #2D3E50;")
        ars_layout = QVBoxLayout(ars_frame)
        ars_layout.setContentsMargins(15, 15, 15, 15)
        ars_layout.setSpacing(10)
        
        lbl_ars_bullet1 = QLabel("• 국번없이 1369번 (전자 금융 공동망 대고객 서비스)으로 전화를 거신 후 안내에 따라 조회 가능합니다.")
        lbl_ars_bullet1.setWordWrap(True)
        lbl_ars_bullet1.setStyleSheet("font-size: 11pt; color: #B0BEC5; background: transparent; border: none; line-height: 1.4;")
        
        lbl_ars_bullet2 = QLabel("• 수표조회는 2#을 누르시면 이용 가능합니다.")
        lbl_ars_bullet2.setWordWrap(True)
        lbl_ars_bullet2.setStyleSheet("font-size: 11pt; color: #B0BEC5; background: transparent; border: none; line-height: 1.4;")
        
        ars_layout.addWidget(lbl_ars_bullet1)
        ars_layout.addWidget(lbl_ars_bullet2)
        left_layout.addWidget(ars_frame)
        
        left_layout.addStretch()
        
        # Highlight Box at the bottom
        lbl_warning_footer = QLabel("'정상 수표' 로 조회되지 않으면 절대 받으시면 안됩니다.")
        lbl_warning_footer.setWordWrap(True)
        lbl_warning_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_warning_footer.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: #FF5252;
            background-color: #2C1F2D;
            border: 1px solid #D32F2F;
            border-radius: 5px;
            padding: 12px;
        """)
        left_layout.addWidget(lbl_warning_footer)
        
        content_layout.addWidget(left_frame, stretch=35)
 
        # --- Right Column: Search Form ---
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Guide Illustration Image at top
        lbl_img = QLabel()
        img_path = resource_path(os.path.join("assets", "image", "check_specimen.png"))
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            lbl_img.setPixmap(pixmap.scaled(styles.s(750), styles.s(260), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            lbl_img.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl_img.mousePressEvent = self.show_large_check
            lbl_img.setToolTip("클릭하면 크게 봅니다")
        else:
            lbl_img.setText("[수표 조회 안내 이미지]")
            lbl_img.setStyleSheet("font-size: 14pt; color: #999; border: 1px dashed #CCC; background-color: #EEE; min-height: 180px; border-radius: 8px;")
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(lbl_img)
        
        # Zoom indicator label below the check
        if not pixmap.isNull():
            lbl_zoom_hint = QLabel("🔍 이미지를 클릭하면 수표를 더 크게 볼 수 있습니다.")
            lbl_zoom_hint.setStyleSheet("font-size: 10pt; color: #7B68EE; font-weight: bold; background: transparent; border: none; margin-bottom: 5px;")
            lbl_zoom_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(lbl_zoom_hint)
        
        form_frame = QFrame()
        form_frame.setObjectName("FormFrame")
        form_frame.setStyleSheet(f"""
            QFrame#FormFrame {{
                background-color: white;
                border: 1px solid #DEE2E6;
                border-radius: 8px;
            }}
            QLineEdit, QDateEdit {{
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 10px;
                padding-right: 10px;
                font-size: {styles.fs(12)};
                min-height: {styles.s(40)}px;
            }}
            QDateEdit QLineEdit {{
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                color: #333333;
                min-height: {styles.s(40)}px;
            }}
            QLineEdit:focus, QDateEdit:focus {{
                border: 2px solid #7B68EE;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: #2D3E50;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar QLabel {{
                color: white;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {{
                color: white;
                background-color: transparent;
            }}
            QCalendarWidget QAbstractItemView {{
                color: #333333;
                background-color: white;
                selection-background-color: #7B68EE;
                selection-color: white;
            }}
        """)
        
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)
        
        # 1. 수표번호
        self.edit_num = QLineEdit()
        self.edit_num.setPlaceholderText("수표번호 8자리 입력")
        form_layout.addWidget(BadgeLabel(1, "수표번호"), 0, 0)
        form_layout.addWidget(self.edit_num, 0, 1)
        
        # 2. 은행코드
        self.edit_bank_code = QLineEdit()
        self.edit_bank_code.setPlaceholderText("은행코드 입력 (예: 04)")
        form_layout.addWidget(BadgeLabel(2, "은행코드"), 1, 0)
        form_layout.addWidget(self.edit_bank_code, 1, 1)
        
        # 3. 지점코드
        self.edit_branch_code = QLineEdit()
        self.edit_branch_code.setPlaceholderText("지점코드 입력")
        form_layout.addWidget(BadgeLabel(3, "지점코드"), 2, 0)
        form_layout.addWidget(self.edit_branch_code, 2, 1)
        
        # 4. 일련번호
        self.edit_serial = QLineEdit()
        self.edit_serial.setPlaceholderText("일련번호 입력")
        form_layout.addWidget(BadgeLabel(4, "일련번호"), 3, 0)
        form_layout.addWidget(self.edit_serial, 3, 1)
        
        # 5. 권종코드
        self.edit_type_code = QLineEdit()
        self.edit_type_code.setPlaceholderText("권종코드 입력")
        form_layout.addWidget(BadgeLabel(5, "권종코드"), 4, 0)
        form_layout.addWidget(self.edit_type_code, 4, 1)
        
        # 6. 수표금액
        self.edit_amt = QLineEdit()
        self.edit_amt.setPlaceholderText("수표금액 입력 (예: 100,000)")
        form_layout.addWidget(BadgeLabel(None, "수표금액"), 5, 0)
        form_layout.addWidget(self.edit_amt, 5, 1)
        
        # 7. 발행일자
        self.edit_date = QDateEdit()
        self.edit_date.setCalendarPopup(True)
        self.edit_date.setDisplayFormat("yyyy-MM-dd")
        self.edit_date.setDate(QDate.currentDate())
        self.edit_date.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        form_layout.addWidget(BadgeLabel(6, "발행일자"), 6, 0)
        form_layout.addWidget(self.edit_date, 6, 1)
        
        # Buttons Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        self.btn_bank_search = QPushButton("은행코드 조회")
        self.btn_bank_search.setFixedHeight(styles.s(50))
        self.btn_bank_search.setStyleSheet("""
            QPushButton {
                background-color: #2D3E50;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 5px;
                padding-left: 20px;
                padding-right: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1F2B38;
            }
        """)
        self.btn_bank_search.clicked.connect(self.search_bank_code)
        
        self.btn_query = QPushButton("확인")
        self.btn_query.setFixedHeight(styles.s(50))
        self.btn_query.setFixedWidth(styles.s(180))
        self.btn_query.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        self.btn_query.clicked.connect(self.process_inquiry)
        
        btn_row.addStretch()
        btn_row.addWidget(self.btn_bank_search)
        btn_row.addWidget(self.btn_query)
        
        right_layout.addWidget(form_frame)
        right_layout.addLayout(btn_row)
        
        content_layout.addLayout(right_layout, stretch=65)
        
        main_layout.addWidget(content_widget, stretch=1)
 
        # 3. Bottom Navigation
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(100)
        bottom_frame.setStyleSheet("background-color: #CAD2D9; border-top: 1px solid #CCC;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(30, 10, 30, 10)
        bottom_layout.setSpacing(20)
        
        btn_back = QPushButton("◀  이전 [CLEAR]")
        btn_back.setFixedSize(220, 65)
        btn_back.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 15pt; border-radius: 5px;")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.backRequested.emit)
        bottom_layout.addWidget(btn_back)
        bottom_layout.addStretch()
        
        main_layout.addWidget(bottom_frame)
 
    def search_bank_code(self):
        dialog = BankCodeDialog(self)
        if dialog.exec():
            code = dialog.get_selected_code()
            if code:
                self.edit_bank_code.setText(code)
                self.edit_bank_code.setFocus()
 
    def process_inquiry(self):
        check_num = self.edit_num.text().strip()
        bank_code = self.edit_bank_code.text().strip()
        branch_code = self.edit_branch_code.text().strip()
        serial = self.edit_serial.text().strip()
        type_code = self.edit_type_code.text().strip()
        amount = self.edit_amt.text().strip()
        
        if not all([check_num, bank_code, branch_code, serial, type_code, amount]):
            CustomMessageDialog("알림", "모든 수표 정보를 입력해주세요.", 'warning', self).exec()
            return
            
        # Show alert popup
        CustomMessageDialog(
            "수표 조회 결과", 
            "조회 결과: 유효하지 않거나 등록되지 않은 수표입니다.\n(부도 또는 사고 수표일 수 있으니 주의하십시오.)", 
            'warning', 
            self
        ).exec()
        
        # Clear fields
        self.edit_num.clear()
        self.edit_bank_code.clear()
        self.edit_branch_code.clear()
        self.edit_serial.clear()
        self.edit_type_code.clear()
        self.edit_amt.clear()
        self.edit_date.setDate(QDate.currentDate())
        self.edit_num.setFocus()
 
    def show_large_check(self, event):
        dialog = LargeCheckDialog(self)
        dialog.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.edit_num.setFocus()
