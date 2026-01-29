import datetime
import pytz
import config
from engines.kr_engine import KoreaEngine
from engines.us_engine import USEngine
from notifiers.telegram_bot import send_message

# 🏛️ [시장을 보는 눈: Macro Intelligence] - 최상단 고정 텍스트
MARKET_EYE_TEXT = """
🏛️ **[Market Intelligence: 시장을 읽는 눈]**

1️⃣ **자본의 중력 (금리)**: 미 국채 10년물 실질금리는 자본의 가격입니다. 금리 상승은 나스닥과 한국 성장주의 할인율을 높여 주가를 누릅니다.
2️⃣ **자금의 이동경로 (환율)**: 환율은 수급의 댐입니다. 1,350원 상단 돌파 시 외국인은 환차손을 피해 한국 시장에서 기계적으로 이탈합니다.
3️⃣ **실물 경기 선행지표 (중국/구리)**: 구리 가격과 중국 PMI는 한국 제조업의 선행 지표입니다. 10시 중국 개장 상황이 한국 장중 변동성을 결정합니다.
--------------------------------------------
"""

def get_report_by_time():
    # 한국 시간(KST) 설정
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(kst)
    hour = now.hour

    kr_bot = KoreaEngine()
    us_bot = USEngine()

    # 🕒 스케줄링 로직 (사용자 기획안 반영)
    if 19 <= hour <= 21:
        # [20:00] 내일의 매매를 위한 전일 전략 브리핑
        report_title = "🌙 **[Next Day Strategy: 내일의 전략]**\n"
        content = kr_bot.analyze(config.KR_PORTFOLIO) # 전일 수급 + 공시 분석
        content += us_bot.analyze(config.US_PORTFOLIO) # 미 프리마켓 추세
    
    elif 8 <= hour <= 9:
        # [08:50] 장 시작 전 최종 점검
        report_title = "☀️ **[Market Open Check: 장전 최종 점검]**\n"
        content = "✅ 새벽 미 증시 마감 및 환율/금리 최종 반영 완료\n"
        content += kr_bot.analyze(config.KR_PORTFOLIO)

    elif 10 <= hour <= 11:
        # [10:00] 중국 시장 연동 섹터 대응
        report_title = "🇨🇳 **[China-Korea Link: 중국 연동 브리핑]**\n"
        content = "📊 중국 상해/항셍 지수 개장 반영 분석\n"
        content += kr_bot.analyze(config.KR_PORTFOLIO) # 소비재/화학 중심

    else:
        # 그 외 시간: 일반 현황 보고
        report_title = "🔄 **[Current Market Status: 현재 시장 상황]**\n"
        content = kr_bot.analyze(config.KR_PORTFOLIO)

    return MARKET_EYE_TEXT + report_title + content

if __name__ == "__main__":
    print("🚀 시장 분석 엔진 가동...")
    final_report = get_report_by_time()
    send_message(final_report)
    print("✅ 리포트 전송 완료.")