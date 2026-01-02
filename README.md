# CU Retail POS System (Python/PyQt6)

이 프로젝트는 Python과 PyQt6를 사용하여 구현된 CU 스타일의 소매점 POS(Point of Sale) 시스템입니다. 직관적인 사용자 인터페이스와 실시간 결제 처리, 데이터 영속성을 특징으로 합니다.

## 주요 기능 (Main Features)

### 1. 시작 페이지 (Welcome Page)
- **인트로 화면**: CU 브랜드 마스코트와 고해상도 배너가 포함된 깔끔한 시작 화면을 제공합니다.
- **바코드 자동 스캔**: 시작 페이지에서 바코드를 스캔(또는 5자리 입력)하면 즉시 판매 페이지로 전환되어 상품이 등록됩니다.
- **직전 결제 내역**: 가장 최근에 완료된 결제의 총 금액, 결제 금액, 거스름돈을 메인 화면에서 바로 확인할 수 있습니다.
- **금고 보관 관리**: 실시간 현금 입출금을 반영하여 금고 내 현금 잔액을 표시합니다. 더블클릭을 통해 실제 금고 금액으로 수동 조정이 가능합니다.

### 2. 판매 및 결제 시스템 (Sales & Payment)
- **상품 등록**: 바코드 스캔을 통한 실시간 상품 추가 및 수량 조절 기능.
- **다양한 결제 수단**: 
  - **신용카드**: 카드 번호(12자리) 입력을 통한 가상 결제 처리.
  - **현금**: 받은 금액 입력, 거스름돈 계산, 현금영수증 발행 여부 선택 가능.
- **결제 데이터 영속성**: 모든 결제 내역은 `transactions.json` 파일에 저장되어 관리됩니다.

### 3. 상품 관리 (Product Management)
- **상품 데이터베이스**: `product_manager.json`을 통해 상품 정보를 관리합니다.
- **설정 페이지**: 새로운 상품을 등록하거나 기존 상품의 정보를 수정할 수 있는 전용 관리자 인터페이스를 제공합니다.

## 설치 및 실행 방법 (Installation & Execution)

### 요구 사항
- Python 3.10 이상
- PyQt6

### 실행 순서
1. 프로젝트 폴더로 이동:
   ```bash
   cd cu_mart
   ```
2. 필요한 라이브러리 설치 (필요 시):
   ```bash
   pip install PyQt6
   ```
3. 어플리케이션 실행:
   ```bash
   python main.py
   ```

## 프로젝트 구조 (Project Structure)
- `main.py`: 어플리케이션의 핵심 로직 및 메인 윈도우 관리.
- `welcome_page.py`: 시작 화면 UI 및 이벤트 처리.
- `ui_components.py`: 버튼, 대화상자 등 커스텀 UI 컴포넌트 모음.
- `product_manager.py`: 상품 데이터 입출력 및 검색 로직.
- `transaction_manager.py`: 결제 내역 저장 및 통계 처리 로직.
- `styles.py`: 전역 스타일시트 및 디자인 토큰 정의.
- `payment_ui.py`: 카드 및 현금 결제 전용 다이얼로그 UI.

## 기술 스택
- **Language**: Python 3.13
- **GUI Framework**: PyQt6
- **Data Storage**: JSON (Local Persistence)
