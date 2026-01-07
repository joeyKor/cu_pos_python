import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QTextBrowser, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import styles

class ReceiptInquiryPage(QWidget):
    backRequested = pyqtSignal()
    
    def __init__(self, transaction_manager, receipt_manager, parent=None):
        super().__init__(parent)
        self.tm = transaction_manager
        self.rm = receipt_manager
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

        # --- Left: Receipt Preview ---
        left_layout = QVBoxLayout()
        lbl_receipt_title = QLabel("영수증")
        lbl_receipt_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background-color: #2D3E50; padding: 10px; border-top-left-radius: 5px; border-top-right-radius: 5px;")
        left_layout.addWidget(lbl_receipt_title)
        
        self.receipt_view = QTextBrowser()
        self.receipt_view.setStyleSheet("background-color: white; border: 2px solid #2D3E50; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px;")
        left_layout.addWidget(self.receipt_view)
        
        content_layout.addLayout(left_layout, stretch=4)

        # --- Right: Transaction Table ---
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
        
        content_layout.addLayout(right_layout, stretch=6)
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
        transactions = self.tm.get_all_transactions()
        self.transactions = transactions
        self.table.setRowCount(len(transactions))
        
        for i, tx in enumerate(transactions):
            self.table.setItem(i, 0, QTableWidgetItem(str(len(transactions) - i)))
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
                # Set color to red if refunded
                if is_refunded:
                    from PyQt6.QtGui import QColor
                    item.setForeground(QColor("#D32F2F"))
                
                if col == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        
        if transactions:
            self.table.selectRow(0)

    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        tx_data = self.transactions[row]
        html = self.rm.generate_html(tx_data)
        self.receipt_view.setHtml(html)

    def print_selected_receipt(self):
        # reuse print functionality from ui_components if possible, or simple preview
        from ui_components import ReceiptPreviewDialog
        html = self.receipt_view.toHtml()
        if html:
            ReceiptPreviewDialog(html, self).exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_transactions()
