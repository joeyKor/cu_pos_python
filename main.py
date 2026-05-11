import sys, random, datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLabel, QLineEdit, QGridLayout, QFrame, QAbstractItemView, 
                             QPushButton, QStackedWidget, QInputDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

import styles
from ui_components import (ActionButton, StatusLabel, SummaryFrame, EditItemDialog, 
                               CustomMessageDialog, SafeBalanceEditDialog, ReceiptPreviewDialog, StoreRegistrationDialog)
from product_manager import ProductManager
from settings_page import SettingsPage
from payment_ui import CreditCardPaymentDialog, CashPaymentDialog, CashReceiptDialog
from welcome_page import WelcomePage
from refund_page import RefundPage
from receipt_inquiry_page import ReceiptInquiryPage
from transaction_manager import TransactionManager
from receipt_manager import ReceiptManager
from post_payment_page import PostPaymentPage, PostPaymentOptionDialog

class POSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DU Retail POS System")
        
        # 1. Detect Screen Resolution and set SCALE_FACTOR
        # Standard height 768 is our baseline (1.0)
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.availableGeometry()
            actual_height = screen_geom.height()
            # If height is less than 760, we scale down (e.g. 720/768 = 0.93)
            # You can also use a fixed 0.7 if the user explicitly wants 30% smaller
            # Here let's auto-scale if below 768, otherwise stay at 1.0 or use user preference
            if actual_height < 768:
                styles.SCALE_FACTOR = actual_height / 768.0
            else:
                styles.SCALE_FACTOR = 1.0
                
            # Reload styles to apply new SCALE_FACTOR
            styles.reload_styles()
                
        self.setGeometry(100, 100, styles.s(1024), styles.s(768)) # Standard POS resolution
        
        # Initialize Product Manager and Transaction Manager
        self.product_manager = ProductManager()
        self.transaction_manager = TransactionManager()
        self.receipt_manager = ReceiptManager()
        
        self.tm = self.transaction_manager
        self.rm = self.receipt_manager
        self.wait_slots = [None, None, None]
        self.current_wait_index = -1
        self.total_paid = 0
        self.payments = []
        
        self.init_ui()

        # Apply Styles
        self.setStyleSheet(styles.MAIN_WINDOW_STYLE)

    def init_ui(self):
        self.cart = [] # List of {"barcode": str, "qty": int}
        
        # Main Stacked Widget
        self.central_stack = QStackedWidget()
        
        # Wrap the stack in a Scroll Area for low resolution support
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.central_stack)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        self.setCentralWidget(scroll_area)
        
        # 0. Welcome Page (Start Screen)
        self.welcome_page = WelcomePage()
        self.welcome_page.barcodeScanned.connect(self.switch_to_sales_and_add)
        self.welcome_page.settingsRequested.connect(self.open_settings)
        self.welcome_page.safeBalanceEditRequested.connect(self.handle_safe_balance_edit)
        self.welcome_page.storeRegistrationRequested.connect(self.handle_store_registration)
        self.welcome_page.lastReceiptPrintRequested.connect(self.handle_welcome_receipt_print)
        self.welcome_page.refundRequested.connect(lambda: self.switch_page(2))
        self.welcome_page.receiptInquiryRequested.connect(lambda: self.switch_page(3))
        self.welcome_page.waitRequested.connect(self.handle_restore_wait)
        self.welcome_page.postPaymentRequested.connect(lambda: self.switch_page(5))
        self.central_stack.addWidget(self.welcome_page)
        
        # Load last transaction for welcome page
        self.update_welcome_history()
        
        # 1. Sales Page (Current POS UI)
        self.sales_widget = QWidget()
        self.setup_sales_ui()
        self.central_stack.addWidget(self.sales_widget)

        # 2. Refund Page
        self.refund_page = RefundPage()
        self.refund_page.backRequested.connect(lambda: self.switch_page(0))
        self.refund_page.receiptInquiryRequested.connect(lambda: self.switch_page(3))
        self.refund_page.barcodeScanned.connect(self.handle_refund_barcode)
        self.central_stack.addWidget(self.refund_page)

        # 3. Receipt Inquiry Page
        self.receipt_inquiry_page = ReceiptInquiryPage(self.transaction_manager, self.receipt_manager)
        self.receipt_inquiry_page.backRequested.connect(self.handle_inquiry_back)
        self.central_stack.addWidget(self.receipt_inquiry_page)

        # 4. Settings (Product Management) Page
        self.settings_page = SettingsPage(self.product_manager, self.receipt_manager)
        self.settings_page.backRequested.connect(self.handle_inquiry_back)
        self.central_stack.addWidget(self.settings_page)
        
        # 5. Post Payment Page
        self.post_payment_page = PostPaymentPage()
        self.post_payment_page.backRequested.connect(lambda: self.switch_page(0))
        self.post_payment_page.previousTransactionRequested.connect(self.handle_post_prev_tx)
        self.post_payment_page.barcodeScanned.connect(self.handle_post_barcode)
        self.central_stack.addWidget(self.post_payment_page)
        
        # Start at Welcome Page
        self.central_stack.setCurrentIndex(0)
        self.page_history = [0]

    def setup_sales_ui(self):
        main_layout = QVBoxLayout(self.sales_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Top Header
        main_layout.addWidget(self.create_header_frame()) # Use the frame returned by the new method

        # 2. Middle Section (Split Left and Right)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)
        middle_layout.setContentsMargins(10, 10, 10, 10)
        
        middle_layout.addLayout(self.create_left_panel(), stretch=70)
        middle_layout.addLayout(self.create_right_panel(), stretch=30)
        
        main_layout.addLayout(middle_layout, stretch=1) # Stretch to fill space

        # 3. Bottom Quick Menu
        main_layout.addWidget(self.create_bottom_panel_frame())
        
        # Initialize Table
        self.populate_table()

        # Keyboard search focus timer
        self.focus_timer = QTimer(self)
        self.focus_timer.setInterval(500)
        self.focus_timer.timeout.connect(self.ensure_barcode_focus)
        self.focus_timer.start()

    def switch_to_sales_and_add(self, barcode):
        # Switch to sales page
        self.central_stack.setCurrentIndex(1)
        # Process the barcode
        self.input_barcode.setText(barcode)
        self.handle_barcode_input()
        # Ensure focus is on the sales page barcode input
        self.input_barcode.setFocus()

    def go_to_home(self):
        self.clear_cart()
        self.reset_wait_state()
        self.update_welcome_history()
        # Return to Welcome Page
        self.central_stack.setCurrentIndex(0)

    def reset_wait_state(self):
        self.current_wait_index = -1
        if hasattr(self, 'btn_wait'):
            self.btn_wait.setText("대기")

    def ensure_barcode_focus(self):
        current_index = self.central_stack.currentIndex()
        if current_index == 1: # Sales Page
            if not self.input_barcode.hasFocus():
                self.input_barcode.setFocus()
        elif current_index == 0: # Welcome Page
            if hasattr(self, 'welcome_page') and not self.welcome_page.barcode_input.hasFocus():
                self.welcome_page.barcode_input.setFocus()
        elif current_index == 2: # Refund Page
            if hasattr(self, 'refund_page') and not self.refund_page.barcode_input.hasFocus():
                self.refund_page.barcode_input.setFocus()

    def switch_page(self, index):
        self.page_history.append(index)
        self.central_stack.setCurrentIndex(index)

    def handle_inquiry_back(self):
        if len(self.page_history) > 1:
            self.page_history.pop() # Remove current page
            prev_index = self.page_history.pop() # Get previous page
            self.switch_page(prev_index)
        else:
            self.switch_page(0)

    def create_header_frame(self):
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {styles.WHITE}; border: none;")
        layout = QHBoxLayout(header_frame)
        
        # Home Button
        btn_home = QPushButton("🏠 홈 (Home)")
        btn_home.setStyleSheet(styles.BUTTON_PURPLE_STYLE)
        btn_home.setFixedHeight(styles.s(50))
        btn_home.clicked.connect(self.go_to_home)
        layout.addWidget(btn_home)

        label = QLabel("상품을 스캔해 주세요. 상품등록 완료시 [결제선택] 버튼을 누르세요.")
        label.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-family: '{styles.FONT_FAMILY}'; font-weight: bold; color: {styles.TEXT_COLOR};")
        
        layout.addWidget(label)
        layout.addStretch()
        
        # Settings Button
        btn_settings = QPushButton("상품관리")
        btn_settings.setStyleSheet(styles.BUTTON_BOTTOM_STYLE)
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.clicked.connect(self.open_settings)
        
        # Exit Button
        btn_exit = QPushButton("종료")
        btn_exit.setStyleSheet(styles.BUTTON_BOTTOM_STYLE.replace("white", "#FFEBEE").replace(styles.TEXT_COLOR, "#D32F2F")) 
        btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exit.clicked.connect(self.close)
        
        layout.addWidget(btn_settings)
        layout.addWidget(btn_exit)
        
        return header_frame

    def create_left_panel(self):
        # Outer Layout for Table + Footer + Scroll Buttons
        main_table_layout = QHBoxLayout()
        main_table_layout.setSpacing(0)
        
        # Left side: Table + Footer
        table_footer_column = QVBoxLayout()
        table_footer_column.setSpacing(0)

        # Product Table
        self.table = QTableWidget()
        self.table.setMinimumHeight(400) # Minimum height instead of fixed
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["NO", "상품명", "수량", "단가", "금액", "할인"])
        self.table.setStyleSheet(styles.TABLE_STYLE + styles.SCROLLBAR_STYLE)
        self.table.verticalScrollBar().setFixedWidth(0) # Hide the actual bar but keep logic
        
        # Table Header Config
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setMinimumHeight(styles.s(60))
        self.table.setColumnWidth(0, styles.s(60))   # NO
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Product Name stretches
        self.table.setColumnWidth(2, styles.s(100))  # Qty
        self.table.setColumnWidth(3, styles.s(180))  # Unit Price
        self.table.setColumnWidth(4, styles.s(180))  # Amount
        self.table.setColumnWidth(5, styles.s(120))  # Discount
        
        # Remove grid lines/Selection behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(styles.s(80)) # Ensure row is tall enough for padding
        self.table.setShowGrid(False)  # Match clean look
        
        # Connect Click Event
        self.table.cellClicked.connect(self.open_edit_dialog)
        
        table_footer_column.addWidget(self.table)
        
        # === Table Footer (Totals Row) ===
        footer_frame = QFrame()
        footer_frame.setFixedHeight(styles.s(50))
        footer_frame.setStyleSheet("background-color: #D1D5DB; border-top: 1px solid #99A1AC;")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(0)
        
        lbl_foot_title_box = QLabel("합계")
        lbl_foot_title_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_foot_title_box.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #333;")
        footer_layout.addWidget(lbl_foot_title_box, stretch=1) # NO + Product Name
        
        self.lbl_foot_qty = QLabel("0")
        self.lbl_foot_qty.setFixedWidth(styles.s(100))
        self.lbl_foot_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_foot_qty.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #333;")
        footer_layout.addWidget(self.lbl_foot_qty)
        
        self.lbl_foot_price = QLabel("") # Unit price sum usually not shown or 0
        self.lbl_foot_price.setFixedWidth(styles.s(180))
        self.lbl_foot_price.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_foot_price.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #333; padding-right: {styles.s(15)}px;")
        footer_layout.addWidget(self.lbl_foot_price)
        
        self.lbl_foot_amt = QLabel("0")
        self.lbl_foot_amt.setFixedWidth(styles.s(180))
        self.lbl_foot_amt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_foot_amt.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #333; padding-right: {styles.s(15)}px;")
        footer_layout.addWidget(self.lbl_foot_amt)
        
        self.lbl_foot_disc = QLabel("0")
        self.lbl_foot_disc.setFixedWidth(styles.s(120))
        self.lbl_foot_disc.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_foot_disc.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #D32F2F; padding-right: {styles.s(15)}px;")
        footer_layout.addWidget(self.lbl_foot_disc)
        
        table_footer_column.addWidget(footer_frame)
        
        main_table_layout.addLayout(table_footer_column)
        
        # Custom Scroll Button Panel
        scroll_panel = QVBoxLayout()
        scroll_panel.setSpacing(1)
        
        btn_top = QPushButton("⏫")
        btn_up = QPushButton("🔼")
        btn_down = QPushButton("🔽")
        btn_bottom = QPushButton("⏬")
        
        for btn in [btn_top, btn_up, btn_down, btn_bottom]:
            btn.setFixedWidth(styles.s(60)) 
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            btn.setStyleSheet(styles.WELCOME_SCROLL_BUTTON_STYLE)
            scroll_panel.addWidget(btn)
        
        btn_top.clicked.connect(lambda: self.table.verticalScrollBar().setValue(0))
        btn_up.clicked.connect(lambda: self.table.verticalScrollBar().setValue(self.table.verticalScrollBar().value() - 30))
        btn_down.clicked.connect(lambda: self.table.verticalScrollBar().setValue(self.table.verticalScrollBar().value() + 30))
        btn_bottom.clicked.connect(lambda: self.table.verticalScrollBar().setValue(self.table.verticalScrollBar().maximum()))
        
        main_table_layout.addLayout(scroll_panel)
        
        left_layout = QVBoxLayout() # The final panel layout
        left_layout.addLayout(main_table_layout)
        
        # Total Summary & Input Area
        summary_widget = QWidget()
        summary_widget.setStyleSheet(styles.SUMMARY_CONTAINER_STYLE)
        summary_widget.setMaximumHeight(styles.s(250)) # Further increased to reduce list view dominance
        summary_layout = QHBoxLayout(summary_widget)
        summary_layout.setContentsMargins(20, 25, 20, 50) # Increased bottom padding specifically
        summary_layout.setSpacing(15)
        
        # --- Left Side: Barcode Input ---
        barcode_container = QVBoxLayout()
        barcode_container.setContentsMargins(0, 0, 0, 0)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("상품의 바코드를 스캔하세요...")
        self.input_barcode.setStyleSheet(styles.BARCODE_INPUT_STYLE)
        self.input_barcode.setFixedHeight(styles.s(60)) # Slightly shorter input
        self.input_barcode.returnPressed.connect(self.handle_barcode_input)
        self.input_barcode.textChanged.connect(self.on_barcode_text_changed)
        
        barcode_container.addStretch()
        barcode_container.addWidget(self.input_barcode)
        barcode_container.addStretch()
        
        summary_layout.addLayout(barcode_container, stretch=3)
        
        # v_divider removed
        
        # --- Right Side: Payment Info ---
        pay_info_group = QWidget()
        # Wrapper to allow centering it if needed, but we keep it tightly grouped
        pay_info_vbox = QVBoxLayout(pay_info_group)
        pay_info_vbox.setContentsMargins(0, 0, 0, 0)
        pay_info_vbox.setSpacing(0)
        
        pay_info_layout = QGridLayout()
        pay_info_layout.setContentsMargins(10, 0, 0, 0)
        pay_info_layout.setSpacing(5) # Reduced spacing
        pay_info_layout.setVerticalSpacing(styles.s(8)) # Increased for better readability
        
        # Row 0: 받을 금액 (Red Highlight)
        lbl_receive_title = QLabel("받을 금액")
        lbl_receive_title.setStyleSheet(styles.SUMMARY_LABEL_STYLE)
        
        self.lbl_final_price = QLabel("0")
        self.lbl_final_price.setStyleSheet(styles.SUMMARY_TOTAL_RED)
        
        lbl_unit_1 = QLabel("원")
        lbl_unit_1.setStyleSheet(styles.SUMMARY_UNIT)
        lbl_unit_1.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        pay_info_layout.addWidget(lbl_receive_title, 0, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pay_info_layout.addWidget(self.lbl_final_price, 0, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pay_info_layout.addWidget(lbl_unit_1, 0, 2, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Row 1: 결제한 금액
        lbl_paid_title = QLabel("결제한 금액")
        lbl_paid_title.setStyleSheet(styles.SUMMARY_LABEL_STYLE)
        
        self.lbl_received_amount = QLabel("0") 
        self.lbl_received_amount.setStyleSheet(styles.SUMMARY_TOTAL_DARK)
        
        lbl_unit_2 = QLabel("원")
        lbl_unit_2.setStyleSheet(styles.SUMMARY_UNIT)
        lbl_unit_2.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        pay_info_layout.addWidget(lbl_paid_title, 1, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pay_info_layout.addWidget(self.lbl_received_amount, 1, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pay_info_layout.addWidget(lbl_unit_2, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Row 2: 거스름돈
        lbl_change_title = QLabel("거스름돈")
        lbl_change_title.setStyleSheet(styles.SUMMARY_LABEL_STYLE)
        
        self.lbl_change_amount = QLabel("0")
        self.lbl_change_amount.setStyleSheet(styles.SUMMARY_TOTAL_DARK)
        
        lbl_unit_3 = QLabel("원")
        lbl_unit_3.setStyleSheet(styles.SUMMARY_UNIT)
        lbl_unit_3.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        pay_info_layout.addWidget(lbl_change_title, 2, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pay_info_layout.addWidget(self.lbl_change_amount, 2, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pay_info_layout.addWidget(lbl_unit_3, 2, 2, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        pay_info_vbox.addLayout(pay_info_layout)
        
        summary_layout.addWidget(pay_info_group, stretch=4)
        
        left_layout.addLayout(main_table_layout, stretch=1) # Give table space priority
        left_layout.addWidget(summary_widget)
        
        return left_layout

    def create_right_panel(self):
        right_layout = QVBoxLayout()
        right_layout.setSpacing(2)

        # Buttons
        button_min_height = styles.s(80) # Smaller minimum height to allow shrinking
        
        btn_affiliate = ActionButton("제휴 할인 및\n포인트 적립/사용", styles.BUTTON_GREEN_STYLE, "ⓟ")
        btn_affiliate.setMinimumHeight(button_min_height)
        
        btn_coupon = ActionButton("DU키핑쿠폰 발급", styles.BUTTON_GREEN_STYLE, "🎫")
        btn_coupon.setMinimumHeight(button_min_height)
        
        btn_card = ActionButton("신용카드", styles.BUTTON_PURPLE_STYLE, "💳")
        btn_card.setMinimumHeight(button_min_height)
        btn_card.clicked.connect(self.open_card_payment)
        
        btn_cash = ActionButton("현금", styles.BUTTON_PURPLE_STYLE, "💰")
        btn_cash.setMinimumHeight(button_min_height)
        btn_cash.clicked.connect(self.open_cash_payment)
        
        btn_mobile_pay = ActionButton("모바일\n(DU머니 번호결제)", styles.BUTTON_PURPLE_STYLE, "📱")
        btn_mobile_pay.setMinimumHeight(button_min_height)
        
        btn_pay_select = ActionButton("결제선택", styles.BUTTON_GREEN_STYLE, "👛")
        btn_pay_select.setMinimumHeight(button_min_height)

        # Store references for multi-payment
        self.btn_card = btn_card
        self.btn_cash = btn_cash
        self.btn_mobile_pay = btn_mobile_pay
        
        # Split Cancel/Wait
        split_btns = QHBoxLayout()
        btn_cancel = ActionButton("전체취소", styles.BUTTON_RED_STYLE)
        btn_cancel.setMinimumHeight(button_min_height)
        btn_cancel.clicked.connect(self.clear_cart)
        
        btn_wait = ActionButton("대기", styles.BUTTON_PURPLE_STYLE.replace(styles.PRIMARY_PURPLE, "#78909C")) # Grayish
        btn_wait.setMinimumHeight(button_min_height)
        btn_wait.clicked.connect(self.handle_wait_click)
        self.btn_wait = btn_wait
        split_btns.addWidget(btn_cancel)
        split_btns.addWidget(btn_wait)
        right_layout.addWidget(btn_affiliate)
        right_layout.addWidget(btn_coupon)
        right_layout.addWidget(btn_card)
        right_layout.addWidget(btn_cash)
        right_layout.addWidget(btn_mobile_pay)
        right_layout.addWidget(btn_pay_select)
        right_layout.addLayout(split_btns)
        
        return right_layout

    def create_bottom_panel_frame(self):
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(styles.s(60))
        bottom_frame.setStyleSheet(f"background-color: #EEEEEE; border: none;")
        layout = QHBoxLayout(bottom_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        buttons = [
            ("검수/폐기", styles.BUTTON_BOTTOM_STYLE),
            ("수표조회", styles.BUTTON_BOTTOM_STYLE),
            ("영수증조회", styles.BUTTON_BOTTOM_STYLE),
            ("상품조회", styles.BUTTON_BOTTOM_STYLE),
            ("판매보류/해제", styles.BUTTON_BOTTOM_STYLE),
            ("서비스", styles.BUTTON_BOTTOM_STYLE),
            ("통합조회", styles.BUTTON_BOTTOM_STYLE),
            ("도움말", styles.BUTTON_BOTTOM_STYLE)
        ]
        
        for text, style in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(style)
            btn.setFixedHeight(styles.s(40))
            layout.addWidget(btn)
            
        return bottom_frame

    def create_bottom_panel(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(2)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        
        container = QFrame()
        container.setStyleSheet(f"background-color: {styles.WHITE}; border: none;")
        grid = QGridLayout(container)
        grid.setSpacing(2)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Row 1: Common Items (Shortcuts)
        # Using some predefined barcodes for these buttons
        common_items = [
            ("친환경)DU백색봉투대\n100", "8801000000003"), 
            ("아이시스2L P6입\n3,600", "8801000000004"), 
            ("유앤)포켓몬볼모양젤\n1,000", "8801000000005"), 
            ("츄파춥스12g\n300", "8801000000006"), 
            ("트롤리지구젤리(낱개)\n1,000", "8801000000007")
        ]
        for i, (item_text, barcode) in enumerate(common_items):
            btn = ActionButton(item_text, styles.BUTTON_BOTTOM_STYLE)
            btn.clicked.connect(lambda checked, b=barcode: self.add_product(b))
            grid.addWidget(btn, 0, i)
            
        # Row 2: Categories
        categories = ["일반상품", "소분상품", "신문/상품권", "쓰레기 봉투/화장", "GET 커피", "고구마"]
        for i, cat_text in enumerate(categories):
            btn = ActionButton(cat_text, styles.BUTTON_BOTTOM_STYLE)
            # Make category buttons darker
            btn.setStyleSheet(styles.BUTTON_BOTTOM_STYLE.replace("#E0E0E0", "#546E7A").replace(styles.TEXT_COLOR, "white"))
            grid.addWidget(btn, 1, i)
            
        self.main_layout.addWidget(container)

    def populate_table(self):
        # Initial empty state
        self.cart = [] # List of {"barcode": str, "qty": int}
        self.update_table_view()

    def on_barcode_text_changed(self, text):
        if len(text) >= 13:
            # Auto submit
            self.add_product(text.strip())
            self.input_barcode.clear()
            self.input_barcode.setFocus()

    def handle_barcode_input(self):
        barcode = self.input_barcode.text().strip()
        if barcode:
            self.add_product(barcode)
            self.input_barcode.clear()
            self.input_barcode.setFocus()
            
    def add_product(self, barcode):
        product = self.product_manager.get_product(barcode)
        if not product:
            # Show alert for product not found
            dialog = CustomMessageDialog("상품 없음", f"바코드[{barcode}]\n등록되지 않은 상품입니다.", 'warning', self)
            dialog.exec()
            # Clear input after alert
            self.input_barcode.clear()
            self.input_barcode.setFocus()
            return

        # Check if already in cart
        found = False
        for item in self.cart:
            if item["barcode"] == barcode:
                item["qty"] += 1
                found = True
                break
        
        if not found:
            self.cart.append({"barcode": barcode, "qty": 1})
            
        self.update_table_view()
        self.update_totals()

    def update_table_view(self):
        self.table.setRowCount(len(self.cart))
        
        for row, item in enumerate(self.cart):
            barcode = item["barcode"]
            product = self.product_manager.get_product(barcode)
            
            # No.
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            # Name
            self.table.setItem(row, 1, QTableWidgetItem(product["name"]))
            # Qty
            self.table.setItem(row, 2, QTableWidgetItem(str(item["qty"])))
            # Price
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['price']:,}"))
            # Amount
            amt = product['price'] * item['qty']
            self.table.setItem(row, 4, QTableWidgetItem(f"{amt:,}"))
            # Discount (0 for now)
            self.table.setItem(row, 5, QTableWidgetItem("0"))
            
            # Alignments
            for col in range(6):
                it = self.table.item(row, col)
                if col == 5: # Discount
                    it.setForeground(QColor("#D32F2F"))
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif col in [3, 4]:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                    
        self.table.scrollToBottom()

    def update_totals(self):
        total_qty = sum(item["qty"] for item in self.cart)
        total_amt = 0
        total_disc = 0
        for item in self.cart:
             product = self.product_manager.get_product(item["barcode"])
             if product:
                 total_amt += product["price"] * item["qty"]
        
        # Update Footer
        self.lbl_foot_qty.setText(str(total_qty))
        self.lbl_foot_amt.setText(f"{total_amt:,}")
        self.lbl_foot_disc.setText(f"{total_disc:,}")
        
        # Update Big Total (Payments Area)
        self.lbl_final_price.setText(f"{(total_amt - self.total_paid):,}")
        self.lbl_received_amount.setText(f"{self.total_paid:,}")
        self.lbl_change_amount.setText("0")
        
    def clear_cart(self):
        self.cart = []
        self.total_paid = 0
        self.payments = []
        self.reset_wait_state()
        self.update_table_view()
        self.update_totals()
        
        # Reset button icons
        if hasattr(self, 'btn_card'): self.btn_card.set_checked(False)
        if hasattr(self, 'btn_cash'): self.btn_cash.set_checked(False)
        if hasattr(self, 'btn_mobile_pay'): self.btn_mobile_pay.set_checked(False)
        
        self.input_barcode.setFocus()
        
    def open_edit_dialog(self, row, col):
        if row < 0 or row >= len(self.cart):
            return
            
        item_data = self.cart[row]
        barcode = item_data["barcode"]
        product = self.product_manager.get_product(barcode)
        
        dialog = EditItemDialog(product["name"], item_data["qty"], self)
        
        if dialog.exec():
            if dialog.delete_clicked:
                del self.cart[row]
            else:
                new_qty = dialog.get_new_qty()
                self.cart[row]["qty"] = new_qty
            
            self.update_table_view()
            self.update_totals()

    def generate_tx_barcode(self):
        # Format: YYMMDDHHMMSS + 4 random digits
        now = datetime.datetime.now()
        base = now.strftime("%y%m%d%H%M%S")
        rand = "".join([str(random.randint(0, 9)) for _ in range(4)])
        return base + rand

    def open_card_payment(self):
        # Calculate remaining total
        full_total = sum(self.product_manager.get_product(item["barcode"])["price"] * item["qty"] for item in self.cart)
        remaining = full_total - self.total_paid
        
        if full_total == 0:
            CustomMessageDialog("결제 불가", "결제할 상품이 없습니다.", 'warning', self).exec()
            return

        # Toggle off if already paid
        if hasattr(self, 'btn_card') and self.btn_card.is_checked:
            # Find and remove the card payment from list
            for i, p in enumerate(self.payments):
                if p["method"] == "Card":
                    self.total_paid -= p["amount"]
                    self.payments.pop(i)
                    break
            self.btn_card.set_checked(False)
            self.update_totals()
            return

        if remaining <= 0:
            CustomMessageDialog("알림", "이미 결제가 완료되었습니다.", 'info', self).exec()
            return
            
        dialog = CreditCardPaymentDialog(remaining, self)
        if dialog.exec():
            paid_now = dialog.get_payment_amount()
            self.total_paid += paid_now
            self.payments.append({
                "method": "Card",
                "amount": paid_now,
                "details": {"card_number": dialog.get_card_number()}
            })
            if hasattr(self, 'btn_card'): self.btn_card.set_checked(True)
            self.update_totals()
            
            # If fully paid, finalize
            if self.total_paid >= full_total:
                self.finalize_transaction()

    def open_cash_payment(self):
        # Calculate remaining total
        full_total = sum(self.product_manager.get_product(item["barcode"])["price"] * item["qty"] for item in self.cart)
        remaining = full_total - self.total_paid
        
        if full_total == 0:
            CustomMessageDialog("결제 불가", "결제할 상품이 없습니다.", 'warning', self).exec()
            return

        # Toggle off if already paid
        if hasattr(self, 'btn_cash') and self.btn_cash.is_checked:
            # Find and remove cash payment from list
            for i, p in enumerate(self.payments):
                if p["method"] == "Cash":
                    self.total_paid -= p["amount"]
                    self.payments.pop(i)
                    break
            self.btn_cash.set_checked(False)
            # Reset change label if it was showing
            self.lbl_change_amount.setText("0")
            self.update_totals()
            return

        if remaining <= 0:
            CustomMessageDialog("알림", "이미 결제가 완료되었습니다.", 'info', self).exec()
            return
            
        dialog = CashPaymentDialog(remaining, self)
        if dialog.exec():
            paid_now = dialog.received_amount
            
            # Use all cash up to remaining
            cash_applied = min(paid_now, remaining)
            change = max(0, paid_now - remaining)
            
            self.total_paid += cash_applied
            self.payments.append({
                "method": "Cash",
                "amount": cash_applied,
                "details": {"received_amt": paid_now, "change_amt": change}
            })
            if hasattr(self, 'btn_cash'): self.btn_cash.set_checked(True)
            self.update_totals()
            
            if change > 0:
                self.lbl_change_amount.setText(f"{change:,}")
            
            if self.total_paid >= full_total:
                # If fully paid, finalize
                self.finalize_transaction()

    def finalize_transaction(self):
        full_total = sum(self.product_manager.get_product(item["barcode"])["price"] * item["qty"] for item in self.cart)
        items_data = []
        for item in self.cart:
            prod = self.product_manager.get_product(item["barcode"])
            items_data.append({
                "name": prod["name"],
                "qty": item["qty"],
                "price": prod["price"]
            })
            
        tx_barcode = self.generate_tx_barcode()
        
        # Determine primary payment method for simple lookup, but store full list
        primary_method = self.payments[0]["method"] if self.payments else "Unknown"
        
        # Prepare transaction data for receipt generator
        tx_data = {
            "items": items_data,
            "total_amt": full_total,
            "payment_method": primary_method,
            "payments": self.payments, # Full list of all partial payments
            "tx_barcode": tx_barcode
        }
        
        self.transaction_manager.save_transaction(
            items=items_data,
            total_amt=full_total,
            payment_method=primary_method,
            payments=self.payments,
            tx_barcode=tx_barcode
        )
            
        # Update UI and show receipt
        self.update_welcome_history()
        
        receipt_html = self.receipt_manager.generate_html(tx_data)
        ReceiptPreviewDialog(receipt_html, self).exec()
        
        # Done
        self.clear_cart()
        self.go_to_home()
        CustomMessageDialog("결제 완료", f"총 {full_total:,}원 결제가 완료되었습니다.", 'info', self).exec()

    def update_welcome_history(self):
        last_tx = self.transaction_manager.get_last_transaction()
        self.welcome_page.update_last_transaction(last_tx)
        
        # Update Safe Balance
        base_safe_amt = self.transaction_manager.get_base_safe_amt()
        cash_total = self.transaction_manager.get_cash_total()
        self.welcome_page.update_safe_balance(base_safe_amt + cash_total)

    def handle_safe_balance_edit(self):
        current_total = self.transaction_manager.get_base_safe_amt() + self.transaction_manager.get_cash_total()
        
        dialog = SafeBalanceEditDialog(current_total, self)
        
        if dialog.exec():
            amount = dialog.get_amount()
            # New Base = New Total - Cash from transactions
            cash_total = self.transaction_manager.get_cash_total()
            new_base = amount - cash_total
            self.transaction_manager.set_base_safe_amt(new_base)
            self.update_welcome_history()
            
            CustomMessageDialog("수정 완료", f"금고 보관 금액이 {amount:,}원으로 수정되었습니다.", 'info', self).exec()

    def handle_store_registration(self):
        store_info = {
            "store_name": self.receipt_manager.store_name,
            "biz_num": self.receipt_manager.biz_num,
            "address": self.receipt_manager.address,
            "owner": self.receipt_manager.owner,
            "tel": self.receipt_manager.tel
        }
        
        dialog = StoreRegistrationDialog(store_info, self)
        if dialog.exec():
            new_info = dialog.get_store_info()
            self.receipt_manager.store_name = new_info["store_name"]
            self.receipt_manager.biz_num = new_info["biz_num"]
            self.receipt_manager.address = new_info["address"]
            self.receipt_manager.owner = new_info["owner"]
            self.receipt_manager.tel = new_info["tel"]
            
            self.receipt_manager.save_store_info()
            CustomMessageDialog("저장 완료", "점포 정보가 성공적으로 저장되었습니다.", 'info', self).exec()

    def handle_welcome_receipt_print(self):
        last_tx = self.transaction_manager.get_last_transaction()
        if not last_tx:
            CustomMessageDialog("출력 오류", "이전 결제 내역이 없습니다.", 'warning', self).exec()
            return
            
        receipt_html = self.receipt_manager.generate_html(last_tx)
        ReceiptPreviewDialog(receipt_html, self).exec()

    def open_settings(self):
        self.switch_page(4)
        # Refresh lists when entering
        self.settings_page.load_data()

    def handle_settings_back(self):
        self.handle_inquiry_back() # Reuse same history logic
        # Refresh the current sale view if any product details changed
        self.update_table_view()
        self.update_totals()

    def handle_refund_barcode(self, barcode):
        if len(barcode) != 16:
            return
            
        result = self.transaction_manager.mark_as_refunded(barcode)
        
        if result == "Success":
            CustomMessageDialog("환불 처리", "환불처리되었습니다.", 'info', self).exec()
            self.update_welcome_history()
        elif result == "AlreadyRefunded":
            CustomMessageDialog("알림", "이미 환불 처리된 영수증입니다.", 'warning', self).exec()
        elif result == "NotFound":
            CustomMessageDialog("조회 실패", "해당 바코드의 영수증을 찾을 수 없습니다.", 'warning', self).exec()
        else:
            CustomMessageDialog("오류", "환불 처리 중 오류가 발생했습니다.", 'warning', self).exec()

    def handle_wait_click(self):
        if not self.cart:
            CustomMessageDialog("알림", "대기 처리할 상품이 없습니다.", 'warning', self).exec()
            return

        # If it's a restored wait session, it acts as "Cancel"
        if self.current_wait_index != -1:
            self.clear_cart()
            # self.reset_wait_state() is called within clear_cart
            self.go_to_home()
            return

        # Find first empty slot
        idx = -1
        for i, slot in enumerate(self.wait_slots):
            if slot is None:
                idx = i
                break
        
        if idx == -1:
            CustomMessageDialog("알림", "더 이상 대기할 공간이 없습니다.", 'warning', self).exec()
            return
            
        # Store cart
        self.wait_slots[idx] = [item.copy() for item in self.cart]
        self.clear_cart()
        
        # Update Welcome Page UI
        self.welcome_page.update_wait_status(self.wait_slots)
        
        # Go to home
        self.go_to_home()
        CustomMessageDialog("알림", f"대기{idx+1}에 저장되었습니다.", 'info', self).exec()

    def handle_restore_wait(self, index):
        if self.wait_slots[index] is None:
            return
            
        if self.cart:
            CustomMessageDialog("알림", "현재 작업 중인 상품이 있습니다.\n먼저 처리하거나 취소해주세요.", 'warning', self).exec()
            return
            
        # Restore cart
        self.cart = self.wait_slots[index]
        self.wait_slots[index] = None
        self.current_wait_index = index
        self.btn_wait.setText("대기 취소")
        
        # Update Welcome Page UI
        self.welcome_page.update_wait_status(self.wait_slots)
        
        # Switch to Sales Page
        self.central_stack.setCurrentIndex(1)
        self.update_table_view()
        self.update_totals()

    def handle_post_prev_tx(self):
        # Logic for "직전거래" button on post-payment page
        last_tx = self.transaction_manager.get_last_transaction()
        if last_tx:
            dialog = PostPaymentOptionDialog(self)
            dialog.exec()
        else:
            CustomMessageDialog("알림", "직전 거래 내역이 없습니다.", 'warning', self).exec()

    def handle_post_barcode(self, barcode):
        # Logic for barcode scan on post-payment page
        tx = self.transaction_manager.get_transaction_by_barcode(barcode)
        if tx:
            dialog = PostPaymentOptionDialog(self)
            dialog.exec()
        else:
            CustomMessageDialog("조회 실패", f"바코드[{barcode}]에 해당하는 거래가 없습니다.", 'warning', self).exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Font
    font = app.font()
    font.setFamily(styles.FONT_FAMILY)
    app.setFont(font)
    
    window = POSMainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
