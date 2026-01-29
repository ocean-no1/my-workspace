import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ==========================================
# 1. 🏛️ 박시동 전문가 전략 (50 vs 50)
# ==========================================
SAFE_PORTFOLIO = {
    "069500": "KODEX 200",       # 시장 지수
    "148020": "KBSTAR 200고배당", # 배당주
}

ACTIVE_PORTFOLIO = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "005380": "현대차",
    "012450": "한화에어로스페이스"
}

# 매매 기준 점수
BUY_THRESHOLD = 80
SELL_THRESHOLD = 40

# ==========================================
# 2. 🔑 비밀번호 설정 (따옴표 필수!)
# ==========================================

# [주의1] 변수명은 무조건 TELEGRAM_CHAT_ID 여야 합니다. (CHAT_ID 아님!)
# [주의2] 봇 이름(@Seans...) 말고 "숫자 ID"를 넣으세요! (예: "59123456")
TELEGRAM_CHAT_ID = "6065623727"

# [주의3] 토큰도 따옴표(" ") 안에 넣으세요
TELEGRAM_TOKEN = "7961790388:AAETsbKAtGH663EfFNQDnrkDOn5E4RGly7M"

# [주의4] 오픈다트 키도 따옴표(" ") 필수!
OPENDART_API_KEY = "31454fc4d3e30dcfd74f62b0e5bce4a146eb8d01"