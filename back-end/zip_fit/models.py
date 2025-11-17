from pydantic import BaseModel
from typing import Dict, Any

# Chatting, LlmEngine, Router가 모두 사용할 Pydantic 모델
class ChatRequest(BaseModel):
    user_input: str
    user_id: int = 0

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    processed_by: str = "Chatting Class"