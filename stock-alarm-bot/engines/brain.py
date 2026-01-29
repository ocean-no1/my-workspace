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
        프롬프트 엔지니어링: config에 정의된 페르소나 적용
        """
        system_role = config.SYSTEM_ROLE if hasattr(config, 'SYSTEM_ROLE') else "You are a helpful financial assistant."
        
        return f"""
        {system_role}
        
        [Task]
        Analyze the following stock market data (Sectors & Macro Indicators) and write a strategic daily briefing.
        
        [Data Provided]
        {json.dumps(data, indent=2, ensure_ascii=False)}
        
        [Instructions]
        1. Start with a catchy title summarizing the overall market sentiment.
        2. Analyze Macro Indicators first (Rates, Dollar, Gold, Bitcoin) to set the context.
        3. For each SECTOR, analyze the trend and key stocks.
        4. Specifically mention 'Buying Opportunity' or 'Caution'.
        5. Use emojis effectively (📈, 📉, 🔥, ⚠️, ✅).
        6. Write in KOREAN (한국어).
        7. Keep it sharp and concise.
        """
