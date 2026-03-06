import os
from dotenv import load_dotenv
from google import genai


# 1. .env 파일 로드
load_dotenv("api.env")

# 2. 환경 변수에서 API 키 가져오기 (만약을 위해 .strip()으로 공백/줄바꿈 완벽 제거)
MY_API_KEY = os.getenv("GEMINI_API_KEY")

if not MY_API_KEY:
    print("오류: .env 파일에서 GEMINI_API_KEY를 찾을 수 없습니다.")
    exit()

# 3. 클라이언트 초기화
client = genai.Client(api_key=MY_API_KEY.strip())

# 4. 챗봇 세션 시작 (빠르고 가벼운 flash 모델 사용)
chat = client.chats.create(model="gemini-2.5-flash")

print("노래방 AI 도우미와 대화를 시작합니다. (종료하려면 '종료' 입력)")

# 5. 반복문을 통한 대화 구현
while True:
    user_input = input("나: ")
    
    if user_input == '종료':
        print("대화를 종료합니다.")
        break
        
    try:
        response = chat.send_message(user_input)
        print(f"AI 도우미: {response.text}")
    except Exception as e:
        print(f"에러가 발생했습니다: {e}")