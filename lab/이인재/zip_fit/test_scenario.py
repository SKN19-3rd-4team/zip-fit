import requests

# 서버가 켜져 있어야 합니다 (uvicorn main:app --reload)
URL = "http://127.0.0.1:8000/api/v1/chat/"

def chat(user_id, text):
    print(f"\n📨 [User {user_id}] 요청: {text}")
    try:
        res = requests.post(URL, json={"user_input": text, "user_id": user_id})
        if res.status_code == 200:
            print(f"🤖 [AI 응답]: {res.json()['response']}")
        else:
            print(f"❌ 오류: {res.text}")
    except Exception as e:
        print(f"❌ 연결 실패: 서버 실행 여부를 확인하세요.")

if __name__ == "__main__":
    print("🚀 zip-fit 챗봇 테스트 시작!")
    
    # 시나리오 1: 1번 유저(김철수)가 101번 공고 문의 -> 서울 공고 정보가 나와야 함
    chat(1, "공고 101번 내용이 뭐야?")
    
    # 시나리오 2: 2번 유저(이영희)가 202번 공고 문의 -> 경기 공고 정보가 나와야 함
    chat(2, "공고 202번 조건 알려줘")
    
    # 시나리오 3: 1번 유저가 다시 질문 (기억력 테스트) -> 아까 물어본 내용 문맥 파악
    chat(1, "아까 그거 보증금이 얼마라고 했지?")