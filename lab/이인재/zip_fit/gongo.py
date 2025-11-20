import asyncio
from typing import Dict, Any, List

class Gongo:
    """
    R-DB 및 Vector-DB에서 LLM 프롬프트 구성을 위한 데이터를 조회하는 클래스입니다.
    """
    def __init__(self):
        # NOTE: 여기에 비동기 Postgre SQL 연결 풀, Vector DB 클라이언트 등이 초기화됩니다.
        # 테스트용 가짜 데이터베이스 초기화
        self.mock_user_db = {
            1: {"name": "김철수", "grade": "VIP", "region": "서울"},
            2: {"name": "이영희", "grade": "Standard", "region": "경기"},
        }
        
        # 테스트용 가짜 공고 내용 vector DB
        self.mock_vector_db = {
            "101": "문서내용: [서울 101호 공고] 청년 매입 임대, 보증금 1000만원, 월세 15만원.",
            "202": "문서내용: [경기 202호 공고] 신혼부부 전세 임대, 최대 2억원 지원, 이자 1.5%.",
        }
        
        print("💡 Gongo Data Engine Initialized!")
        pass

    async def get_contextual_data(self, user_id: int, query: str) -> str:
        """
        사용자 ID와 쿼리를 기반으로 R-DB 및 Vector DB에서 컨텍스트 데이터를 조회합니다.
        
        Args:
            user_id: 현재 채팅 중인 사용자 ID.
            query: 사용자의 현재 질문.
            
        Returns:
            LLM 프롬프트에 삽입할 준비가 된 텍스트 문자열.
        """
        # 🚨 실제 데이터베이스 조회 대신, Mock 데이터를 반환합니다.
        
        # 1. R-DB Mock (정책, 사용자 정보 등)
        # rdb_data = f"사용자 ID({user_id})는 VIP 등급이며, 오늘 질문: '{query}'와 관련된 '최신 서비스 정책'이 유효합니다."
        
        # 2. Vector DB Mock (문서, 지식 베이스)
        # vector_data = "지식 베이스 문서 검색 결과: zip-fit 서비스의 환불 정책은 '구매 후 7일 이내'이며, 모든 문의는 고객센터(1234-5678)를 통해 처리됩니다."
        
        # 1. 가짜 RDB 조회
        user_info = self.mock_user_db.get(user_id, {"name": "Guest", "grade": "None", "region": "Unknown"})
        rdb_context = f"사용자 정보: 이름={user_info['name']}, 등급={user_info['grade']}, 거주지={user_info['region']}"
        
        # 2. Vector DB 조회 시늉 (키워드 매칭)
        vector_context = "관련 공고 문서 없음 (일반 대화)"
        
        if "101" in query:
            vector_context = self.mock_vector_db["101"]
        elif "202" in query:
            vector_context = self.mock_vector_db["202"]
        elif "추천" in query:
            vector_context = f"사용자 거주지 '{user_info['region']}' 기반 추천 공고 검색 결과..."
        
        # 비동기 처리를 시뮬레이션하기 위해 잠시 대기합니다.
        await asyncio.sleep(0.01)
        
        return (
            f"--- [Gongo Data] ---\n"
            f"RDB: {rdb_context}\n"
            f"VectorDB: {vector_context}\n"
            f"--------------------"
        )
        
        # 두 데이터를 결합하여 LLM에 전달할 최종 문자열을 만듭니다.
        # context_string = (
        #     "--- SYSTEM DATA START ---\n"
        #     f"RDB Context: {rdb_data}\n"
        #     f"VectorDB Context: {vector_data}\n"
        #     "--- SYSTEM DATA END ---\n"
        # )
        
        # return context_string