import os
import datetime
import pytz
import config
from engines.scout import Scout
from engines.brain import Brain
from notifiers.telegram_bot import send_message

def get_report_by_time():
    """
    시간대별 리포트 생성 로직
    - Scout: 데이터 수집
    - Brain: 분석 및 글쓰기
    """
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(kst)
    hour = now.hour

    # 1. 포트폴리오 선택
    if 8 <= hour <= 15: # 장중/장전 (한국장 중심)
        portfolio = config.ACTIVE_PORTFOLIO
        portfolio.update(config.SAFE_PORTFOLIO_EXPANDED if hasattr(config, 'SAFE_PORTFOLIO_EXPANDED') else {})
    else: # 장마감/야간 (전체 + 미국장)
        portfolio = config.ACTIVE_PORTFOLIO
    
    # Scout와 Brain 초기화
    scout = Scout()
    
    try:
        brain = Brain()
        ai_available = True
    except Exception as e:
        print(f"⚠️ AI 초기화 실패 ({e}). 기본 리포트로 전환합니다.")
        ai_available = False

    # 2. 데이터 수집
    market_data = scout.collect_data(portfolio)
    
    # 3. 리포트 생성
    if ai_available:
        print("🧠 Brain: AI 분석 시작...")
        report = brain.analyze_market(market_data)
    else:
        # AI 사용 불가 시 간단 요약 (Fallback)
        report = "🔌 **[데이터 수집 리포트]** (AI 미연동)\n\n"
        report += "```\n"
        for name, data in market_data.items():
            report += f"{name}: {data}\n"
        report += "```"

    return report

if __name__ == "__main__":
    print(f"🚀 Stock Alarm Bot 시작 (Time: {datetime.datetime.now()})")
    
    try:
        final_report = get_report_by_time()
        print("📨 텔레그램 전송 중...")
        send_message(final_report)
        print("✅ 모든 작업 완료.")
        
    except Exception as e:
        print(f"❌ 치명적 오류 발생: {e}")