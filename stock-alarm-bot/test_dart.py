import os
from dotenv import load_dotenv
import OpenDartReader

# 1. 금고(.env)에서 키 꺼내기
load_dotenv()
api_key = os.getenv("OPENDART_API_KEY")

# 2. 키가 잘 들어왔는지 확인
if not api_key:
    print("❌ 에러: .env 파일에 키가 없거나 저장되지 않았습니다.")
    exit()

print(f"🔑 감지된 키: {api_key[:5]}..." + "(뒤에는 비밀)")

# 3. DART에서 삼성전자(005930) 정보 긁어오기
try:
    print("📡 금융감독원 서버에 접속 중...")
    dart = OpenDartReader(api_key)
    
    # 삼성전자 기업 개황 가져오기
    samsung = dart.company("005930")
    
    print("\n" + "="*30)
    print(f"🏢 기업명: {samsung['corp_name']}")
    print(f"👤 CEO: {samsung['ceo_nm']}")
    print(f"📍 주소: {samsung['adres']}")
    print("="*30)
    print("\n✅ 테스트 성공! 봇이 정상적으로 데이터를 받아옵니다.")
    
except Exception as e:
    print("\n❌ 연결 실패! API 키를 다시 확인해주세요.")
    print(f"에러 메시지: {e}")
