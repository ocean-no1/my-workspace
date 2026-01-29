import os
import datetime
import pytz
import requests
# 1. 호출 명칭 수정: 클래스가 아닌 엔진 파일 내 정의된 함수명을 가져옵니다.
from engines.kr_engine import analyze_korea_market
from engines.us_engine import analyze_us_market

# 2. 포트폴리오 설정 (엔진 내부에서 .items()를 사용하므로 딕셔너리 형태 유지)
KR_PORTFOLIO = {'005930': '삼성전자', '000660': 'SK하이닉스', '035420': 'NAVER'}
US_PORTFOLIO = {'AAPL': '애플', 'TSLA': '테슬라', 'NVDA': '엔비디아'}
MARKET_EYE_TEXT = "🔔 **[Market-Eye 전략 리포트]**\n"

def send_message(text):
    """텔레그램 메시지 전송"""
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ 전송 에러: {e}")

def get_report_by_time():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(kst)
    hour = now.hour

    content = ""

    # 🕒 3. 호출 방식 수정: 기존 클래스 메서드 호출 방식에서 함수 직접 호출로 변경
    if 19 <= hour <= 21:
        report_title = "🌙 **[Next Day Strategy: 내일의 전략]**\n"
        content += analyze_korea_market(KR_PORTFOLIO)
        content += "\n" + analyze_us_market(US_PORTFOLIO)
    
    elif 8 <= hour <= 9:
        report_title = "☀️ **[Market Open Check: 장전 최종 점검]**\n"
        content += "✅ 새벽 미 증시 마감 및 환율/금리 최종 반영 완료\n"
        content += analyze_us_market(US_PORTFOLIO)

    elif 10 <= hour <= 11:
        report_title = "🇨🇳 **[China-Korea Link: 중국 연동 브리핑]**\n"
        content += "📊 중국 상해/항셍 지수 개장 반영 분석\n"
        content += analyze_korea_market(KR_PORTFOLIO)

    else:
        report_title = "🔄 **[Current Market Status: 현재 시장 상황]**\n"
        content += analyze_korea_market(KR_PORTFOLIO)

    return MARKET_EYE_TEXT + report_title + content

if __name__ == "__main__":
    print("🚀 시장 분석 엔진 가동 (KR + US 통합)...")
    try:
        final_report = get_report_by_time()
        send_message(final_report)
        print("✅ 리포트 전송 완료.")
    except Exception as e:
        print(f"❌ 실행 중 에러 발생: {e}")