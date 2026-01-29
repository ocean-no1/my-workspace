import os
from pykrx import stock
import OpenDartReader
from datetime import datetime, timedelta

def get_latest_trading_date():
    """삼성전자 데이터를 조회해 실제 장이 열렸던 최신 날짜를 반환"""
    try:
        now = datetime.now()
        # 최근 10일치 데이터를 가져와서 가장 마지막 날짜(영업일) 선택
        df = stock.get_market_ohlcv((now - timedelta(days=10)).strftime("%Y%m%d"), 
                                    now.strftime("%Y%m%d"), "005930")
        return df.index[-1].strftime("%Y%m%d")
    except:
        return (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

def analyze_korea_market(tickers):
    """
    tickers: {'종목코드': '종목명'} 형태의 딕셔너리
    """
    target_date = get_latest_trading_date()
    api_key = os.environ.get('OPENDART_API_KEY')
    dart = OpenDartReader(api_key)
    
    report = f"🇰🇷 **[한국장 전략 브리핑]**\n📅 기준: {target_date}\n"
    report += "-" * 20 + "\n"

    # 만약 tickers가 리스트로 들어오면 딕셔너리로 변환 (방어 코드)
    if isinstance(tickers, list):
        tickers = {code: code for code in tickers}

    for code, name in tickers.items():
        try:
            # 1. 수급 및 시세 데이터
            df = stock.get_market_trading_value_by_date(target_date, target_date, code)
            price_df = stock.get_market_ohlcv(target_date, target_date, code)
            
            if df.empty or price_df.empty: continue

            f_col = '외국인합계' if '외국인합계' in df.columns else '외국인'
            i_col = '기관합계' if '기관합계' in df.columns else '기관'
            
            f_net = df[f_col].values[0]
            i_net = df[i_col].values[0]
            price = price_df['종가'].values[0]
            rate = price_df['등락률'].values[0]

            # 2. 박시동 점수 계산
            score = 0
            if f_net > 0: score += 40
            if i_net > 0: score += 30
            if rate > 0: score += 30
            
            # 3. 공시 데이터
            dis_list = dart.list(code, start=target_date, kind='A')
            dis_text = "   📢 공시: "
            if dis_list is not None and not dis_list.empty:
                dis_text += dis_list['report_nm'].values[0]
            else:
                dis_text += "특이사항 없음"

            # 4. 리포트 조립
            icon = "🔺" if rate > 0 else "🔹"
            f_amt = f_net // 100000000 # 억 단위
            report += f"{icon} **{name}**: {price:,}원 ({rate:.2f}%)\n"
            report += f"   └ 전략: {score}점 (외:{f_amt}억) / {dis_text}\n\n"

        except Exception as e:
            print(f"❌ {name} 분석 실패: {str(e)}")
            continue
            
    return report