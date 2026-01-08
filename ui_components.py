from PyQt6.QtWidgets import (QPushButton, QLabel, QFrame, QVBoxLayout, QDialog, 
                             QHBoxLayout, QSpinBox, QGraphicsDropShadowEffect, QLineEdit, QTextBrowser)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import styles

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

class StatusLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(styles.LABEL_HEADER_STYLE)

class SummaryFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.TOTAL_AREA_STYLE)

class EditItemDialog(QDialog):
    def __init__(self, product_name, current_qty, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 350)
        
        # Main Container with rounding and shadow
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 430, 330)
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
        layout.setSpacing(15)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {styles.PRIMARY_PURPLE};
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        
        lbl_title = QLabel("상품 수량 변경 / 삭제")
        lbl_title.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; font-family: 'Malgun Gothic';")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Content Layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 0, 20, 0)
        
        # Product Name
        lbl_name = QLabel(product_name)
        lbl_name.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {styles.TEXT_COLOR}; border-bottom: 2px solid {styles.PRIMARY_PURPLE}; padding-bottom: 10px;")
        lbl_name.setWordWrap(True)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(lbl_name)
        
        content_layout.addSpacing(10)
        
        # Quantity Control (Big Buttons)
        qty_layout = QHBoxLayout()
        qty_layout.setSpacing(15)
        
        btn_minus = QPushButton("-")
        btn_minus.setFixedSize(50, 50)
        btn_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_minus.setStyleSheet(f"background-color: #E0E0E0; border-radius: 25px; font-size: 20pt; font-weight: bold; color: {styles.TEXT_COLOR};")
        btn_minus.clicked.connect(self.decrease_qty)
        
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 999)
        self.spin_qty.setValue(current_qty)
        self.spin_qty.setFixedSize(100, 50)
        self.spin_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_qty.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {styles.TEXT_COLOR}; border: 2px solid {styles.BORDER_COLOR}; border-radius: 10px; background-color: {styles.WHITE};")
        # Hide standard buttons to use custom ones
        self.spin_qty.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        
        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(50, 50)
        btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_plus.setStyleSheet(f"background-color: {styles.PRIMARY_PURPLE}; border-radius: 25px; font-size: 20pt; font-weight: bold; color: white;")
        btn_plus.clicked.connect(self.increase_qty)
        
        qty_layout.addStretch()
        qty_layout.addWidget(btn_minus)
        qty_layout.addWidget(self.spin_qty)
        qty_layout.addWidget(btn_plus)
        qty_layout.addStretch()
        
        content_layout.addLayout(qty_layout)
        layout.addLayout(content_layout)
        
        layout.addStretch()
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(20, 0, 20, 0)
        
        btn_update = QPushButton("수정 완료")
        btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.ACCENT_GREEN};
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {styles.DARK_GREEN}; }}
        """)
        btn_update.clicked.connect(self.accept)
        
        btn_delete = QPushButton("삭제")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.CANCEL_RED};
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #C62828; }}
        """)
        btn_delete.clicked.connect(self.delete_item)
        
        btn_cancel = QPushButton("취소")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #BDBDBD;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #9E9E9E; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_update, stretch=2)
        btn_layout.addWidget(btn_delete, stretch=1)
        btn_layout.addWidget(btn_cancel, stretch=1)
        layout.addLayout(btn_layout)
        
        self.delete_clicked = False

    def decrease_qty(self):
        val = self.spin_qty.value()
        if val > 1:
            self.spin_qty.setValue(val - 1)
            
    def increase_qty(self):
        self.spin_qty.setValue(self.spin_qty.value() + 1)

    def delete_item(self):
        self.delete_clicked = True
        self.accept()
    
    def get_new_qty(self):
        return self.spin_qty.value()

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
        self.setFixedSize(450, 300)
        
        self.new_amount = current_amount
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 430, 280)
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
        layout.setSpacing(15)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {styles.PRIMARY_PURPLE};
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        
        lbl_title = QLabel("금고 보관 금액 수정")
        lbl_title.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; font-family: 'Malgun Gothic';")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 10, 30, 10)
        
        lbl_hint = QLabel("현재 금고 전체 실물 금액을 입력해주세요:")
        lbl_hint.setStyleSheet(f"color: {styles.TEXT_COLOR}; font-size: 11pt;")
        content_layout.addWidget(lbl_hint)
        
        self.txt_amount = QLineEdit(str(current_amount))
        self.txt_amount.setFixedHeight(60)
        self.txt_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_amount.setStyleSheet(f"""
            QLineEdit {{
                font-size: 24pt;
                font-weight: bold;
                color: {styles.PRIMARY_PURPLE};
                border: 2px solid {styles.PRIMARY_PURPLE};
                border-radius: 10px;
                background-color: #F3E5F5;
                padding: 5px;
            }}
        """)
        content_layout.addWidget(self.txt_amount)
        layout.addLayout(content_layout)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(30, 0, 30, 0)
        
        btn_save = QPushButton("수정 완료")
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
        txt = self.txt_amount.text().replace(",", "").strip()
        if not txt.isdigit():
            CustomMessageDialog("오류", "숫자만 입력해 주세요.", 'warning', self).exec()
            return
        
        self.new_amount = int(txt)
        self.accept()

    def get_amount(self):
        return self.new_amount

class ReceiptPreviewDialog(QDialog):
    def __init__(self, html_content, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 700)
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 430, 680)
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
        
        lbl_title = QLabel("기 결제 영수증 확인")
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
        self.setFixedSize(500, 550)
        
        self.store_info = store_info
        
        # Main Container
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 480, 530)
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
        self.new_info = {
            "store_name": self.edit_name.text().strip(),
            "biz_num": self.edit_biz.text().strip(),
            "address": self.edit_addr.text().strip(),
            "owner": self.edit_owner.text().strip(),
            "tel": self.edit_tel.text().strip()
        }
        
        if not self.new_info["store_name"]:
            CustomMessageDialog("알림", "점포명은 필수 입력 사항입니다.", 'warning', self).exec()
            return
            
        self.accept()

    def get_store_info(self):
        return self.new_info
