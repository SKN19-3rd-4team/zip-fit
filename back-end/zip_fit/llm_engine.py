from typing import Dict, Any
import asyncio
from .models import ChatRequest 
# 🌟 Gongo 임포트
from .gongo import Gongo 

class LlmEngine:
    """
    LLM 호출, 프롬프트 구성, LangChain/LangGraph 등의 지능형 처리를 담당하는 클래스입니다.
    """
    # 🌟 생성자를 통해 Gongo 인스턴스를 주입받습니다.
    def __init__(self, gongo_service: Gongo):
        self.gongo_service = gongo_service
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
        # 비동기 처리를 시뮬레이션하기 위해 잠시 대기합니다.
        await asyncio.sleep(0.05)
        
        # Mock 응답을 구성합니다.
        mock_llm_response = {
            "llm_output": f"LLM이 성공적으로 처리했습니다. (프롬프트 길이: {len(prompt_text)} 문자)",
            "prompt_used": prompt_text,
            "usage_tokens": len(prompt_text) // 5 # 대략적인 토큰 Mock
        }
        
        return mock_llm_response

    async def generate_response(self, request: ChatRequest) -> Dict[str, Any]:
        """
        Chatting 클래스에서 호출되는 메인 처리 메서드입니다.
        """
        # 1. Gongo를 통해 데이터 가져오기
        prompt_text = await self._get_llm_input_text(request)
        
        # 2. LLM 호출
        llm_result = await self._call_llm_api(prompt_text)
        
        return llm_result