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
        self.model = genai.GenerativeModel('gemini-pro')

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
        프롬프트 엔지니어링: 금융 전문가 페르소나 부여
        """
        return f"""
        You are a top-tier financial analyst and investment strategist named 'Market-Eye'.
        Your style is sharp, professional, yet easy to understand.
        
        Analyze the following stock market data and write a strategic daily briefing.
        
        [Data Provided]
        {json.dumps(data, indent=2, ensure_ascii=False)}
        
        [Instructions]
        1. Start with a catchy title summarizing the overall market sentiment.
        2. For each stock, analyze the price movement and key indicators (Foreigner net buy, RSI, MA20).
        3. Specifically mentioning 'Buying Opportunity' or 'Caution' based on the data.
        4. Use emojis effectively (📈, 📉, 🔥, ⚠️, ✅) to make it readable.
        5. Write in KOREAN (한국어).
        6. Keep the report concise but insightful.
        """
