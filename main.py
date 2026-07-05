import sys, os, random, datetime, pyttsx3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLabel, QLineEdit, QGridLayout, QFrame, QAbstractItemView, 
                             QPushButton, QStackedWidget, QInputDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPixmap

import styles
from ui_components import (ActionButton, StatusLabel, SummaryFrame, EditItemDialog, 
                               CustomMessageDialog, SafeBalanceEditDialog, ReceiptPreviewDialog, StoreRegistrationDialog, PromotionDialog, VoucherExchangeDialog, KeepingLookupDialog, KeepingCouponIssueDialog, PromoAlertWithRelatedDialog)
from product_manager import ProductManager
from settings_page import SettingsPage
from payment_ui import CreditCardPaymentDialog, CashPaymentDialog, CashReceiptDialog, AffiliateDiscountDialog
from welcome_page import WelcomePage
from refund_page import RefundPage
from receipt_inquiry_page import ReceiptInquiryPage
from check_inquiry_page import CheckInquiryPage
from transit_card_page import TransitCardPage
from product_inquiry_page import ProductInquiryPage
from calculator_page import CalculatorPage
from change_accumulation_page import ChangeAccumulationPage
from parcel_service_page import ParcelServicePage
from transaction_manager import TransactionManager
from receipt_manager import ReceiptManager
from post_payment_page import PostPaymentPage, PostPaymentOptionDialog

# Globally monkey-patch QPushButton to play an asynchronous beep sound on click
import threading
import winsound
import time

last_beep_timestamp = 0
beep_lock = threading.Lock()

def play_beep_async(event_timestamp):
    global last_beep_timestamp
    if not getattr(styles, "BEEP_ENABLED", True):
        return
    with beep_lock:
        if event_timestamp - last_beep_timestamp < 250: # 250ms Cooldown
            return
        last_beep_timestamp = event_timestamp
        
    def beep():
        try:
            winsound.Beep(2000, 80)
        except Exception:
            pass
    threading.Thread(target=beep, daemon=True).start()

original_mousePressEvent = QPushButton.mousePressEvent
def patched_mousePressEvent(self, event):
    ts = getattr(event, "timestamp", None)
    if ts:
        event_timestamp = ts()
    else:
        event_timestamp = int(time.time() * 1000)
    play_beep_async(event_timestamp)
    original_mousePressEvent(self, event)
