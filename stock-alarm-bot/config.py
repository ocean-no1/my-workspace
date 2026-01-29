import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ==========================================
# 1. � 섹터 및 종목 설정 (yfinance 호환 티커)
# ==========================================
# 한국 주식: .KS(코스피), .KQ(코스닥) 접미어 필수
SECTORS = {
    "반도체": {
        "005930.KS": "삼성전자",
        "000660.KS": "SK하이닉스",
        "042700.KS": "한미반도체",
        "058470.KQ": "리노공업"
    },
    "2차전지": {
        "373220.KS": "LG에너지솔루션",
        "006400.KS": "삼성SDI",
        "005490.KS": "POSCO홀딩스",
        "247540.KQ": "에코프로비엠"
    },
    "자동차/운송": {
        "005380.KS": "현대차",
        "000270.KS": "기아",
        "012450.KS": "한화에어로스페이스"
    },
    "플랫폼/AI": {
        "035420.KS": "NAVER",
        "035720.KS": "Kakao",
        "GOOGL": "구글(Alphabet)", # 미국주식은 접미어 없음
        "MSFT": "마이크로소프트"
    }
}

# ==========================================
# 2. 🌍 거시경제 지표 (Macro)
# ==========================================
# yfinance 티커 기준
MACRO_TICKERS = {
    "US_10Y": "^TNX",      # 미국채 10년물 금리
    "US_2Y": "^IRX",       # 미국채 2년물 (주의: yfinance에서 ^IRX는 통상 13주 단기채이나 요청에 따라 매핑)
    "DX_Y": "DX-Y.NYB",    # 달러 인덱스
    "GOLD": "GC=F",        # 금 선물
    "BITCOIN": "BTC-USD",  # 비트코인
    "WTI": "CL=F"          # (옵션) WTI 원유
}

# ==========================================
# 3. 🔗 데이터 수집 URLs (네이버 금융)
# ==========================================
URLS = {
    "DEPOSIT": "https://finance.naver.com/sise/sise_deposit.naver",          # 고객 예탁금
    "INVESTOR_TREND": "https://finance.naver.com/sise/sise_trans_style.naver", # 투자자별 매매동향
    "NEWS_LATEST": "https://finance.naver.com/news/mainnews.naver",          # 주요 뉴스
    "BOK_RATE": "https://www.bok.or.kr"                                      # (참고) 한국은행 기준금리 등
}

# ==========================================
# 4. 🧠 AI 프롬프트 설정 (Persona)
# ==========================================
SYSTEM_ROLE = """
당신은 '워렌 버핏'의 장기 투자 철학과 '찰리 멍거'의 냉철한 판단력을 겸비한 세계 최고의 투자 전략가입니다.
당신의 이름은 'Market-Eye'입니다.

[분석 스타일]
1. 단순한 시세 나열이 아닌, 데이터 이면에 숨겨진 '시장 심리'와 '본질적 가치'를 꿰뚫어 봅니다.
2. 상승장에서는 "탐욕을 경계하라"고 조언하고, 하락장에서는 "공포에 매수하라"는 역발상 관점을 유지합니다.
3. 말투는 정중하지만 단호하며, 전문적인 금융 용어를 적절히 사용하되, 초보자도 이해할 수 있도록 명쾌하게 설명합니다.
4. 모든 조언은 '데이터'에 기반해야 합니다. 감에 의존하지 마십시오.

[작성 원칙]
- 핵심부터 두괄식으로 요약합니다.
- 중요한 수치나 변화는 굵은 글씨(**)로 강조합니다.
- 적절한 이모지를 사용하여 가독성을 높입니다.
"""

# ==========================================
# 5. 🔑 API 키 및 시스템 설정
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENDART_API_KEY = os.environ.get("OPENDART_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️  [Config] GOOGLE_API_KEY가 없습니다. AI 분석 기능이 제한됩니다.")