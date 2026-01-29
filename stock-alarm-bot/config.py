import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ==========================================
# 1. 🏭 섹터 및 종목 설정 (yfinance 호환 티커)
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
# 매크로 지표 (Key: Name, Value: Ticker/Code)
MACRO_TICKERS = {
    "USD/KRW": "KRW=X",        # 원/달러 환율
    "US 10Y Treasury": "^TNX", # 미국채 10년물 금리
    "WTI Crude": "CL=F",       # 서부 텍사스유
    "Gold": "GC=F",            # 금 선물
    "Bitcoin": "BTC-USD"       # 비트코인
}

# [V16.6] Safe Haven (위기 시 대피처)
SAFE_HAVEN_TICKERS = {
    "Inverse 2X": "252670.KS", # KODEX 200선물인버스2X
    "Gold ETF": "132030.KS",   # KODEX 골드선물(H)
    "USD ETF": "261240.KS"     # KODEX 미국달러선물
}

# [V16.6] Crisis Keywords & Weights (Pulse Layer)
# 가중치: 정치적 쇼크(2.0) vs 경제 노이즈(0.5)
CRISIS_KEYWORDS = {
    "계엄": 2.0, "탄핵": 2.0, "내란": 2.0, "헌법": 1.5,
    "ICE": 1.5, "압수수색": 1.5, "부정선거": 1.5,
    "금리": 0.5, "환율": 0.5, "고용": 0.5, "생산": 0.5
}

# 뉴스 검색 키워드 (기존 단순 리스트 대체 가능하나 호환성 유지)
NEWS_KEYWORDS = list(CRISIS_KEYWORDS.keys())

# ==========================================
# 3. 🔗 데이터 수집 URLs (네이버 금융)
# ==========================================
URLS = {
    "DEPOSIT": "https://finance.naver.com/sise/sise_deposit.naver",          # 고객 예탁금
    "INVESTOR_TREND": "https://finance.naver.com/sise/sise_trans_style.naver", # 투자자별 매매동향
    "PROGRAM_TRADE": "https://finance.naver.com/sise/sise_program.naver",    # 프로그램 매매동향
    "NEWS_LATEST": "https://finance.naver.com/news/mainnews.naver",          # 주요 뉴스
    "NEWS_SEARCH": "https://search.naver.com/search.naver?where=news&query=", # 뉴스 검색
    "BOK_RATE": "https://www.bok.or.kr"                                      # (참고) 한국은행 기준금리 등
}

# ==========================================
# 4. 📰 뉴스 검색 키워드
# ==========================================
NEWS_KEYWORDS = [
    "금투세", "밸류업", "상속세", "물적분할", "반도체 보조금", # 5대 쟁점
    "중국 비자", "러시아 전쟁", "엔화 환율"                 # 지정학
]

# ==========================================
# 5. 🧠 AI 프롬프트 설정 (Persona)
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
# 6. 🔑 API 키 및 시스템 설정
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENDART_API_KEY = os.environ.get("OPENDART_API_KEY")
DATA_GO_KR_API_KEY = os.environ.get("DATA_GO_KR_API_KEY") # 공공데이터포털
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️  [Config] GOOGLE_API_KEY가 없습니다. AI 분석 기능이 제한됩니다.")