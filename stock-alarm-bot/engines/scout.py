import requests
from bs4 import BeautifulSoup
from pykrx import stock
import time
import yfinance as yf
import pandas as pd
import config
from datetime import datetime, timedelta
import re

import pandas_datareader.data as pdr

class Scout:
    """
    [Scout V16.0]
    웹 크롤링(BeautifulSoup)과 yfinance를 사용하여 원천 데이터를 수집하는 정찰병.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def collect_data(self, sectors, macros):
        """
        통합 데이터 수집 (4대 임무 수행)
        """
        print(f"🕵️ Scout: 정찰 임무 시작... (Time: {datetime.now().strftime('%H:%M:%S')})")
        
        # [V16.8] SNR Calculation
        risk = self.get_risk_indices()
        pulse = self.calculate_pulse_score()
        
        try:
            vix_slope = float(risk.get("VIX_Slope", 0)) # dZ/dt (Acceleration of Impact)
            pulse_score = float(pulse.get("score", 0))
            
            # [Math Formula V16.10]
            # SNR = (Pulse * dZ/dt) / sigma_noise
            AVG_NOISE_INTENSITY = 1.0 # sigma_noise (Historical Average)
            
            # Pulse가 0일 경우를 대비해 최소 0.5 보정 (Silent Crisis 방지)
            adjusted_pulse = max(pulse_score, 0.5)
            
            # Calculate SNR
            snr = (adjusted_pulse * abs(vix_slope)) / AVG_NOISE_INTENSITY
            
            # 방향성 보정: Slope가 음수면 SNR도 음수로 표기 (Crisis Fading)
            if vix_slope < 0:
                snr = -snr
        except:
            snr = 0.0

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_indices": risk,
            "pulse_score": pulse,
            "snr": f"{snr:.2f}", # [V16.8] 신호 대 소음비
            "market_index": self.get_korea_market_index(),
            "macro": self.get_macro_data(macros),
            "players": self.get_players_data(),
            "policy_news": self.get_policy_news(),
            "micro": self.get_micro_data(sectors),
            "safe_haven_data": self.get_micro_data({"Defensive Assets": config.SAFE_HAVEN_TICKERS})
        }
        
        print(f"  - [SNR Analysis] Score: {snr:.2f} (Pulse: {pulse.get('score')}, Slope: {risk.get('VIX_Slope')})")
        print("✅ Scout: 정찰 임무 완료.")
        return data

    def get_macro_data(self, macro_tickers):
        """
        임무 1: 거시경제 정찰 (금리, 환율, 대체자산, 머니무브)
        """
        print("  - [1/4] 거시경제 지표 수집 중...")
        result = {}

        # 1-1. 글로벌 지표 (yfinance)
        for key, ticker_symbol in macro_tickers.items():
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    result[key] = f"{current:,.2f} ({change:+.2f}%)"
                else:
                    result[key] = "N/A"
            except Exception:
                result[key] = "Error"

        # 1-2. 한국 국고채 금리 (네이버 금융 크롤링) - yfinance 데이터 부족 보완
        try:
            url = "https://finance.naver.com/marketindex/"
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, "html.parser")
            
            # (CSS 선택자는 네이버 금융 구조에 맞춰 조정 필요, 여기서는 예시 로직)
            # 시장지표 리스트 순회 로직이 복잡하므로 간단히 환율 체크만 예시로 구현하거나
            # 정확한 파싱 로직이 필요. 여기서는 '머니무브'에 집중하기로 함.
            pass 
        except Exception as e:
            print(f"    ⚠️ 국고채 수집 실패: {e}")

        # 1-3. 머니무브 (유동성) - 예탁금, 신용융자 등
        try:
            url = config.URLS["DEPOSIT"]
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 예탁금 테이블 파싱 (가정: class='type_2')
            # 실제 네이버 증시자금동향 페이지 구조 기반
            table = soup.select_one("div.box_type_m > table.type_2")
            if table:
                rows = table.select("tr")
                # 일반적으로 상단 행들에 데이터 위치
                # 예: 고객예탁금(3번째 rows), 신용융자(...), CMA(...)
                # 정확한 행 인덱스는 페이지 변경에 취약하므로 텍스트 검색 권장
                
                labels = ["고객예탁금", "신용융자", "CMA", "MMF"]
                for row in rows:
                    cols = row.select("td")
                    if len(cols) >= 2:
                        label = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        
                        for target in labels:
                            if target in label:
                                result[target] = value # 콤마 포함 문자열 그대로
        except Exception as e:
             print(f"    ⚠️ 머니무브 수집 실패: {e}")
             

        return result

    def get_risk_indices(self):
        """
        [V16.5] Global Risk Indices (EPU, VIX Z-Score, GPR Proxy)
        """
        print("  - [Plus] 글로벌 리스크 지표(EPU, VIX, GPR) 정밀 분석 중...")
        result = {"EPU": "N/A", "VIX": "N/A", "VIX_Z": "0.0", "GPR": "N/A"}
        
        # 1. US Economic Policy Uncertainty Index (FRED)
        try:
            start = datetime.now() - timedelta(days=60)
            end = datetime.now()
            epu_data = pdr.DataReader('USEPUINDXD', 'fred', start, end)
            if not epu_data.empty:
                result["EPU"] = f"{epu_data.iloc[-1].item():.2f}"
        except Exception as e:
            print(f"    ⚠️ EPU 수집 실패: {e}")

        # 2. VIX Z-Score (yfinance)
        try:
            vix = yf.Ticker("^VIX")
            # 30일 데이터 확보 (Z-Score 계산용)
            hist = vix.history(period="3mo") # 넉넉히 3개월
            if len(hist) >= 30:
                 # Rolling Window로 구현하면 좋으나, 단순화를 위해 전체기간 Mean/Std 사용하되
                 # 최근 데이터 변화를 반영
                recent = hist['Close']
                
                # Z-Score Calculation
                mean_vix = recent.mean()
                std_vix = recent.std()
                
                current_vix = recent.iloc[-1]
                prev_vix = recent.iloc[-2]
                prev2_vix = recent.iloc[-3]
                
                z_current = (current_vix - mean_vix) / std_vix if std_vix != 0 else 0
                z_prev = (prev_vix - mean_vix) / std_vix if std_vix != 0 else 0
                z_prev2 = (prev2_vix - mean_vix) / std_vix if std_vix != 0 else 0
                
                # Vp (Velocity)
                velocity_current = z_current - z_prev
                velocity_prev = z_prev - z_prev2
                
                # Ap (Acceleration)
                acceleration = velocity_current - velocity_prev
                
                result["VIX"] = f"{current_vix:.2f}"
                result["VIX_Z"] = f"{z_current:.2f}"
                result["VIX_Slope"] = f"{velocity_current:.2f}" # Vp
                result["VIX_Accel"] = f"{acceleration:.2f}" # Ap
        except Exception as e:
            print(f"    ⚠️ VIX 수집 실패: {e}")

        # 3. GPR Proxy (News Keyword Velocity)
        result["GPR_Proxy"] = self.get_gpr_proxy()
            
        return result

    def get_gpr_proxy(self):
        """
        [V16.5] 정치 리스크 프록시 (Risk Velocity)
        - 특정 키워드(계엄, 탄핵 등)의 뉴스 출현 빈도 체크
        """
        keywords = ['계엄', '내란', '탄핵', 'ICE', 'FBI 수색', '부정선거']
        hit_count = 0
        
        base_url = "https://search.naver.com/search.naver?where=news&sort=1&query="
        
        for kw in keywords:
            try:
                res = requests.get(base_url + kw, headers=self.headers, timeout=3)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    # 뉴스 리스트 아이템 개수 (최대 10개) 카운트
                    # 'news_area'는 각 뉴스 아이템의 클래스
                    items = soup.select("div.news_area")
                    
                    # 간단한 로직: 상위 10개 중 '1시간 이내' 기사가 몇 개인지 체크하면 좋으나
                    # 여기서는 단순 검색 결과 노출 여부로 판단 (각 키워드 당 최대 1점)
                    if items:
                        hit_count += 1
            except:
                continue
                
        # Risk Level Logic
        risk_level = "Stable"
        if hit_count >= 3:
            risk_level = "CRITICAL (Political Shock)"
        elif hit_count >= 1:
            risk_level = "Warning"
            
        return {"score": hit_count, "status": risk_level}

    def calculate_pulse_score(self):
        """
        [V16.6] Pulse Layer: 뉴스 센티먼트 점수화
        - 위기 단어(2.0) vs 일반 단어(0.5) 가중치 합산
        """
        print("  - [Plus] Pulse Score (News Sentiment) 계산 중...")
        total_score = 0.0
        details = []
        
        keywords = config.CRISIS_KEYWORDS if hasattr(config, 'CRISIS_KEYWORDS') else {}
        base_url = "https://search.naver.com/search.naver?where=news&sort=1&query="
        
        for kw, weight in keywords.items():
            try:
                # 단순 검색 노출 여부 확인 (빠른 속도를 위해 timeout 짧게)
                res = requests.get(base_url + kw, headers=self.headers, timeout=2)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    if soup.select("div.news_area"):
                        total_score += weight
                        details.append(kw)
            except:
                 continue
                 
        return {"score": total_score, "matches": ", ".join(details[:5])} # 상위 5개만 표기

    # -------------------------------------------------------------------------
    # 기존 메소드들 (get_macro_data 등) 유지...
    def get_korea_market_index(self):
        """
        [공공데이터포털] 국내 지수 시세 (KOSPI, KOSDAQ)
        """
        print("  - [Plus] 국내 지수(KOSPI/KOSDAQ) 확인 중...")
        data = {"KOSPI": {"price": "0", "change": "0"}, "KOSDAQ": {"price": "0", "change": "0"}}
        
        api_key = config.DATA_GO_KR_API_KEY
        if not api_key:
            return data

        base_url = "https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex"
        # 최근 영업일 데이터 확보를 위해 오늘~3일 전까지 조회 (최근 데이터 획득용)
        # today = datetime.now().strftime("%Y%m%d") # Unused variable removed
        
        # basDt는 필수. 주말 고려하여 최근 평일로 설정
        # 단, API 특성상 정확한 날짜를 모르면 루프를 돌거나 범위를 줘야 하는데, 
        # numOfRows=10 & resultType=json으로 최근 데이터가 상위에 오는지 확인 필요.
        # 공공데이터포털은 보통 basDt를 지정해야 함. 어제 날짜로 시도.
        
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        if datetime.now().weekday() == 0: # 월요일이면 금요일 데이터
            target_date = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")
        elif datetime.now().weekday() == 6: # 일요일이면 금요일
            target_date = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")

        params = {
            "serviceKey": api_key,
            "resultType": "json",
            "numOfRows": "10",
            "basDt": target_date
        }
        
        try:
            res = requests.get(base_url, params=params, timeout=5)
            if res.status_code == 200:
                try:
                    items = res.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    for item in items:
                        name = item.get("idxNm")
                        price = item.get("clpr") # 종가
                        flt = item.get("fltRt") # 등락률
                        
                        if name == "코스피":
                            data["KOSPI"] = {"price": price, "change": flt, "date": item.get("basDt")}
                        elif name == "코스닥":
                            data["KOSDAQ"] = {"price": price, "change": flt, "date": item.get("basDt")}
                except:
                    pass
            elif res.status_code == 403:
                print("    ⚠️ 공공데이터포털 접근 권한 없음 (활용신청 필요)")
        except Exception as e:
            print(f"    ⚠️ 지수 데이터 수집 실패: {e}")
            
        return data

    # 상단 import 추가는 별도 처리하지 않고, 여기서 메소드 교체만 수행
    # (import는 multi-replace 또는 별도 호출로 처리해야 하므로, 이 도구 호출에서는 메소드 본문만 교체하고
    #  import 문은 파일 상단에 추가해야 함. 하지만 replace_file_content는 한 번에 하나의 블록만 수정 가능.
    #  따라서 여기서는 메소드를 교체하고, 다음 호출에서 import를 추가하겠음.)
    
    def get_players_data(self):
        """
        [수급 데이터 수집]
        네이버 크롤링 차단 시 대안: PyKRX (한국거래소 데이터) 사용
        """
        try:
            today = datetime.now()
            today_str = today.strftime("%Y%m%d")
            
            # 요일 계산 (0:월 ~ 6:일)
            idx = today.weekday()
            
            # 날짜 범위 설정 (YYYYMMDD 포맷)
            # 1. 이번주 (월요일 ~ 오늘)
            this_week_start_dt = today - timedelta(days=idx)
            this_week_start = this_week_start_dt.strftime("%Y%m%d")
            this_week_end = today_str
            
            # 2. 지난주 (지난주 월 ~ 지난주 금)
            last_week_end_dt = this_week_start_dt - timedelta(days=3) # 지난주 금요일 (월-3일)
            last_week_start_dt = last_week_end_dt - timedelta(days=4) # 지난주 월요일 (금-4일)
            
            last_week_start = last_week_start_dt.strftime("%Y%m%d")
            last_week_end = last_week_end_dt.strftime("%Y%m%d")

            # KRX에서 기간별 투자자 순매수 데이터 조회 (코스피 전체)
            # IP 차단 등으로 데이터가 비어있을 경우 대비
            try:
                from pykrx import stock
                df_this = stock.get_market_trading_value_by_date(this_week_start, this_week_end, "KOSPI")
                df_last = stock.get_market_trading_value_by_date(last_week_start, last_week_end, "KOSPI")
            except Exception as e:
                print(f"    ⚠️ PyKRX 접속 실패: {e}")
                df_this = pd.DataFrame()
                df_last = pd.DataFrame()

            # 데이터가 비어있을 경우 (장 시작 전 또는 차단됨) 0으로 처리
            if df_this.empty:
                this_foreign = 0
                this_inst = 0
                this_ant = 0
            else:
                try:
                    # 억 원 단위로 변환
                    this_foreign = int(df_this['외국인'].sum() / 100000000)
                    this_inst = int(df_this['기관합계'].sum() / 100000000)
                    this_ant = int(df_this['개인'].sum() / 100000000)
                except:
                    this_foreign = 0; this_inst = 0; this_ant = 0

            if df_last.empty:
                last_foreign = 0
                last_inst = 0
                last_ant = 0
            else:
                try:
                    last_foreign = int(df_last['외국인'].sum() / 100000000)
                    last_inst = int(df_last['기관합계'].sum() / 100000000)
                    last_ant = int(df_last['개인'].sum() / 100000000)
                except:
                    last_foreign = 0; last_inst = 0; last_ant = 0

            return {
                "this_week": {'foreign': this_foreign, 'inst': this_inst, 'ant': this_ant},
                "last_week": {'foreign': last_foreign, 'inst': last_inst, 'ant': last_ant},
                "d_day": idx + 1
            }

        except Exception as e:
            print(f"⚠️ KRX 데이터 수집 실패: {e}")
            return {
                "this_week": {'foreign': 0, 'inst': 0, 'ant': 0},
                "last_week": {'foreign': 0, 'inst': 0, 'ant': 0},
                "d_day": 0,
                "error": str(e)
            }

    def get_policy_news(self):
        """
        임무 3: 정책 및 지정학 뉴스 감청
        """
        print("  - [3/4] 뉴스 키워드 감청 중...")
        news_report = {}
        
        keywords = config.NEWS_KEYWORDS if hasattr(config, 'NEWS_KEYWORDS') else []
        base_url = "https://search.naver.com/search.naver?where=news&sort=1&query="
        
        for keyword in keywords:
            try:
                url = base_url + keyword
                res = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(res.text, "html.parser")
                
                # 뉴스 리스트 첫 번째 아이템
                news_item = soup.select_one("div.news_area")
                if news_item:
                    title_tag = news_item.select_one("a.news_tit")
                    if title_tag:
                        title = title_tag.get_text()
                        link = title_tag['href']
                        news_report[keyword] = {"title": title, "link": link}
            except Exception:
                continue
                
        return news_report

    def get_micro_data(self, sectors):
        """
        임무 4: 섹터 정밀 타격 (버핏/멍거 지표 포함)
        """
        print("  - [4/4] 섹터별 정밀 분석 중...")
        micro_data = {}

        for sector, tickers in sectors.items():
            sector_data = {}
            for ticker_code, name in tickers.items():
                try:
                    t = yf.Ticker(ticker_code)
                    info = t.info
                    
                    price = info.get('currentPrice', 0)
                    prev_close = info.get('previousClose', price)
                    change_rate = ((price - prev_close) / prev_close) * 100 if prev_close else 0
                    
                    # 핵심 지표 (Buffett/Munger style)
                    gpm = info.get('grossMargins', 0) * 100 # GPM
                    opm = info.get('operatingMargins', 0) * 100 # OPM
                    roe = info.get('returnOnEquity', 0) * 100 # ROE
                    
                    sector_data[name] = {
                        "price": f"{price:,.0f}" if "KS" in ticker_code or "KQ" in ticker_code else f"${price:.2f}",
                        "change": f"{change_rate:+.2f}%",
                        "GPM": f"{gpm:.1f}%",
                        "OPM": f"{opm:.1f}%",
                        "ROE": f"{roe:.1f}%"
                    }
                except Exception as e:
                    # yfinance info 누락 시 대비 단순 계산 시도
                    # (여기서는 에러 로깅 후 패스)
                    # print(f"    ⚠️ {name} 수집 실패: {e}")
                    sector_data[name] = "Data Unavailable"
            
            micro_data[sector] = sector_data
            
        return micro_data
