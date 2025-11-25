from fastapi import APIRouter, HTTPException
import asyncpg
from typing import Dict, List, Any
from dependencies import get_db_config
from models import StatsResponse
import gongo

# 라우터 객체 생성
router = APIRouter()

# 공유 세션 저장소
# router.py에서 'from info import user_sessions'로 가져가서 사용합니다.
user_sessions: Dict[str, List[Dict]] = {}

# 1. 통계 정보 조회 API
@router.get("/stats", response_model=StatsResponse)
async def get_dashboard_stats():
    """
    공고 상태별 통계 정보를 반환합니다.
    """
    db_config = get_db_config()
    conn = await asyncpg.connect(**db_config)
    try:
        sql = """
            SELECT
                count(*) as "CNT_ALL",
                sum(CASE WHEN status = '공고중' THEN 1 ELSE 0 END) AS "CNT_NOTE_ING",
                sum(CASE WHEN status = '접수중' THEN 1 ELSE 0 END) AS "CNT_APP_ING",
                sum(CASE WHEN status NOT IN ('공고중','접수중') THEN 1 ELSE 0 END) as "CNT_ELSE"
            FROM public.announcements
        """
        
        row = await conn.fetchrow(sql)
        
        if not row:
            return {
                "CNT_ALL": 0, "CNT_NOTE_ING": 0, "CNT_APP_ING": 0, "CNT_ELSE": 0
            }
            
        return dict(row)

    except Exception as e:
        print(f"[Error] 통계 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
        
    finally:
        await conn.close()

# 2. 메모리 세션 상태 확인 API (프론트엔드 연결 테스트용)
@router.get("/sessions")
async def get_active_sessions():
    """
    현재 메모리에 저장된 모든 유저의 대화 세션을 확인합니다.
    URL: /api/v1/sessions
    """
    return {
        "active_user_count": len(user_sessions),
        "user_ids": list(user_sessions.keys()),
        "full_data": user_sessions
    }

# 3. DB 대화 로그 조회 API (백엔드 로직 검증용)
@router.get("/logs")
async def get_chat_logs(limit: int = 20):
    """
    DB에 저장된 대화 로그를 최신순으로 조회합니다.
    URL: /api/v1/logs
    """
    try:
        if hasattr(gongo, 'get_chat_logs'):
            logs = await gongo.get_chat_logs(limit)
            return {"count": len(logs), "logs": logs}
        else:
            return {"error": "DB Logging 기능이 gongo.py에 구현되지 않았습니다."}
    except Exception as e:
        return {"error": "로그 조회 실패", "detail": str(e)}