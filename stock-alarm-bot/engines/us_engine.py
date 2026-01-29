import yfinance as yf
from datetime import datetime

def analyze_us_market(tickers):
    """
    미국 주식 추세 분석: 20일 이동평균선 및 RSI 지표 활용
    """
    report = f"🇺🇸 **[미국장 추세 브리핑]**\n📅 기준: {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "-" * 20 + "\n"

    for symbol, name in tickers.items():
        try:
            # 1. 데이터 다운로드 (최근 60일치)
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="60d")
            
            if df.empty:
                continue

            # 2. 기술적 지표 계산
            # [이동평균선] 최근 20일간의 평균 가격
            df['MA20'] = df['Close'].rolling(window=20).mean()
            
            # [RSI] 과매수/과매도 지표 (14일 기준)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # 3. 최신 값 추출
            current_price = df['Close'].iloc[-1]
            last_ma20 = df['MA20'].iloc[-1]
            last_rsi = df['RSI'].iloc[-1]
            change_rate = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100

            # 4. 추세 판정 로직
            # - 주가가 20일선 위에 있으면 '상승 추세'
            # - RSI가 70 이상이면 '과열', 30 이하면 '침체'
            if current_price > last_ma20:
                trend = "📈 상승 우위"
                score = "🔥" if last_rsi < 70 else "⚠️ 과열주의"
            else:
                trend = "📉 하락 우위"
                score = "💤 관망"

            # 5. 리포트 작성
            report += f"{score} **{name} ({symbol})**: ${current_price:.2f} ({change_rate:.2f}%)\n"
            report += f"   └ 추세: {trend} / RSI: {last_rsi:.1f}\n\n"

        except Exception as e:
            print(f"미국장 분석 오류 ({symbol}): {e}")
            continue
            
    return report