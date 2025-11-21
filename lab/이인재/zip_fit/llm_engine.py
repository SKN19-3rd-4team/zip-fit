from typing import Dict, Any
import asyncio
from .models import ChatRequest 
# config.py에서 설정을 가져옵니다.
from .config import settings
# Gongo 임포트
from .gongo import Gongo
# OpenAI 비동기 클라이언트 임포트
from openai import AsyncOpenAI
# 세션 관리 유틸리티 임포트
from .session import set_session, get_session

class LlmEngine:
    """
    LLM 호출, 프롬프트 구성, LangChain/LangGraph 등의 지능형 처리를 담당하는 클래스입니다.
    """
    # 생성자를 통해 Gongo 인스턴스를 주입받습니다.
    def __init__(self, gongo_service: Gongo):
        self.gongo_service = gongo_service
    # 실제 OpenAI 클라이언트 초기화 (Config에서 API Key 사용)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        print("LlmEngine Initialized with Gongo service.")
    
    
    async def generate_response(self, request: ChatRequest) -> Dict[str, Any]:
        
        # 1. 세션 키 생성(사용자 식별)
        session_key = f"messages_userid_{request.user_id}"

        # 2. 대화 히스토리(질문, AI 답변만) 불러오기 (파일 / 메모리에서 읽기)
        history = await get_session(session_key, "conversation")
        
        if not history:
            # 기록 없으면 초기화
            history = []

        # 3. 이번 질문(request.user_input)에 딱 필요한 정보만 DB(Gongo)에서 가져옵니다.
        context_data = await self.gongo_service.get_contextual_data(
            request.user_id, 
            request.user_input
        )

        # 4. 이번 질문 프롬프트 구성
        system_message = {
            "role": "system", 
            "content": (
                "당신은 zip-fit AI 상담원입니다. 친절하고 명확하게 답변하세요.\n"
                f"아래 [참고 자료]를 바탕으로 답변하고, 자료에 없는 내용은 지어내지 마세요.\n\n"
                f"[참고 자료]\n{context_data}"
            )
        }
        
        # OpenAI에 보낼 전체 메시지 (Context는 System 메시지에만 일회성으로 주입)
        # 구조: [시스템(자료 포함)] + [과거 대화] + [이번 질문]
        messages_to_send = [system_message] + history + [{"role": "user", "content": request.user_input}]

        try:
            # 5. LLM 호출 (Generation)
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_to_send, 
                temperature=0.3
            )
            ai_answer = response.choices[0].message.content
            
            # 6. 답변을 히스토리에 추가
            # Context가 포함되지 않은 순수 질문만 저장
            history.append({"role": "user", "content": request.user_input})
            history.append({"role": "assistant", "content": ai_answer})
            
            # 세션 갱신(메모리 / 파일)
            await set_session(session_key, "conversation", history)
            
            return {
                "llm_output": ai_answer,
                "usage_tokens": response.usage.total_tokens
            }
            
        except Exception as e:
            return {"llm_output": f"Error: {str(e)}", "usage_tokens": 0}