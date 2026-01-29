import requests
import config

def send_message(message):
    """
    텔레그램으로 메시지를 발송하는 함수
    """
    try:
        token = config.TELEGRAM_TOKEN
        chat_id = config.TELEGRAM_CHAT_ID
        
        # 메시지가 없으면 발송 취소
        if not message:
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"  # 굵은 글씨 등 스타일 적용
        }
        
        response = requests.post(url, data=data)
        
        # 전송 실패 시 로그 출력
        if response.status_code != 200:
            print(f"❌ 텔레그램 전송 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 텔레그램 에러: {e}")