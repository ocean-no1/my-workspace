import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ==========================================
# 1. 🏛️ 포트폴리오 설정
# ==========================================
# [안전형] 예: 지수 추종, 배당주
SAFE_PORTFOLIO = {
    "069500": "KODEX 200",       
    "148020": "KBSTAR 200고배당", 
}

# [공격형] 예: 주요 기술주 - (종목코드, 종목명, 국가)
ACTIVE_PORTFOLIO = {
    "005930": {"name": "삼성전자", "market": "KR"},
    "000660": {"name": "SK하이닉스", "market": "KR"},
    "005380": {"name": "현대차", "market": "KR"},
    "TSLA": {"name": "테슬라", "market": "US"},
    "NVDA": {"name": "엔비디아", "market": "US"},
    "AAPL": {"name": "애플", "market": "US"},
}

# ==========================================
# 2. 🔑 비밀번호 & API 설정
# ==========================================

# 텔레그램 설정
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "6065623727")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "7961790388:AAETsbKAtGH663EfFNQDnrkDOn5E4RGly7M")

# 데이터 API 설정
OPENDART_API_KEY = os.environ.get("OPENDART_API_KEY", "31454fc4d3e30dcfd74f62b0e5bce4a146eb8d01")

# [NEW] Google AI 설정
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ [경고] GOOGLE_API_KEY가 설정되지 않았습니다. AI 분석이 불가능할 수 있습니다.")