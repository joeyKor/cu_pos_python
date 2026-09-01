import json
import os
from datetime import datetime

class TransitCardManager:
    """
    교통카드(T-Money, 캐시비, 레일플러스 등) 데이터 및 잔액 관리자.
    JSON 파일(json/transit_cards.json)을 기반으로 카드의 잔액 충전, 조회, 결제, 환불 및 거래 내역을 관리합니다.
    """
    
    DEFAULT_CARDS = {
        "46d10b9e": {
            "card_id": "46d10b9e",
            "card_name": "Tmoney",
            "card_type": "Tmoney",
            "balance": 10000,
            "created_at": "2026-09-01 09:00:00",
            "updated_at": "2026-09-01 09:00:00",
            "history": []
        },
        "a6081a9e": {
            "card_id": "a6081a9e",
            "card_name": "Tmoney",
            "card_type": "Tmoney",
            "balance": 25000,
            "created_at": "2026-09-01 09:00:00",
            "updated_at": "2026-09-01 09:00:00",
            "history": []
        },
        "b68a039e": {
            "card_id": "b68a039e",
            "card_name": "Tmoney",
            "card_type": "Tmoney",
            "balance": 5000,
            "created_at": "2026-09-01 09:00:00",
            "updated_at": "2026-09-01 09:00:00",
            "history": []
        },
        "d6f5139e": {
            "card_id": "d6f5139e",
            "card_name": "Tmoney",
            "card_type": "Tmoney",
            "balance": 0,
            "created_at": "2026-09-01 09:00:00",
            "updated_at": "2026-09-01 09:00:00",
            "history": []
        },
        "6687109e": {
            "card_id": "6687109e",
            "card_name": "Tmoney",
            "card_type": "Tmoney",
            "balance": 50000,
            "created_at": "2026-09-01 09:00:00",
            "updated_at": "2026-09-01 09:00:00",
            "history": []
        },
        "a623f59d": {
            "card_id": "a623f59d",
            "card_name": "Tmoney",
            "card_type": "Tmoney",
            "balance": 13000,
            "created_at": "2026-09-01 09:00:00",
            "updated_at": "2026-09-01 09:00:00",
            "history": []
        }
    }

    def __init__(self, file_path=None):
        os.makedirs("json", exist_ok=True)
        self.file_path = file_path or os.path.join("json", "transit_cards.json")
        self.cards = {}
        self._load_cards()

    def _load_cards(self):
        """JSON 파일에서 카드 데이터를 불러옵니다. 없으면 기본 데이터를 생성합니다."""
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            self.cards = dict(self.DEFAULT_CARDS)
            self._save_cards()
        else:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.cards = json.load(f)
                # 카드 종류 및 이름 Tmoney로 일원화
                for cid, cinfo in self.cards.items():
                    cinfo["card_name"] = "Tmoney"
                    cinfo["card_type"] = "Tmoney"
                self._save_cards()
            except Exception as e:
                print(f"[TransitCardManager] Error loading JSON: {e}")
                self.cards = dict(self.DEFAULT_CARDS)
                self._save_cards()

    def _save_cards(self):
        """현재 카드 데이터를 JSON 파일에 저장합니다."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.cards, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"[TransitCardManager] Error saving JSON: {e}")
            return False

    def normalize_id(self, card_id):
        """카드 ID의 공백 제거 및 소문자 정규화"""
        if not card_id:
            return ""
        return str(card_id).strip().lower()

    def get_card(self, card_id):
        """카드 정보 반환 (없으면 None)"""
        cid = self.normalize_id(card_id)
        return self.cards.get(cid)

    def get_or_create_card(self, card_id, default_type="Tmoney"):
        """
        카드를 조회하고, 등록되어 있지 않은 신규 카드인 경우 0원 잔액으로 자동 등록 후 반환합니다.
        """
        cid = self.normalize_id(card_id)
        if not cid:
            return None
            
        if cid not in self.cards:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cards[cid] = {
                "card_id": cid,
                "card_name": "Tmoney",
                "card_type": default_type,
                "balance": 0,
                "created_at": now_str,
                "updated_at": now_str,
                "history": []
            }
            self._save_cards()
            
        return self.cards[cid]

    def recharge_card(self, card_id, amount, payment_method="현금", memo="교통카드 충전"):
        """
        교통카드 충전 처리
        Returns: (success: bool, new_balance: int, message: str, tx_record: dict)
        """
        cid = self.normalize_id(card_id)
        if not cid:
            return False, 0, "유효한 카드 ID가 입력되지 않았습니다.", None

        if amount <= 0:
            return False, 0, "충전 금액은 0원보다 커야 합니다.", None

        card = self.get_or_create_card(cid)
        current_bal = int(card.get("balance", 0))
        new_bal = current_bal + int(amount)
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tx_record = {
            "timestamp": now_str,
            "type": "충전",
            "amount": int(amount),
            "balance_before": current_bal,
            "balance_after": new_bal,
            "payment_method": payment_method,
            "memo": memo
        }
        
        card["balance"] = new_bal
        card["updated_at"] = now_str
        if "history" not in card:
            card["history"] = []
        card["history"].append(tx_record)
        
        self._save_cards()
        return True, new_bal, f"{amount:,}원이 성공적으로 충전되었습니다.", tx_record

    def refund_card(self, card_id, fee=500, memo="교통카드 환불"):
        """
        교통카드 잔액 환불 처리 (수수료 차감 후 잔액 0원 처리)
        Returns: (success: bool, refund_amt: int, fee: int, message: str, tx_record: dict)
        """
        cid = self.normalize_id(card_id)
        if not cid:
            return False, 0, 0, "유효한 카드 ID가 입력되지 않았습니다.", None

        card = self.get_card(cid)
        if not card:
            return False, 0, 0, "등록되지 않은 카드입니다.", None

        current_bal = int(card.get("balance", 0))
        if current_bal <= 0:
            return False, 0, 0, "환불 가능한 카드 잔액이 없습니다 (잔액: 0원).", None

        if current_bal < fee:
            return False, 0, 0, f"카드 잔액({current_bal:,}원)이 환불 수수료({fee:,}원)보다 적습니다.", None

        refund_amt = current_bal - fee
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        tx_record = {
            "timestamp": now_str,
            "type": "환불",
            "amount": -current_bal,
            "refund_net_amount": refund_amt,
            "fee": fee,
            "balance_before": current_bal,
            "balance_after": 0,
            "memo": memo
        }
        
        card["balance"] = 0
        card["updated_at"] = now_str
        if "history" not in card:
            card["history"] = []
        card["history"].append(tx_record)
        
        self._save_cards()
        return True, refund_amt, fee, f"잔액 {current_bal:,}원 중 수수료 {fee:,}원을 제외한 {refund_amt:,}원이 환불되었습니다.", tx_record

    def pay_with_card(self, card_id, amount, memo="POS 상품 결제"):
        """
        교통카드 결제 차감 처리
        Returns: (success: bool, new_balance: int, message: str, tx_record: dict)
        """
        cid = self.normalize_id(card_id)
        if not cid:
            return False, 0, "유효한 카드 ID가 입력되지 않았습니다.", None

        card = self.get_card(cid)
        if not card:
            return False, 0, "등록되지 않은 교통카드입니다.", None

        current_bal = int(card.get("balance", 0))
        if current_bal < amount:
            shortage = amount - current_bal
            return False, current_bal, f"교통카드 잔액이 부족합니다.\n(현재 잔액: {current_bal:,}원 / 필요 금액: {amount:,}원 / 부족액: {shortage:,}원)", None

        new_bal = current_bal - int(amount)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        tx_record = {
            "timestamp": now_str,
            "type": "결제",
            "amount": -int(amount),
            "balance_before": current_bal,
            "balance_after": new_bal,
            "memo": memo
        }
        
        card["balance"] = new_bal
        card["updated_at"] = now_str
        if "history" not in card:
            card["history"] = []
        card["history"].append(tx_record)
        
        self._save_cards()
        return True, new_bal, f"{amount:,}원이 정상 결제되었습니다.", tx_record

    def get_card_history(self, card_id):
        """특정 카드의 전체 거래 내역 반환 (최신순)"""
        card = self.get_card(card_id)
        if not card:
            return []
        history = list(card.get("history", []))
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)

    def get_all_cards(self):
        """전체 카드 딕셔너리 반환"""
        return self.cards
