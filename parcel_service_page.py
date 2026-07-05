import os
import sys
import random
import json
import requests
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGridLayout, 
                             QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QColor, QPixmap, QImage
import styles
from ui_components import CustomMessageDialog

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

ADDRESS_DATABASE = [
    {"zonecode": "06234", "address": "서울특별시 강남구 테헤란로 123", "building": "역삼빌딩", "dong": "역삼동"},
    {"zonecode": "06235", "address": "서울특별시 강남구 테헤란로 201", "building": "아진타워", "dong": "역삼동"},
    {"zonecode": "06240", "address": "서울특별시 강남구 강남대로 342", "building": "역삼동 메디타워", "dong": "역삼동"},
    {"zonecode": "06253", "address": "서울특별시 강남구 도곡로 112", "building": "도곡한신아파트", "dong": "역삼동"},
    {"zonecode": "06123", "address": "서울특별시 강남구 봉은사로 161", "building": "규정빌딩", "dong": "역삼동"},
    {"zonecode": "06620", "address": "서울특별시 서초구 서초대로 301", "building": "법조타워", "dong": "서초동"},
    {"zonecode": "06624", "address": "서울특별시 서초구 강남대로 455", "building": "서초오피스텔", "dong": "서초동"},
    {"zonecode": "06648", "address": "서울특별시 서초구 반포대로 108", "building": "예술의전당", "dong": "서초동"},
    {"zonecode": "06712", "address": "서울특별시 서초구 남부순환로 2420", "building": "서초타운", "dong": "서초동"},
    {"zonecode": "07325", "address": "서울특별시 영등포구 여의대로 108", "building": "파크원타워", "dong": "여의도동"},
    {"zonecode": "07333", "address": "서울특별시 영등포구 의사당대로 1", "building": "국회의사당", "dong": "여의도동"},
    {"zonecode": "07326", "address": "서울특별시 영등포구 국제금융로 10", "building": "국제금융센터(IFC)", "dong": "여의도동"},
    {"zonecode": "07345", "address": "서울특별시 영등포구 여의동로 330", "building": "시범아파트", "dong": "여의도동"},
    {"zonecode": "04175", "address": "서울특별시 마포구 마포대로 56", "building": "한화오벨리스크", "dong": "마포동"},
    {"zonecode": "04157", "address": "서울특별시 마포구 독막로 311", "building": "마포재개발빌딩", "dong": "마포동"},
    {"zonecode": "04117", "address": "서울특별시 마포구 백범로 202", "building": "공덕역센트럴자이", "dong": "공덕동"},
    {"zonecode": "04100", "address": "서울특별시 마포구 굴레방로 13", "building": "아현동래미안", "dong": "아현동"},
    {"zonecode": "03149", "address": "서울특별시 종로구 인사동길 44", "building": "쌈지길", "dong": "인사동"},
    {"zonecode": "03150", "address": "서울특별시 종로구 율곡로 102", "building": "안국빌딩", "dong": "인사동"},
    {"zonecode": "04400", "address": "서울특별시 용산구 독서당로 111", "building": "한남더힐", "dong": "한남동"},
    {"zonecode": "04419", "address": "서울특별시 용산구 이태원로 200", "building": "한남빌딩", "dong": "한남동"},
    {"zonecode": "06015", "address": "서울특별시 강남구 압구정로 402", "building": "청담프라자", "dong": "청담동"},
    {"zonecode": "06018", "address": "서울특별시 강남구 영동대로 741", "building": "청담자이아파트", "dong": "청담동"},
    {"zonecode": "13554", "address": "경기도 성남시 분당구 정자일로 95", "building": "정자네이버타워", "dong": "정자동"},
    {"zonecode": "13561", "address": "경기도 성남시 분당구 성남대로 331", "building": "두산타워", "dong": "정자동"},
    {"zonecode": "13494", "address": "경기도 성남시 분당구 대왕판교로 644", "building": "판교테크노밸리", "dong": "삼평동"},
    {"zonecode": "13487", "address": "경기도 성남시 분당구 판교역로 166", "building": "카카오판교오피스", "dong": "삼평동"},
    {"zonecode": "48058", "address": "부산광역시 해운대구 센텀서로 30", "building": "센텀타워", "dong": "우동"},
    {"zonecode": "48060", "address": "부산광역시 해운대구 마린시티2로 33", "building": "해운대두산위브더제니스", "dong": "우동"},
    {"zonecode": "48110", "address": "부산광역시 해운대구 해운대로 802", "building": "좌동 웅신시네아트", "dong": "좌동"},
    {"zonecode": "42100", "address": "대구광역시 수성구 동대구로 311", "building": "범어타워", "dong": "범어동"},
    {"zonecode": "42112", "address": "대구광역시 수성구 달구벌대로 2450", "building": "범어센트럴푸르지오", "dong": "범어동"},
    {"zonecode": "22003", "address": "인천광역시 연수구 송도과학로 32", "building": "송도테크노파크IT센터", "dong": "송도동"},
    {"zonecode": "22008", "address": "인천광역시 연수구 벤첸로 12", "building": "송도IT타워", "dong": "송도동"}
]

class AddressSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("주소 검색")
        self.resize(550, 520)
        self.selected_address = ""
        self.selected_zonecode = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        lbl_guide = QLabel("🔍 검색할 도로명이나 '동' 이름을 입력하세요.\n(예: 역삼동, 서초대로, 센텀서로 등)")
        lbl_guide.setStyleSheet("font-size: 11pt; font-weight: bold; color: #475569; line-height: 1.4;")
        layout.addWidget(lbl_guide)
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        self.txt_query = QLineEdit()
        self.txt_query.setPlaceholderText("동 또는 도로명 입력... (예: 역삼동, 테헤란로)")
        self.txt_query.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 8px;
                font-size: 11pt;
                min-height: 38px;
            }
            QLineEdit:focus {
                border: 2px solid #7B68EE;
            }
        """)
        self.txt_query.returnPressed.connect(self.perform_search)
        
        btn_search = QPushButton("검색")
        btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #7B68EE;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 4px;
                min-height: 38px;
                padding-left: 15px;
                padding-right: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5A44E5;
            }
        """)
        btn_search.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.txt_query, stretch=1)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)
        
        btn_api_toggle = QPushButton("⚙️ API 승인키 설정")
        btn_api_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_api_toggle.setFixedHeight(28)
        btn_api_toggle.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                font-weight: bold;
                font-size: 9pt;
                border-radius: 4px;
                border: 1px solid #CBD5E1;
                padding-left: 10px;
                padding-right: 10px;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        btn_api_toggle.clicked.connect(self.toggle_api_settings)
        layout.addWidget(btn_api_toggle)
        
        self.api_settings_frame = QFrame()
        self.api_settings_frame.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
            QLabel {
                font-size: 9pt;
                font-weight: bold;
                color: #334155;
                border: none;
                background: transparent;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding-left: 8px;
                font-size: 9pt;
                min-height: 26px;
            }
        """)
        self.api_settings_frame.setVisible(False)
        
        api_grid = QGridLayout(self.api_settings_frame)
        api_grid.setSpacing(8)
        api_grid.setContentsMargins(12, 12, 12, 12)
        
        api_grid.addWidget(QLabel("🔑 행안부 Juso API 키:"), 0, 0)
        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("행안부 도로명주소 API 승인키")
        api_grid.addWidget(self.txt_api_key, 0, 1)
        
        api_btns = QHBoxLayout()
        api_btns.setSpacing(6)
        
        btn_save = QPushButton("저장")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFixedHeight(28)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-weight: bold;
                font-size: 9pt;
                border-radius: 4px;
                padding-left: 15px;
                padding-right: 15px;
                border: none;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_save.clicked.connect(self.save_api_key)
        
        btn_guide = QPushButton("발급 및 도움말")
        btn_guide.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guide.setFixedHeight(28)
        btn_guide.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
                font-size: 9pt;
                border-radius: 4px;
                padding-left: 15px;
                padding-right: 15px;
                border: none;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        btn_guide.clicked.connect(self.show_api_help)
        
        api_btns.addWidget(btn_save)
        api_btns.addWidget(btn_guide)
        api_btns.addStretch()
        
        api_grid.addLayout(api_btns, 1, 0, 1, 2)
        layout.addWidget(self.api_settings_frame)
        
        self.lbl_info = QLabel("💡 API 키를 등록하면 실시간 주소 검색이 활성화됩니다.")
        self.lbl_info.setStyleSheet("color: #475569; font-size: 9pt; font-weight: bold;")
        layout.addWidget(self.lbl_info)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["우편번호", "주소", "건물명"])
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setShowGrid(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #222222;
                gridline-color: #E2E8F0;
                border: 1px solid #CBD5E1;
                font-size: 10pt;
                border-radius: 4px;
            }
            QTableWidget::item {
                color: #222222;
                background-color: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #1E293B;
                padding: 6px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #CBD5E1;
            }
            QTableWidget::item:selected {
                background-color: #EDE9FE;
                color: #1E1B4B;
            }
        """)
        self.table.doubleClicked.connect(self.confirm_selection)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(2, 120)
        
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_select = QPushButton("선택 완료")
        btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 4px;
                min-height: 40px;
                padding-left: 20px;
                padding-right: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_select.clicked.connect(self.confirm_selection)
        
        btn_close = QPushButton("닫기")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 4px;
                min-height: 40px;
                padding-left: 20px;
                padding-right: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        btn_close.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_select)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        self.txt_query.setPlaceholderText("동 또는 도로명 입력... (예: 역삼동, 테헤란로)")
        self.lbl_info.setText("💡 행안부 도로명주소 API를 사용하여 검색합니다.")
        self.load_api_key()

    def toggle_api_settings(self):
        self.api_settings_frame.setVisible(not self.api_settings_frame.isVisible())

    def load_api_key(self):
        config_path = "json/address_api_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.txt_api_key.setText(config.get("juso_api_key", ""))
            except:
                pass

    def save_api_key(self):
        juso_key = self.txt_api_key.text().strip()
        config_path = "json/address_api_config.json"
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            config_data = {
                "juso_api_key": juso_key
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            CustomMessageDialog("성공", "API 설정 정보가 저장되었습니다.", "info", self).exec()
            self.api_settings_frame.setVisible(False)
        except Exception as e:
            CustomMessageDialog("오류", f"설정 저장 중 오류가 발생했습니다: {str(e)}", "warning", self).exec()

    def show_api_help(self):
        import webbrowser
        msg = (
            "🔑 [행안부 도로명주소 API 발급 방법]\n"
            "1. '도로명주소 개발자센터' 접속 (juso.go.kr)\n"
            "2. '검색 API' -> '신청하기' 클릭 (개발용/90일 즉시 발급)"
        )
        webbrowser.open("https://business.juso.go.kr/addrlink/openApi/apiReqst.do")
        CustomMessageDialog("API 승인키 발급 및 도움말", msg, "info", self).exec()

    def perform_search(self):
        query = self.txt_query.text().strip()
        if not query:
            self.display_results(ADDRESS_DATABASE)
            return

        juso_key = ""
        config_path = "json/address_api_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    juso_key = config.get("juso_api_key", "")
            except:
                pass

        if not juso_key:
            self.lbl_info.setText("⚠️ API 키가 없어 로컬 테스트 데이터에서 검색합니다.")
            self.lbl_info.setStyleSheet("color: #E28743; font-size: 9pt; font-weight: bold;")
            self.local_search(query)
            return

        try:
            self.lbl_info.setText("🔍 API 실시간 검색 중...")
            self.lbl_info.setStyleSheet("color: #7B68EE; font-size: 9pt; font-weight: bold;")
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
            
            url = "https://business.juso.go.kr/addrlink/addrLinkApi.do"
            params = {
                "confmKey": juso_key,
                "currentPage": 1,
                "countPerPage": 20,
                "keyword": query,
                "resultType": "json"
            }
            print(f"[Juso API Request] url: {url}, keyword: {query}")
            response = requests.get(url, params=params, timeout=10)
            print(f"[Juso API Response] status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                juso_results = data.get("results", {})
                err_code = juso_results.get("common", {}).get("errorCode", "0")
                err_msg = juso_results.get("common", {}).get("errorMessage", "")
                print(f"[Juso API Response] errorCode: {err_code}, errorMessage: {err_msg}")
                
                if err_code == "0":
                    juso_list = juso_results.get("juso", [])
                    print(f"[Juso API Response] result count: {len(juso_list)}")
                    if juso_list:
                        print(f"[Juso API Response] First result: {juso_list[0]}")
                    
                    if not juso_list:
                        self.lbl_info.setText("❌ 검색 결과가 없습니다.")
                        self.lbl_info.setStyleSheet("color: #EF4444; font-size: 9pt; font-weight: bold;")
                        self.table.setRowCount(0)
                        return
                        
                    results = []
                    for j in juso_list:
                        results.append({
                            "zonecode": j.get("zipNo", ""),
                            "address": j.get("roadAddr", ""),
                            "building": j.get("bdNm", ""),
                            "dong": j.get("emdNm", "")
                        })
                    self.lbl_info.setText(f"✅ 실시간 검색 완료 ({len(results)}건)")
                    self.lbl_info.setStyleSheet("color: #10B981; font-size: 9pt; font-weight: bold;")
                    self.display_results(results)
                else:
                    self.lbl_info.setText(f"❌ API 오류: {err_msg} (로컬 검색으로 전환)")
                    self.lbl_info.setStyleSheet("color: #EF4444; font-size: 9pt; font-weight: bold;")
                    self.local_search(query)
            else:
                self.lbl_info.setText("❌ HTTP 오류 (로컬 검색으로 전환)")
                self.lbl_info.setStyleSheet("color: #EF4444; font-size: 9pt; font-weight: bold;")
                self.local_search(query)
        except Exception as e:
            print(f"[Juso API Error] {e}")
            self.lbl_info.setText("❌ 네트워크 오류 (로컬 검색으로 전환)")
            self.lbl_info.setStyleSheet("color: #EF4444; font-size: 9pt; font-weight: bold;")
            self.local_search(query)

    def local_search(self, query):
        query = query.lower()
        results = []
        for item in ADDRESS_DATABASE:
            if (query in item["dong"].lower() or 
                query in item["address"].lower() or 
                query in item["building"].lower()):
                results.append(item)
                
        if not results and len(query) >= 2:
            results = [
                {"zonecode": "08172", "address": f"서울특별시 마포구 {query} 12길 3", "building": f"{query} 프라자", "dong": query},
                {"zonecode": "08173", "address": f"서울특별시 서초구 {query}대로 55", "building": f"{query} 타워", "dong": query},
                {"zonecode": "48192", "address": f"부산광역시 해운대구 {query}로 189", "building": f"{query} 빌라", "dong": query},
            ]
            
        self.display_results(results)
        
    def display_results(self, items):
        print(f"[Table Debug] display_results called with {len(items)} items")
        self.table.setRowCount(len(items))
        print(f"[Table Debug] Table row count set to {self.table.rowCount()}")
        for r, item in enumerate(items):
            self.table.setItem(r, 0, QTableWidgetItem(item["zonecode"]))
            self.table.setItem(r, 1, QTableWidgetItem(item["address"]))
            self.table.setItem(r, 2, QTableWidgetItem(item["building"]))
            
            item_0 = self.table.item(r, 0)
            item_1 = self.table.item(r, 1)
            item_2 = self.table.item(r, 2)
            print(f"[Table Debug] Row {r} values: zonecode='{item_0.text() if item_0 else 'None'}', address='{item_1.text() if item_1 else 'None'}', building='{item_2.text() if item_2 else 'None'}'")
            
            if item_0:
                item_0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
    def confirm_selection(self):
        row = self.table.currentRow()
        print(f"[Table Debug] confirm_selection called. Current row: {row}")
        if row < 0:
            CustomMessageDialog("알림", "선택된 주소가 없습니다. 주소를 먼저 선택해 주세요.", 'warning', self).exec()
            return
            
        self.selected_zonecode = self.table.item(row, 0).text()
        self.selected_address = self.table.item(row, 1).text()
        
        building = self.table.item(row, 2).text()
        if building and building not in self.selected_address:
            self.selected_address += f" ({building})"
            
        print(f"[Table Debug] confirm_selection success. Selected: {self.selected_zonecode}, {self.selected_address}")
        self.accept()
            
class WaybillPreviewDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("운송장 출력 (Waybill Preview)")
        self.setFixedSize(500, 720)
        self.data = data
        self.init_ui()
        
    def init_ui(self):
        # Dark slate background to look consistent with POS system
        self.setStyleSheet("background-color: #1E293B;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # White paper widget mimicking a thermal waybill
        paper = QFrame()
        paper.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #000000;
                border-radius: 4px;
            }
            QLabel {
                color: #000000;
                border: none;
                background: transparent;
                font-family: 'Malgun Gothic';
            }
        """)
        paper_layout = QVBoxLayout(paper)
        paper_layout.setContentsMargins(15, 15, 15, 15)
        paper_layout.setSpacing(10)
        
        # 1. Header Layout (QR + Title block)
        hdr_layout = QHBoxLayout()
        hdr_layout.setSpacing(12)
        
        # Generate QR code
        qr_lbl = QLabel()
        qr_lbl.setFixedSize(110, 110)
        qr_lbl.setStyleSheet("border: 1px solid #CCCCCC;")
        
        try:
            import qrcode
            from io import BytesIO
            
            qr = qrcode.QRCode(version=1, box_size=5, border=1)
            qr.add_data(f"WAYBILL:{self.data['waybill']}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img._img.save(buffer, format="PNG")
            qimg = QImage.fromData(buffer.getvalue())
            qr_lbl.setPixmap(QPixmap.fromImage(qimg).scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            qr_lbl.setText("QR CODE")
            qr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        hdr_layout.addWidget(qr_lbl)
        
        hdr_txt_layout = QVBoxLayout()
        hdr_txt_layout.setSpacing(4)
        
        lbl_h1 = QLabel("고객보관용/POS스캔용")
        lbl_h1.setStyleSheet("font-size: 13pt; font-weight: bold;")
        
        lbl_h2 = QLabel("운송장은 왼쪽 QR코드로\n꼭 결제(등록)해 주세요\n(영수증은 편의점에서 발급)")
        lbl_h2.setStyleSheet("font-size: 9pt; line-height: 1.3;")
        
        hdr_txt_layout.addWidget(lbl_h1)
        hdr_txt_layout.addWidget(lbl_h2)
        hdr_txt_layout.addStretch()
        
        hdr_layout.addLayout(hdr_txt_layout)
        paper_layout.addLayout(hdr_layout)
        
        # Separator Line
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("background-color: #000000; max-height: 1px; border: none;")
        paper_layout.addWidget(line1)
        
        # 2. Terms & Contact Details
        terms_layout = QVBoxLayout()
        terms_layout.setSpacing(3)
        
        lbl_t1 = QLabel("● 당사는 배송사고 시 공정거래위원회가 정한 약관에 준하여 보상처리합니다.")
        lbl_t2 = QLabel("● 물품가액은 배송사고 시 배상금액의 기준이 됩니다.")
        lbl_t3 = QLabel("● 택배 접수불가 품목의 경우 배송사고 발생 시 보상되지 않습니다.")
        for lbl in [lbl_t1, lbl_t2, lbl_t3]:
            lbl.setStyleSheet("font-size: 7.5pt; font-weight: bold;")
            terms_layout.addWidget(lbl)
            
        terms_layout.addSpacing(6)
        
        lbl_info1 = QLabel(f"배송문의) CJ대한통운 : 1577-1287           운송약관은 후면 참조")
        lbl_info1.setStyleSheet("font-size: 8pt; font-weight: bold;")
        
        lbl_info2 = QLabel("119-86-23709 (주)비지에프네트웍스 서울특별시 강남구 테헤란로56길 85, 24층")
        lbl_info2.setStyleSheet("font-size: 7pt;")
        
        terms_layout.addWidget(lbl_info1)
        terms_layout.addWidget(lbl_info2)
        
        paper_layout.addLayout(terms_layout)
        
        # Separator Line
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: #000000; max-height: 2px; border: none;")
        paper_layout.addWidget(line2)
        
        # 3. Grid details
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Cell border stylesheet helper
        CELL_STYLE = """
            QLabel {
                border: 1px solid #000000;
                padding: 6px;
                font-size: 10pt;
                font-weight: bold;
                background-color: transparent;
            }
        """
        
        def add_cell(text, row, col, rowspan=1, colspan=1):
            lbl = QLabel(text)
            lbl.setStyleSheet(CELL_STYLE)
            lbl.setWordWrap(True)
            grid.addWidget(lbl, row, col, rowspan, colspan)
            
        # Row 0
        add_cell(f"운임 선불 {self.data['fare']:,}원", 0, 0)
        add_cell(f"운송장번호 {self.data['waybill']}", 0, 1)
        
        # Row 1
        add_cell(f"물품가액 {self.data['item_value']:,}원", 1, 0)
        add_cell(f"비고 파손면책 동의함", 1, 1)
        
        # Row 2
        add_cell(f"접수일자 {self.data['date']}", 2, 0)
        add_cell(f"중량 {self.data['weight']}g", 2, 1)
        
        # Row 3
        add_cell(f"받는사람: {self.data['receiver']}\n({self.data['r_addr']})", 3, 0)
        add_cell(f"보내는사람: {self.data['sender']}\n({self.data['s_addr']})", 3, 1)
        
        # Adjust row/column stretch to make cells fill perfectly
        grid.setRowStretch(3, 1) # Give address row more vertical space
        
        paper_layout.addLayout(grid)
        layout.addWidget(paper)
        
        # Print / Close actions
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_print = QPushButton("🖨️ 인쇄 (Print)")
        btn_print.setFixedHeight(45)
        btn_print.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_print.clicked.connect(self.accept)
        
        btn_close = QPushButton("닫기")
        btn_close.setFixedHeight(45)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #5A6268; }
        """)
        btn_close.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_print, stretch=2)
        btn_layout.addWidget(btn_close, stretch=1)
        layout.addLayout(btn_layout)

