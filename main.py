import sys, random, datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLabel, QLineEdit, QGridLayout, QFrame, QAbstractItemView, QPushButton, QStackedWidget, QInputDialog)
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

class POSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CU Retail POS System")
        self.setGeometry(100, 100, 1024, 768) # Standard POS resolution
        
        # Initialize Product Manager and Transaction Manager
        self.product_manager = ProductManager()
        self.transaction_manager = TransactionManager()
        self.receipt_manager = ReceiptManager()
        
        self.tm = self.transaction_manager
        self.rm = self.receipt_manager
        self.wait_slots = [None, None, None]
        
        self.init_ui()

        # Apply Styles
        self.setStyleSheet(styles.MAIN_WINDOW_STYLE)

    def init_ui(self):
        self.cart = [] # List of {"barcode": str, "qty": int}
        
        # Main Stacked Widget
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
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
        # Return to Welcome Page
        self.central_stack.setCurrentIndex(0)

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
        btn_home.setFixedHeight(50)
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
        left_layout = QVBoxLayout()
        
        # Product Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["NO", "상품명", "수량", "단가", "금액", "할인"])
        self.table.setStyleSheet(styles.TABLE_STYLE)
        
        # Table Header Config
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Product Name stretches
        
        # Remove grid lines/Selection behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)  # Match clean look
        
        # Connect Click Event
        self.table.cellClicked.connect(self.open_edit_dialog)
        
        left_layout.addWidget(self.table)
        
        # Total Summary & Input Area
        summary_widget = QWidget()
        summary_widget.setStyleSheet(f"background-color: {styles.GRAY_BG};")
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setContentsMargins(0, 10, 0, 0)

        # Totals Row (Total items, Total Amt, Discount) - This is a bit complex in the image
        # Simplified for now:
        totals_row = QHBoxLayout()
        
        self.lbl_total_qty = QLabel("합계   0")
        self.lbl_total_amt = QLabel("0")
        self.lbl_discount = QLabel("0")
        
        # Style them
        base_style = f"font-size: {styles.FONT_SIZE_MEDIUM}; font-weight: bold; color: {styles.TEXT_COLOR};"
        self.lbl_total_qty.setStyleSheet(base_style)
        self.lbl_total_amt.setStyleSheet(base_style)
        self.lbl_discount.setStyleSheet(base_style + "color: #E57373;")

        totals_row.addWidget(self.lbl_total_qty)
        totals_row.addStretch()
        totals_row.addWidget(self.lbl_total_amt)
        totals_row.addSpacing(20)
        totals_row.addWidget(self.lbl_discount)
        
        summary_layout.addLayout(totals_row)
        
        # Input and Big Total Row
        bottom_summary_layout = QHBoxLayout()
        
        # Input Box
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Scan barcode here...")
        self.input_barcode.setStyleSheet(f"border: none; border-bottom: 3px solid {styles.PRIMARY_PURPLE}; padding: 10px; font-size: {styles.FONT_SIZE_LARGE}; background-color: {styles.WHITE}; color: {styles.TEXT_COLOR};")
        self.input_barcode.setFixedHeight(50)
        self.input_barcode.returnPressed.connect(self.handle_barcode_input)
        self.input_barcode.textChanged.connect(self.on_barcode_text_changed)
        
        # Payment Info
        pay_info_layout = QGridLayout()
        lbl_to_receive = QLabel("받을 금액")
        lbl_to_receive.setStyleSheet(f"font-size: {styles.FONT_SIZE_LARGE}; font-weight: bold; color: {styles.TEXT_COLOR};")
        
        self.lbl_final_price = QLabel("0 원")
        self.lbl_final_price.setStyleSheet(styles.BIG_PRICE_STYLE)
        
        lbl_received = QLabel("결제한 금액    0 원")
        lbl_change = QLabel("거스름돈        0 원")
        lbl_received.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR};")
        lbl_change.setStyleSheet(f"font-size: {styles.FONT_SIZE_MEDIUM}; color: {styles.TEXT_COLOR};")

        pay_info_layout.addWidget(lbl_to_receive, 0, 0)
        pay_info_layout.addWidget(self.lbl_final_price, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
        pay_info_layout.addWidget(lbl_received, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
        pay_info_layout.addWidget(lbl_change, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)

        bottom_summary_layout.addWidget(self.input_barcode, stretch=1)
        bottom_summary_layout.addLayout(pay_info_layout, stretch=1)
        
        summary_layout.addLayout(bottom_summary_layout)
        left_layout.addWidget(summary_widget)
        
        return left_layout

    def create_right_panel(self):
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # Buttons
        btn_affiliate = ActionButton("제휴 할인 및\n포인트 적립/사용", styles.BUTTON_GREEN_STYLE)
        btn_coupon = ActionButton("CU키핑쿠폰 발급", styles.BUTTON_GREEN_STYLE)
        
        btn_card = ActionButton("신용카드", styles.BUTTON_PURPLE_STYLE)
        btn_card.clicked.connect(self.open_card_payment)
        btn_cash = ActionButton("현금", styles.BUTTON_PURPLE_STYLE)
        btn_cash.clicked.connect(self.open_cash_payment)
        btn_mobile_pay = ActionButton("모바일\n(CU머니 번호결제)", styles.BUTTON_PURPLE_STYLE)
        
        btn_pay_select = ActionButton("결제선택", styles.BUTTON_GREEN_STYLE) # Darker green highlight?
        
        # Split Cancel/Wait
        split_btns = QHBoxLayout()
        btn_cancel = ActionButton("전체취소", styles.BUTTON_RED_STYLE)
        btn_cancel.clicked.connect(self.clear_cart)
        
        btn_wait = ActionButton("대기", styles.BUTTON_PURPLE_STYLE.replace(styles.PRIMARY_PURPLE, "#78909C")) # Grayish
        btn_wait.clicked.connect(self.handle_wait_click)
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
        bottom_frame.setFixedHeight(60)
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
            btn.setFixedHeight(40)
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
            ("친환경)CU백색봉투대\n100", "8801000000003"), 
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
                if col in [3, 4, 5]:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                    
        self.table.scrollToBottom()

    def update_totals(self):
        total_qty = sum(item["qty"] for item in self.cart)
        total_amt = 0
        for item in self.cart:
             product = self.product_manager.get_product(item["barcode"])
             if product:
                 total_amt += product["price"] * item["qty"]
        
        self.lbl_total_qty.setText(f"합계   {total_qty}")
        self.lbl_total_amt.setText(f"{total_amt:,}")
        self.lbl_final_price.setText(f"{total_amt:,} 원")
        # Ensure it's large if not already
        self.lbl_final_price.setStyleSheet(styles.BIG_PRICE_STYLE)
        
    def clear_cart(self):
        self.cart = []
        self.update_table_view()
        self.update_totals()
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
        # Calculate total
        total_amt = sum(self.product_manager.get_product(item["barcode"])["price"] * item["qty"] for item in self.cart)
        
        if total_amt == 0:
            dialog = CustomMessageDialog("결제 불가", "결제할 상품이 없습니다.", 'warning', self)
            dialog.exec()
            return
            
        dialog = CreditCardPaymentDialog(total_amt, self)
        if dialog.exec():
            # Save Transaction
            items_data = []
            for item in self.cart:
                prod = self.product_manager.get_product(item["barcode"])
                items_data.append({
                    "name": prod["name"],
                    "qty": item["qty"],
                    "price": prod["price"]
                })
            card_num = dialog.get_card_number()
            tx_barcode = self.generate_tx_barcode()
            
            self.transaction_manager.save_transaction(
                items=items_data,
                total_amt=total_amt,
                payment_method="Card",
                payment_details={"card_number": card_num},
                tx_barcode=tx_barcode
            )
            
            # Show Receipt
            tx_data = {
                "items": items_data,
                "total_amt": total_amt,
                "payment_method": "Card",
                "payment_details": {"card_number": card_num},
                "tx_barcode": tx_barcode
            }
            receipt_html = self.receipt_manager.generate_html(tx_data)
            ReceiptPreviewDialog(receipt_html, self).exec()
            
            self.clear_cart()
            self.update_welcome_history()
            CustomMessageDialog("결제 완료", f"{total_amt:,}원 결제가 완료되었습니다.", 'info', self).exec()

    def open_cash_payment(self):
        # Calculate total
        total_amt = sum(self.product_manager.get_product(item["barcode"])["price"] * item["qty"] for item in self.cart)
        
        if total_amt == 0:
            dialog = CustomMessageDialog("결제 불가", "결제할 상품이 없습니다.", 'warning', self)
            dialog.exec()
            return
            
        # Stage 1: Payment Check
        dlg_pay = CashPaymentDialog(total_amt, self)
        if dlg_pay.exec():
            # Stage 2: Receipt (passed totals)
            dlg_receipt = CashReceiptDialog(total_amt, dlg_pay.received_amount, self)
            if dlg_receipt.exec():
                # Save Transaction
                items_data = []
                for item in self.cart:
                    prod = self.product_manager.get_product(item["barcode"])
                    items_data.append({
                        "name": prod["name"],
                        "qty": item["qty"],
                        "price": prod["price"]
                    })
                received_amt = dlg_pay.received_amount
                change_amt = dlg_receipt.change_amount
                receipt_id = dlg_receipt.get_receipt_id()
                tx_barcode = self.generate_tx_barcode()

                self.transaction_manager.save_transaction(
                    items=items_data,
                    total_amt=total_amt,
                    payment_method="Cash",
                    received_amt=received_amt,
                    change_amt=change_amt,
                    payment_details={"receipt_id": receipt_id},
                    tx_barcode=tx_barcode
                )
                
                # Show Receipt
                tx_data = {
                    "items": items_data,
                    "total_amt": total_amt,
                    "payment_method": "Cash",
                    "received_amt": received_amt,
                    "change_amt": change_amt,
                    "payment_details": {"receipt_id": receipt_id},
                    "tx_barcode": tx_barcode
                }
                receipt_html = self.receipt_manager.generate_html(tx_data)
                ReceiptPreviewDialog(receipt_html, self).exec()

                self.clear_cart()
                self.update_welcome_history()
                
                CustomMessageDialog("결제 완료", f"현금 {total_amt:,}원 결제가 완료되었습니다.\n거스름돈: {change_amt:,}원", 'info', self).exec()

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
        
        # Update Welcome Page UI
        self.welcome_page.update_wait_status(self.wait_slots)
        
        # Switch to Sales Page
        self.central_stack.setCurrentIndex(1)
        self.update_table_view()
        self.update_totals()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Font
    font = app.font()
    font.setFamily(styles.FONT_FAMILY)
    app.setFont(font)
    
    window = POSMainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
