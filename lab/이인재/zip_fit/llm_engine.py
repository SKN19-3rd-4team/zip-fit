from typing import Dict, Any
import asyncio
from .models import ChatRequest 
# 🌟 config.py에서 설정을 가져옵니다.
from .config import settings
# 🌟 Gongo 임포트
from .gongo import Gongo
# 🌟 OpenAI 비동기 클라이언트 임포트
from openai import AsyncOpenAI

class LlmEngine:
    """
    LLM 호출, 프롬프트 구성, LangChain/LangGraph 등의 지능형 처리를 담당하는 클래스입니다.
    """
    # 🌟 생성자를 통해 Gongo 인스턴스를 주입받습니다.
    def __init__(self, gongo_service: Gongo):
        self.gongo_service = gongo_service
    # 🌟 실제 OpenAI 클라이언트 초기화 (Config에서 API Key 사용)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        print("⚙️ LlmEngine Initialized with Gongo service.")

    # ----------------------------------------------------
    # 🌟 요청하신 메서드 1: Gongo에서 텍스트를 읽어오는 메서드
    # ----------------------------------------------------
    async def _get_llm_input_text(self, request: ChatRequest) -> str:
        """
        Gongo 서비스에서 RAG 및 컨텍스트 데이터를 가져와 LLM 입력 텍스트를 생성합니다.
        """
        # Gongo 서비스를 호출하여 컨텍스트 데이터를 가져옵니다.
        context_data = await self.gongo_service.get_contextual_data(
            user_id=request.user_id, 
            query=request.user_input
        )
        
        # 최종적으로 LLM에 전달할 프롬프트 텍스트를 구성합니다.
        llm_input_text = (
            f"주어진 컨텍스트를 바탕으로 사용자 질문에 답하세요.\n\n"
            f"{context_data}\n\n"
            f"사용자 질문: {request.user_input}"
        )
        
        return llm_input_text

    # ----------------------------------------------------
    # 🌟 요청하신 메서드 2: LLM을 호출하는 메서드 (Mock)
    # ----------------------------------------------------
    async def _call_llm_api(self, prompt_text: str) -> Dict[str, Any]:
        """
        OpenAI, LangChain 등을 이용하여 실제 LLM API를 호출하고 응답을 받습니다. (현재는 Mock)
        """
        
        # 🌟 실제 OpenAI LLM 호출
        # 시스템 프롬프트
        system_prompt = "당신은 최고의 분석가이자 조언자입니다. 정확하게 답변하세요"
        
        # API에 전달할 메세지
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text}
        ]
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3
            )
            # 응답 결과 파싱
            llm_output = response.choices[0].message.content
            
            return {
                "llm_output": llm_output,
                "prompt_used": prompt_text,
                "usage_tokens": response.usage.total_tokens
            }
        
        except Exception as e:
            # 오류 처리
            return {
                "llm_output": f"LLM 호출 중 오류: {str(e)}",
                "prompt_used": prompt_text,
                "usage_tokens": 0
            }
        
        # # 비동기 처리를 시뮬레이션하기 위해 잠시 대기합니다.
        # await asyncio.sleep(0.05)
        
        # # Mock 응답을 구성합니다.
        # mock_llm_response = {
        #     "llm_output": f"LLM이 성공적으로 처리했습니다. (프롬프트 길이: {len(prompt_text)} 문자)",
        #     "prompt_used": prompt_text,
        #     "usage_tokens": len(prompt_text) // 5 # 대략적인 토큰 Mock
        # }
        
        # return mock_llm_response


    async def generate_response(self, request: ChatRequest) -> Dict[str, Any]:
        """
        Chatting 클래스에서 호출되는 메인 처리 메서드입니다.
        """
        # 1. Gongo를 통해 데이터 가져오기
        prompt_text = await self._get_llm_input_text(request)
        
        # 2. LLM 호출
        llm_result = await self._call_llm_api(prompt_text)
        
        return llm_result