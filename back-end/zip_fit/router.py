from fastapi import APIRouter, Depends
from typing import Dict, Any

from .chatting import Chatting 
from .models import ChatRequest, ChatResponse
from .dependencies import get_chatting_service

# 라우터 인스턴스
router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chatting"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    # 🌟 의존성 주입: Chatting 인스턴스를 깔끔하게 주입받습니다!
    chat_service: Chatting = Depends(get_chatting_service)
):
    """
    HTTP POST 요청을 받아 Chatting 서비스로 처리를 위임합니다.
    """
    # 주입받은 인스턴스(chat_service)를 사용하여 메서드 호출!
    response = await chat_service.get_chat_response(request)
    return response


# ----------------------------------------------------
# 🌟 요청하신 API 1: LlmEngine까지 다녀오는 엔드포인트
# ----------------------------------------------------
@router.post("/test/llm-only", response_model=ChatResponse)
async def test_llm_only(
    request: ChatRequest,
    chat_service: Chatting = Depends(get_chatting_service)
):
    """
    Gongo -> LlmEngine 호출 로직까지만 테스트합니다.
    """
    # Chatting 서비스에서 LlmEngine을 가져옵니다.
    llm_engine = chat_service.get_llm_engine()
    
    # LlmEngine의 메인 처리 메서드를 호출합니다.
    llm_result = await llm_engine.generate_response(request)
    
    # LlmEngine의 결과를 직접 반환 (Chatting의 최종 가공 우회)
    return ChatResponse(
        response=f"**LlmEngine Mock 호출 성공.** (사용 프롬프트: {len(llm_result.get('prompt_used'))}자)",
        status="llm_engine_mocked",
        processed_by=f"LlmEngine only test"
    )


# ----------------------------------------------------
# 🌟 요청하신 API 2: Gongo까지 다녀오는 엔드포인트
# ----------------------------------------------------
@router.post("/test/gongo-only", response_model=Dict[str, Any])
async def test_gongo_only(
    request: ChatRequest,
    chat_service: Chatting = Depends(get_chatting_service)
):
    """
    Gongo 클래스의 데이터 조회 로직까지만 테스트합니다.
    """
    # Chatting 서비스에서 Gongo 인스턴스를 가져옵니다.
    gongo_service = chat_service.get_gongo_service()
    
    # Gongo의 데이터 조회 메서드를 직접 호출합니다.
    context_data = await gongo_service.get_contextual_data(
        user_id=request.user_id,
        query=request.user_input
    )
    
    # 조회된 원본 텍스트 데이터를 반환합니다.
    return {
        "status": "gongo_service_mocked",
        "processed_by": "Gongo only test",
        "gongo_raw_output": context_data,
        "context_length": len(context_data)
    }