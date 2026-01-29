import yfinance as yf
from pykrx import stock
import OpenDartReader
import config
from datetime import datetime, timedelta

class Scout:
    """
    시장 데이터를 수집하는 정찰병 역할의 클래스
    - 한국장: PyKRX, OpenDart
    - 미국장: yfinance
    """
    def __init__(self):
        self.dart = OpenDartReader(config.OPENDART_API_KEY)

    def _get_kr_trading_date(self):
        """가장 최근 영업일 계산"""
        try:
            now = datetime.now()
            # 5일치 조회해서 마지막 인덱스 가져옴
            df = stock.get_market_ohlcv((now - timedelta(days=5)).strftime("%Y%m%d"), 
                                        now.strftime("%Y%m%d"), "005930")
            return df.index[-1].strftime("%Y%m%d")
        except:
            return (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    def collect_data(self, portfolio):
        """
        포트폴리오 내 모든 종목의 데이터 수집
        """
        results = {}
        kr_date = self._get_kr_trading_date()
        
        print(f"🕵️ Scout: 시장 데이터 수집 중... (기준일: KR {kr_date})")

        for code, info in portfolio.items():
            name = info['name']
            market = info['market']
            
            try:
                if market == 'KR':
                    data = self._collect_kr_stock(code, kr_date)
                else:
                    data = self._collect_us_stock(code)
                
                results[name] = data
                
            except Exception as e:
                print(f"❌ {name} 데이터 수집 실패: {e}")
                results[name] = {"error": str(e)}
                
        return results

    def _collect_kr_stock(self, code, date):
        # 1. 시세 및 수급
        df_price = stock.get_market_ohlcv(date, date, code)
        df_trade = stock.get_market_trading_value_by_date(date, date, code)
        
        price = df_price['종가'].values[0]
        change_rate = df_price['등락률'].values[0]
        
        # 컬럼명 대응 (버전 차이 방지)
        if '외국인합계' in df_trade.columns:
            f_col = '외국인합계'
        elif '외국인' in df_trade.columns:
            f_col = '외국인'
        else:
            f_col = None

        if '기관합계' in df_trade.columns:
            i_col = '기관합계'
        elif '기관' in df_trade.columns:
            i_col = '기관'
        else:
            i_col = None
        
        f_net = df_trade[f_col].values[0] if f_col else 0
        i_net = df_trade[i_col].values[0] if i_col else 0
        
        # 2. 공시 (최근 3일)
        start_dt = (datetime.strptime(date, "%Y%m%d") - timedelta(days=3)).strftime("%Y%m%d")
        dis_list = self.dart.list(code, start=start_dt, kind='A')
        disclosure = "없음"
        if dis_list is not None and not dis_list.empty:
            titles = dis_list['report_nm'].head(2).tolist()
            disclosure = ", ".join(titles)

        return {
            "market": "KOREA",
            "price": int(price),
            "change_rate": round(float(change_rate), 2),
            "foreigner_net": int(f_net),
            "institution_net": int(i_net),
            "disclosure": disclosure
        }

    def _collect_us_stock(self, symbol):
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="60d")
        
        if history.empty:
            return {"error": "No Data"}
            
        current = history.iloc[-1]
        prev = history.iloc[-2]
        
        price = current['Close']
        change_rate = ((price - prev['Close']) / prev['Close']) * 100
        
        # MA20
        ma20 = history['Close'].rolling(window=20).mean().iloc[-1]
        
        # RSI
        delta = history['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return {
            "market": "U.S.",
            "price": round(float(price), 2),
            "change_rate": round(float(change_rate), 2),
            "ma20_trend": "Above" if price > ma20 else "Below",
            "rsi": round(float(rsi.iloc[-1]), 1)
        }