class AddressBridge(QObject):
    address_selected = pyqtSignal(str, str, str) # target, address, zonecode


class ParcelServicePage(QWidget):
    backRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parcels = [
            {"waybill": "98127389211", "sender": "홍길동", "receiver": "김철수", "item": "의류", "status": "배송 중"},
            {"waybill": "98127389212", "sender": "이영희", "receiver": "박민수", "item": "잡화", "status": "점포 대기"},
            {"waybill": "98127389213", "sender": "최수민", "receiver": "정지호", "item": "도서", "status": "배송 완료"}
        ]
        self.address_bridge = AddressBridge()
        self.address_bridge.address_selected.connect(self.on_address_selected)
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
        
        self.lbl_title = QLabel("택배 서비스")
        self.lbl_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #333;")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        
        self.lbl_breadcrumb = QLabel("통합조회 > 택배")
        self.lbl_breadcrumb.setStyleSheet("font-size: 14pt; color: #7B68EE; font-weight: bold;")
        header_layout.addWidget(self.lbl_breadcrumb)
        main_layout.addWidget(header_frame)
        
        # 2. Stack Widget for screens
        self.stack = QStackedWidget()
        
        self.init_menu_screen()
        self.init_register_screen()
        self.init_track_screen()
        self.init_pickup_screen()
        
        self.stack.addWidget(self.menu_widget)
        self.stack.addWidget(self.register_widget)
        self.stack.addWidget(self.track_widget)
        self.stack.addWidget(self.pickup_widget)
        
        main_layout.addWidget(self.stack, stretch=1)
        
        # 3. Bottom Navigation Frame
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(100)
        bottom_frame.setStyleSheet("background-color: #CAD2D9; border-top: 1px solid #CCC;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(30, 10, 30, 10)
        
        self.btn_back = QPushButton("◀  이전 [CLEAR]")
        self.btn_back.setFixedSize(220, 65)
        self.btn_back.setStyleSheet("background-color: #2D3E50; color: white; font-weight: bold; font-size: 15pt; border-radius: 5px;")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.handle_back_action)
        
        bottom_layout.addWidget(self.btn_back)
        bottom_layout.addStretch()
        main_layout.addWidget(bottom_frame)
        
        self.show_menu()
        
    def handle_back_action(self):
        if self.stack.currentIndex() != 0:
            self.show_menu()
        else:
            self.backRequested.emit()
            
    def show_menu(self):
        self.lbl_title.setText("택배 서비스")
        self.lbl_breadcrumb.setText("통합조회 > 택배")
        self.stack.setCurrentIndex(0)
        
    def show_register(self):
        self.lbl_title.setText("택배 접수")
        self.lbl_breadcrumb.setText("택배 > 택배 접수")
        self.txt_s_name.clear()
        self.txt_s_tel.clear()
        self.txt_s_addr.clear()
        self.txt_s_detail.clear()
        self.txt_r_name.clear()
        self.txt_r_tel.clear()
        self.txt_r_addr.clear()
        self.txt_r_detail.clear()
        self.txt_item_value.clear()
        self.txt_weight.setText("0")
        self.lbl_fare.setText("기본 운임: 0 원")
        self.stack.setCurrentIndex(1)
        
    def show_track(self):
        self.lbl_title.setText("택배 조회")
        self.lbl_breadcrumb.setText("택배 > 조회")
        self.txt_track_search.clear()
        self.load_parcel_table()
        self.stack.setCurrentIndex(2)
        
    def show_pickup(self):
        self.lbl_title.setText("택배 픽업")
        self.lbl_breadcrumb.setText("택배 > 택배 픽업")
        self.txt_pickup_code.clear()
        self.lbl_pickup_status.setText("픽업 대기 운송장 번호를 입력하세요.")
        self.stack.setCurrentIndex(3)
        
    def init_menu_screen(self):
        self.menu_widget = QWidget()
        layout = QVBoxLayout(self.menu_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.addStretch(1)
        
        menu_content = QHBoxLayout()
        menu_content.setSpacing(35)
        menu_content.addStretch(1)
        
        def create_menu_card(title, icon, accent_color, index):
            card = QFrame()
            card.setFixedSize(260, 360)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {accent_color};
                    border-radius: 12px;
                }}
            """)
            card_lyt = QVBoxLayout(card)
            card_lyt.setContentsMargins(0, 30, 0, 0)
            card_lyt.setSpacing(20)
            
            # Circle Icon
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedSize(110, 110)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(f"""
                background-color: {accent_color};
                color: white;
                font-size: 45pt;
                border-radius: 55px;
                border: none;
            """)
            card_lyt.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Title
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("font-size: 22pt; font-weight: bold; color: #333333; border: none; background: transparent;")
            card_lyt.addWidget(title_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            card_lyt.addStretch()
            
            # Bottom select bar
            bottom_bar = QLabel("선택하기")
            bottom_bar.setFixedHeight(60)
            bottom_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bottom_bar.setStyleSheet(f"""
                background-color: {accent_color};
                color: white;
                font-size: 16pt;
                font-weight: bold;
                border: none;
                border-top: 1px solid {accent_color};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            """)
            card_lyt.addWidget(bottom_bar)
            
            card.mousePressEvent = lambda e, idx=index: self.menu_card_selected(idx)
            return card
            
        card_register = create_menu_card("택배 접수", "🎁", "#8BC34A", 1)
        card_track = create_menu_card("조회", "🔍", "#FF8A65", 2)
        card_pickup = create_menu_card("택배 픽업", "📦", "#7B68EE", 3)
        
        menu_content.addWidget(card_register)
        menu_content.addWidget(card_track)
        menu_content.addWidget(card_pickup)
        menu_content.addStretch(1)
        
        layout.addLayout(menu_content)
        layout.addStretch(1)
        
    def menu_card_selected(self, index):
        if index == 1:
            self.show_register()
        elif index == 2:
            self.show_track()
        elif index == 3:
            self.show_pickup()
            
    def init_register_screen(self):
        self.register_widget = QWidget()
        layout = QHBoxLayout(self.register_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Left Panel (Input Form)
        left_frame = QFrame()
        left_frame.setObjectName("left_frame")
        left_frame.setStyleSheet("""
            QFrame#left_frame {
                background-color: white;
                border: 1px solid #DEE2E6;
                border-radius: 8px;
            }
        """)
        left_layout = QGridLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(10)
        
        LBL_STYLE = "font-size: 11pt; font-weight: bold; color: #475569;"
        INPUT_STYLE = """
            QLineEdit {
                background-color: white;
                color: #333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 8px;
                font-size: 11pt;
                min-height: 38px;
            }
            QLineEdit:focus {
                border: 2px solid #7B68EE;
            }
        """
        
        # Sender Details
        lbl_s_sec = QLabel("📌 보내는 사람 정보")
        lbl_s_sec.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2D3E50;")
        left_layout.addWidget(lbl_s_sec, 0, 0, 1, 2)
        
        lbl_s_name = QLabel("이름")
        lbl_s_name.setStyleSheet(LBL_STYLE)
        self.txt_s_name = QLineEdit()
        self.txt_s_name.setStyleSheet(INPUT_STYLE)
        left_layout.addWidget(lbl_s_name, 1, 0)
        left_layout.addWidget(self.txt_s_name, 1, 1)
        
        lbl_s_tel = QLabel("전화번호")
        lbl_s_tel.setStyleSheet(LBL_STYLE)
        self.txt_s_tel = QLineEdit()
        self.txt_s_tel.setStyleSheet(INPUT_STYLE)
        self.txt_s_tel.setPlaceholderText("예: 010-1234-5678")
        left_layout.addWidget(lbl_s_tel, 2, 0)
        left_layout.addWidget(self.txt_s_tel, 2, 1)
        
        lbl_s_addr = QLabel("주소")
        lbl_s_addr.setStyleSheet(LBL_STYLE)
        
        s_addr_layout = QHBoxLayout()
        s_addr_layout.setContentsMargins(0, 0, 0, 0)
        s_addr_layout.setSpacing(5)
        
        self.txt_s_addr = QLineEdit()
        self.txt_s_addr.setStyleSheet(INPUT_STYLE)
        
        self.btn_s_addr_search = QPushButton("주소 검색")
        self.btn_s_addr_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_s_addr_search.setStyleSheet("""
            QPushButton {
                background-color: #7B68EE;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                border-radius: 4px;
                min-height: 38px;
                padding-left: 10px;
                padding-right: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5A44E5;
            }
        """)
        self.btn_s_addr_search.clicked.connect(lambda: self.start_address_search('sender'))
        
        s_addr_layout.addWidget(self.txt_s_addr, stretch=1)
        s_addr_layout.addWidget(self.btn_s_addr_search)
        
        left_layout.addWidget(lbl_s_addr, 3, 0)
        left_layout.addLayout(s_addr_layout, 3, 1)
        
        # Sender Detail (상세 주소)
        lbl_s_detail = QLabel("상세 주소")
        lbl_s_detail.setStyleSheet(LBL_STYLE)
        self.txt_s_detail = QLineEdit()
        self.txt_s_detail.setStyleSheet(INPUT_STYLE)
        self.txt_s_detail.setPlaceholderText("상세 주소 입력 (동, 호수, 빌딩명 등)")
        left_layout.addWidget(lbl_s_detail, 4, 0)
        left_layout.addWidget(self.txt_s_detail, 4, 1)
        
        # Receiver Details
        lbl_r_sec = QLabel("📌 받는 사람 정보")
        lbl_r_sec.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2D3E50; margin-top: 10px;")
        left_layout.addWidget(lbl_r_sec, 5, 0, 1, 2)
        
        lbl_r_name = QLabel("이름")
        lbl_r_name.setStyleSheet(LBL_STYLE)
        self.txt_r_name = QLineEdit()
        self.txt_r_name.setStyleSheet(INPUT_STYLE)
        left_layout.addWidget(lbl_r_name, 6, 0)
        left_layout.addWidget(self.txt_r_name, 6, 1)
        
        lbl_r_tel = QLabel("전화번호")
        lbl_r_tel.setStyleSheet(LBL_STYLE)
        self.txt_r_tel = QLineEdit()
        self.txt_r_tel.setStyleSheet(INPUT_STYLE)
        self.txt_r_tel.setPlaceholderText("예: 010-8765-4321")
        left_layout.addWidget(lbl_r_tel, 7, 0)
        left_layout.addWidget(self.txt_r_tel, 7, 1)
        
        lbl_r_addr = QLabel("주소")
        lbl_r_addr.setStyleSheet(LBL_STYLE)
        
        r_addr_layout = QHBoxLayout()
        r_addr_layout.setContentsMargins(0, 0, 0, 0)
        r_addr_layout.setSpacing(5)
        
        self.txt_r_addr = QLineEdit()
        self.txt_r_addr.setStyleSheet(INPUT_STYLE)
        
        self.btn_r_addr_search = QPushButton("주소 검색")
        self.btn_r_addr_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_r_addr_search.setStyleSheet("""
            QPushButton {
                background-color: #7B68EE;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                border-radius: 4px;
                min-height: 38px;
                padding-left: 10px;
                padding-right: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5A44E5;
            }
        """)
        self.btn_r_addr_search.clicked.connect(lambda: self.start_address_search('receiver'))
        
        r_addr_layout.addWidget(self.txt_r_addr, stretch=1)
        r_addr_layout.addWidget(self.btn_r_addr_search)
        
        left_layout.addWidget(lbl_r_addr, 8, 0)
        left_layout.addLayout(r_addr_layout, 8, 1)
        
        # Receiver Detail (상세 주소)
        lbl_r_detail = QLabel("상세 주소")
        lbl_r_detail.setStyleSheet(LBL_STYLE)
        self.txt_r_detail = QLineEdit()
        self.txt_r_detail.setStyleSheet(INPUT_STYLE)
        self.txt_r_detail.setPlaceholderText("상세 주소 입력 (동, 호수, 빌딩명 등)")
        left_layout.addWidget(lbl_r_detail, 9, 0)
        left_layout.addWidget(self.txt_r_detail, 9, 1)
        
        # Item Details (물품 정보)
        lbl_item_sec = QLabel("📌 물품 정보")
        lbl_item_sec.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2D3E50; margin-top: 10px;")
        left_layout.addWidget(lbl_item_sec, 10, 0, 1, 2)
        
        lbl_item_value = QLabel("물품 가액")
        lbl_item_value.setStyleSheet(LBL_STYLE)
        self.txt_item_value = QLineEdit()
        self.txt_item_value.setStyleSheet(INPUT_STYLE)
        self.txt_item_value.setPlaceholderText("원 단위 입력 (예: 100000)")
        left_layout.addWidget(lbl_item_value, 11, 0)
        left_layout.addWidget(self.txt_item_value, 11, 1)
        
        left_layout.setRowStretch(12, 1)
        
        layout.addWidget(left_frame, stretch=60)
        
        # Right Panel (Weight scale and Confirm)
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: #202D3D; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(25, 25, 25, 25)
        right_layout.setSpacing(15)
        
        lbl_scale_sec = QLabel("⚖️ 중량 및 운임 측정")
        lbl_scale_sec.setStyleSheet("font-size: 14pt; font-weight: bold; color: white; background: transparent;")
        right_layout.addWidget(lbl_scale_sec)
        
        # Scale Display
        scale_box = QFrame()
        scale_box.setFixedHeight(100)
        scale_box.setStyleSheet("background-color: #1E293B; border-radius: 6px;")
        scale_lyt = QHBoxLayout(scale_box)
        scale_lyt.setContentsMargins(20, 10, 20, 10)
        
        lbl_sc_title = QLabel("무게 (Weight)")
        lbl_sc_title.setStyleSheet("color: #94A3B8; font-size: 12pt; font-weight: bold; background: transparent;")
        self.txt_weight = QLineEdit("0")
        self.txt_weight.setReadOnly(True)
        self.txt_weight.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_weight.setStyleSheet("QLineEdit { color: #8BC34A; font-size: 24pt; font-weight: bold; background: transparent; border: none; }")
        lbl_unit = QLabel(" g")
        lbl_unit.setStyleSheet("color: #8BC34A; font-size: 18pt; font-weight: bold; background: transparent;")
        
        scale_lyt.addWidget(lbl_sc_title)
        scale_lyt.addWidget(self.txt_weight)
        scale_lyt.addWidget(lbl_unit)
        right_layout.addWidget(scale_box)
        
        # Quick weight simulate buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        weights = [("200g", 200), ("500g", 500), ("1kg", 1000), ("3kg", 3000), ("5kg", 5000)]
        for label, val in weights:
            btn = QPushButton(label)
            btn.setFixedHeight(35)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D3E50;
                    color: #CBD5E1;
                    font-size: 10pt;
                    font-weight: bold;
                    border: 1px solid #485A6A;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #3F51B5; color: white; }
            """)
            btn.clicked.connect(lambda checked, v=val: self.simulate_weight(v))
            quick_layout.addWidget(btn)
        right_layout.addLayout(quick_layout)
        
        right_layout.addSpacing(10)
        
        # Fare Display Card
        self.lbl_fare = QLabel("기본 운임: 0 원")
        self.lbl_fare.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_fare.setStyleSheet("font-size: 16pt; font-weight: bold; color: white; background-color: #2C1F2D; border: 1px solid #FF8A65; border-radius: 6px; padding: 15px;")
        right_layout.addWidget(self.lbl_fare)
        
        right_layout.addStretch()
        
        # Action Confirm
        self.btn_confirm_reg = QPushButton("접수 완료 (운송장 출력)")
        self.btn_confirm_reg.setFixedHeight(55)
        self.btn_confirm_reg.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_confirm_reg.clicked.connect(self.process_registration)
        right_layout.addWidget(self.btn_confirm_reg)
        
        layout.addWidget(right_frame, stretch=40)
        
    def simulate_weight(self, grams):
        self.txt_weight.setText(str(grams))
        # Standard Korean convenience store parcel fare simulation:
        # <= 350g: 3000 Won
        # <= 1000g: 3500 Won
        # <= 5000g: 4500 Won
        # > 5000g: 6000 Won
        if grams <= 350:
            fare = 3000
        elif grams <= 1000:
            fare = 3500
        elif grams <= 5000:
            fare = 4500
        else:
            fare = 6000
        self.lbl_fare.setText(f"기본 운임: {fare:,} 원")
        
    def process_registration(self):
        if (not self.txt_s_name.text().strip() or not self.txt_r_name.text().strip() or 
            not self.txt_s_tel.text().strip() or not self.txt_r_tel.text().strip() or
            not self.txt_s_addr.text().strip() or not self.txt_r_addr.text().strip()):
            CustomMessageDialog("알림", "보내는 사람 및 받는 사람의 이름, 전화번호, 주소를 모두 입력해 주세요.", 'warning', self).exec()
            return
            
        weight = int(self.txt_weight.text())
        if weight <= 0:
            CustomMessageDialog("알림", "택배 중량을 측정해 주세요.", 'warning', self).exec()
            return
            
        # Parse item value
        val_str = self.txt_item_value.text().strip()
        item_value = 50000
        if val_str:
            try:
                item_value = int(val_str.replace(",", ""))
            except ValueError:
                CustomMessageDialog("알림", "물품 가액은 올바른 숫자로 입력해 주세요.", 'warning', self).exec()
                return
                
        # Calculate fare
        if weight <= 350:
            fare = 3000
        elif weight <= 1000:
            fare = 3500
        elif weight <= 5000:
            fare = 4500
        else:
            fare = 6000
            
        import datetime
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        
        # Generate 12-digit Waybill number starting with 3641
        waybill = "3641" + "".join(str(random.randint(0, 9)) for _ in range(8))
        
        s_addr = self.txt_s_addr.text().strip()
        if self.txt_s_detail.text().strip():
            s_addr += " " + self.txt_s_detail.text().strip()
            
        r_addr = self.txt_r_addr.text().strip()
        if self.txt_r_detail.text().strip():
            r_addr += " " + self.txt_r_detail.text().strip()
            
        new_parcel = {
            "waybill": waybill,
            "sender": self.txt_s_name.text().strip(),
            "receiver": self.txt_r_name.text().strip(),
            "s_addr": s_addr,
            "r_addr": r_addr,
            "item": "일반 소포",
            "status": "점포 대기",
            "fare": fare,
            "item_value": item_value,
            "weight": weight,
            "date": date_str
        }
        self.parcels.append(new_parcel)
        
        self.btn_confirm_reg.setText("⏳ 운송장 발행 중...")
        QTimer.singleShot(1500, lambda: self.complete_registration(new_parcel))
        
    def complete_registration(self, new_parcel):
        self.btn_confirm_reg.setText("접수 완료 (운송장 출력)")
        dialog = WaybillPreviewDialog(new_parcel, self)
        dialog.exec()
        self.show_menu()
        
    def init_track_screen(self):
        self.track_widget = QWidget()
        layout = QVBoxLayout(self.track_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Search bar
        search_lyt = QHBoxLayout()
        search_lyt.setSpacing(10)
        
        self.txt_track_search = QLineEdit()
        self.txt_track_search.setPlaceholderText("운송장 번호 또는 받는 사람 이름을 입력하세요")
        self.txt_track_search.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 10px;
                font-size: 12pt;
                font-weight: bold;
                min-height: 45px;
            }
            QLineEdit:focus { border: 2px solid #7B68EE; }
        """)
        self.txt_track_search.textChanged.connect(self.filter_parcel_table)
        
        btn_track_clr = QPushButton("초기화")
        btn_track_clr.setFixedWidth(100)
        btn_track_clr.setFixedHeight(45)
        btn_track_clr.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #5A6268; }
        """)
        btn_track_clr.clicked.connect(self.txt_track_search.clear)
        
        search_lyt.addWidget(self.txt_track_search, stretch=1)
        search_lyt.addWidget(btn_track_clr)
        layout.addLayout(search_lyt)
        
        # Table of parcels
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["No", "운송장 번호", "보낸 사람", "받는 사람", "배송 상태"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #333333;
                border: 1px solid #DEE2E6;
                font-size: 11pt;
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
                background-color: #EDE9FE;
                color: #1E1B4B;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
    def load_parcel_table(self):
        self.table.setRowCount(len(self.parcels))
        for i, parcel in enumerate(self.parcels):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(parcel["waybill"]))
            self.table.setItem(i, 2, QTableWidgetItem(parcel["sender"]))
            self.table.setItem(i, 3, QTableWidgetItem(parcel["receiver"]))
            
            status_item = QTableWidgetItem(parcel["status"])
            if parcel["status"] == "배송 완료":
                status_item.setForeground(QColor("#10B981"))
            elif parcel["status"] == "점포 대기":
                status_item.setForeground(QColor("#7B68EE"))
            else:
                status_item.setForeground(QColor("#FF8A65"))
            self.table.setItem(i, 4, status_item)
            
            for col in range(5):
                self.table.item(i, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                
    def filter_parcel_table(self, text):
        search_text = text.strip().lower()
        for r in range(self.table.rowCount()):
            waybill_item = self.table.item(r, 1)
            sender_item = self.table.item(r, 2)
            receiver_item = self.table.item(r, 3)
            
            waybill = waybill_item.text().lower() if waybill_item else ""
            sender = sender_item.text().lower() if sender_item else ""
            receiver = receiver_item.text().lower() if receiver_item else ""
            
            if search_text in waybill or search_text in sender or search_text in receiver:
                self.table.setRowHidden(r, False)
            else:
                self.table.setRowHidden(r, True)
                
    def init_pickup_screen(self):
        self.pickup_widget = QWidget()
        layout = QVBoxLayout(self.pickup_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        lbl_guide = QLabel("📦 고객에게 배송 완료된 점포 보관 택배를 픽업 출고합니다.")
        lbl_guide.setStyleSheet("font-size: 13pt; font-weight: bold; color: #475569;")
        layout.addWidget(lbl_guide)
        
        # Form grid
        form_lyt = QHBoxLayout()
        form_lyt.setSpacing(15)
        
        self.txt_pickup_code = QLineEdit()
        self.txt_pickup_code.setPlaceholderText("점포 보관 11자리 운송장 번호를 스캔하거나 입력")
        self.txt_pickup_code.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 10px;
                font-size: 14pt;
                font-weight: bold;
                min-height: 50px;
            }
            QLineEdit:focus { border: 2px solid #7B68EE; }
        """)
        self.txt_pickup_code.textChanged.connect(self.check_pickup_waybill)
        
        form_lyt.addWidget(self.txt_pickup_code, stretch=1)
        layout.addLayout(form_lyt)
        
        # Details box
        self.pickup_card = QFrame()
        self.pickup_card.setFixedHeight(160)
        self.pickup_card.setStyleSheet("QFrame { background-color: white; border: 1px solid #CBD5E1; border-radius: 8px; }")
        self.pickup_card_layout = QVBoxLayout(self.pickup_card)
        self.pickup_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_pickup_status = QLabel("픽업 대기 운송장 번호를 입력하세요.")
        self.lbl_pickup_status.setStyleSheet("font-size: 13pt; font-weight: bold; color: #4B5563; background: transparent; border: none;")
        self.pickup_card_layout.addWidget(self.lbl_pickup_status)
        layout.addWidget(self.pickup_card)
        
        # Confirm Button
        self.btn_confirm_pickup = QPushButton("고객 전달 및 완료 (픽업 처리)")
        self.btn_confirm_pickup.setFixedHeight(60)
        self.btn_confirm_pickup.setEnabled(False)
        self.btn_confirm_pickup.setStyleSheet("""
            QPushButton {
                background-color: #94A3B8;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
        """)
        self.btn_confirm_pickup.clicked.connect(self.process_pickup)
        layout.addWidget(self.btn_confirm_pickup)
        layout.addStretch()
        
    def check_pickup_waybill(self, text):
        code = text.strip()
        found_parcel = None
        for p in self.parcels:
            if p["waybill"] == code:
                found_parcel = p
                break
                
        if found_parcel:
            if found_parcel["status"] == "배송 완료":
                self.lbl_pickup_status.setText(f"❌ 이미 픽업이 완료된 택배입니다. (운송장: {code})")
                self.btn_confirm_pickup.setEnabled(False)
                self.btn_confirm_pickup.setStyleSheet("QPushButton { background-color: #94A3B8; color: white; font-size: 14pt; font-weight: bold; border-radius: 6px; border: none; }")
            else:
                self.lbl_pickup_status.setText(
                    f"✅ 픽업 가능 택배 확인!\n"
                    f"• 보낸사람: {found_parcel['sender']} | 받는사람: {found_parcel['receiver']}\n"
                    f"• 물품종류: {found_parcel['item']} | 현재상태: {found_parcel['status']}"
                )
                self.btn_confirm_pickup.setEnabled(True)
                self.btn_confirm_pickup.setStyleSheet("QPushButton { background-color: #10B981; color: white; font-size: 14pt; font-weight: bold; border-radius: 6px; border: none; } QPushButton:hover { background-color: #059669; }")
        else:
            if len(code) >= 11:
                self.lbl_pickup_status.setText(f"❌ 점포에 보관된 택배 목록에 없는 번호입니다. ({code})")
            else:
                self.lbl_pickup_status.setText("픽업 대기 운송장 번호를 입력하세요.")
            self.btn_confirm_pickup.setEnabled(False)
            self.btn_confirm_pickup.setStyleSheet("QPushButton { background-color: #94A3B8; color: white; font-size: 14pt; font-weight: bold; border-radius: 6px; border: none; }")
            
    def process_pickup(self):
        code = self.txt_pickup_code.text().strip()
        for p in self.parcels:
            if p["waybill"] == code:
                p["status"] = "배송 완료"
                break
                
        self.btn_confirm_pickup.setText("⏳ 출고 승인 처리 중...")
        QTimer.singleShot(1500, lambda: self.complete_pickup(code))
        
    def complete_pickup(self, code):
        self.btn_confirm_pickup.setText("고객 전달 및 완료 (픽업 처리)")
        CustomMessageDialog("성공", f"운송장 [{code}] 택배의 고객 인도가 정상 완료되었습니다.\n전산 출고 승인 완료.", 'info', self).exec()
        self.show_menu()

    def on_address_selected(self, target, address, zonecode):
        display_address = f"[{zonecode}] {address}" if zonecode else address
        if target == 'sender':
            self.txt_s_addr.setText(display_address)
        elif target == 'receiver':
            self.txt_r_addr.setText(display_address)

    def start_address_search(self, target):
        dialog = AddressSearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            address = dialog.selected_address
            zonecode = dialog.selected_zonecode
            self.address_bridge.address_selected.emit(target, address, zonecode)
