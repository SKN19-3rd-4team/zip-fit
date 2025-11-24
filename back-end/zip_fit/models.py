from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="사용자 식별 ID (예: 'user123')")
    query: str = Field(..., description="사용자 질문")

class ResetRequest(BaseModel):
    user_id: str

class SourceInfo(BaseModel):
    announcement_id: str
    announcement_title: str
    announcement_date: Optional[str] = None
    announcement_url: Optional[str] = None
    announcement_status: Optional[str] = None
    matched_content: Optional[str] = Field(None, description="검색된 원문 텍스트 요약")
    region: str
    notice_type: str
    category: str
    rerank_score: float
    num_chunks: int

class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceInfo]
    metadata: Optional[Dict[str, Any]] = None
    session_history: Optional[List[Dict[str, Any]]] = Field(None, description="현재 세션의 전체 대화 기록")
    process_info: Optional[Dict[str, Any]] = Field(None, description="질문 재구성 및 분석 정보")

class StatsResponse(BaseModel):
    CNT_ALL: int = Field(..., description="전체 공고 수")
    CNT_NOTE_ING: int = Field(..., description="공고중인 건수")
    CNT_APP_ING: int = Field(..., description="접수중인 건수")
    CNT_ELSE: int = Field(..., description="그 외(마감 등) 건수")