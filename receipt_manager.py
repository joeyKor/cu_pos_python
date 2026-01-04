import datetime
import json
import os

class ReceiptManager:
    def __init__(self, store_name="CU 화도오월점"):
        self.config_path = "store_info.json"
        self.default_info = {
            "store_name": "CU 화도오월점",
            "biz_num": "8522100347",
            "address": "경기도 남양주시 화도읍 경춘로1896-8, (녹촌리) 1층",
            "owner": "김하순",
            "tel": "0315115187"
        }
        self.load_store_info()

    def load_store_info(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.store_name = data.get("store_name", self.default_info["store_name"])
                    self.biz_num = data.get("biz_num", self.default_info["biz_num"])
                    self.address = data.get("address", self.default_info["address"])
                    self.owner = data.get("owner", self.default_info["owner"])
                    self.tel = data.get("tel", self.default_info["tel"])
            except Exception as e:
                print(f"Error loading store info: {e}")
                self._set_defaults()
        else:
            self._set_defaults()
            self.save_store_info()

    def _set_defaults(self):
        self.store_name = self.default_info["store_name"]
        self.biz_num = self.default_info["biz_num"]
        self.address = self.default_info["address"]
        self.owner = self.default_info["owner"]
        self.tel = self.default_info["tel"]

    def save_store_info(self):
        data = {
            "store_name": self.store_name,
            "biz_num": self.biz_num,
            "address": self.address,
            "owner": self.owner,
            "tel": self.tel
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving store info: {e}")

    def generate_barcode_base64(self, text):
        try:
            import barcode
            from barcode.writer import ImageWriter
            from io import BytesIO
            import base64
            
            # Use Code 128 for a real, scannable barcode
            code128 = barcode.get('code128', text, writer=ImageWriter())
            
            # Customize writer options for a clean look
            options = {
                'module_height': 5.0,
                'module_width': 0.2,
                'quiet_zone': 3.0,
                'font_size': 0,      # Hide the text as it's displayed separately in HTML
                'text_distance': 0,
            }
            
            fp = BytesIO()
            code128.write(fp, options=options)
            
            return f"data:image/png;base64,{base64.b64encode(fp.getvalue()).decode()}"
        except Exception as e:
            print(f"Real Barcode gen error: {e}")
            # Fallback to visual-only if something goes wrong
            return self._fallback_barcode_gen(text)

    def _fallback_barcode_gen(self, text):
        try:
            from PyQt6.QtGui import QImage, QPainter, QColor
            from PyQt6.QtCore import QBuffer, QIODevice, Qt
            
            width = 400
            height = 80
            image = QImage(width, height, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            
            painter = QPainter(image)
            painter.setBrush(QColor(0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            
            x = 30
            for char in text:
                val = int(char) if char.isdigit() else 5
                pattern = bin(val + 16)[-5:]
                for bit in pattern:
                    if bit == '1':
                        painter.drawRect(x, 10, 3, 60)
                        x += 5
                    else:
                        x += 3
                x += 2
            painter.end()
            
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            image.save(buffer, "PNG")
            return f"data:image/png;base64,{bytes(buffer.data().toBase64()).decode()}"
        except:
            return ""

    def generate_html(self, transaction_data):
        timestamp = transaction_data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        items = transaction_data.get("items", [])
        total_amt = transaction_data.get("total_amt", 0)
        payment_method = transaction_data.get("payment_method", "Card")
        received_amt = transaction_data.get("received_amt", total_amt)
        change_amt = transaction_data.get("change_amt", 0)
        payment_details = transaction_data.get("payment_details", {})

        # Calculate taxes (10% VAT included in total)
        vat = int(total_amt * 0.1 / 1.1)
        taxable_amt = total_amt - vat

        items_html = ""
        for item in items:
            name = item.get("name", "Unknown")
            qty = item.get("qty", 1)
            price = item.get("price", 0)
            subtotal = price * qty
            items_html += f"""
            <tr>
                <td class="col-name">{name}</td>
                <td class="col-qty">{qty}</td>
                <td class="col-amt">{subtotal:,}</td>
            </tr>
            """

        # Payment Specifics
        payment_info_html = ""
        if payment_method == "Card":
            card_num = payment_details.get("card_number", "4854-79**-****-0348")
            if len(card_num) == 12:
                card_num = f"{card_num[:4]}-{card_num[4:6]}**-****-{card_num[10:]}"
            payment_info_html = f"""
            <tr><td colspan="3" style="border-top: 1px dashed #000; padding: 5px 0 0 0;"></td></tr>
            <tr>
                <td class="bold">신 용 카 드</td>
                <td colspan="2" class="col-amt bold">{total_amt:,}</td>
            </tr>
            <tr><td colspan="3" class="center">********* 신 용 카 드 *********</td></tr>
            <tr><td colspan="3">카드번호: {card_num}</td></tr>
            <tr><td colspan="3">승인번호: {datetime.datetime.now().strftime("%H%M%S%f")[:8]}</td></tr>
            <tr>
                <td>결제금액:</td>
                <td colspan="2" class="col-amt">{total_amt:,}</td>
            </tr>
            """
        else: # Cash
            receipt_id = payment_details.get("receipt_id", "")
            payment_info_html = f"""
            <tr><td colspan="3" style="border-top: 1px dashed #000; padding: 5px 0 0 0;"></td></tr>
            <tr>
                <td class="bold">현 금</td>
                <td colspan="2" class="col-amt bold">{received_amt:,}</td>
            </tr>
            <tr>
                <td>거스름돈:</td>
                <td colspan="2" class="col-amt">{change_amt:,}</td>
            </tr>
            {"<tr><td colspan='3'>현금영수증: " + receipt_id + "</td></tr>" if receipt_id else ""}
            """

        # Barcode Logic
        tx_barcode = transaction_data.get("tx_barcode", "92019072427083018679")
        barcode_base64 = self.generate_barcode_base64(tx_barcode)

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Malgun Gothic', sans-serif; font-size: 9pt; line-height: 1.2; width: 300px; padding: 5px; color: #000; background-color: #fff; }}
                .center {{ text-align: center; }}
                .bold {{ font-weight: bold; }}
                .logo {{ font-size: 24pt; font-weight: 900; }}
                .again {{ border: 2px solid #000; border-radius: 12px; padding: 1px 8px; font-size: 14pt; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 5px; table-layout: fixed; }}
                td {{ vertical-align: middle; padding: 1px 0; }}
                .col-name {{ width: 60%; text-align: left; overflow: hidden; }}
                .col-qty {{ width: 15%; text-align: left; padding-left: 5px; }}
                .col-amt {{ width: 25%; text-align: right; }}
                .dashed-line {{ border-top: 1px dashed #000; }}
                .solid-line {{ border-top: 2px solid #000; }}
            </style>
        </head>
        <body>
            <div class="center">
                <span class="logo">CU</span> <span class="again">Again</span>
            </div>
            <div class="center" style="margin-top: 8px; font-weight: bold;">
                ******* 최근영수증발행인쇄 *******
            </div>
            <div style="margin-top: 5px;">
                {self.store_name}<br>
                사업자등록번호: {self.biz_num}<br>
                {self.address}<br>
                {self.owner} TEL: {self.tel}
            </div>
            <div style="margin: 8px 0; font-size: 8pt; line-height: 1.3;">
                정부 방침에 의해 12년 7월 1일부터 현금 결제 취소시, 영수증이 없으면 교환/환불이 불가합니다.
            </div>
            <div>
                {timestamp} &nbsp; POS-01
            </div>

            <table>
                <thead>
                    <tr>
                        <th class="col-name" style="text-align: left; border-top: 1px dashed #000; border-bottom: 1px dashed #000;">상품명</th>
                        <th class="col-qty" style="text-align: left; border-top: 1px dashed #000; border-bottom: 1px dashed #000; padding-left: 5px;">수량</th>
                        <th class="col-amt" style="text-align: right; border-top: 1px dashed #000; border-bottom: 1px dashed #000;">금액</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                    
                    <!-- Total Purchase Amount with Dividers -->
                    <tr><td colspan="3" class="dashed-line" style="padding-top: 5px;"></td></tr>
                    <tr class="bold" style="font-size: 11pt;">
                        <td>총 구 매 액</td>
                        <td class="col-qty">{len(items)}</td>
                        <td class="col-amt">{total_amt:,}</td>
                    </tr>
                    <tr><td colspan="3" class="dashed-line" style="padding-bottom: 5px;"></td></tr>
                    
                    <!-- Taxes -->
                    <tr style="font-size: 8pt;">
                        <td>부 가 가 액</td>
                        <td colspan="2" class="col-amt">{taxable_amt:,}</td>
                    </tr>
                    <tr style="font-size: 8pt;">
                        <td>부 가 세</td>
                        <td colspan="2" class="col-amt">{vat:,}</td>
                    </tr>
                    
                    <!-- Total Payment -->
                    <tr><td colspan="3" style="padding-top: 5px;"></td></tr>
                    <tr class="bold" style="font-size: 13pt; border-bottom: 2px solid #000;">
                        <td>결 제 금 액</td>
                        <td colspan="2" class="col-amt">{total_amt:,}</td>
                    </tr>
                    
                    {payment_info_html}
                    
                    <!-- Bottom Info -->
                    <tr><td colspan="3" class="dashed-line" style="padding-top: 10px;"></td></tr>
                    <tr>
                        <td colspan="3" class="center" style="font-size: 8pt;">
                            *표시 상품은 부가세 면세 품목 임.<br>
                            환불:30일내 영수증/카드지참시 가능<br>
                            객층:12 담당:이유숙 NO:8679 04:07
                        </td>
                    </tr>
                    
                    <!-- Barcode -->
                    <tr>
                        <td colspan="3" class="center" style="padding-top: 15px;">
                            <img src="{barcode_base64}" width="220" height="40"><br>
                            <span style="font-size: 8pt; letter-spacing: 1px;">{tx_barcode}</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        return html
