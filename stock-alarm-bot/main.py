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
import logging

# 로깅 설정 (파일 및 콘솔 출력)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_report_by_time():
    """
    시간대별 리포트 생성 로직
    - Scout: 데이터 수집 (전체 섹터 + 매크로)
    - Brain: 분석 및 글쓰기
    """
    logging.info(f"🚀 Stock Alarm Bot 시작 (Time: {datetime.datetime.now()})")

    # Scout와 Brain 초기화
    scout = Scout()
    
    try:
        brain = Brain()
        ai_available = True
    except Exception as e:
        logging.error(f"⚠️ AI 초기화 실패 ({e}). 기본 리포트로 전환합니다.")
        ai_available = False

    # 1. 데이터 수집 (섹터 전체 + 매크로)
    # config에 정의된 SECTORS와 MACRO_TICKERS를 모두 전달
    market_data = scout.collect_data(config.SECTORS, config.MACRO_TICKERS)
    logging.info("데이터 수집 완료")
    
    # 2. 리포트 생성
    if ai_available:
        logging.info("🧠 Brain: AI 분석 시작...")
        report = brain.analyze_market(market_data)
    else:
        # AI 사용 불가 시 간단 요약 (Fallback)
        report = "🔌 **[데이터 수집 리포트]** (AI 미연동 - V16.0)\n\n"
        report += "```\n"
        
        # 1. Macro
        report += "[Macro Indicators]\n"
        for k, v in market_data.get('macro', {}).items():
            report += f"{k}: {v}\n"
        
        # 2. Players (Supply/Demand)
        report += "\n[Players - Net Buy]\n"
        players = market_data.get('players', {})
        if 'this_week' in players:
            report += f"This Week: {players['this_week']}\n"
        if 'last_week' in players:
            report += f"Last Week: {players['last_week']}\n"

        # 3. Policy News
        report += "\n[Policy News]\n"
        for kw, info in market_data.get('policy_news', {}).items():
            report += f"- {kw}: {info.get('title', 'No Title')}\n"

        # 4. Micro (Sectors)
        report += "\n[Sector Analysis]\n"
        for sector, stocks in market_data.get('micro', {}).items():
            report += f"\n- {sector}\n"
            if isinstance(stocks, dict):
                for name, data in stocks.items():
                    if isinstance(data, dict):
                        price = data.get('price', 'N/A')
                        change = data.get('change', 'N/A')
                        report += f"  {name}: {price} ({change})\n"
                    else:
                        report += f"  {name}: {data}\n"
        report += "```"
        logging.warning("AI 분석 실패로 기본 리포트 생성됨")

    return report

if __name__ == "__main__":
    try:
        # [Heartbeat] 생존 신고
        start_msg = f"🚀 **[System Start]** Stock Alarm Bot V16.1 가동 시작\n- Env: {'Cloud (GitHub)' if os.environ.get('GITHUB_ACTIONS') else 'Local'}\n- Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_message(start_msg)

        final_report = get_report_by_time()
        logging.info("📨 텔레그램 전송 중...")
        send_message(final_report)
        logging.info("✅ 모든 작업 완료.")
        
    except Exception as e:
        error_msg = f"❌ 치명적 오류 발생: {e}"
        logging.critical(error_msg)
        # 텔레그램으로 에러 알림 전송 (가능한 경우)
        try:
            send_message(f"⚠️ **[Bot Error]** 봇 가동 중 에러 발생:\n{str(e)}")
        except:
            pass