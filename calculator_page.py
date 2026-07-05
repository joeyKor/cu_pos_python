import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import styles

class CalculatorPage(QWidget):
    backRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formula = ""
        self.current_value = "0"
        self.is_result_shown = False
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
        
        self.lbl_title = QLabel("계산기")
        self.lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("서비스 > 계산기")
        lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #7B68EE; font-weight: bold;")
        header_layout.addWidget(lbl_breadcrumb)
        main_layout.addWidget(header_frame)
        
        # 2. Main Content Area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # --- Left Column: VAT Helper & Guide ---
        left_frame = QFrame()
        left_frame.setStyleSheet("QFrame { background-color: #202D3D; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)
        
        lbl_guide_title = QLabel("🧮 계산기 기능 안내")
        lbl_guide_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background: transparent; border: none;")
        left_layout.addWidget(lbl_guide_title)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #2D3E50; max-height: 1px; border: none;")
        left_layout.addWidget(divider)
        
        bullets = [
            "• 일반 사칙연산(+, -, *, /)을 신속하게 지원합니다.",
            "• 편의점 계산용 고액 입력에 맞추어 [00] 및 [000] 단추를 제공합니다.",
            "• [Backspace] 단추를 사용하여 끝자리를 수정할 수 있습니다."
        ]
        
        for bullet in bullets:
            lbl_bullet = QLabel(bullet)
            lbl_bullet.setWordWrap(True)
            lbl_bullet.setStyleSheet("font-size: 11pt; color: #E0E0E0; background: transparent; border: none;")
            left_layout.addWidget(lbl_bullet)
            
        left_layout.addSpacing(20)
        
        # VAT Calculator Card
        vat_card = QFrame()
        vat_card.setStyleSheet("QFrame { background-color: #2D3E50; border-radius: 6px; }")
        vat_layout = QVBoxLayout(vat_card)
        vat_layout.setContentsMargins(15, 15, 15, 15)
        vat_layout.setSpacing(10)
        
        lbl_vat_title = QLabel("🏷️ 간편 부가세 계산기")
        lbl_vat_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #8BC34A; background: transparent;")
        vat_layout.addWidget(lbl_vat_title)
        
        self.txt_vat_input = QLineEdit()
        self.txt_vat_input.setPlaceholderText("금액 입력 (공급대가)")
        self.txt_vat_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333;
                border: 1px solid #485A6A;
                border-radius: 4px;
                padding: 6px;
                font-size: 11pt;
            }
        """)
        self.txt_vat_input.textChanged.connect(self.calculate_vat)
        vat_layout.addWidget(self.txt_vat_input)
        
        self.lbl_supply_value = QLabel("공급가액: 0 원")
        self.lbl_supply_value.setStyleSheet("font-size: 11pt; color: white; background: transparent;")
        self.lbl_vat_amount = QLabel("부가세액: 0 원")
        self.lbl_vat_amount.setStyleSheet("font-size: 11pt; color: white; background: transparent;")
        
        vat_layout.addWidget(self.lbl_supply_value)
        vat_layout.addWidget(self.lbl_vat_amount)
        
        left_layout.addWidget(vat_card)
        left_layout.addStretch()
        content_layout.addWidget(left_frame, stretch=35)
        
        # --- Right Column: Sleek Calculator Interface ---
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #DEE2E6; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        
        # Digital Display
        display_frame = QFrame()
        display_frame.setFixedHeight(120)
        display_frame.setStyleSheet("background-color: #1E293B; border-radius: 6px;")
        display_layout = QVBoxLayout(display_frame)
        display_layout.setContentsMargins(15, 10, 15, 10)
        display_layout.setSpacing(5)
        
        self.lbl_formula = QLabel("")
        self.lbl_formula.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_formula.setStyleSheet("color: #94A3B8; font-size: 14pt; background: transparent; border: none;")
        
        self.lbl_display = QLabel("0")
        self.lbl_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_display.setStyleSheet("color: white; font-size: 32pt; font-weight: bold; background: transparent; border: none;")
        
        display_layout.addWidget(self.lbl_formula)
        display_layout.addWidget(self.lbl_display)
        right_layout.addWidget(display_frame)
        
        # Calculator Button Grid
        grid_widget = QWidget()
        grid_widget.setStyleSheet("border: none; background: transparent;")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        
        buttons = [
            ("C", 0, 0, "#EF5350", "white"), ("CE", 0, 1, "#F3F4F6", "#4B5563"), ("⌫", 0, 2, "#F3F4F6", "#4B5563"), ("÷", 0, 3, "#EDE9FE", "#7B68EE"),
            ("7", 1, 0, "#F9FAFB", "#1F2937"), ("8", 1, 1, "#F9FAFB", "#1F2937"), ("9", 1, 2, "#F9FAFB", "#1F2937"), ("×", 1, 3, "#EDE9FE", "#7B68EE"),
            ("4", 2, 0, "#F9FAFB", "#1F2937"), ("5", 2, 1, "#F9FAFB", "#1F2937"), ("6", 2, 2, "#F9FAFB", "#1F2937"), ("-", 2, 3, "#EDE9FE", "#7B68EE"),
            ("1", 3, 0, "#F9FAFB", "#1F2937"), ("2", 3, 1, "#F9FAFB", "#1F2937"), ("3", 3, 2, "#F9FAFB", "#1F2937"), ("+", 3, 3, "#EDE9FE", "#7B68EE"),
            ("0", 4, 0, "#F9FAFB", "#1F2937"), ("00", 4, 1, "#F9FAFB", "#1F2937"), ("000", 4, 2, "#F9FAFB", "#1F2937"), ("=", 4, 3, "#10B981", "white")
        ]
        
        for text, r, c, bg, fg in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(60)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            font_weight = "bold" if text in ["C", "CE", "⌫", "÷", "×", "-", "+", "=", "00", "000"] else "normal"
            font_size = "18pt" if text == "=" else "14pt"
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {fg};
                    font-size: {font_size};
                    font-weight: {font_weight};
                    border: 1px solid #E5E7EB;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    filter: brightness(0.9);
                    background-color: {self.get_hover_color(bg)};
                }}
            """)
            btn.clicked.connect(lambda checked, t=text: self.button_clicked(t))
            grid.addWidget(btn, r, c)
            
        right_layout.addWidget(grid_widget, stretch=1)
        content_layout.addWidget(right_frame, stretch=65)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # 3. Bottom Navigation
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
        
    def get_hover_color(self, bg):
        if bg == "#10B981":
            return "#059669"
        elif bg == "#EF5350":
            return "#E53935"
        elif bg == "#EDE9FE":
            return "#DDD6FE"
        elif bg == "#F3F4F6":
            return "#E5E7EB"
        elif bg == "#F9FAFB":
            return "#F3F4F6"
        return bg
        
    def button_clicked(self, char):
        if char == "C":
            self.formula = ""
            self.current_value = "0"
            self.is_result_shown = False
        elif char == "CE":
            self.current_value = "0"
        elif char == "⌫":
            if self.is_result_shown:
                self.formula = ""
                self.is_result_shown = False
            else:
                self.current_value = self.current_value[:-1]
                if not self.current_value:
                    self.current_value = "0"
        elif char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "00", "000"]:
            if self.is_result_shown:
                self.current_value = ""
                self.formula = ""
                self.is_result_shown = False
                
            if self.current_value == "0" and char not in ["00", "000"]:
                self.current_value = char
            elif self.current_value != "0":
                self.current_value += char
        elif char in ["+", "-", "×", "÷"]:
            op = "*" if char == "×" else "/" if char == "÷" else char
            
            # If a result was just shown, use it to start new calculation
            if self.is_result_shown:
                self.formula = self.current_value + " " + op + " "
                self.is_result_shown = False
            else:
                self.formula += self.current_value + " " + op + " "
                
            self.current_value = "0"
        elif char == "=":
            if not self.formula:
                return
                
            full_equation = self.formula + self.current_value
            eval_equation = full_equation.replace("×", "*").replace("÷", "/")
            
            try:
                # Basic safety check on eval input
                allowed_chars = "0123456789+-*/. "
                if all(c in allowed_chars for c in eval_equation):
                    res = eval(eval_equation)
                    # Format integer results without decimal
                    if isinstance(res, float) and res.is_integer():
                        res = int(res)
                    
                    self.lbl_formula.setText(full_equation + " =")
                    self.current_value = f"{res:,}" if isinstance(res, (int, float)) else str(res)
                    self.is_result_shown = True
                else:
                    self.current_value = "Error"
            except Exception:
                self.current_value = "Error"
                
            self.formula = ""
            
        self.update_display()
        
    def update_display(self):
        # Format the display value (removing commas first to handle logic, adding them back)
        display_raw = self.current_value.replace(",", "")
        
        # Don't try to format error strings or float inputs currently typed
        if display_raw.replace("-", "").isdigit():
            formatted = f"{int(display_raw):,}"
        else:
            formatted = self.current_value
            
        self.lbl_display.setText(formatted)
        
        # Update formula label
        formula_formatted = self.formula.replace("*", "×").replace("/", "÷")
        self.lbl_formula.setText(formula_formatted)
        
    def calculate_vat(self, text):
        clean_text = text.replace(",", "")
        if not clean_text.isdigit():
            self.lbl_supply_value.setText("공급가액: 0 원")
            self.lbl_vat_amount.setText("부가세액: 0 원")
            return
            
        amount = int(clean_text)
        
        # Standard Korean VAT calculation:
        # Supply Value = Gross Amount / 1.1
        # VAT = Gross Amount - Supply Value
        supply = int(round(amount / 1.1))
        vat = amount - supply
        
        self.lbl_supply_value.setText(f"공급가액: {supply:,} 원")
        self.lbl_vat_amount.setText(f"부가세액: {vat:,} 원")
        
        # Automatically format the input text with commas
        self.txt_vat_input.blockSignals(True)
        self.txt_vat_input.setText(f"{amount:,}")
        self.txt_vat_input.blockSignals(False)
