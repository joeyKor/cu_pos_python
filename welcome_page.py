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
    refundRequested = pyqtSignal()
    receiptInquiryRequested = pyqtSignal()
    waitRequested = pyqtSignal(int)

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
        header_frame.setFixedHeight(360) # Reduced from 450 to save space
        header_frame.setObjectName("header_banner")
        # Universal White background to eliminate color mismatches
        header_frame.setStyleSheet("background-color: white; border: none;")
        
        base_path = r"C:\Users\joy\.gemini\antigravity\brain\eeed31fe-3ea1-4e4b-86a1-382a798d07a3"
        store_img = os.path.join(base_path, "cu_store_recreated_v1_1767798621656.png")
        mascot_img = os.path.join(base_path, "cu_mascot_fullbody_white_background_1767715363864.png")

        # Background Landscape is now a solid color matching the assets
        self.bg_label = None 

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 10, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Top Right Button Area (Overlay)
        top_btn_container = QWidget(header_frame)
        top_btn_layout = QHBoxLayout(top_btn_container)
        top_btn_layout.setContentsMargins(0, 0, 20, 0)
        top_btn_layout.addStretch()
        
        btn_exit = QPushButton("종료")
        btn_exit.setFixedSize(70, 35)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 83, 80, 0.1);
                color: #EF5350;
                font-weight: bold;
                border: 1px solid #EF5350;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #EF5350; color: white; }
        """)
        btn_exit.clicked.connect(self.handle_exit)
        top_btn_layout.addWidget(btn_exit)
        self.top_btn_container = top_btn_container

        # Greeting Text
        greeting_label = QLabel("어서오세요. CU입니다.")
        greeting_label.setStyleSheet("font-size: 34pt; font-weight: bold; color: #2C3E50; background: transparent;")
        header_layout.addWidget(greeting_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        header_layout.addSpacing(10)

        # Flanking Layout: [Store] [Barcode] [Mascot]
        middle_row = QWidget()
        middle_row_layout = QHBoxLayout(middle_row)
        middle_row_layout.setContentsMargins(0, 0, 0, 0)
        middle_row_layout.setSpacing(0) 
        middle_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        middle_row_layout.addStretch()

        # Store Icon (Left of Barcode) - Aligned to Top
        if os.path.exists(store_img):
            self.store_label = QLabel()
            # Scaling slightly smaller to fit well without clipping
            store_pix = QPixmap(store_img).scaled(280, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.store_label.setPixmap(store_pix)
            # AlignTop helps "move it up" while ensuring it fits in the layout
            self.store_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.store_label.setFixedSize(280, 280)
            middle_row_layout.addWidget(self.store_label)
            middle_row_layout.addSpacing(20) # Spacer between store and barcode

        # Barcode Area (Center)
        barcode_container_outer = QWidget()
        barcode_container_outer.setFixedWidth(650)
        barcode_container_outer.setFixedHeight(75)
        barcode_container_outer.setObjectName("input_container")
        barcode_container_outer.setStyleSheet("""
            QWidget#input_container {
                background-color: #F8F9FA;
                border: none;
                border-radius: 37px;
            }
        """)
        barcode_inner_lyt = QHBoxLayout(barcode_container_outer)
        barcode_inner_lyt.setContentsMargins(30, 0, 30, 0)
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("바코드를 스캔하세요")
        self.barcode_input.setStyleSheet(styles.WELCOME_INPUT_STYLE + "background: transparent; color: #333; font-size: 20pt;")
        self.barcode_input.returnPressed.connect(self.on_barcode_return)
        self.barcode_input.textChanged.connect(self.on_barcode_text_changed)
        barcode_inner_lyt.addWidget(self.barcode_input)
        barcode_icon = QLabel("| [||||]|")
        barcode_icon.setStyleSheet("font-size: 20pt; color: #7F8C8D; background: transparent;")
        barcode_inner_lyt.addWidget(barcode_icon)
        middle_row_layout.addWidget(barcode_container_outer)

        # Mascot Icon (Right of Barcode) - Full-body
        if os.path.exists(mascot_img):
            self.mascot_label = QLabel()
            mascot_pix = QPixmap(mascot_img).scaled(280, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.mascot_label.setPixmap(mascot_pix)
            self.mascot_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.mascot_label.setFixedSize(280, 280)
            # No spacing between barcode and mascot for "immediately right"
            middle_row_layout.addWidget(self.mascot_label)

        middle_row_layout.addStretch()
        header_layout.addWidget(middle_row)
        header_layout.addSpacing(30) # Bottom padding as requested

        # Stats Card
        stats_widget = QFrame(header_frame)
        stats_widget.setFixedSize(260, 160)
        stats_widget.setStyleSheet("""
            QFrame {
                background: rgba(248, 249, 250, 0.95); 
                border: none; 
                border-radius: 12px;
            }
        """)
        s_lyt = QVBoxLayout(stats_widget)
        s_lyt.setContentsMargins(15, 12, 15, 12)
        s_lyt.setSpacing(6)
        lbl_s_title = QLabel("지금 포스에서는")
        lbl_s_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_s_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #34495E; background: transparent;")
        s_lyt.addWidget(lbl_s_title)
        
        def add_stat(label, value):
            h = QHBoxLayout()
            lbl_l = QLabel(label)
            lbl_l.setStyleSheet("font-size: 10pt; color: #5D6D7E; background: transparent;")
            h.addWidget(lbl_l)
            h.addStretch()
            v = QLabel(value)
            v.setStyleSheet("font-size: 10pt; color: #9162C0; font-weight: bold; background: transparent; text-decoration: underline;")
            h.addWidget(v)
            s_lyt.addLayout(h)
            
        add_stat("환불 :", "0건")
        add_stat("전체취소 :", "0건")
        add_stat("등록취소 :", "0건")
        
        lbl_occ = QLabel("발생하였습니다.")
        lbl_occ.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_occ.setStyleSheet("font-size: 10pt; font-weight: bold; color: #34495E; background: transparent;")
        s_lyt.addWidget(lbl_occ)
        
        self.stats_widget = stats_widget
        
        main_layout.addWidget(header_frame)

        # 2. Main Body Dashboard
        body_container = QWidget()
        body_layout = QHBoxLayout(body_container)
        body_layout.setContentsMargins(15, 15, 15, 15)
        body_layout.setSpacing(15)

        # --- Dashboard LEFT: Inquiry & Service (Side-by-side) ---
        dashboard_left_frame = QFrame()
        dashboard_left_frame.setStyleSheet("background-color: #2D2F3A; border-radius: 12px;")
        group_layout = QHBoxLayout(dashboard_left_frame)
        group_layout.setContentsMargins(15, 15, 15, 15)
        group_layout.setSpacing(15)

        def create_group_box(title, color, items):
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            # Header Button-style label
            hdr = QPushButton(title)
            hdr.setFixedHeight(110)
            hdr.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    font-size: 24pt;
                    border-radius: 12px;
                    border: none;
                }}
            """)
            layout.addWidget(hdr)

            # Grid for sub-items
            grid = QGridLayout()
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setSpacing(8)
            
            for i, text in enumerate(items):
                btn = QPushButton()
                btn_layout = QVBoxLayout(btn)
                btn_layout.setContentsMargins(0, 0, 0, 10)
                btn_layout.setSpacing(0)
                
                # Top Accent Bar
                accent = QFrame()
                accent.setFixedHeight(8)
                accent.setStyleSheet(f"background-color: {color}; border-top-left-radius: 6px; border-top-right-radius: 6px;")
                btn_layout.addWidget(accent)
                
                btn_layout.addStretch()
                
                # Text Label
                lbl = QLabel(text)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: white; font-weight: bold; font-size: 13pt; background: transparent;")
                lbl.setWordWrap(True)
                btn_layout.addWidget(lbl)
                
                btn_layout.addStretch()
                
                # Bottom Icon (Circle with dot/arrow)
                icon_lbl = QLabel("▼") # Using a simple character for the icon as per visual
                icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon_lbl.setFixedSize(20, 20)
                icon_lbl.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; font-size: 8pt; margin-bottom: 5px;")
                btn_layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)

                btn.setFixedHeight(140)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #3F414E;
                        border-radius: 8px;
                        border: none;
                    }}
                    QPushButton:pressed {{
                        background-color: #2D2F3A;
                    }}
                """)
                
                if text == "영수증조회":
                    btn.clicked.connect(self.receiptInquiryRequested.emit)
                elif text == "교통카드잔액조회":
                    # Potentially add logic if needed, but for now just UI
                    pass
                
                grid.addWidget(btn, i // 2, i % 2)
            
            layout.addLayout(grid)
            return container

        inquiry_box = create_group_box("통합조회", "#7AB800", ["상품조회", "영수증조회", "수표조회", "교통카드잔액조회"])
        # Connect 영수증조회 button (it's the 2nd button in the items list)
        # items are ["상품조회", "영수증조회", "수표조회", "교통카드잔액조회"]
        # In create_group_box, buttons are added to a grid. We need to find the right button.
        # Let's modify create_group_box to handle clicks if needed or find it manually.
        service_box = create_group_box("서비스", "#8A79B6", ["교통카드", "택배", "프리페이드", "공공요금"])
        
        group_layout.addWidget(inquiry_box)
        group_layout.addWidget(service_box)
        body_layout.addWidget(dashboard_left_frame, stretch=6)

        # --- Dashboard CENTER: Payment & Safe & History ---
        center_col_frame = QFrame()
        center_col_frame.setStyleSheet("background-color: #2D2F3A; border-radius: 12px;")
        center_col = QVBoxLayout(center_col_frame)
        center_col.setContentsMargins(10, 10, 10, 10)
        center_col.setSpacing(10)

        # Top row: Payment & Safe (Side-by-side)
        pay_safe_row = QHBoxLayout()
        pay_safe_row.setSpacing(10)

        btn_disc_top = QPushButton("결제 후\n할인 · 현금영수증")
        btn_disc_top.setFixedHeight(160)
        btn_disc_top.setStyleSheet("background: #ECEFF1; border: none; border-radius: 8px; font-weight: bold; font-size: 15pt; color: #333;")
        
        safe_frame = QFrame()
        safe_frame.setFixedHeight(160)
        safe_frame.setStyleSheet("background: #ECEFF1; border: none; border-radius: 8px;")
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
        hist_box.setFixedHeight(210) # Reduced from 240
        hist_box.setStyleSheet("background: white; border: none; border-radius: 8px;")
        hist_lyt = QVBoxLayout(hist_box)
        hist_lyt.setContentsMargins(30, 15, 30, 15) # Adjusted vertical margin
        hist_lyt.setSpacing(10) # Reduced spacing to fit larger fonts
        
        h_title_lyt = QHBoxLayout()
        lbl_h_title = QLabel("직전결제내역")
        lbl_h_title.setStyleSheet("font-weight: bold; font-size: 20pt; color: #333;")
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
            lbl.setStyleSheet("font-size: 16pt; color: #555;")
            h_row.addWidget(lbl)
            h_row.addStretch()
            v = QLabel(val)
            f_bold = "font-weight: bold;" if bold else ""
            color = "#333" if not bold else "#D32F2F" if "거스름돈" not in label else "#333"
            v.setStyleSheet(f"font-size: 22pt; {f_bold} color: {color};")
            h_row.addWidget(v)
            hist_lyt.addLayout(h_row)
            return v
            
        self.lbl_hist_total = add_hist_row("총 구매액", "0 원", True)
        self.lbl_hist_paid = add_hist_row("결제한 금액", "0 원", True)
        self.lbl_hist_change = add_hist_row("거스름돈", "0 원")
        
        center_col.addWidget(hist_box) # Removed stretch to respect fixed height
        body_layout.addWidget(center_col_frame, stretch=3)

        # --- Dashboard RIGHT: Wait & Refund (Wait above, Refund below) ---
        right_col_frame = QFrame()
        right_col_frame.setStyleSheet("background-color: #2D2F3A; border-radius: 12px;")
        right_col = QVBoxLayout(right_col_frame)
        right_col.setContentsMargins(10, 10, 10, 10)
        right_col.setSpacing(10)
        
        wait_stack = QVBoxLayout()
        wait_stack.setSpacing(8)
        self.wait_buttons = []
        for i in range(1, 4):
            btn_wait = QPushButton(f"대기{i}")
            btn_wait.setFixedHeight(75) # Increased from 50
            btn_wait.setStyleSheet(styles.WELCOME_SMALL_BUTTON)
            btn_wait.clicked.connect(lambda checked, idx=i-1: self.waitRequested.emit(idx))
            wait_stack.addWidget(btn_wait)
            self.wait_buttons.append(btn_wait)
        right_col.addLayout(wait_stack)
        
        btn_refund = QPushButton("환불")
        btn_refund.setFixedHeight(180) # Increased from 120
        btn_refund.setStyleSheet("background: #EF5350; color: white; font-weight: bold; font-size: 24pt; border-radius: 8px;")
        btn_refund.clicked.connect(self.refundRequested.emit)
        right_col.addWidget(btn_refund)
        
        body_layout.addWidget(right_col_frame, stretch=1)

        main_layout.addWidget(body_container, stretch=1)

        # 3. Bottom Quick Items & Categories
        bottom_widget = QWidget()
        bottom_lyt = QVBoxLayout(bottom_widget)
        bottom_lyt.setContentsMargins(10, 0, 10, 10)
        
        # Quick items
        q_row = QHBoxLayout()
        q_row.setSpacing(5)
        q_items = [
            ("친환경)CU백색봉투대\n100", "8801000000003"), 
            ("아이시스2L P6입\n3,600", "8801000000004"), 
            ("유앤)포켓몬볼모양젤\n1,000", "8801000000005"), 
            ("츄파춥스12g\n300", "8801000000006"), 
            ("트롤리지구젤리(낱개)\n1,000", "8801000000007")
        ]
        
        for name, barcode in q_items:
            # Need to get current price for these but let's use placeholders as per image
            f = QFrame()
            f.setFixedHeight(65)
            f.setObjectName("quick_item")
            f.setStyleSheet(styles.WELCOME_QUICK_ITEM_FRAME)
            l = QVBoxLayout(f)
            l.setContentsMargins(5, 5, 5, 5)
            l.setSpacing(0)
            
            n_parts = name.split("\n")
            it_name = QLabel(n_parts[0])
            it_name.setStyleSheet(styles.WELCOME_ITEM_NAME_LABEL)
            it_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            it_price = QLabel(n_parts[1] if len(n_parts) > 1 else "0")
            it_price.setStyleSheet(styles.WELCOME_PRICE_LABEL)
            it_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            l.addWidget(it_name)
            l.addWidget(it_price)
            q_row.addWidget(f, stretch=1)
            
        bottom_lyt.addLayout(q_row)
        
        # Category Tabs
        cat_row = QHBoxLayout()
        cat_row.setSpacing(2)
        btn_l_arr = QPushButton("<")
        btn_l_arr.setFixedSize(40, 50)
        btn_l_arr.setStyleSheet("background: white; border: none;")
        cat_row.addWidget(btn_l_arr)
        
        cats = [("일반상품", "#7AB800"), ("소분상품", "#6C757D"), ("신문/상품권", "#6C757D"), ("쓰레기봉투/화장", "#6C757D"), ("점포등록", "#6C757D"), ("상품관리", "#6C757D")]
        for n, c in cats:
            b = QPushButton(n)
            b.setFixedHeight(50)
            b.setStyleSheet(f"background: white; color: #333; font-weight: bold; border: none; border-top: 4px solid {c};")
            if n == "상품관리":
                b.clicked.connect(self.settingsRequested.emit)
            elif n == "점포등록":
                b.clicked.connect(self.storeRegistrationRequested.emit)
            cat_row.addWidget(b, stretch=1)
            
        btn_r_arr = QPushButton(">")
        btn_r_arr.setFixedSize(40, 50)
        btn_r_arr.setStyleSheet("background: white; border: none;")
        cat_row.addWidget(btn_r_arr)
        
        bottom_lyt.addLayout(cat_row)
        
        main_layout.addWidget(bottom_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # 1. Position Stats Widget (Top Right Overlay)
        if hasattr(self, 'stats_widget') and self.stats_widget:
            self.stats_widget.move(self.width() - 280, 60) # Moved up from 80
            
        # 2. Position Top Buttons Container
        if hasattr(self, 'top_btn_container') and self.top_btn_container:
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
        if len(text) >= 13:
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

    def update_wait_status(self, wait_slots):
        for i, slot in enumerate(wait_slots):
            if i < len(self.wait_buttons):
                if slot is not None:
                    # Green background for occupied slot
                    self.wait_buttons[i].setStyleSheet(
                        styles.WELCOME_SMALL_BUTTON.replace("background-color: #AAB3BF;", "background-color: #7AB800; color: white;")
                    )
                else:
                    # Original style for empty slot
                    self.wait_buttons[i].setStyleSheet(styles.WELCOME_SMALL_BUTTON)

    def showEvent(self, event):
        super().showEvent(event)
        self.barcode_input.setFocus()
