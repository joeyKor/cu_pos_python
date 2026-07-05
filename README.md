# 🏪 DU Retail POS System (Python/PyQt6)

이 프로젝트는 Python과 PyQt6를 활용하여 구현된 대구대학교(DU) 스타일의 스마트 소매점 POS(Point of Sale) 시스템입니다. 직관적인 사용자 인터페이스와 다양한 결제 모듈, 그리고 Firebase Firestore를 통한 클라우드 동기화 및 로컬 백업(Mock DB) 시스템을 지원합니다.

---

## 🌟 주요 기능 (Key Features)

### 1. 시작 및 대기 화면 (Welcome Page)
* **DU 마스코트 & 배너**: DU 브랜드 아이덴티티가 강조된 고해상도 그래픽과 깔끔한 대기화면을 제공합니다.
* **직전 결제 내역 확인**: 가장 최근에 완료된 결제 금액, 받은 금액, 거스름돈을 메인 화면에서 한눈에 파악할 수 있습니다.
* **금고 잔액 관리 (Cash Drawer)**: 실시간 현금 거래를 자동으로 반영하여 금고 내 현금 잔액을 실시간 표시합니다. 금액 표시 부분을 더블클릭하여 실제 시설 금액으로 수동 조정할 수 있습니다.
* **즉각적인 바코드 등록**: 대기 화면에서 바코드를 스캔하거나 입력창에 5자리 상품 코드를 입력하면 즉시 판매 화면으로 전환되어 상품이 등록됩니다.

### 2. 판매 및 상품 등록 (Sales Screen)
* **실시간 상품 추가 및 수량 조절**: 바코드 스캔 또는 수동 입력을 통한 실시간 테이블 상품 추가, 수량 변경 및 개별/전체 삭제 기능.
* **통합 계산기 페이지**: 판매 화면 내에서 즉시 계산을 도와주는 편리한 보조 계산기 패널을 탑재하였습니다.

### 3. 강력하고 다양한 결제 모듈 (Multi-Payment System)
* **💳 신용카드 결제**: 가상의 카드 정보(12자리 카드번호 등) 입력을 통해 한도 및 승인 처리를 시뮬레이션합니다.
* **💵 현금 결제**: 받은 금액 입력 시 거스름돈을 자동으로 계산하며, 현금영수증(소득공제/지출증빙) 발행을 선택하고 처리할 수 있습니다.
* **📱 모바일 간편결제**: 바코드 또는 QR 코드를 리더기로 스캔하여 간편결제(네이버페이, 카카오페이, 토스페이 등) 승인을 시뮬레이션합니다.
* **🚌 교통카드 서비스**: 교통카드(T-money 등)의 잔액 조회, 충전 및 결제 기능을 제공합니다.
* **📝 후불 및 외상 결제**: 외상(후불) 결제 내역을 등록하여 관리할 수 있는 기능을 지원합니다.
* **💰 거스름돈 적립**: 거스름돈 발생 시 현금 대신 고객 계좌나 포인트로 적립하는 서비스 기능을 탑재하였습니다.

### 4. 부가 서비스 (Special Services)
* **📦 택배 서비스 (Parcel Service)**: 보내는 사람/받는 사람 주소 입력 및 검색, 무게 측정 시뮬레이션, 운송장 출력 등의 풀 프로세스를 탑재한 무인 택배 접수 시스템입니다.
* **🔄 환불 및 반품 (Refund)**: 이전 영수증 번호를 조회하거나 영수증 목록에서 직접 거래를 선택하여 즉시 환불 및 취소 처리가 가능합니다.
* **📑 영수증 조회**: 과거에 발행되었던 전체 영수증 내역을 상세 조회할 수 있는 영수증 관리 뷰어를 지원합니다.

### 5. 데이터 영속성 및 동기화 (Data Persistence)
* **Firebase Firestore 연동**: 실시간으로 클라우드 데이터베이스에 상품 및 거래 내역을 동기화합니다.
* **로컬 Mock DB 지원**: `json/firebase_credentials.json` 자격증명 파일이 없거나 오프라인 상태일 경우, 자동으로 `json/firebase_mock_db.json`을 사용하여 로컬에서 완벽하게 작동하는 오프라인 폴백(Fallback) 시스템을 구축했습니다.

