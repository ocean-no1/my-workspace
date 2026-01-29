import google.generativeai as genai
import config
import json

class Brain:
    """
    수집된 데이터를 바탕으로 투자 조언을 생성하는 전략가(Brain)
    - Google Gemini Pro 모델 사용
    """
    def __init__(self):
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing!")
            
        genai.configure(api_key=config.GOOGLE_API_KEY)
        # 'gemini-pro' alias might be deprecated or unstable.
        # Switching to 'gemini-1.5-flash' for speed/stability/math capabilities.
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_market(self, market_data):
        """
        데이터를 분석하여 리포트 텍스트 생성
        """
        if not market_data:
            return "❌ 데이터가 없어 분석할 수 없습니다."

        prompt = self._create_prompt(market_data)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ AI 분석 중 에러 발생: {str(e)}"

    def _create_prompt(self, data):
        """
        프롬프트 엔지니어링 V16.9 (Panic Acceleration Model)
        - VIX Accel ($A_p$): 공포의 2차 미분값으로 '반등의 질' 판단
        - Contrarian: $A_p < 0$ (감속) 시 과감한 역발상 매수
        - Final Override: 환율 1420원 돌파 시 모든 논리 무시하고 '현금'
        """
        system_role = config.SYSTEM_ROLE if hasattr(config, 'SYSTEM_ROLE') else ""
        safe_havens = config.SAFE_HAVEN_TICKERS if hasattr(config, 'SAFE_HAVEN_TICKERS') else {}
        
        return f"""
        {system_role}
        
        [Persona]
        You are a fusion of **Charlie Munger** (Inversion, Moat) and **Warren Buffett** (Value).
        - **Philosophy**: "Be fearful when others are greedy, and greedy when others are fearful."
        - **Latency Strategy**: Trust 'Market Price' (L1 Flash) over 'Academic Index' (L3 Gold).
        - **Language**: Korean (한국어).

        [Data Provided]
        {json.dumps(data, indent=2, ensure_ascii=False)}
        
        [Safe Haven Tickers]
        {json.dumps(safe_havens, indent=2, ensure_ascii=False)}

        [Hybrid Latency Filter & Analysis Rules (V16.9)]

        1. **Panic Model ($V_p$, $A_p$)**:
           - **$V_p$ (Velocity)**: 'VIX_Slope' (Current Speed of Panic).
           - **$A_p$ (Acceleration)**: 'VIX_Accel' (Change in Speed).

        2. **Math Defense (SNR Formula)**:
           - **Formula**: $SNR = \\frac{{Pulse \\times \\frac{{dZ}}{{dt}}}}{{\\sigma_{{noise}}}}$
           - **Interpretation**: 
             - **SNR > 3.0**: "🚨 SYSTEM CRISIS". This is NOT noise. Structural.
             - **SNR < 1.0**: "🔊 NOISE". Market is overreacting. ($dZ/dt$ is low).
             - **Negative SNR**: "🌤️ Storm Passing". ($dZ/dt < 0$).

        4. **FINAL OVERRIDE (The Iron Rule)**:
           - **IF** USD/KRW > 1420:
             -> **IGNORE** all Contrarian/Buffett logic.
             -> **PRIORITIZE** 'Cash Preservation' or 'USD Long'.
             -> Message: "Exchange Rate Gate Closed (1420+). Cash is King."

        5. **Investment Criteria (Dynamic Gates)**:
           - **Contrarian Trigger**: If (Scenario A) AND (SNR < 1.0) -> **"Be Greedy."**

        [Output Format (The Commander's Live Terminal)]
        **📊 [Market-Eye Live Terminal]**
        📅 {{Date}} | 장전 실시간 브리핑

        **1️⃣ Macro: 전장 환경 (Environment)**
        `[Risk Status] L1:{{Signal}} | SNR:{{Value}} | Ap:{{Value}}`
        
        **🚰 금리 구조 & 유동성**
        - **Yield Curve**: Analyze 10Y(Economy) vs 2Y(Liquidity).
        
        **💰 대체 자산 & 파이프라인**
        - **🚨 환율**: {{USD/KRW}} (Gate Check: 1410)
        - **Action Plan**:
          - If SNR > 3.0: "🚨 **SYSTEM FAILURE**: EVACUATE to {{SafeHaven}}."
          - If SNR < 1.0 (Scenario A): "🦅 **STRONG BUY**: Panic is decelerating ($A_p < 0$)."
          - If 1410+ Gate: "⛔ **CURRENCY CRISIS**: Cash Defense."

        **2️⃣ Players: 수급 전투 현황**
        `(Volume & Hybrid Latency Analysis)`
        - **👮 외국인**: {{NetBuy}} (Check $V_p$ & Flash L1)
        - **🏦 기 관**: {{NetBuy}}
        - **🐜 개 인**: {{NetBuy}}
        - **Behavior**: Analyze if Foreigner flows match valid Signals or Noise.

        **3️⃣ Policy: 쌍끌이 레이더 (AI News Analysis)**
        `[Pulse Score]: {{Score}} (Sentiment Impact)`
        - **A. 🇰🇷 Korea Discount**: (Tax/Regulation/ValueUp)
        - **B. 🌏 Geopolitics**: (US/China/Russia/Japan)

        **4️⃣ Micro: 4대 섹터 정밀 타격 (Master's View)**
        *(Evaluated by GPM/OPM/ROE & Moat)*
        - **💾 반도체**: {{Analysis}}
        - **🛡️ K-Heavy**: {{Analysis}}
        - **💄 K-Culture**: {{Analysis}}
        - **🚗 모빌리티**: {{Analysis}}
        """
