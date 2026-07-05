import os
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QTextBrowser, QAbstractItemView,
                             QComboBox, QLineEdit, QDateEdit, QTimeEdit, QGridLayout, QAbstractSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime
from PyQt6.QtGui import QColor
import styles


class ReceiptInquiryPage(QWidget):
    backRequested = pyqtSignal()
    
    def __init__(self, transaction_manager, receipt_manager, product_manager, parent=None):
        super().__init__(parent)
        self.tm = transaction_manager
        self.rm = receipt_manager
        self.pm = product_manager
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
        
        lbl_title = QLabel("영수증조회")
        lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        lbl_breadcrumb = QLabel("통합조회 > 영수증조회")
        lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #777;")
        header_layout.addWidget(lbl_breadcrumb)
        main_layout.addWidget(header_frame)

        # 2. Main Content
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # --- Column 1: Search Conditions Panel ---
        search_layout = QVBoxLayout()
        lbl_search_title = QLabel("조회조건 입력")
        lbl_search_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: white; background-color: #2D3E50; padding: 6px; border-top-left-radius: 5px; border-top-right-radius: 5px;")
        lbl_search_title.setFixedHeight(40)
        lbl_search_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_layout.addWidget(lbl_search_title)
        
        form_frame = QFrame()
        form_frame.setObjectName("FormFrame")
        form_frame.setStyleSheet("""
            QFrame#FormFrame {
                background-color: white;
                border: 2px solid #2D3E50;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #333333;
                border: none;
                background: transparent;
            }
            QComboBox, QLineEdit, QDateEdit, QTimeEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 6px;
                padding-right: 6px;
                padding-top: 0px;
                padding-bottom: 0px;
                font-size: 11pt;
                min-height: 38px;
            }
            QDateEdit QLineEdit, QTimeEdit QLineEdit {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                color: #333333;
                min-height: 38px;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus {
                border: 2px solid #7B68EE;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333333;
                selection-background-color: #7B68EE;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2D3E50;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar QLabel {
                color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {
                color: white;
                background-color: transparent;
            }
            QCalendarWidget QAbstractItemView {
                color: #333333;
                background-color: white;
                selection-background-color: #7B68EE;
                selection-color: white;
            }
        """)
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(15)

        # Row 0: POS No
        lbl_pos = QLabel("POS No")
        self.cb_pos = QComboBox()
        self.cb_pos.addItems(["전체", "01"])
        form_layout.addWidget(lbl_pos, 0, 0)
        form_layout.addWidget(self.cb_pos, 0, 1)

        # Row 1: 거래종류
        lbl_tx_type = QLabel("거래종류")
        self.cb_tx_type = QComboBox()
        self.cb_tx_type.addItems(["전체", "현금", "카드", "반품/환불"])
        form_layout.addWidget(lbl_tx_type, 1, 0)
        form_layout.addWidget(self.cb_tx_type, 1, 1)

        # Row 2: 조회번호
        lbl_tx_id = QLabel("조회번호")
        self.txt_tx_id = QLineEdit()
        self.txt_tx_id.setPlaceholderText("바코드/영수증 ID")
        form_layout.addWidget(lbl_tx_id, 2, 0)
        form_layout.addWidget(self.txt_tx_id, 2, 1)

        # Row 3: 영업일자
        lbl_date = QLabel("영업일자")
        date_range_layout = QHBoxLayout()
        date_range_layout.setContentsMargins(0, 0, 0, 0)
        date_range_layout.setSpacing(2)
        
        self.de_start = QDateEdit()
        self.de_start.setCalendarPopup(True)
        self.de_start.setDisplayFormat("yyyy-MM-dd")
        self.de_start.setDate(QDate(2026, 1, 1))
        self.de_start.setMinimumWidth(105)
        self.de_start.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        
        self.de_end = QDateEdit()
        self.de_end.setCalendarPopup(True)
        self.de_end.setDisplayFormat("yyyy-MM-dd")
        self.de_end.setDate(QDate.currentDate())
        self.de_end.setMinimumWidth(105)
        self.de_end.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        
        lbl_tilde1 = QLabel("~")
        lbl_tilde1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_range_layout.addWidget(self.de_start)
        date_range_layout.addWidget(lbl_tilde1)
        date_range_layout.addWidget(self.de_end)
        form_layout.addLayout(date_range_layout, 3, 1)
        form_layout.addWidget(lbl_date, 3, 0)

        # Row 4: 시간대별
        lbl_time = QLabel("시간대별")
        time_range_layout = QHBoxLayout()
        time_range_layout.setContentsMargins(0, 0, 0, 0)
        time_range_layout.setSpacing(2)
        
        self.te_start = QTimeEdit()
        self.te_start.setDisplayFormat("HH:mm")
        self.te_start.setTime(QTime(0, 0))
        self.te_start.setMinimumWidth(105)
        self.te_start.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        
        self.te_end = QTimeEdit()
        self.te_end.setDisplayFormat("HH:mm")
        self.te_end.setTime(QTime(23, 59))
        self.te_end.setMinimumWidth(105)
        self.te_end.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        
        lbl_tilde2 = QLabel("~")
        lbl_tilde2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_range_layout.addWidget(self.te_start)
        time_range_layout.addWidget(lbl_tilde2)
        time_range_layout.addWidget(self.te_end)
        form_layout.addLayout(time_range_layout, 4, 1)
        form_layout.addWidget(lbl_time, 4, 0)

        # Row 5: 금액별
        lbl_amt = QLabel("금액별")
        amt_range_layout = QHBoxLayout()
        amt_range_layout.setContentsMargins(0, 0, 0, 0)
        amt_range_layout.setSpacing(2)
        
        self.txt_amt_min = QLineEdit("0")
        self.txt_amt_min.setMinimumWidth(105)
        self.txt_amt_max = QLineEdit("9999999")
        self.txt_amt_max.setMinimumWidth(105)
        
        lbl_tilde3 = QLabel("~")
        lbl_tilde3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amt_range_layout.addWidget(self.txt_amt_min)
        amt_range_layout.addWidget(lbl_tilde3)
        amt_range_layout.addWidget(self.txt_amt_max)
        form_layout.addLayout(amt_range_layout, 5, 1)
        form_layout.addWidget(lbl_amt, 5, 0)

        # Row 6: 상품바코드1
        lbl_barcode1 = QLabel("상품바코드1")
        bc1_layout = QHBoxLayout()
        self.txt_barcode1 = QLineEdit()
        self.txt_barcode1.setPlaceholderText("바코드")
        btn_search_p1 = QPushButton("검색")
        btn_search_p1.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; border-radius: 4px; padding: 8px 10px; font-size: 11pt;")
        btn_search_p1.clicked.connect(lambda: self.search_product_for_field(self.txt_barcode1))
        bc1_layout.addWidget(self.txt_barcode1, stretch=7)
        bc1_layout.addWidget(btn_search_p1, stretch=3)
        form_layout.addLayout(bc1_layout, 6, 1)
        form_layout.addWidget(lbl_barcode1, 6, 0)

        # Row 7: 상품바코드2
        lbl_barcode2 = QLabel("상품바코드2")
        bc2_layout = QHBoxLayout()
        self.txt_barcode2 = QLineEdit()
        self.txt_barcode2.setPlaceholderText("바코드")
        btn_search_p2 = QPushButton("검색")
        btn_search_p2.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; border-radius: 4px; padding: 8px 10px; font-size: 11pt;")
        btn_search_p2.clicked.connect(lambda: self.search_product_for_field(self.txt_barcode2))
        bc2_layout.addWidget(self.txt_barcode2, stretch=7)
        bc2_layout.addWidget(btn_search_p2, stretch=3)
        form_layout.addLayout(bc2_layout, 7, 1)
        form_layout.addWidget(lbl_barcode2, 7, 0)

        # Row 8: 조회 버튼
        self.btn_query = QPushButton("조회")
        self.btn_query.setStyleSheet("""
            QPushButton {
                background-color: #7B68EE;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #634FD9;
            }
        """)
        self.btn_query.clicked.connect(self.on_search_clicked)
        form_layout.addWidget(self.btn_query, 8, 0, 1, 2)
        
        search_layout.addWidget(form_frame)
        content_layout.addLayout(search_layout, stretch=5)

        # --- Column 2: Receipt Preview ---
        left_layout = QVBoxLayout()
        lbl_receipt_title = QLabel("영수증")
        lbl_receipt_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background-color: #2D3E50; padding: 10px; border-top-left-radius: 5px; border-top-right-radius: 5px;")
        left_layout.addWidget(lbl_receipt_title)
        
        self.receipt_view = QTextBrowser()
        self.receipt_view.setStyleSheet("background-color: white; border: 2px solid #2D3E50; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px;")
        left_layout.addWidget(self.receipt_view)
        
        content_layout.addLayout(left_layout, stretch=3)

        # --- Column 3: Transaction Table ---
        right_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["NO", "POS", "거래 시간", "거래 형태", "금 액"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #333;
                border: 1px solid #DEE2E6;
                font-size: 12pt;
            }
            QHeaderView::section {
                background-color: #E9ECEF;
                color: #333;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #DEE2E6;
            }
            QTableWidget::item:selected {
                background-color: #7AB800;
                color: white;
            }
        """)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        right_layout.addWidget(self.table)
        
        # Add instruction label at the bottom of the table
        lbl_info = QLabel("※ 조회 번호에 해당 라인을 입력 후 [반복/입력]키를 누르거나 화면에서 해당 항목을 선택하시면 왼쪽에 선택된 영수증 팝업이 보여집니다.")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("font-size: 10pt; color: #555555; margin-top: 10px;")
        right_layout.addWidget(lbl_info)
        
        content_layout.addLayout(right_layout, stretch=4)
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
        
        btn_temp_receipt = QPushButton("간이영수증출력")
        btn_temp_receipt.setFixedSize(220, 65)
        btn_temp_receipt.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 15pt; border-radius: 5px;")
        bottom_layout.addWidget(btn_temp_receipt)
        
        bottom_layout.addStretch()
        
        btn_print = QPushButton("인쇄")
        btn_print.setFixedSize(180, 65)
        btn_print.setStyleSheet("background-color: #6C757D; color: white; font-weight: bold; font-size: 15pt; border-radius: 5px;")
        btn_print.clicked.connect(self.print_selected_receipt)
        bottom_layout.addWidget(btn_print)
        
        main_layout.addWidget(bottom_frame)

    def load_transactions(self):
        import datetime
        transactions = self.tm.get_all_transactions()
        
        # Parse inputs
        pos_filter = self.cb_pos.currentText()
        tx_type_filter = self.cb_tx_type.currentText()
        tx_id_filter = self.txt_tx_id.text().strip().lower()
        
        qstart_date = self.de_start.date()
        start_date = datetime.date(qstart_date.year(), qstart_date.month(), qstart_date.day())
        qend_date = self.de_end.date()
        end_date = datetime.date(qend_date.year(), qend_date.month(), qend_date.day())
        
        qstart_time = self.te_start.time()
        start_time = datetime.time(qstart_time.hour(), qstart_time.minute(), qstart_time.second())
        qend_time = self.te_end.time()
        end_time = datetime.time(qend_time.hour(), qend_time.minute(), qend_time.second())
        
        try:
            min_amt = int(self.txt_amt_min.text().strip())
        except ValueError:
            min_amt = 0
            
        try:
            max_amt = int(self.txt_amt_max.text().strip())
        except ValueError:
            max_amt = 9999999
            
        barcode1 = self.txt_barcode1.text().strip()
        barcode2 = self.txt_barcode2.text().strip()
        
        # Resolve names for barcodes
        p1_name = ""
        if barcode1:
            p1 = self.pm.get_product(barcode1)
            if p1:
                p1_name = p1.get("name", "").lower()
            else:
                p1_name = barcode1.lower()
                
        p2_name = ""
        if barcode2:
            p2 = self.pm.get_product(barcode2)
            if p2:
                p2_name = p2.get("name", "").lower()
            else:
                p2_name = barcode2.lower()
                
        filtered = []
        for tx in transactions:
            ts_str = tx.get("timestamp", "")
            try:
                dt = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                tx_date = dt.date()
                tx_time = dt.time()
            except Exception:
                continue
                
            # Date range check
            if not (start_date <= tx_date <= end_date):
                continue
                
            # Time range check
            if not (start_time <= tx_time <= end_time):
                continue
                
            # POS No check
            if pos_filter != "전체" and pos_filter != "01":
                continue
                
            # Tx type check
            is_refunded = tx.get("status") == "Refunded"
            method = tx.get("payment_method", "Cash")
            if tx_type_filter == "현금":
                if is_refunded or method != "Cash":
                    continue
            elif tx_type_filter == "카드":
                if is_refunded or method != "Card":
                    continue
            elif tx_type_filter == "반품/환불":
                if not is_refunded:
                    continue
                    
            # Tx Barcode/ID search
            if tx_id_filter:
                tx_barcode = tx.get("tx_barcode", "").lower()
                payment_details = tx.get("payment_details", {})
                card_number = payment_details.get("card_number", "").lower() if payment_details else ""
                receipt_id = payment_details.get("receipt_id", "").lower() if payment_details else ""
                
                if tx_id_filter not in tx_barcode and tx_id_filter not in card_number and tx_id_filter not in receipt_id:
                    continue
                    
            # Amount range check
            amt = tx.get("total_amt", 0)
            if not (min_amt <= amt <= max_amt):
                continue
                
            # Product barcodes check
            tx_items = tx.get("items", [])
            item_names = [it.get("name", "").lower() for it in tx_items]
            
            if barcode1 and p1_name not in item_names:
                continue
            if barcode2 and p2_name not in item_names:
                continue
                
            filtered.append(tx)
            
        self.transactions = filtered
        self.table.setRowCount(len(self.transactions))
        
        from PyQt6.QtGui import QColor
        for i, tx in enumerate(self.transactions):
            self.table.setItem(i, 0, QTableWidgetItem(str(len(self.transactions) - i)))
            self.table.setItem(i, 1, QTableWidgetItem("01"))
            self.table.setItem(i, 2, QTableWidgetItem(tx.get("timestamp", "")))
            
            is_refunded = tx.get("status") == "Refunded"
            method = tx.get("payment_method", "Cash")
            method_text = "현금" if method == "Cash" else "카드"
            if is_refunded:
                method_text += "/환불됨"
            self.table.setItem(i, 3, QTableWidgetItem(method_text))
            
            amt = tx.get("total_amt", 0)
            self.table.setItem(i, 4, QTableWidgetItem(f"{amt:,}"))
            
            for col in range(5):
                item = self.table.item(i, col)
                if is_refunded:
                    item.setForeground(QColor("#D32F2F"))
                
                if col == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        
        if self.transactions:
            self.table.selectRow(0)
        else:
            self.receipt_view.clear()

    def on_search_clicked(self):
        self.load_transactions()

    def search_product_for_field(self, line_edit):
        from ui_components import ProductInquiryDialog
        dialog = ProductInquiryDialog(self.pm, sales_mode=False, parent=self)
        if dialog.exec():
            barcode = dialog.get_selected_barcode()
            if barcode:
                line_edit.setText(barcode)

    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        tx_data = self.transactions[row]
        html = self.rm.generate_html(tx_data)
        self.receipt_view.setHtml(html)

    def print_selected_receipt(self):
        from ui_components import ReceiptPreviewDialog
        html = self.receipt_view.toHtml()
        if html:
            ReceiptPreviewDialog(html, self).exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_transactions()
