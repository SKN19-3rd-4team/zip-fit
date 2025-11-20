from typing import Any, Dict
import asyncio

# 🌟 1. 메모리에 저장할 전역 변수 (딕셔너리)
_MEMORY_DB: Dict[str, Any] = {}

# 🌟 2. 동시성 제어를 위한 락
_db_lock = asyncio.Lock()

async def get_session(session_name: str, variable: str = None) -> Any:
    """
    메모리에서 세션 데이터를 조회합니다.
    """
    async with _db_lock:
        # 세션 자체가 없으면 None 반환
        if session_name not in _MEMORY_DB:
            return None
            
        # 특정 변수만 요청했으면 그것만 반환
        if variable:
            return _MEMORY_DB[session_name].get(variable)
        else:
            return _MEMORY_DB[session_name]

async def set_session(session_name: str, variable: str, value: Any) -> None:
    """
    메모리에 세션 데이터를 저장합니다.
    """
    async with _db_lock:
        # 해당 세션 키가 없으면 초기화
        if session_name not in _MEMORY_DB:
            _MEMORY_DB[session_name] = {}
            
        # 딕셔너리에 값 할당
        _MEMORY_DB[session_name][variable] = value

async def clear_session(session_name: str) -> None:
    """
    메모리에서 특정 세션을 삭제합니다.
    """
    async with _db_lock:
        if session_name in _MEMORY_DB:
            del _MEMORY_DB[session_name]
            print(f"🧹 Memory Session cleared: {session_name}")

async def get_all_sessions() -> Dict[str, Any]:
    """
    [디버그용] 메모리에 있는 모든 세션 데이터를 반환합니다.
    router.py의 디버그 엔드포인트에서 사용합니다.
    """
    async with _db_lock:
        # 안전하게 복사본 반환
        return _MEMORY_DB.copy()