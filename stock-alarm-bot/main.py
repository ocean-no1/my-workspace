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
    - Scout: 데이터 수집 (전체 섹터 + 매크로)
    - Brain: 분석 및 글쓰기
    """
    print(f"🚀 Stock Alarm Bot 시작 (Time: {datetime.datetime.now()})")

    # Scout와 Brain 초기화
    scout = Scout()
    
    try:
        brain = Brain()
        ai_available = True
    except Exception as e:
        print(f"⚠️ AI 초기화 실패 ({e}). 기본 리포트로 전환합니다.")
        ai_available = False

    # 1. 데이터 수집 (섹터 전체 + 매크로)
    # config에 정의된 SECTORS와 MACRO_TICKERS를 모두 전달
    market_data = scout.collect_data(config.SECTORS, config.MACRO_TICKERS)
    
    # 2. 리포트 생성
    if ai_available:
        print("🧠 Brain: AI 분석 시작...")
        report = brain.analyze_market(market_data)
    else:
        # AI 사용 불가 시 간단 요약 (Fallback)
        report = "🔌 **[데이터 수집 리포트]** (AI 미연동)\n\n"
        report += "```\n"
        
        # 매크로
        report += "[Macro]\n"
        for k, v in market_data.get('macros', {}).items():
            report += f"{k}: {v}\n"
        
        # 섹터
        report += "\n[Sectors]\n"
        for sector, stocks in market_data.get('sectors', {}).items():
            report += f"\n- {sector}\n"
            for name, data in stocks.items():
                report += f"  {name}: {data}\n"
        report += "```"

    return report

if __name__ == "__main__":
    try:
        final_report = get_report_by_time()
        print("📨 텔레그램 전송 중...")
        send_message(final_report)
        print("✅ 모든 작업 완료.")
        
    except Exception as e:
        print(f"❌ 치명적 오류 발생: {e}")