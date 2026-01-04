import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QLineEdit, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush
import styles

class ClickableLabel(QLabel):
    doubleClicked = pyqtSignal()
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

class WelcomePage(QWidget):
    barcodeScanned = pyqtSignal(str)
    settingsRequested = pyqtSignal()
    safeBalanceEditRequested = pyqtSignal()
    storeRegistrationRequested = pyqtSignal()
    lastReceiptPrintRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Base Style
        self.setStyleSheet(f"background-color: #F8F9FA;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header (Banner Area)
        header_frame = QFrame()
        header_frame.setFixedHeight(300)
        header_frame.setObjectName("header_banner")
        header_frame.setStyleSheet("background-color: white; border-bottom: 2px solid #DEE2E6;")
        
        # Background Image (Using QLabel for better scaling control)
        banner_path = r"C:\Users\joy\.gemini\antigravity\brain\6adb7436-f2cf-4cd3-90c3-8b61c64acc9a\cu_store_mascot_bg_1767191372811.png"
        if os.path.exists(banner_path):
            bg_label = QLabel(header_frame)
            pixmap = QPixmap(banner_path)
            self.original_pixmap = pixmap # Store the original pixmap
            bg_label.setPixmap(pixmap)
            # bg_label.setScaledContents(True) # Removed to maintain aspect ratio manually
            bg_label.resize(1920, 300) # Initial size
            bg_label.lower() 
            self.bg_label = bg_label 
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 50, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Top Right Button Area (Overlay)
        top_btn_container = QWidget(header_frame)
        top_btn_layout = QHBoxLayout(top_btn_container)
        top_btn_layout.setContentsMargins(0, 0, 20, 0)
        top_btn_layout.addStretch()
        
        btn_exit = QPushButton("종료")
        btn_exit.setFixedSize(80, 40)
        btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #EF5350;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        btn_exit.clicked.connect(self.handle_exit)
        top_btn_layout.addWidget(btn_exit)
        self.top_btn_container = top_btn_container # For positioning

        # Greeting Text (Transparent Background)
        greeting_label = QLabel("어서오세요. CU입니다.")
        greeting_label.setStyleSheet("font-size: 32pt; font-weight: bold; color: #333333; background: transparent;")
        header_layout.addWidget(greeting_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Center Barcode Area (White Rounded Container)
        barcode_container_outer = QWidget()
        barcode_container_outer.setFixedWidth(600)
        barcode_container_outer.setFixedHeight(70)
        barcode_container_outer.setObjectName("input_container")
        barcode_container_outer.setStyleSheet(styles.WELCOME_INPUT_CONTAINER)
        
        barcode_inner_lyt = QHBoxLayout(barcode_container_outer)
        barcode_inner_lyt.setContentsMargins(20, 0, 20, 0)
        
        # Logo placeholder
        chatbot_logo = QLabel("CU스쿨\nChatbot")
        chatbot_logo.setStyleSheet("font-size: 8pt; color: #333; font-weight: bold; line-height: 1.0; background: transparent;")
        barcode_inner_lyt.addWidget(chatbot_logo)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("바코드를 스캔하세요")
        self.barcode_input.setStyleSheet(styles.WELCOME_INPUT_STYLE + "background: transparent;")
        self.barcode_input.returnPressed.connect(self.on_barcode_return)
        self.barcode_input.textChanged.connect(self.on_barcode_text_changed)
        barcode_inner_lyt.addWidget(self.barcode_input)
        
        barcode_icon = QLabel("[ |||| ]") # Placeholder for scanner icon
        barcode_icon.setStyleSheet("font-size: 18pt; color: #999; background: transparent;")
        barcode_inner_lyt.addWidget(barcode_icon)
        
        header_layout.addSpacing(20)
        header_layout.addWidget(barcode_container_outer, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Stats Overlay (Top Right of Main Frame)
        stats_widget = QFrame(header_frame)
        stats_widget.setFixedSize(240, 140)
        stats_widget.setStyleSheet("background: rgba(255, 255, 255, 0.7); border: none; border-radius: 8px;") # More transparent
        
        s_lyt = QVBoxLayout(stats_widget)
        s_lyt.setSpacing(4)
        
        lbl_s_title = QLabel("지금 포스에서는")
        lbl_s_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #555; background: transparent;")
        s_lyt.addWidget(lbl_s_title)
        
        def add_stat(label, value):
            h = QHBoxLayout()
            lbl_l = QLabel(label)
            lbl_l.setStyleSheet("font-size: 11pt; color: #333; background: transparent;")
            h.addWidget(lbl_l)
            h.addStretch()
            v = QLabel(value)
            v.setStyleSheet("font-size: 11pt; color: #D32F2F; font-weight: bold; background: transparent;")
            h.addWidget(v)
            s_lyt.addLayout(h)
            
        add_stat("환불 :", "0건")
        add_stat("전체취소 :", "0건")
        add_stat("등록취소 :", "1건")
        
        lbl_occ = QLabel("발생하였습니다.")
        lbl_occ.setStyleSheet("font-size: 10pt; color: #555;")
        s_lyt.addWidget(lbl_occ)
        
        self.stats_widget = stats_widget # Keep reference for positioning
        
        main_layout.addWidget(header_frame)

        # 2. Main Body Dashboard
        body_container = QWidget()
        body_layout = QHBoxLayout(body_container)
        body_layout.setContentsMargins(15, 15, 15, 15)
        body_layout.setSpacing(15)

        # --- Dashboard LEFT: Inquiry & Service (Side-by-side) ---
        group_layout = QHBoxLayout()
        group_layout.setSpacing(10)

        def create_group_box(title, color, items):
            box = QFrame()
            box.setStyleSheet(f"background: #ECEFF1; border-radius: 8px; border: none;")
            lyt = QVBoxLayout(box)
            lyt.setContentsMargins(0, 0, 0, 0)
            lyt.setSpacing(0)
            
            hdr = QPushButton(title)
            hdr.setFixedHeight(80) # Reduced from 110
            hdr.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; font-size: 18pt; border-top-left-radius: 8px; border-top-right-radius: 8px; border: none;")
            lyt.addWidget(hdr)
            
            grid = QGridLayout()
            grid.setContentsMargins(10, 10, 10, 10)
            grid.setSpacing(10)
            for i, text in enumerate(items):
                btn = QPushButton(text)
                btn.setFixedHeight(65) # Reduced from 85
                btn.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; font-size: 11pt; border-top: 4px solid white; border-bottom: 4px solid rgba(0,0,0,0.1);")
                grid.addWidget(btn, i // 2, i % 2)
            lyt.addLayout(grid)
            return box

        inquiry_box = create_group_box("통합조회", "#7AB800", ["상품조회", "영수증조회", "수표조회", "교통카드잔액조회"])
        service_box = create_group_box("서비스", "#8A79B6", ["교통카드", "택배", "프리페이드", "공공요금"])
        
        group_layout.addWidget(inquiry_box)
        group_layout.addWidget(service_box)
        body_layout.addLayout(group_layout, stretch=6)

        # --- Dashboard CENTER: Payment & Safe & History ---
        center_col = QVBoxLayout()
        center_col.setSpacing(10)

        # Top row: Payment & Safe (Side-by-side)
        pay_safe_row = QHBoxLayout()
        pay_safe_row.setSpacing(10)

        btn_disc_top = QPushButton("결제 후\n할인 · 현금영수증")
        btn_disc_top.setFixedHeight(160)
        btn_disc_top.setStyleSheet("background: #ECEFF1; border: none; border-radius: 8px; font-weight: bold; font-size: 15pt; color: #333;") # Removed border, increased font
        
        safe_frame = QFrame()
        safe_frame.setFixedHeight(160)
        safe_frame.setStyleSheet("background: #ECEFF1; border: none; border-radius: 8px;") # Removed border
        safe_lyt = QVBoxLayout(safe_frame)
        safe_lyt.setContentsMargins(15, 15, 15, 15)
        safe_lyt.addWidget(QLabel("금고보관", styleSheet="font-weight: bold; font-size: 14pt; color: #555;"))
        self.lbl_safe_val = ClickableLabel("472,000")
        self.lbl_safe_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_safe_val.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_safe_val.setStyleSheet("background: white; color: #D32F2F; font-weight: bold; font-size: 20pt; padding: 10px; border-radius: 4px; border: none;") # Removed border
        self.lbl_safe_val.doubleClicked.connect(self.safeBalanceEditRequested.emit)
        safe_lyt.addWidget(self.lbl_safe_val)

        pay_safe_row.addWidget(btn_disc_top, stretch=1)
        pay_safe_row.addWidget(safe_frame, stretch=1)
        center_col.addLayout(pay_safe_row)

        # Transaction History (Below)
        hist_box = QFrame()
        hist_box.setFixedHeight(240) # Decreased height from stretching to fixed 240
        hist_box.setStyleSheet("background: white; border: none; border-radius: 8px;")
        hist_lyt = QVBoxLayout(hist_box)
        hist_lyt.setContentsMargins(30, 15, 30, 15) # Adjusted vertical margin
        hist_lyt.setSpacing(10) # Reduced spacing to fit larger fonts
        
        h_title_lyt = QHBoxLayout()
        lbl_h_title = QLabel("직전결제내역")
        lbl_h_title.setStyleSheet("font-weight: bold; font-size: 20pt; color: #333;") # Increased from 16pt
        h_title_lyt.addWidget(lbl_h_title)
        
        btn_print = QPushButton("영수증 출력")
        btn_print.setStyleSheet("background: #8A79B6; color: white; border-radius: 20px; font-weight: bold; font-size: 11pt; padding: 7px 20px;")
        btn_print.clicked.connect(self.lastReceiptPrintRequested.emit)
        h_title_lyt.addStretch()
        h_title_lyt.addWidget(btn_print)
        hist_lyt.addLayout(h_title_lyt)
        
        def add_hist_row(label, val, bold=False):
            h_row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 16pt; color: #555;") # Increased from 14pt
            h_row.addWidget(lbl)
            h_row.addStretch()
            v = QLabel(val)
            f_bold = "font-weight: bold;" if bold else ""
            color = "#333" if not bold else "#D32F2F" if "거스름돈" not in label else "#333"
            v.setStyleSheet(f"font-size: 22pt; {f_bold} color: {color};") # Increased from 16pt
            h_row.addWidget(v)
            hist_lyt.addLayout(h_row)
            return v
            
        self.lbl_hist_total = add_hist_row("총 구매액", "0 원", True)
        self.lbl_hist_paid = add_hist_row("결제한 금액", "0 원", True)
        self.lbl_hist_change = add_hist_row("거스름돈", "0 원")
        
        center_col.addWidget(hist_box) # Removed stretch to respect fixed height
        body_layout.addLayout(center_col, stretch=3)

        # --- Dashboard RIGHT: Wait & Refund (Wait above, Refund below) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        
        wait_stack = QVBoxLayout()
        wait_stack.setSpacing(8)
        for i in range(1, 4):
            btn_wait = QPushButton(f"대기{i}")
            btn_wait.setFixedHeight(75) # Increased from 50
            btn_wait.setStyleSheet(styles.WELCOME_SMALL_BUTTON)
            wait_stack.addWidget(btn_wait)
        right_col.addLayout(wait_stack)
        
        btn_refund = QPushButton("환불")
        btn_refund.setFixedHeight(180) # Increased from 120
        btn_refund.setStyleSheet("background: #EF5350; color: white; font-weight: bold; font-size: 24pt; border-radius: 8px;")
        right_col.addWidget(btn_refund)
        
        body_layout.addLayout(right_col, stretch=1)

        main_layout.addWidget(body_container, stretch=1)

        # 3. Bottom Quick Items & Categories
        bottom_widget = QWidget()
        bottom_lyt = QVBoxLayout(bottom_widget)
        bottom_lyt.setContentsMargins(10, 0, 10, 10)
        
        # Quick items
        q_row = QHBoxLayout()
        q_row.setSpacing(5)
        q_items = [
            ("친환경)CU백색봉투대\n100", "8803"), 
            ("아이시스2L P6입\n3,600", "8804"), 
            ("유앤)포켓몬볼모양젤\n1,000", "8805"), 
            ("츄파춥스12g\n300", "8806"), 
            ("트롤리지구젤리(낱개)\n1,000", "8807")
        ]
        
        for name, barcode in q_items:
            # Need to get current price for these but let's use placeholders as per image
            f = QFrame()
            f.setFixedHeight(80)
            f.setObjectName("quick_item")
            f.setStyleSheet(styles.WELCOME_QUICK_ITEM_FRAME)
            l = QVBoxLayout(f)
            l.setContentsMargins(10, 10, 10, 10)
            
            n_parts = name.split("\n")
            it_name = QLabel(n_parts[0])
            it_name.setStyleSheet(styles.WELCOME_ITEM_NAME_LABEL)
            it_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            it_price = QLabel(n_parts[1] if len(n_parts) > 1 else "0")
            it_price.setStyleSheet(styles.WELCOME_PRICE_LABEL)
            it_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            l.addWidget(it_name)
            l.addStretch()
            l.addWidget(it_price)
            q_row.addWidget(f, stretch=1)
            
        bottom_lyt.addLayout(q_row)
        
        # Category Tabs
        cat_row = QHBoxLayout()
        cat_row.setSpacing(2)
        btn_l_arr = QPushButton("<")
        btn_l_arr.setFixedSize(40, 50)
        btn_l_arr.setStyleSheet("background: white; border: 1px solid #DEE2E6;")
        cat_row.addWidget(btn_l_arr)
        
        cats = [("일반상품", "#7AB800"), ("소분상품", "#6C757D"), ("신문/상품권", "#6C757D"), ("쓰레기봉투/화장", "#6C757D"), ("점포등록", "#6C757D"), ("상품관리", "#6C757D")]
        for n, c in cats:
            b = QPushButton(n)
            b.setFixedHeight(50)
            b.setStyleSheet(f"background: white; color: #333; font-weight: bold; border: 1px solid #DEE2E6; border-top: 4px solid {c};")
            if n == "상품관리":
                b.clicked.connect(self.settingsRequested.emit)
            elif n == "점포등록":
                b.clicked.connect(self.storeRegistrationRequested.emit)
            cat_row.addWidget(b, stretch=1)
            
        btn_r_arr = QPushButton(">")
        btn_r_arr.setFixedSize(40, 50)
        btn_r_arr.setStyleSheet("background: white; border: 1px solid #DEE2E6;")
        cat_row.addWidget(btn_r_arr)
        
        bottom_lyt.addLayout(cat_row)
        
        main_layout.addWidget(bottom_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # 1. Scaled Background Banner (Maintaining Aspect Ratio)
        if hasattr(self, 'bg_label') and hasattr(self, 'original_pixmap'):
            canvas_w = self.width()
            canvas_h = 300 # Fixed banner height
            
            # Scale pixmap to fill the width while maintaining aspect ratio
            scaled_pixmap = self.original_pixmap.scaled(
                canvas_w, canvas_h, 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled_pixmap)
            self.bg_label.resize(canvas_w, canvas_h)
            
            # Center the pixmap if it's larger than the label after scaling
            # (KeepAspectRatioByExpanding ensures it fills, but we might want to offset)
            # For now, just setting it to fill the label is usually enough if it's centered.

        # 2. Position Stats Widget (Top Right)
        if hasattr(self, 'stats_widget'):
            self.stats_widget.move(self.width() - 250, 40)
            
        # 3. Position Top Buttons Container
        if hasattr(self, 'top_btn_container'):
            self.top_btn_container.setGeometry(0, 0, self.width(), 50)
    def handle_exit(self):
        window = self.window()
        if window:
            window.close()

    def on_barcode_return(self):
        barcode = self.barcode_input.text().strip()
        if barcode:
            self.barcodeScanned.emit(barcode)
            self.barcode_input.clear()

    def on_barcode_text_changed(self, text):
        if len(text) >= 5:
            self.on_barcode_return()

    def update_last_transaction(self, data):
        if not data:
            return
        
        total_amt = data.get("total_amt", 0)
        received_amt = data.get("received_amt", 0)
        change_amt = data.get("change_amt", 0)
        
        self.lbl_hist_total.setText(f"{total_amt:,} 원")
        self.lbl_hist_paid.setText(f"{received_amt:,} 원")
        self.lbl_hist_change.setText(f"{change_amt:,} 원")

    def update_safe_balance(self, amount):
        self.lbl_safe_val.setText(f"{amount:,}")

    def showEvent(self, event):
        super().showEvent(event)
        self.barcode_input.setFocus()
