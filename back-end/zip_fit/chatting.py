from typing import Dict, Any
# 🌟 models.py에서 Pydantic 모델 임포트
from .models import ChatRequest, ChatResponse
# LlmEngine 임포트
from .llm_engine import LlmEngine


class Chatting:
    """
    순수한 서비스 로직만 담고 있는 클래스입니다. 
    LlmEngine을 주입받아 사용합니다.
    """
    # 🌟 생성자를 통해 LlmEngine 인스턴스를 주입받습니다.
    def __init__(self, llm_engine: LlmEngine):
        self.llm_engine = llm_engine
        print("💡 Chatting Class initialized with LlmEngine.")
        
    # 🌟🌟🌟 누락되었을 가능성이 높은 Getter 메서드 🌟🌟🌟
    def get_llm_engine(self):
        """LlmEngine 인스턴스를 반환하는 Getter 메서드"""
        return self.llm_engine
    
    def get_gongo_service(self):
        """Gongo 인스턴스를 반환하는 Getter 메서드"""
        # LlmEngine이 Gongo를 가지고 있으므로 LlmEngine을 통해 접근합니다.
        return self.llm_engine.gongo_service
    # 🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟

    async def get_chat_response(self, request: ChatRequest) -> ChatResponse:
        """
        사용자의 요청을 받아 LlmEngine을 호출하고 응답을 반환합니다.
        """
        # 🌟 LlmEngine의 generate_response 메서드를 호출합니다.
        llm_result = await self.llm_engine.generate_response(request)
        
        # LlmEngine의 결과를 ChatResponse 형식에 맞게 가공합니다.
        final_response = llm_result.get("llm_output", "LLM 응답이 생성되지 않았습니다.")
        
        return ChatResponse(
            response=f"[LLM 엔진 처리 결과] {final_response}",
            status="llm_mock_processed",
            processed_by=f"Chatting -> LlmEngine (Used Tokens: {llm_result.get('usage_tokens')})"
        )