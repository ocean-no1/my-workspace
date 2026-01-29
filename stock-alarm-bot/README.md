# 📈 Stock Alarm Bot (Market-Eye)

이 프로젝트는 한국(KR) 및 미국(US) 주식 시장의 추세를 분석하고, 텔레그램으로 정기 리포트를 전송하는 자동화 봇입니다.

## 📁 프로젝트 구조

```
stock-alarm-bot/
├── main.py                 # 🚀 진입점 (Entry Point): 시간대별 로직 실행 및 리포트 전송
├── config.py               # ⚙️ 설정값: API 키, 포트폴리오 목록(종목), 매매 기준 등
├── requirements.txt        # 📦 의존성 패키지 목록
├── README.md               # 📖 프로젝트 설명 (현재 파일)
├── engines/                # 🧠 분석 엔진 폴더
│   ├── kr_engine.py        # 🇰🇷 한국장 분석 (PyKRX, OpenDart 사용)
│   └── us_engine.py        # 🇺🇸 미국장 분석 (YFinance 사용)
└── notifiers/              # 📢 알림 모듈
    └── telegram_bot.py     # 텔레그램 메시지 발송 헬퍼 (main.py에도 내장됨)
```

## 🛠️ 주요 기능

### 1. 시간대별 자동 실행 (`main.py`)

`get_report_by_time()` 함수가 현재 시각(KST)을 기준으로 다른 리포트를 생성합니다.

- **08:00 ~ 09:00**: **[Market Open Check]** 장전 점검 (환율, 금리, 미 증시 마감 반영)
- **10:00 ~ 11:00**: **[China-Korea Link]** 중국 증시 개장 영향 분석
- **19:00 ~ 21:00**: **[Next Day Strategy]** 내일의 전략 (한국장 마감 + 미국장 개장 전)
- **기타 시간**: **[Current Market Status]** 현재 시장 브리핑

### 2. 한국장 분석 (`engines/kr_engine.py`)

- **데이터 소스**: `pykrx` (시세/수급), `OpenDartReader` (공시)
- **박시동 전문가 전략**:
  - 외국인 순매수 (+40점)
  - 기관 순매수 (+30점)
  - 주가 상승 (+30점)
  - **총점 80점 이상**이면 매수 시그널로 활용
- **공시 체크**: 최근 공시 사항 확인

### 3. 미국장 분석 (`engines/us_engine.py`)

- **데이터 소스**: `yfinance`
- **기술적 분석**:
  - **이동평균선(MA20)**: 20일선 위면 "상승 우위", 아래면 "하락 우위"
  - **RSI (상대강도지수)**: 70 이상(과열), 30 이하(침체) 판단

## ⚙️ 설정 (`config.py`)

- `SAFE_PORTFOLIO` / `ACTIVE_PORTFOLIO`: 분석할 종목 리스트 관리
- `TELEGRAM_TOKEN`, `CHAT_ID`: 텔레그램 봇 연동 정보
- `OPENDART_API_KEY`: 다트(Dart) API 키

## 🚀 실행 방법 (GitHub Actions)

이 프로젝트는 `.github/workflows/stock_bot.yml`에 정의된 워크플로우를 통해 자동 실행됩니다.

- **Schedule**: 정해진 시간(CRON)에 따라 자동 실행
- **Workflow Dispatch**: GitHub Actions 탭에서 수동 실행 가능