---

## 🛠 기술 스택 (Tech Stack)

* **Programming Language**: Python 3.13
* **GUI Framework**: PyQt6 (POS 메인 화면), Tkinter (IC 카드 읽기/쓰기 유틸리티)
* **Database**: Firebase Firestore (온라인) & Local JSON (오프라인)
* **Sound Effects**: Pygame Mixer (결제 완료, 경고 등 사운드 알림 지원)
* **Hardware Integration**: smartcard (`pyscard` 패키지를 이용한 실제 IC 스마트카드 APDU 통신 지원)

---

## 📁 프로젝트 구조 (Project Structure)

```yaml
cu_mart/
│
├── main.py                     # 애플리케이션 진입점 및 메인 윈도우(컨테이너) 관리
├── welcome_page.py             # 시작 및 대기 화면 UI와 이벤트 처리
├── payment_ui.py               # 신용카드, 현금, 간편결제 등 핵심 결제 화면 로직
│
├── calculator_page.py          # 계산기 보조 도구 화면
├── change_accumulation_page.py # 거스름돈 적립 서비스 화면
├── check_inquiry_page.py       # 수표 조회 및 현금영수증 발행 확인 화면
├── parcel_service_page.py      # 주소 검색, 무게 측정, 운송장 출력을 포함한 택배 화면
├── post_payment_page.py        # 후불/외상 처리 관리 화면
├── product_inquiry_page.py     # 등록된 상품 검색 및 재고 조회 화면
├── receipt_inquiry_page.py     # 전체 영수증 조회 및 상세 내역 확인 화면
├── refund_page.py              # 영수증 조회를 통한 환불/반품 처리 화면
├── settings_page.py            # 상품 정보 추가/수정/삭제 관리자 페이지
├── transit_card_page.py        # 교통카드 충전 및 결제 화면
│
├── firebase_manager.py         # Firebase Firestore 연결 및 로컬 Mock DB 폴백 로직
├── product_manager.py          # 상품 데이터 로드 및 로컬 검색 엔진
├── receipt_manager.py          # 영수증 데이터 저장 및 로컬 포맷팅 관리
├── transaction_manager.py      # 거래(매출) 데이터 통계 및 영속성 처리
├── styles.py                   # 전역 테마 스타일, 폰트, 색상 토큰 정의
├── ui_components.py            # 공통 커스텀 버튼, 다이얼로그 등 공용 위젯
│
├── bank_card_app.py            # [유틸리티] 실제 IC 스마트카드 리더/라이터 (Tkinter)
├── build_exe.ps1               # PyInstaller 실행 파일 빌드 스크립트
├── .gitignore                  # Git 버전 관리 제외 설정
└── README.md                   # 프로젝트 문서 설명서
```

---

## 🚀 설치 및 실행 방법 (Installation & Run)

### 1. 요구 사항 설치
본 프로젝트는 사운드 출력 및 스마트카드 기능 등을 포함하므로 아래 패키지 설치가 필요합니다.
```bash
pip install PyQt6 firebase-admin pygame pyscard
```
> **참고**: `pyscard` 패키지는 실제 스마트카드 판독 장비(IC Card Reader)를 사용하는 유틸리티 `bank_card_app.py`를 실행할 때 필요합니다. 만약 스마트카드 하드웨어 모듈을 사용하지 않는다면 제외하셔도 메인 POS 프로그램 실행에는 문제가 없습니다.

### 2. Firebase 자격증명 파일 추가 (선택사항)
실제 Firebase Firestore 클라우드와 연동하려면 아래 경로에 서비스 계정 키 파일을 생성 및 위치시켜 주세요.
* 경로: `json/firebase_credentials.json`
* 파일이 없을 경우 프로그램이 시작될 때 자동으로 **Mock 데이터베이스 모드**(`json/firebase_mock_db.json`)로 작동합니다.

### 3. POS 프로그램 실행
```bash
python main.py
```

### 4. 스마트카드 리더/라이터 앱 실행 (선택사항)
실제 IC 카드에 계좌 번호 정보를 입력하거나 읽어들일 때는 다음 독립 앱을 실행합니다.
```bash
python bank_card_app.py
```
