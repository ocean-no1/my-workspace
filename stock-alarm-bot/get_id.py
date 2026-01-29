import os
import requests
from dotenv import load_dotenv

# .env 파일 로딩
load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
    print("❌ 토큰이 없습니다. .env 파일을 저장했는지 확인하세요!")
    exit()

# 텔레그램 서버에 "나한테 말 건 사람 있어?" 하고 물어보기
url = f"https://api.telegram.org/bot{token}/getUpdates"
response = requests.get(url).json()

try:
    if not response['result']:
        print("\n❌ 봇에게 말을 안 거셨군요!")
        print("👉 텔레그램에서 봇을 찾아 'Start' 버튼을 누르거나 'hi'라고 말을 걸고 다시 실행하세요.")
    else:
        # 가장 최근에 말 건 사람의 ID 가져오기
        chat_id = response['result'][-1]['message']['chat']['id']
        print(f"\n✅ 찾았다! 님의 Chat ID는: {chat_id}")
        print("👉 이 숫자를 복사해서 .env 파일의 TELEGRAM_CHAT_ID에 넣으세요.")
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    print("봇 토큰이 정확한지 확인해주세요.")
