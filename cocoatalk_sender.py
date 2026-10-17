import os
import re
import base64
import requests
from typing import Optional, Tuple, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QMessageBox, QWidget, QScrollArea, QApplication
)
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
)
from PyQt6.QtCore import Qt, QBuffer, QIODevice, QRectF

import styles
from ui_components import CustomMessageDialog

PB_BASE_URL = "https://pb.joyfamkr.synology.me"
DUMART_SENDER_EMAIL = "dumart@cocoatalk.com"
DUMART_SENDER_NAME = "DU마트"


class CocoaTalkSender:
    """PocketBase 기반 코코아톡 메시지 연동 클래스"""

    @staticmethod
    def generate_direct_room_id(email1: str, email2: str) -> str:
        """코코아톡의 1:1 대화방 고유 ID 생성 규칙 (알파벳 정렬 후 특수문자 치환)"""
        sorted_emails = sorted([email1.lower().strip(), email2.lower().strip()])
        joined = "_".join(sorted_emails)
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', joined)
        return f"room_{clean}"

    @staticmethod
    def search_user(query: str) -> Optional[Dict[str, Any]]:
        """전화번호 또는 이메일로 cocoa_users 컬렉션에서 사용자 검색"""
        clean_query = query.strip()
        if not clean_query:
            return None

        try:
            if "@" in clean_query:
                # 이메일 검색
                filter_str = f'(email="{clean_query.lower()}")'
            else:
                # 전화번호 검색 (하이픈 포함 및 숫자만 모두 검색)
                digits_only = re.sub(r'[^0-9]', '', clean_query)
                filter_str = f'(phone_number="{clean_query}"||phone_number="{digits_only}")'

            res = requests.get(
                f"{PB_BASE_URL}/api/collections/cocoa_users/records",
                params={"filter": filter_str, "perPage": 1},
                timeout=5
            )
            if res.status_code == 200:
                items = res.json().get("items", [])
                if items:
                    return items[0]
        except Exception as e:
            print(f"[CocoaTalkSender] search_user error: {e}")
            return None

        return None

    @staticmethod
    def render_voucher_pixmap(voucher: dict, target_product: Optional[dict], receipt_manager) -> QPixmap:
        """
        PyQt6 QPainter를 사용하여 코코아톡에 전송할 세련된 모바일 상품권 쿠폰 카드 이미지 생성
        (너비 400 x 높이 600의 고화질 비트맵)
        """
        width, height = 400, 600
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 1. 전체 카드 배경 (화이트 둥근 사각 박스 + 외곽 테두리)
        card_rect = QRectF(4, 4, width - 8, height - 8)
        painter.setPen(QPen(QColor("#E2E8F0"), 1.5))
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawRoundedRect(card_rect, 20.0, 20.0)

        # 2. 상단 헤더 영역 (그라데이션 배경)
        header_height = 190.0
        header_rect = QRectF(4, 4, width - 8, header_height)
        header_grad = QLinearGradient(0, 0, width, header_height)
        header_grad.setColorAt(0.0, QColor("#FF6B6B"))
        header_grad.setColorAt(1.0, QColor("#FF8E53"))

        painter.save()
        # 둥근 모서리 클리핑
        from PyQt6.QtGui import QPainterPath
        header_path = QPainterPath()
        header_path.addRoundedRect(card_rect, 20.0, 20.0)
        painter.setClipPath(header_path)
        painter.fillRect(header_rect, header_grad)

        # 상단 브랜드 텍스트
        painter.setPen(QColor("#FFFFFF"))
        font_brand = QFont("Malgun Gothic", 11, QFont.Weight.Bold)
        font_brand.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        painter.setFont(font_brand)
        painter.drawText(QRectF(20, 16, width - 40, 24), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "DU MART VOUCHER")

        # 상품 이미지 박스 (중앙 흰색 둥근 사각형)
        img_box_size = 120.0
        img_box_x = (width - img_box_size) / 2
        img_box_y = 52.0
        img_box_rect = QRectF(img_box_x, img_box_y, img_box_size, img_box_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawRoundedRect(img_box_rect, 14.0, 14.0)

        # 상품 사진 로드 및 그리기
        target_barcode = voucher.get("product_barcode", "")
        product_img = None
        for ext in ["png", "jpg", "jpeg", "webp"]:
            p = os.path.join(os.path.abspath("."), "photo", f"{target_barcode}.{ext}")
            if os.path.exists(p):
                product_img = QPixmap(p)
                break
        if not product_img:
            for ext in ["png", "jpg", "jpeg"]:
                p = os.path.join(os.path.abspath("."), "assets", f"{target_barcode}.{ext}")
                if os.path.exists(p):
                    product_img = QPixmap(p)
                    break

        if product_img and not product_img.isNull():
            scaled_img = product_img.scaled(
                int(img_box_size - 16), int(img_box_size - 16),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            dest_x = img_box_x + (img_box_size - scaled_img.width()) / 2
            dest_y = img_box_y + (img_box_size - scaled_img.height()) / 2
            painter.drawPixmap(int(dest_x), int(dest_y), scaled_img)
        else:
            # 기본 상품 아이콘/이모지 표시
            painter.setPen(QColor("#FF7A50"))
            painter.setFont(QFont("Segoe UI Emoji", 42))
            painter.drawText(img_box_rect, Qt.AlignmentFlag.AlignCenter, "🎁")

        painter.restore()

        # 3. 바디 정보 영역 (상품명 및 가격)
        cur_y = header_height + 20

        # DU 로고 태그
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(20, cur_y, width - 40, 18), Qt.AlignmentFlag.AlignCenter, "DU 편의점 모바일 교환권")
        cur_y += 24

        # 상품 이름
        product_name = target_product["name"] if target_product else voucher.get("name", "상품권")
        painter.setPen(QColor("#1E293B"))
        painter.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        name_rect = QRectF(25, cur_y, width - 50, 42)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, product_name)
        cur_y += 46

        # 가치 / 가격
        price = voucher.get("price", 0)
        price_str = f"{price:,}원"
        painter.setPen(QColor("#6366F1"))
        painter.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold))
        painter.drawText(QRectF(20, cur_y, width - 40, 22), Qt.AlignmentFlag.AlignCenter, price_str)
        cur_y += 28

        # 4. 점선 구분선
        painter.setPen(QPen(QColor("#CBD5E1"), 1.0, Qt.PenStyle.DashLine))
        painter.drawLine(30, int(cur_y), width - 30, int(cur_y))
        cur_y += 18

        # 5. 바코드 영역
        barcode_num = voucher.get("barcode", "")
        barcode_b64 = receipt_manager.generate_barcode_base64(barcode_num)
        barcode_pixmap = None
        if barcode_b64 and "," in barcode_b64:
            raw_data = base64.b64decode(barcode_b64.split(",")[1])
            barcode_pixmap = QPixmap()
            barcode_pixmap.loadFromData(raw_data)

        # 바코드 배경 흰색 박스
        bc_box_w, bc_box_h = 300.0, 75.0
        bc_box_x = (width - bc_box_w) / 2
        bc_box_rect = QRectF(bc_box_x, cur_y, bc_box_w, bc_box_h)

        painter.setPen(QPen(QColor("#E2E8F0"), 1.0))
        painter.setBrush(QBrush(QColor("#FAFAFA")))
        painter.drawRoundedRect(bc_box_rect, 8.0, 8.0)

        if barcode_pixmap and not barcode_pixmap.isNull():
            scaled_bc = barcode_pixmap.scaled(
                int(bc_box_w - 20), int(bc_box_h - 14),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            bc_draw_x = bc_box_x + (bc_box_w - scaled_bc.width()) / 2
            bc_draw_y = cur_y + (bc_box_h - scaled_bc.height()) / 2
            painter.drawPixmap(int(bc_draw_x), int(bc_draw_y), scaled_bc)
        cur_y += bc_box_h + 10

        # 바코드 13자리 텍스트 (4자리씩 스페이스 구분)
        spaced_bc = " ".join([barcode_num[i:i+4] for i in range(0, len(barcode_num), 4)])
        painter.setPen(QColor("#0F172A"))
        font_num = QFont("Consolas", 14, QFont.Weight.Bold)
        font_num.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        painter.setFont(font_num)
        painter.drawText(QRectF(20, cur_y, width - 40, 24), Qt.AlignmentFlag.AlignCenter, spaced_bc)
        cur_y += 32

        # 6. 하단 유의사항 문구
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Malgun Gothic", 9))
        painter.drawText(QRectF(20, cur_y, width - 40, 18), Qt.AlignmentFlag.AlignCenter, "결제 시 계산대 직원에게 바코드를 제시해 주세요.")
        cur_y += 18
        painter.drawText(QRectF(20, cur_y, width - 40, 16), Qt.AlignmentFlag.AlignCenter, "DU마트 전 매장에서 유효합니다.")

        painter.end()
        return pixmap

    @classmethod
    def send_voucher_to_user(
        cls,
        target_user: Dict[str, Any],
        voucher: Dict[str, Any],
        voucher_pixmap: QPixmap,
        custom_message: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        포켓베이스 cocoa_messages 컬렉션에 쿠폰 카드 이미지 메시지 및 안내 텍스트 발송
        """
        receiver_email = target_user.get("email", "").strip().lower()
        if not receiver_email:
            return False, "수신자 이메일 정보가 올바르지 않습니다."

        receiver_name = target_user.get("nickname") or target_user.get("name") or receiver_email.split("@")[0]

        # 1. 고유 1:1 대화방 ID 생성
        room_id = cls.generate_direct_room_id(DUMART_SENDER_EMAIL, receiver_email)

        # 2. QPixmap을 JPEG Base64로 인코딩
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        voucher_pixmap.save(buffer, "JPEG", quality=85)
        raw_bytes = buffer.data().data()
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        image_uri = f"data:image/jpeg;base64,{b64_str}"

        # 3. 이미지 메시지 발송
        image_payload = {
            "room_id": room_id,
            "sender_email": DUMART_SENDER_EMAIL,
            "sender_name": DUMART_SENDER_NAME,
            "receiver_email": receiver_email,
            "content": image_uri,
            "type": "image",
            "emoticon_asset": "",
            "unread_count": 1
        }

        try:
            img_res = requests.post(
                f"{PB_BASE_URL}/api/collections/cocoa_messages/records",
                json=image_payload,
                timeout=7
            )
            if img_res.status_code not in (200, 201):
                return False, f"이미지 전송 실패 (코드: {img_res.status_code})"

            # 4. 안내 텍스트 메시지 발송
            voucher_name = voucher.get("name", "모바일 상품권")
            guide_text = custom_message.strip() if custom_message and custom_message.strip() else (
                f"☕ [DU마트] {receiver_name}님께 '{voucher_name}' 모바일 상품권이 도착했습니다!\n"
                f"매장 계산대에서 바코드를 스캔하여 바로 교환하실 수 있습니다."
            )

            text_payload = {
                "room_id": room_id,
                "sender_email": DUMART_SENDER_EMAIL,
                "sender_name": DUMART_SENDER_NAME,
                "receiver_email": receiver_email,
                "content": guide_text,
                "type": "text",
                "unread_count": 1
            }

            requests.post(
                f"{PB_BASE_URL}/api/collections/cocoa_messages/records",
                json=text_payload,
                timeout=5
            )

            return True, f"'{receiver_name}'님께 코코아톡으로 모바일 상품권이 성공적으로 발송되었습니다!"

        except Exception as e:
            return False, f"네트워크 통신 중 오류가 발생했습니다: {e}"


class CocoaTalkVoucherDialog(QDialog):
    """모바일 상품권 코코아톡 발송 다이얼로그"""

    def __init__(self, barcode: str, voucher: dict, target_product: Optional[dict], receipt_manager, parent=None):
        super().__init__(parent)
        self.barcode = barcode
        self.voucher = dict(voucher)
        self.voucher["barcode"] = barcode
        self.target_product = target_product
        self.receipt_manager = receipt_manager
        self.target_user = None

        self.setWindowTitle("☕ 코코아톡 모바일 상품권 전송")
        self.setFixedSize(styles.s(820), styles.s(650))
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        # 쿠폰 카드 비트맵 생성
        self.voucher_pixmap = CocoaTalkSender.render_voucher_pixmap(
            self.voucher, self.target_product, self.receipt_manager
        )

        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ---------------- 좌측: 쿠폰 카드 미리보기 ----------------
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)

        lbl_preview_title = QLabel("📱 전송될 쿠폰 이미지 미리보기")
        lbl_preview_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #334155; border: none;")
        left_layout.addWidget(lbl_preview_title)

        self.lbl_preview_img = QLabel()
        self.lbl_preview_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview_img.setStyleSheet("border: none;")

        # 다이얼로그 높이에 맞추어 스케일링된 미리보기 표시
        scaled_preview = self.voucher_pixmap.scaled(
            styles.s(340), styles.s(530),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_preview_img.setPixmap(scaled_preview)
        left_layout.addWidget(self.lbl_preview_img)
        left_layout.addStretch()

        main_layout.addWidget(left_frame)

        # ---------------- 우측: 수신자 검색 및 전송 폼 ----------------
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(22, 22, 22, 22)
        right_layout.setSpacing(14)

        # 상단 타이틀
        lbl_title = QLabel("코코아톡(CocoaTalk) 전송")
        lbl_title.setStyleSheet("font-size: 15pt; font-weight: bold; color: #1E293B; border: none;")
        right_layout.addWidget(lbl_title)

        lbl_desc = QLabel("수신자의 코코아톡 등록 전화번호 또는 이메일을 입력하시면 실시간 대화창으로 모바일 교환권 이미지가 즉시 발송됩니다.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 10pt; color: #64748B; border: none; line-height: 1.4;")
        right_layout.addWidget(lbl_desc)

        # 구분선
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E2E8F0; background-color: #E2E8F0; max-height: 1px; border: none;")
        right_layout.addWidget(sep)

        # 상품권 간략 정보
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #F1F5F9; border-radius: 8px; border: none; padding: 10px;")
        info_layout = QVBoxLayout(info_box)
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(10, 8, 10, 8)

        v_name = self.voucher.get("name", "")
        v_price = self.voucher.get("price", 0)
        v_barcode = self.voucher.get("barcode", "")

        lbl_info_name = QLabel(f"<b>상품권명:</b> {v_name}")
        lbl_info_name.setStyleSheet("font-size: 10.5pt; color: #1E293B; border: none;")
        lbl_info_val = QLabel(f"<b>교환금액:</b> {v_price:,}원  |  <b>바코드:</b> {v_barcode}")
        lbl_info_val.setStyleSheet("font-size: 10pt; color: #475569; border: none;")

        info_layout.addWidget(lbl_info_name)
        info_layout.addWidget(lbl_info_val)
        right_layout.addWidget(info_box)

        # 수신자 입력 라벨 & 행
        lbl_target_input = QLabel("수신자 (전화번호 또는 이메일) *")
        lbl_target_input.setStyleSheet("font-size: 11pt; font-weight: bold; color: #334155; border: none; margin-top: 4px;")
        right_layout.addWidget(lbl_target_input)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.input_target = QLineEdit()
        self.input_target.setPlaceholderText("예: 010-1234-5678 또는 user@email.com")
        self.input_target.setFixedHeight(styles.s(42))
        self.input_target.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 11pt;
                color: #0F172A;
            }
            QLineEdit:focus {
                border: 2px solid #6366F1;
                background-color: #FFFFFF;
            }
        """)
        self.input_target.returnPressed.connect(self.search_receiver)
        input_row.addWidget(self.input_target)

        self.btn_search = QPushButton("회원 조회")
        self.btn_search.setFixedHeight(styles.s(42))
        self.btn_search.setFixedWidth(styles.s(90))
        self.btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #6366F1;
                color: white;
                font-weight: bold;
                font-size: 10.5pt;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4F46E5;
            }
        """)
        self.btn_search.clicked.connect(self.search_receiver)
        input_row.addWidget(self.btn_search)
        right_layout.addLayout(input_row)

        # 조회된 회원 상태 카드
        self.user_card = QFrame()
        self.user_card.setFixedHeight(styles.s(64))
        self.user_card.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px dashed #CBD5E1;
                border-radius: 8px;
            }
        """)
        user_card_layout = QHBoxLayout(self.user_card)
        user_card_layout.setContentsMargins(12, 8, 12, 8)

        self.lbl_user_status = QLabel("전화번호 또는 이메일을 입력 후 [회원 조회]를 눌러주세요.")
        self.lbl_user_status.setStyleSheet("font-size: 10pt; color: #94A3B8; border: none;")
        user_card_layout.addWidget(self.lbl_user_status)
        right_layout.addWidget(self.user_card)

        # 추가 전달 메시지 (선택)
        lbl_msg = QLabel("보내는 메시지 (선택)")
        lbl_msg.setStyleSheet("font-size: 10.5pt; font-weight: bold; color: #334155; border: none; margin-top: 4px;")
        right_layout.addWidget(lbl_msg)

        self.input_msg = QLineEdit()
        self.input_msg.setText(f"🎁 [DU마트] '{v_name}' 상품권이 도착했습니다. 매장에서 교환해 주세요!")
        self.input_msg.setFixedHeight(styles.s(38))
        self.input_msg.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 10px;
                font-size: 10pt;
                color: #334155;
            }
        """)
        right_layout.addWidget(self.input_msg)

        right_layout.addStretch()

        # 하단 액션 버튼 (취소, 전송)
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        btn_cancel = QPushButton("닫기")
        btn_cancel.setFixedHeight(styles.s(44))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        self.btn_send = QPushButton("☕ 코코아톡으로 전송하기")
        self.btn_send.setFixedHeight(styles.s(44))
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #FEE500;
                color: #3C1E1E;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11.5pt;
            }
            QPushButton:hover {
                background-color: #FADA0A;
            }
            QPushButton:disabled {
                background-color: #E2E8F0;
                color: #94A3B8;
            }
        """)
        self.btn_send.setEnabled(False)
        self.btn_send.clicked.connect(self.send_voucher)
        btn_box.addWidget(self.btn_send)

        right_layout.addLayout(btn_box)

        main_layout.addWidget(right_frame)

    def search_receiver(self):
        query = self.input_target.text().strip()
        if not query:
            self.lbl_user_status.setText("⚠️ 전화번호 또는 이메일을 입력해 주세요.")
            self.lbl_user_status.setStyleSheet("font-size: 10pt; color: #EF4444; border: none; font-weight: bold;")
            self.btn_send.setEnabled(False)
            return

        self.lbl_user_status.setText("🔍 코코아톡 회원 정보를 조회 중입니다...")
        self.lbl_user_status.setStyleSheet("font-size: 10pt; color: #6366F1; border: none;")
        QApplication.processEvents()

        user = CocoaTalkSender.search_user(query)
        if user:
            self.target_user = user
            name = user.get("nickname") or user.get("name") or "고객"
            email = user.get("email", "")
            phone = user.get("phone_number", "번호없음")

            self.user_card.setStyleSheet("""
                QFrame {
                    background-color: #F0FDF4;
                    border: 1.5px solid #22C55E;
                    border-radius: 8px;
                }
            """)
            self.lbl_user_status.setText(f"✅ <b>{name}</b> 회원님 확인 완료 ({email} / {phone})")
            self.lbl_user_status.setStyleSheet("font-size: 10.5pt; color: #15803D; border: none;")
            self.btn_send.setEnabled(True)
        else:
            self.target_user = None
            self.user_card.setStyleSheet("""
                QFrame {
                    background-color: #FEF2F2;
                    border: 1.5px solid #EF4444;
                    border-radius: 8px;
                }
            """)
            self.lbl_user_status.setText("❌ 일치하는 코코아톡 회원을 찾을 수 없습니다. (입력정보 확인)")
            self.lbl_user_status.setStyleSheet("font-size: 10pt; color: #B91C1C; border: none; font-weight: bold;")
            self.btn_send.setEnabled(False)

    def send_voucher(self):
        if not self.target_user:
            self.search_receiver()
            if not self.target_user:
                return

        name = self.target_user.get("nickname") or self.target_user.get("name") or "고객"
        v_name = self.voucher.get("name", "상품권")

        # 전송 진행 UI 상태 변경
        self.btn_send.setEnabled(False)
        self.btn_send.setText("⏳ 전송 중...")
        QApplication.processEvents()

        custom_text = self.input_msg.text().strip()
        success, msg = CocoaTalkSender.send_voucher_to_user(
            self.target_user,
            self.voucher,
            self.voucher_pixmap,
            custom_text
        )

        self.btn_send.setText("☕ 코코아톡으로 전송하기")
        self.btn_send.setEnabled(True)

        if success:
            CustomMessageDialog("전송 완료", msg, 'info', self).exec()
            self.accept()
        else:
            CustomMessageDialog("전송 실패", msg, 'error', self).exec()