QPushButton.mousePressEvent = patched_mousePressEvent

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
        
        # Initialize TTS Queue and Background Thread
        import queue
        import threading
        self.tts_queue = queue.Queue()
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        
        self.tm = self.transaction_manager
        self.rm = self.receipt_manager
        self.wait_slots = [None, None, None]
        self.current_wait_index = -1
        self.total_paid = 0
        self.membership_discount = 0
        self.payments = []
        os.makedirs("json", exist_ok=True)
        
        self.init_ui()

        # Apply Styles
        self.setStyleSheet(styles.MAIN_WINDOW_STYLE)

    def init_ui(self):
        self.cart = [] # List of {"barcode": str, "qty": int}
        self.total_cancel_count, self.item_cancel_count = self.transaction_manager.get_pos_stats()
        
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
        self.welcome_page = WelcomePage(self.product_manager)
        self.welcome_page.barcodeScanned.connect(self.switch_to_sales_and_add)
        self.welcome_page.productInquiryRequested.connect(self.open_product_inquiry_welcome)
        self.welcome_page.transitCardRequested.connect(self.open_transit_card)
        self.welcome_page.checkInquiryRequested.connect(self.open_check_inquiry)
        self.welcome_page.calculatorRequested.connect(self.open_calculator)
        self.welcome_page.changeAccumulationRequested.connect(self.open_change_accumulation)
        self.welcome_page.parcelServiceRequested.connect(self.open_parcel_service)
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
        self.receipt_inquiry_page = ReceiptInquiryPage(self.transaction_manager, self.receipt_manager, self.product_manager)
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
        
        # 6. Check Inquiry Page
        self.check_inquiry_page = CheckInquiryPage()
        self.check_inquiry_page.backRequested.connect(self.handle_inquiry_back)
        self.central_stack.addWidget(self.check_inquiry_page)
        
        # 7. Transit Card Page
        self.transit_card_page = TransitCardPage()
        self.transit_card_page.backRequested.connect(self.handle_inquiry_back)
        self.central_stack.addWidget(self.transit_card_page)
        
        # 8. Product Inquiry Page
        self.product_inquiry_page = ProductInquiryPage(self.product_manager)
        self.product_inquiry_page.backRequested.connect(self.handle_inquiry_back)
        self.product_inquiry_page.productSelected.connect(self.handle_product_selection)
        self.central_stack.addWidget(self.product_inquiry_page)
        
        # 9. Calculator Page
        self.calculator_page = CalculatorPage()
        self.calculator_page.backRequested.connect(self.handle_inquiry_back)
        self.central_stack.addWidget(self.calculator_page)
        
        # 10. Change Accumulation Page
        self.change_accumulation_page = ChangeAccumulationPage(self.transaction_manager)
        self.change_accumulation_page.backRequested.connect(self.handle_inquiry_back)
        self.change_accumulation_page.accumulationCompleted.connect(self.handle_change_accumulation_completed)
        self.central_stack.addWidget(self.change_accumulation_page)
        
        # 11. Parcel Service Page
        self.parcel_service_page = ParcelServicePage()
        self.parcel_service_page.backRequested.connect(self.handle_inquiry_back)
        self.central_stack.addWidget(self.parcel_service_page)
        
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
        self.switch_page(1)
        # Process the barcode
        self.input_barcode.setText(barcode)
        self.handle_barcode_input()
        # Ensure focus is on the sales page barcode input
        self.input_barcode.setFocus()

    def open_product_inquiry_welcome(self):
        self.product_inquiry_page.set_sales_mode(False)
        self.product_inquiry_page.reset_ui()
        self.switch_page(8)

    def open_product_inquiry_sales(self):
        self.product_inquiry_page.set_sales_mode(True)
        self.product_inquiry_page.reset_ui()
        self.switch_page(8)

    def handle_product_selection(self, barcode):
        if len(self.page_history) > 1:
            self.page_history.pop() # remove current page (Index 8)
        self.switch_to_sales_and_add(barcode)

    def open_transit_card(self):
        self.switch_page(7)

    def open_calculator(self):
        self.switch_page(9)

    def open_change_accumulation(self):
        self.switch_page(10)

    def open_parcel_service(self):
        self.switch_page(11)

    def handle_change_accumulation_completed(self, amount):
        if len(self.page_history) > 1:
            self.page_history.pop()
        self.switch_page(0)
        
        current_total = self.transaction_manager.get_base_safe_amt() + self.transaction_manager.get_cash_total()
        new_total = current_total + amount
        cash_total = self.transaction_manager.get_cash_total()
        new_base = new_total - cash_total
        
        self.transaction_manager.set_base_safe_amt(new_base)
        self.update_welcome_history()
        
        CustomMessageDialog("적립 완료", f"잔돈 {amount:,}원이 성공적으로 적립되었습니다.\n금고 보관 금액이 {new_total:,}원으로 업데이트되었습니다.", 'info', self).exec()

    def open_check_inquiry(self):
        self.switch_page(6)

    def go_to_home(self):
        self.clear_cart()
        self.reset_wait_state()
        self.update_welcome_history()
        # Return to Welcome Page
        self.central_stack.setCurrentIndex(0)
        self.page_history = [0]

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
        self.table.setColumnWidth(0, styles.s(50))   # NO
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Product Name stretches
        self.table.setColumnWidth(2, styles.s(70))   # Qty
        self.table.setColumnWidth(3, styles.s(140))  # Unit Price
        self.table.setColumnWidth(4, styles.s(140))  # Amount
        self.table.setColumnWidth(5, styles.s(100))  # Discount
        self.lbl_foot_qty_width = 70
        self.lbl_foot_price_width = 140
        self.lbl_foot_amt_width = 140
        self.lbl_foot_disc_width = 100
        
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
        self.lbl_foot_qty.setFixedWidth(styles.s(self.lbl_foot_qty_width))
        self.lbl_foot_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_foot_qty.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #333;")
        footer_layout.addWidget(self.lbl_foot_qty)
        
        self.lbl_foot_price = QLabel("") # Unit price sum usually not shown or 0
        self.lbl_foot_price.setFixedWidth(styles.s(self.lbl_foot_price_width))
        self.lbl_foot_price.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_foot_price.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #333; padding-right: {styles.s(15)}px;")
        footer_layout.addWidget(self.lbl_foot_price)
        
        self.lbl_foot_amt = QLabel("0")
        self.lbl_foot_amt.setFixedWidth(styles.s(self.lbl_foot_amt_width))
        self.lbl_foot_amt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_foot_amt.setStyleSheet(f"font-weight: bold; font-size: {styles.fs(22)}; color: #333; padding-right: {styles.s(15)}px;")
        footer_layout.addWidget(self.lbl_foot_amt)
        
        self.lbl_foot_disc = QLabel("0")
        self.lbl_foot_disc.setFixedWidth(styles.s(self.lbl_foot_disc_width))
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
        summary_layout.setContentsMargins(20, 15, 20, 65) # Adjusted margins to shift widgets slightly upward
        summary_layout.setSpacing(15)
        
        # --- Left Side: Barcode Input ---
        barcode_container = QVBoxLayout()
        barcode_container.setContentsMargins(0, 0, 0, 0)
        
        self.promo_display_layout = QHBoxLayout()
        self.promo_display_layout.setSpacing(15)
        self.promo_display_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_promo_img = QLabel()
        self.lbl_promo_img.setFixedSize(styles.s(80), styles.s(80))
        self.lbl_promo_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_promo_img.setStyleSheet("background-color: transparent; border: none;")
        
        self.lbl_promo_info = QLabel("")
        self.lbl_promo_info.setStyleSheet(f"font-size: {styles.fs(22)}; font-weight: bold; color: #D32F2F; margin-bottom: 5px;")
        self.lbl_promo_info.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        self.promo_display_layout.addWidget(self.lbl_promo_img)
        self.promo_display_layout.addWidget(self.lbl_promo_info)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("상품의 바코드를 스캔하세요...")
        self.input_barcode.setStyleSheet(styles.BARCODE_INPUT_STYLE)
        self.input_barcode.setFixedHeight(styles.s(60)) # Slightly shorter input
        self.input_barcode.returnPressed.connect(self.handle_barcode_input)
        self.input_barcode.textChanged.connect(self.on_barcode_text_changed)
        
        barcode_container.addStretch(1)
        barcode_container.addLayout(self.promo_display_layout)
        barcode_container.addWidget(self.input_barcode)
        barcode_container.addStretch(3) # Increase bottom stretch to push input box upward
        
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
        right_layout.setSpacing(styles.s(4))
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Buttons minimum height to allow shrinking on lower resolutions
        button_min_height = styles.s(50)
        
        # Premium styles matching the user's image colors
        style_affiliate = styles.BUTTON_GREEN_STYLE
        style_coupon = styles.BUTTON_GREEN_STYLE
        style_card = styles.BUTTON_PURPLE_STYLE.replace(styles.PRIMARY_PURPLE, "#5E35B1").replace(styles.DARK_PURPLE, "#4527A0")
        style_cash = styles.BUTTON_PURPLE_STYLE.replace(styles.PRIMARY_PURPLE, "#3F51B5").replace(styles.DARK_PURPLE, "#283593")
        style_mobile = styles.BUTTON_PURPLE_STYLE.replace(styles.PRIMARY_PURPLE, "#7E57C2").replace(styles.DARK_PURPLE, "#5E35B1")
        style_pay_select = styles.BUTTON_GREEN_STYLE.replace(styles.ACCENT_GREEN, "#375A4F").replace(styles.DARK_GREEN, "#223B33")
        style_cancel = styles.BUTTON_RED_STYLE
        style_wait = styles.BUTTON_PURPLE_STYLE.replace(styles.PRIMARY_PURPLE, "#546E7A").replace(styles.DARK_PURPLE, "#37474F")
        
        btn_affiliate = ActionButton("제휴 할인 및\n포인트 적립/사용", style_affiliate, "ⓟ")
        btn_affiliate.clicked.connect(self.open_affiliate_discount)
        btn_coupon = ActionButton("CU키핑쿠폰 발급", style_coupon, "🎫")
        btn_coupon.clicked.connect(self.open_keeping_dialog)
        
        btn_card = ActionButton("신용카드", style_card, "💳")
        btn_card.clicked.connect(self.open_card_payment)
        
        btn_cash = ActionButton("현금", style_cash, "🪙")
        btn_cash.clicked.connect(self.open_cash_payment)
        
        btn_mobile_pay = ActionButton("모바일\n(미래에셋페이 등)", style_mobile, "📱")
        btn_mobile_pay.clicked.connect(self.open_mobile_payment)
        
        btn_pay_select = ActionButton("결제선택", style_pay_select, "👛")

        # Store references for multi-payment/state management
        self.btn_card = btn_card
        self.btn_cash = btn_cash
        self.btn_mobile_pay = btn_mobile_pay
        
        # Split Cancel/Wait buttons
        split_btns = QHBoxLayout()
        split_btns.setSpacing(styles.s(4))
        split_btns.setContentsMargins(0, 0, 0, 0)
        
        btn_cancel = ActionButton("전체취소", style_cancel)
        btn_cancel.clicked.connect(self.handle_all_cancel)
        
        btn_wait = ActionButton("대기", style_wait)
        btn_wait.clicked.connect(self.handle_wait_click)
        self.btn_wait = btn_wait
        
        split_btns.addWidget(btn_cancel)
        split_btns.addWidget(btn_wait)
        
        # Set all buttons to expanding size policy so they fill the vertical height evenly
        for btn in [btn_affiliate, btn_coupon, btn_card, btn_cash, btn_mobile_pay, btn_pay_select, btn_cancel, btn_wait]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(button_min_height)
            
        def create_separator():
            sep = QLabel("▼")
            sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sep.setStyleSheet("color: #90A4AE; font-size: 11pt; font-weight: bold; border: none; background: transparent; margin: 1px 0;")
            sep.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sep.setFixedHeight(styles.s(15))
            return sep

        right_layout.addWidget(btn_affiliate)
        right_layout.addWidget(btn_coupon)
        right_layout.addWidget(create_separator())
        right_layout.addWidget(btn_card)
        right_layout.addWidget(btn_cash)
        right_layout.addWidget(btn_mobile_pay)
        right_layout.addWidget(btn_pay_select)
        right_layout.addWidget(create_separator())
        right_layout.addLayout(split_btns)
        
        return right_layout

    def create_bottom_panel_frame(self):
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(styles.s(60))
        bottom_frame.setStyleSheet(f"background-color: #EEEEEE; border: none;")
        layout = QHBoxLayout(bottom_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        buttons = [
            ("", styles.BUTTON_BOTTOM_STYLE),
            ("수표조회", styles.BUTTON_BOTTOM_STYLE),
            ("영수증조회", styles.BUTTON_BOTTOM_STYLE),
            ("상품조회", styles.BUTTON_BOTTOM_STYLE),
            ("", styles.BUTTON_BOTTOM_STYLE),
            ("", styles.BUTTON_BOTTOM_STYLE),
            ("", styles.BUTTON_BOTTOM_STYLE),
            ("", styles.BUTTON_BOTTOM_STYLE)
        ]
        
        for text, style in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(style)
            btn.setFixedHeight(styles.s(40))
            if not text:
                btn.setEnabled(False)
            elif text == "상품조회":
                btn.clicked.connect(self.open_product_inquiry_sales)
            elif text == "수표조회":
                btn.clicked.connect(self.open_check_inquiry)
            elif text == "영수증조회":
                btn.clicked.connect(lambda: self.switch_page(3))
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
        for kor_prefix in ["ㅔ묘", "ㅖ묘", "ㅔ됴", "ㅖ됴"]:
            if text.startswith(kor_prefix):
                text = "pay" + text[len(kor_prefix):]
                self.input_barcode.blockSignals(True)
                self.input_barcode.setText(text)
                self.input_barcode.blockSignals(False)
                break

        lower_text = text.lower()
        if lower_text.startswith("pay"):
            self.input_barcode.setStyleSheet(styles.BARCODE_INPUT_STYLE.replace("color: #333;", "color: white;"))
        else:
            self.input_barcode.setStyleSheet(styles.BARCODE_INPUT_STYLE)

        should_submit = False
        if lower_text.startswith("pay"):
            digits_count = sum(1 for c in text[3:] if c.isdigit())
            if digits_count >= 13:
                should_submit = True
        else:
            if len(text) >= 13:
                should_submit = True
                
        if should_submit:
            # Auto submit
            self.add_product(text.strip())
            self.input_barcode.clear()
            self.input_barcode.setStyleSheet(styles.BARCODE_INPUT_STYLE)
            self.input_barcode.setFocus()

    def handle_barcode_input(self):
        barcode = self.input_barcode.text().strip()
        if barcode:
            self.add_product(barcode)
            self.input_barcode.clear()
            self.input_barcode.setStyleSheet(styles.BARCODE_INPUT_STYLE)
            self.input_barcode.setFocus()
            
    def get_voucher(self, barcode):
        return self.product_manager.get_voucher(barcode)

    def process_voucher(self, barcode, voucher):
        target_barcode = voucher["product_barcode"]
        target_product = self.product_manager.get_product(target_barcode)
        if not target_product:
            CustomMessageDialog("오류", "상품권 대상 상품이 등록되지 않았습니다.", 'warning', self).exec()
            return

        target_name = target_product["name"]
        voucher_value = target_product["price"]

        # Check if the target product is already in the cart
        in_cart_qty = 0
        for item in self.cart:
            if item["barcode"] == target_barcode:
                in_cart_qty += item["qty"]

        if in_cart_qty > 0:
            # Target product is in the cart! Apply payment directly.
            self.apply_voucher_payment(barcode, target_name, voucher_value)
        elif len(self.cart) == 0:
            # Cart is empty. Automatically add the target product to the cart.
            self.add_product(target_barcode)
            # Apply payment directly.
            self.apply_voucher_payment(barcode, target_name, voucher_value)
        else:
            # Cart is not empty, but target product is not in the cart.
            # Show exchange dialog!
            dialog = VoucherExchangeDialog(self)
            if dialog.exec():
                # User clicked "예 [반복/입력]" (Yes, exchange)
                # Check if remaining payment amount is greater than or equal to voucher value
                total_amt, total_disc, final_amt = self.get_cart_summary()
                remaining = final_amt - self.total_paid
                
                if remaining < voucher_value:
                    CustomMessageDialog("오류", f"상품권 금액({voucher_value:,}원) 이상의 상품을 스캔해 주세요.\n현재 결제 대상 금액: {remaining:,}원", 'warning', self).exec()
                    return
                
                # Apply payment
                self.apply_voucher_payment(barcode, target_name, voucher_value)
            else:
                # User clicked "아니오 [CLEAR]" (No, cancel)
                return

    def apply_voucher_payment(self, barcode, product_name, amount):
        total_amt, total_disc, final_amt = self.get_cart_summary()
        self.total_paid += amount
        self.payments.append({
            "method": "MobileVoucher",
            "amount": amount,
            "details": {"barcode": barcode, "product_name": product_name}
        })
        
        if hasattr(self, 'btn_mobile_pay'):
            self.btn_mobile_pay.set_checked(True)
            
        self.update_totals()
        
    def get_keeping_coupon(self, barcode):
        import json
        import os
        keeping_file = os.path.join(os.path.abspath("."), "json", "keeping.json")
        if os.path.exists(keeping_file):
            try:
                with open(keeping_file, "r", encoding="utf-8") as f:
                    keeping_data = json.load(f)
                return keeping_data.get(barcode)
            except Exception:
                return None
        return None

    def process_keeping_coupon(self, barcode, coupon):
        target_barcode = coupon["product_barcode"]
        target_product = self.product_manager.get_product(target_barcode)
        if not target_product:
            CustomMessageDialog("오류", "키핑쿠폰 대상 상품이 등록되지 않았습니다.", 'warning', self).exec()
            return

        target_name = target_product["name"]
        coupon_value = target_product["price"]

        # Check if the target product is already in the cart
        in_cart_qty = 0
        for item in self.cart:
            if item["barcode"] == target_barcode:
                in_cart_qty += item["qty"]

        def apply_keeping_payment():
            # Mark the coupon as used in keeping.json
            import json
            import os
            keeping_file = os.path.join(os.path.abspath("."), "json", "keeping.json")
            if os.path.exists(keeping_file):
                try:
                    with open(keeping_file, "r", encoding="utf-8") as f:
                        keeping_data = json.load(f)
                    if barcode in keeping_data:
                        keeping_data[barcode]["status"] = "사용완료"
                        with open(keeping_file, "w", encoding="utf-8") as f:
                            json.dump(keeping_data, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print("Error updating keeping status:", str(e))

            self.total_paid += coupon_value
            self.payments.append({
                "method": "KeepingCoupon",
                "amount": coupon_value,
                "details": {"barcode": barcode, "product_name": target_name}
            })
            if hasattr(self, 'btn_coupon'):
                self.btn_coupon.set_checked(True)
                
            self.status_label.setText(f"키핑쿠폰 적용 완료: {target_name}")
            self.update_totals()
            
            _, _, final_amt = self.get_cart_summary()
            if self.total_paid >= final_amt:
                self.finalize_transaction()

        if in_cart_qty > 0:
            apply_keeping_payment()
        elif len(self.cart) == 0:
            self.add_product(target_barcode)
            apply_keeping_payment()
        else:
            dialog = VoucherExchangeDialog(self)
            if dialog.exec():
                _, _, final_amt = self.get_cart_summary()
                remaining = final_amt - self.total_paid
                if remaining < coupon_value:
                    CustomMessageDialog("오류", f"쿠폰 금액({coupon_value:,}원) 이상의 상품을 스캔해 주세요.\n현재 결제 대상 금액: {remaining:,}원", 'warning', self).exec()
                    return
                apply_keeping_payment()

    def open_keeping_dialog(self):
        # Check if cart has keepable items (promo items with qty >= 2)
        keepable_items = []
        for item in self.cart:
            product = self.product_manager.get_product(item["barcode"])
            if product and product.get("promo_type", 0) in [1, 2]:
                max_keepable = item["qty"] - 1
                if max_keepable > 0:
                    keepable_items.append((item, product, max_keepable))
                
        if not keepable_items:
            CustomMessageDialog("키핑 불가", "장바구니에 키핑할 수 있는 행사 상품(수량 2개 이상)이 없습니다.", 'warning', self).exec()
            return
            
        dialog = KeepingLookupDialog(self)
        dialog.exec()
        
        if not dialog.result_value or not dialog.phone_number:
            return
            
        phone = dialog.phone_number
        
        # Show KeepingCouponIssueDialog
        issue_dialog = KeepingCouponIssueDialog(keepable_items, self)
        if not issue_dialog.exec():
            return
            
        # Process coupon issuance
        import json
        import os
        import random
        from datetime import datetime, timedelta
        
        keeping_file = os.path.join(os.path.abspath("."), "json", "keeping.json")
        keeping_data = {}
        if os.path.exists(keeping_file):
            try:
                with open(keeping_file, "r", encoding="utf-8") as f:
                    keeping_data = json.load(f)
            except Exception:
                keeping_data = {}
                
        issued_coupons = []
        
        for item, product, max_keepable in keepable_items:
            barcode = item["barcode"]
            qty_to_issue = issue_dialog.result_quantities.get(barcode, 0)
            if qty_to_issue <= 0:
                continue
                
            name = product["name"]
            
            for _ in range(qty_to_issue):
                while True:
                    rand_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
                    keeping_barcode = f"98{rand_part}"
                    if keeping_barcode not in keeping_data:
                        break
                        
                issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                
                coupon_info = {
                    "phone": phone,
                    "product_barcode": barcode,
                    "product_name": name,
                    "issue_date": issue_date,
                    "expiry_date": expiry_date,
                    "status": "사용가능"
                }
                
                keeping_data[keeping_barcode] = coupon_info
                
                # Generate barcode image
                barcode_img_src = self.receipt_manager.generate_barcode_base64(keeping_barcode)
                spaced_barcode = " ".join([keeping_barcode[i:i+4] for i in range(0, len(keeping_barcode), 4)])
                
                # Image or fallback emoji
                image_html = ""
                import base64
                import sys
                try:
                    base_path = sys._MEIPASS
                except Exception:
                    base_path = os.path.abspath(".")
                image_path = None
                for ext in ["png", "jpg", "jpeg", "webp"]:
                    p = os.path.join(os.path.abspath("."), "photo", f"{barcode}.{ext}")
                    if os.path.exists(p):
                        image_path = p
                        break
                        
                if not image_path:
                    for ext in ["png", "jpg", "jpeg"]:
                        p = os.path.join(base_path, "assets", f"{barcode}.{ext}")
                        if os.path.exists(p):
                            image_path = p
                            break
                        
                if os.path.exists(image_path):
                    try:
                        with open(image_path, "rb") as f_img:
                            img_b64 = base64.b64encode(f_img.read()).decode("utf-8")
                        ext = "jpg" if image_path.endswith(".jpg") else "png"
                        img_src = f"data:image/{ext};base64,{img_b64}"
                        image_html = f'<img src="{img_src}" height="110" style="display: block;" />'
                    except Exception:
                        image_html = ""
                        
                if not image_html:
                    CATEGORY_EMOJIS = {
                        "snack": "🍪",
                        "drink": "🥤",
                        "candy": "🍭",
                        "jelly": "🍬",
                        "water": "🥛",
                        "etc": "🎁",
                        "핫바": "🍢",
                        "식사류": "🍱",
                        "면류": "🍜"
                    }
                    emoji = CATEGORY_EMOJIS.get(product.get("category", "etc"), "🎁")
                    image_html = f'<div style="font-size: 64pt; line-height: 120px; text-align: center;">{emoji}</div>'
                
                issued_coupons.append({
                    "barcode": keeping_barcode,
                    "spaced_barcode": spaced_barcode,
                    "barcode_img_src": barcode_img_src,
                    "product_name": name,
                    "image_html": image_html,
                    "issue_date": issue_date,
                    "expiry_date": expiry_date,
                    "phone": phone
                })
        
        if not issued_coupons:
            return
            
        try:
            with open(keeping_file, "w", encoding="utf-8") as f:
                json.dump(keeping_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            CustomMessageDialog("저장 오류", f"키핑쿠폰 저장 중 오류가 발생했습니다: {str(e)}", 'warning', self).exec()
            return
            
        # Render HTML with all coupons
        coupons_cards_html = ""
        for cp in issued_coupons:
            coupons_cards_html += f"""
            <div class="card-container" style="margin-bottom: 25px;">
                <div class="card-header">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" style="width: 140px; height: 140px; background-color: #ffffff; border-radius: 12px;">
                        <tr>
                            <td align="center" valign="middle" style="height: 140px; width: 140px;">
                                {cp["image_html"]}
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="card-body">
                    <div class="brand-name">CU</div>
                    <div class="product-name">{cp["product_name"]}</div>
                    <div class="coupon-type">DU 키핑쿠폰 (물품교환권)</div>
                    
                    <div class="pay-banner">
                        발급 정보
                    </div>
                    
                    <div class="info-row">· 휴대폰번호: {cp["phone"]}</div>
                    <div class="info-row">· 발급 일시: {cp["issue_date"]}</div>
                    <div class="info-row">· 유효 기간: ~ {cp["expiry_date"]}</div>
                    
                    <div class="barcode-box">
                        <img src="{cp["barcode_img_src"]}" width="220" height="60" />
                    </div>
                    
                    <div class="barcode-number-row">
                        <span class="barcode-num">{cp["spaced_barcode"]}</span>
                    </div>
                </div>
            </div>
            """
            
        coupon_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Malgun Gothic', 'Dotum', sans-serif;
                    background-color: #FAFAFA;
                    margin: 0;
                    padding: 10px;
                }}
                .card-container {{
                    width: 320px;
                    background-color: #ffffff;
                    border: 1px solid #E0E0E0;
                    border-radius: 12px;
                    margin: 0 auto;
                }}
                .card-header {{
                    background: #8E24AA;
                    padding: 25px 0;
                    border-top-left-radius: 11px;
                    border-top-right-radius: 11px;
                    text-align: center;
                }}
                .card-body {{
                    padding: 20px;
                    text-align: center;
                    background-color: #FAFAFA;
                    border-bottom-left-radius: 11px;
                    border-bottom-right-radius: 11px;
                }}
                .brand-name {{
                    font-size: 11pt;
                    color: #888888;
                    font-weight: bold;
                    letter-spacing: 1.5px;
                    margin-bottom: 5px;
                }}
                .product-name {{
                    font-size: 15pt;
                    font-weight: bold;
                    color: #222222;
                    margin-bottom: 5px;
                    line-height: 1.3;
                }}
                .coupon-type {{
                    font-size: 11pt;
                    color: #8E24AA;
                    font-weight: bold;
                    margin-bottom: 15px;
                }}
                .pay-banner {{
                    width: 85%;
                    border-top: 1px solid #E0E0E0;
                    border-bottom: 1px solid #E0E0E0;
                    margin: 10px auto 20px auto;
                    padding: 8px 0;
                    font-size: 9.5pt;
                    color: #757575;
                    font-weight: 500;
                }}
                .info-row {{
                    font-size: 9.5pt;
                    color: #555555;
                    margin: 4px 0;
                    text-align: left;
                    padding-left: 25px;
                }}
                .barcode-box {{
                    background-color: #ffffff;
                    border: 1px solid #EBEBEB;
                    border-radius: 6px;
                    padding: 12px 10px;
                    display: inline-block;
                    margin-top: 15px;
                    margin-bottom: 10px;
                }}
                .barcode-number-row {{
                    margin-top: 5px;
                }}
                .barcode-num {{
                    font-size: 13pt;
                    font-weight: bold;
                    color: #333333;
                    letter-spacing: 1.5px;
                    font-family: 'Courier New', Courier, monospace;
                    vertical-align: middle;
                }}
            </style>
        </head>
        <body>
            {coupons_cards_html}
        </body>
        </html>
        """
        
        # Show coupon image
        ReceiptPreviewDialog(coupon_html, self, title="키핑쿠폰 발급 완료", height=780).exec()


    def add_product(self, barcode):
        # Intercept pay barcode (starts with 'pay' case-insensitively or Korean equivalents)
        for kor_prefix in ["ㅔ묘", "ㅖ묘", "ㅔ됴", "ㅖ됴"]:
            if barcode.startswith(kor_prefix):
                barcode = "pay" + barcode[len(kor_prefix):]
                break

        lower_bc = barcode.lower()
        if lower_bc.startswith("pay"):
            digits_part = "".join(c for c in barcode[3:] if c.isdigit())
            if len(digits_part) == 13:
                self.process_pay_barcode(barcode, digits_part)
            else:
                CustomMessageDialog("결제 오류", f"유효하지 않은 결제 바코드입니다.\n'pay' 뒤에 13자리 계좌번호를 입력해 주세요.\n(입력된 숫자: {len(digits_part)}자리)", 'warning', self).exec()
            return

        # Intercept keeping coupon barcode (starts with 98)
        if barcode.startswith("98"):
            coupon = self.get_keeping_coupon(barcode)
            if coupon:
                if coupon.get("status") == "사용완료":
                    CustomMessageDialog("이미 사용됨", "이미 사용이 완료된 키핑쿠폰입니다.", 'warning', self).exec()
                    return
                self.process_keeping_coupon(barcode, coupon)
                return
            else:
                CustomMessageDialog("쿠폰 없음", f"바코드[{barcode}]\n존재하지 않거나 유효하지 않은 키핑쿠폰입니다.", 'warning', self).exec()
                return

        voucher = self.get_voucher(barcode)
        if voucher:
            self.process_voucher(barcode, voucher)
            return

        product = self.product_manager.get_product(barcode)
        if not product:
            # Show alert for product not found
            dialog = CustomMessageDialog("상품 없음", f"바코드[{barcode}]\n등록되지 않은 상품입니다.", 'warning', self)
            dialog.exec()
            # Clear input after alert
            self.input_barcode.clear()
            self.input_barcode.setFocus()
            return

        # Stock Check
        current_stock = product.get("stock", 0)
        # Calculate how many are already in cart
        in_cart_qty = 0
        for item in self.cart:
            if item["barcode"] == barcode:
                in_cart_qty = item["qty"]
                break
        
        if current_stock <= in_cart_qty:
            dialog = CustomMessageDialog("재고 부족", f"상품 [{product['name']}]의 재고가 부족합니다.\n현재 재고: {current_stock}", 'warning', self)
            dialog.exec()
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
            
        # Promotion Alert (TTS & On-screen inline highlight)
        promo_type = product.get("promo_type", 0)
        if promo_type in [1, 2]:
            promo_name = "1+1" if promo_type == 1 else "2+1"
            tts_name = "원플러스원" if promo_type == 1 else "투플러스원"
            
            # Highlight color (Red for 1+1, Orange for 2+1)
            color = "#D32F2F" if promo_type == 1 else "#F59E0B"
            self.lbl_promo_info.setStyleSheet(f"font-size: {styles.fs(22)}; font-weight: bold; color: {color}; margin-bottom: 5px;")
            self.lbl_promo_info.setText(f"★ {promo_name} 행사 상품입니다! ★")
            
            # Load and display product image
            img_path = None
            for ext in ["png", "jpg", "jpeg", "webp"]:
                p = os.path.join(os.path.abspath("."), "photo", f"{barcode}.{ext}")
                if os.path.exists(p):
                    img_path = p
                    break
            if not img_path:
                for ext in ["png", "jpg", "jpeg"]:
                    p = os.path.join(os.path.abspath("."), "assets", f"{barcode}.{ext}")
                    if os.path.exists(p):
                        img_path = p
                        break
            if img_path:
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.lbl_promo_img.setPixmap(pixmap.scaled(styles.s(80), styles.s(80), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.lbl_promo_img.clear()
            else:
                self.lbl_promo_img.clear()
                
            QApplication.processEvents() # Update UI to show text immediately
            self.speak(f"{tts_name} 상품입니다.")
            
            # Clear message and image after 3 seconds
            QTimer.singleShot(3000, lambda: (self.lbl_promo_info.setText(""), self.lbl_promo_img.clear()))
        else:
            self.lbl_promo_info.setText("")
            self.lbl_promo_img.clear()

        self.update_table_view()
        self.update_totals()

    def speak(self, text):
        self.tts_queue.put(text)

    def _tts_worker(self):
        try:
            import pyttsx3
            import ctypes
            # Initialize COM library for SAPI5 in this background thread
            ctypes.windll.ole32.CoInitialize(None)
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            
            while True:
                text = self.tts_queue.get()
                if text is None:
                    break
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass
                self.tts_queue.task_done()
        except Exception:
            pass

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
            # Amount
            price = product['price']
            qty = item['qty']
            promo_type = product.get("promo_type", 0)
            
            discount = 0
            if promo_type == 1: # 1+1
                discount = (qty // 2) * price
            elif promo_type == 2: # 2+1
                discount = (qty // 3) * price

            amt = (price * qty) - discount
            self.table.setItem(row, 3, QTableWidgetItem(f"{price:,}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{amt:,}"))
            # Discount
            self.table.setItem(row, 5, QTableWidgetItem(f"{discount:,}"))
            
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

    def get_cart_summary(self):
        total_amt = 0
        total_disc = 0
        for item in self.cart:
            product = self.product_manager.get_product(item["barcode"])
            if product:
                price = product["price"]
                qty = item["qty"]
                promo_type = product.get("promo_type", 0)
                
                item_total = price * qty
                item_disc = 0
                if promo_type == 1: # 1+1
                    item_disc = (qty // 2) * price
                elif promo_type == 2: # 2+1
                    item_disc = (qty // 3) * price
                
                total_amt += item_total
                total_disc += item_disc
        return total_amt, total_disc, total_amt - total_disc

    def update_totals(self):
        total_amt, total_disc, final_amt = self.get_cart_summary()
        m_disc = getattr(self, "membership_discount", 0)
        total_disc += m_disc
        final_amt -= m_disc
        
        total_qty = sum(item["qty"] for item in self.cart)
        
        # Update Footer
        self.lbl_foot_qty.setText(str(total_qty))
        self.lbl_foot_amt.setText(f"{total_amt:,}")
        self.lbl_foot_disc.setText(f"{total_disc:,}")
        
        # Update Big Total (Payments Area)
        self.lbl_final_price.setText(f"{(final_amt - self.total_paid):,}")
        self.lbl_received_amount.setText(f"{self.total_paid:,}")
        self.lbl_change_amount.setText("0")
        
    def clear_cart(self):
        self.cart = []
        self.total_paid = 0
        self.membership_discount = 0
        self.payments = []
        self.reset_wait_state()
        self.update_table_view()
        self.update_totals()
        
        # Reset button icons
        if hasattr(self, 'btn_card'): self.btn_card.set_checked(False)
        if hasattr(self, 'btn_cash'): self.btn_cash.set_checked(False)
        if hasattr(self, 'btn_mobile_pay'): self.btn_mobile_pay.set_checked(False)
        
        self.input_barcode.setFocus()
        
    def handle_all_cancel(self):
        if self.cart:
            self.total_cancel_count += 1
            self.transaction_manager.save_pos_stats(self.total_cancel_count, self.item_cancel_count)
            self.clear_cart()
            self.update_welcome_history()
        else:
            self.clear_cart()
        
    def open_edit_dialog(self, row, col):
        if row < 0 or row >= len(self.cart):
            return
            
        item_data = self.cart[row]
        barcode = item_data["barcode"]
        product = self.product_manager.get_product(barcode)
        
        dialog = EditItemDialog(barcode, product, item_data["qty"], self.product_manager, self)
        
        if dialog.exec():
            if dialog.delete_clicked:
                del self.cart[row]
                self.item_cancel_count += 1
                self.transaction_manager.save_pos_stats(self.total_cancel_count, self.item_cancel_count)
                self.update_welcome_history()
            else:
                new_qty = dialog.get_new_qty()
                old_qty = self.cart[row]["qty"]
                if new_qty < old_qty:
                    self.item_cancel_count += 1
                    self.transaction_manager.save_pos_stats(self.total_cancel_count, self.item_cancel_count)
                    self.update_welcome_history()
                self.cart[row]["qty"] = new_qty
            
            self.update_table_view()
            self.update_totals()

    def generate_tx_barcode(self):
        # Format: YYMMDDHHMMSS + 4 random digits
        now = datetime.datetime.now()
        base = now.strftime("%y%m%d%H%M%S")
        rand = "".join([str(random.randint(0, 9)) for _ in range(4)])
        return base + rand

    def open_affiliate_discount(self):
        total_amt, total_disc, final_amt = self.get_cart_summary()
        remaining = final_amt - self.total_paid
        
        if final_amt == 0:
            CustomMessageDialog("조회 불가", "결제할 상품이 없습니다.", 'warning', self).exec()
            return
            
        dialog = AffiliateDiscountDialog(remaining, self)
        # Position the dialog on the left side of the main window under the header
        geom = self.geometry()
        dialog.move(geom.x() + styles.s(10), geom.y() + styles.s(60))
        if dialog.exec():
            discount = dialog.discount_amount
            points = dialog.points_used
            issuer = dialog.card_issuer
            
            # Add membership discount
            self.membership_discount = getattr(self, "membership_discount", 0) + discount
            
            # Log the discount payment
            if discount > 0 or points > 0:
                self.payments.append({
                    "method": "Discount",
                    "amount": discount,
                    "details": {
                        "issuer": issuer,
                        "points_used": points,
                        "card_number": dialog.card_number
                    }
                })
            self.update_totals()

    def open_card_payment(self):
        # Calculate remaining total
        total_amt, total_disc, final_amt = self.get_cart_summary()
        remaining = final_amt - self.total_paid
        
        if final_amt == 0:
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
            
        if not hasattr(self, 'firebase_mgr') or self.firebase_mgr is None:
            try:
                from firebase_manager import FirebaseManager
                self.firebase_mgr = FirebaseManager()
            except Exception:
                self.firebase_mgr = None
                
        dialog = CreditCardPaymentDialog(remaining, self.firebase_mgr, self)
        if dialog.exec():
            paid_now = dialog.get_payment_amount()
            self.total_paid += paid_now
            self.payments.append({
                "method": "Card",
                "amount": paid_now,
                "details": {
                    "card_number": dialog.get_card_number(),
                    "balance_after": getattr(dialog, 'final_balance_after', 0.0)
                }
            })
            if hasattr(self, 'btn_card'): self.btn_card.set_checked(True)
            self.update_totals()
            
            # If fully paid, finalize
            if self.total_paid >= final_amt:
                self.finalize_transaction()


    def open_cash_payment(self):
        # Calculate remaining total
        total_amt, total_disc, final_amt = self.get_cart_summary()
        remaining = final_amt - self.total_paid
        
        if final_amt == 0:
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
            
            # Request Cash Receipt (현금영수증)
            from payment_ui import CashReceiptDialog
            receipt_dlg = CashReceiptDialog(cash_applied, paid_now, self)
            receipt_id = ""
            receipt_dlg.exec()
            if receipt_dlg.receipt_issued:
                receipt_id = receipt_dlg.receipt_id
                
            self.payments.append({
                "method": "Cash",
                "amount": cash_applied,
                "details": {
                    "received_amt": paid_now, 
                    "change_amt": change,
                    "receipt_id": receipt_id
                }
            })
            if hasattr(self, 'btn_cash'): self.btn_cash.set_checked(True)
            self.update_totals()
            
            if change > 0:
                self.lbl_change_amount.setText(f"{change:,}")
            
            if self.total_paid >= final_amt:
                # If fully paid, finalize
                self.finalize_transaction()

    def process_pay_barcode(self, barcode, account_number):
        total_amt, total_disc, final_amt = self.get_cart_summary()
        remaining = final_amt - self.total_paid
        
        if final_amt == 0:
            CustomMessageDialog("결제 불가", "결제할 상품이 없습니다.", 'warning', self).exec()
            return

        if remaining <= 0:
            CustomMessageDialog("알림", "이미 결제가 완료되었습니다.", 'info', self).exec()
            return

        if not hasattr(self, 'firebase_mgr') or self.firebase_mgr is None:
            from firebase_manager import FirebaseManager
            self.firebase_mgr = FirebaseManager()
            
        from ui_components import BarcodePaymentProgressDialog
        dialog = BarcodePaymentProgressDialog(self.firebase_mgr, account_number, remaining, self)
        dialog.exec()
        
        success, message, balance = dialog.get_result()
        
        if success:
            self.total_paid += remaining
            self.payments.append({
                "method": "MobilePay",
                "amount": remaining,
                "details": {
                    "account_number": account_number,
                    "balance_after": balance
                }
            })
            if hasattr(self, 'btn_mobile_pay'): 
                self.btn_mobile_pay.set_checked(True)
            self.update_totals()
            
            # Finalize transaction directly
            self.finalize_transaction()
        else:
            # Show a clean error message dialog
            if "잔액" in message or "부족" in message:
                CustomMessageDialog("승인 거절", "승인이 거절되었습니다.\n(잔액이 부족합니다.)", 'warning', self).exec()
            else:
                CustomMessageDialog("승인 거절", f"승인이 거절되었습니다.\n({message})", 'warning', self).exec()

    def open_mobile_payment(self):
        # Calculate remaining total
        total_amt, total_disc, final_amt = self.get_cart_summary()
        remaining = final_amt - self.total_paid
        
        if final_amt == 0:
            CustomMessageDialog("결제 불가", "결제할 상품이 없습니다.", 'warning', self).exec()
            return

        # Toggle off if already paid
        if hasattr(self, 'btn_mobile_pay') and self.btn_mobile_pay.is_checked:
            # Find and remove the mobile payment from list
            for i, p in enumerate(self.payments):
                if p["method"] == "MobilePay":
                    self.total_paid -= p["amount"]
                    self.payments.pop(i)
                    break
            self.btn_mobile_pay.set_checked(False)
            self.update_totals()
            return

        if remaining <= 0:
            CustomMessageDialog("알림", "이미 결제가 완료되었습니다.", 'info', self).exec()
            return
            
        from mobile_payment_dialog import MobilePaymentDialog
        if not hasattr(self, 'firebase_mgr'):
            from firebase_manager import FirebaseManager
            self.firebase_mgr = FirebaseManager()
            
        dialog = MobilePaymentDialog(remaining, self.firebase_mgr, self)
        if dialog.exec():
            details = dialog.get_payment_details()
            paid_now = details["amount"]
            self.total_paid += paid_now
            self.payments.append({
                "method": "MobilePay",
                "amount": paid_now,
                "details": {
                    "account_number": details["account_number"],
                    "balance_after": details["balance_after"]
                }
            })
            if hasattr(self, 'btn_mobile_pay'): self.btn_mobile_pay.set_checked(True)
            self.update_totals()
            
            # If fully paid, finalize
            if self.total_paid >= final_amt:
                self.finalize_transaction()

    def finalize_transaction(self):
        total_amt, total_disc, final_amt = self.get_cart_summary()
        items_data = []
        for item in self.cart:
            prod = self.product_manager.get_product(item["barcode"])
            items_data.append({
                "name": prod["name"],
                "qty": item["qty"],
                "price": prod["price"]
            })
            # Deduct Stock
            self.product_manager.reduce_stock(item["barcode"], item["qty"])
            
        tx_barcode = self.generate_tx_barcode()
        
        # Determine primary payment method for simple lookup, but store full list
        primary_method = self.payments[0]["method"] if self.payments else "Unknown"
        
        # Prepare transaction data for receipt generator
        tx_data = {
            "items": items_data,
            "total_amt": final_amt, # Use final amount
            "total_discount": total_disc, # Add discount info
            "payment_method": primary_method,
            "payments": self.payments, # Full list of all partial payments
            "tx_barcode": tx_barcode
        }
        
        self.transaction_manager.save_transaction(
            items=items_data,
            total_amt=final_amt,
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

    def update_welcome_history(self):
        last_tx = self.transaction_manager.get_last_transaction()
        self.welcome_page.update_last_transaction(last_tx)
        
        # Update Safe Balance
        base_safe_amt = self.transaction_manager.get_base_safe_amt()
        cash_total = self.transaction_manager.get_cash_total()
        self.welcome_page.update_safe_balance(base_safe_amt + cash_total)
        
        # Update POS statistics
        all_txs = self.transaction_manager.get_all_transactions()
        refund_count = sum(1 for tx in all_txs if tx.get("status") == "Refunded")
        self.welcome_page.update_statistics(refund_count, self.total_cancel_count, self.item_cancel_count)

    def handle_safe_balance_edit(self):
        current_total = self.transaction_manager.get_base_safe_amt() + self.transaction_manager.get_cash_total()
        
        dialog = SafeBalanceEditDialog(current_total, self)
        
        if dialog.exec():
            amount = dialog.get_amount()
            stored_amount = current_total - amount
            # New Base = New Total - Cash from transactions
            cash_total = self.transaction_manager.get_cash_total()
            new_base = amount - cash_total
            self.transaction_manager.set_base_safe_amt(new_base)
            self.update_welcome_history()
            
            CustomMessageDialog("보관 완료", f"금고 보관액 {stored_amount:,}원이 성공적으로 금고에 보관되었습니다.\n현재현금시재: {amount:,}원", 'info', self).exec()

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
            
        tx = self.transaction_manager.get_transaction_by_barcode(barcode)
        if not tx:
            CustomMessageDialog("조회 실패", "해당 바코드의 영수증을 찾을 수 없습니다.", 'warning', self).exec()
            return
            
        if tx.get("status") == "Refunded":
            CustomMessageDialog("알림", "이미 환불 처리된 영수증입니다.", 'warning', self).exec()
            return
            
        # Format the description of the transaction
        items = tx.get("items", [])
        if len(items) == 1:
            items_desc = f"{items[0].get('name')} {items[0].get('qty')}개"
        elif len(items) > 1:
            items_desc = f"{items[0].get('name')} {items[0].get('qty')}개 외 {len(items)-1}건"
        else:
            items_desc = "상품 정보 없음"
            
        total_amt = tx.get("total_amt", 0)
        pay_method = tx.get("payment_method", "결제")
        
        # Translate payment method
        method_map = {"Card": "카드", "Cash": "현금", "MobilePay": "모바일페이"}
        pay_method_ko = method_map.get(pay_method, pay_method)
        
        confirm_msg = (
            f"선택된 영수증 정보:\n"
            f"· 품목: {items_desc}\n"
            f"· 금액: {total_amt:,}원 ({pay_method_ko})\n\n"
            f"정말 환불 처리를 진행하시겠습니까?"
        )
        
        confirm_dlg = CustomMessageDialog("영수증 환불 확인", confirm_msg, 'question', self)
        confirm_dlg.exec()
        
        if confirm_dlg.result_value:
            if not hasattr(self, 'firebase_mgr') or self.firebase_mgr is None:
                from firebase_manager import FirebaseManager
                self.firebase_mgr = FirebaseManager()
                
            from ui_components import BarcodeRefundProgressDialog
            dialog = BarcodeRefundProgressDialog(
                self.transaction_manager, 
                self.firebase_mgr, 
                barcode, 
                total_amt, 
                pay_method, 
                tx, 
                self
            )
            dialog.exec()
            
            success, message = dialog.get_result()
            if success:
                self.update_welcome_history()
                CustomMessageDialog(
                    "환불 완료", 
                    f"영수증 환불 처리가 성공적으로 완료되었습니다.\n\n"
                    f"· 환불 금액: {total_amt:,}원\n"
                    f"· 결제 수단: {pay_method_ko} 반환 완료", 
                    'info', 
                    self
                ).exec()
            else:
                CustomMessageDialog(
                    "환불 실패", 
                    f"환불 진행 중 오류가 발생했습니다:\n{message}", 
                    'warning', 
                    self
                ).exec()

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
        self.switch_page(1)
        self.update_table_view()
        self.update_totals()

    def handle_post_prev_tx(self):
        # Logic for "직전거래" button on post-payment page
        last_tx = self.transaction_manager.get_last_transaction()
        if last_tx:
            dialog = PostPaymentOptionDialog(last_tx, self)
            dialog.exec()
        else:
            CustomMessageDialog("알림", "직전 거래 내역이 없습니다.", 'warning', self).exec()

    def handle_post_barcode(self, barcode):
        # Logic for barcode scan on post-payment page
        tx = self.transaction_manager.get_transaction_by_barcode(barcode)
        if tx:
            dialog = PostPaymentOptionDialog(tx, self)
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
