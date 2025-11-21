import asyncio
from typing import Dict, Any, List
from openai import AsyncOpenAI
from .db import DB
from .config import settings

class Gongo:
    """
    실제 DB 구조(document_chunks + announcements)에 맞춰 RAG 검색을 수행하는 클래스
    """
    def __init__(self):
        self.db_manager = DB()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        print("💡 Gongo initialized: Ready to search 'document_chunks'.")

    async def _get_embedding(self, text: str) -> List[float]:
        """
        [중요] DB 스키마가 vector(1024)이므로, OpenAI에도 1024차원을 요청해야 합니다.
        """
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small", 
                input=text,
                dimensions=1024  # 🌟 핵심 수정: DB 스키마에 맞춤 (기본 1536 -> 1024)
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            return []

    def _fetch_from_db_sync(self, user_id: int, query_vector: List[float]) -> str:
        """
        [Sync] 실제 DB 조회 로직 (JOIN 쿼리 사용)
        """
        conn = None
        cur = None
        try:
            conn = self.db_manager.get_connection()
            cur = conn.cursor()

            # -------------------------------------------------------
            # 1. 사용자 정보 (스키마에 users 테이블이 없으므로 Mocking)
            # -------------------------------------------------------
            # 보내주신 스키마에는 'users' 테이블이 없습니다. 
            # 에러 방지를 위해 가상의 유저 정보를 표시합니다.
            rdb_context = f"사용자 ID: {user_id} (GUEST)"

            # -------------------------------------------------------
            # 2. 벡터 검색 (document_chunks + announcements JOIN)
            # -------------------------------------------------------
            vector_context = "검색된 관련 공고가 없습니다."
            
            if query_vector:
                # 🌟 핵심 쿼리: 
                # 1. document_chunks(dc)와 announcements(a)를 조인
                # 2. 벡터 거리(Cosine Distance)로 정렬
                sql = """
                    SELECT 
                        a.title,        -- 공고 제목
                        a.region,       -- 지역
                        a.category,     -- 카테고리 (매매/임대)
                        dc.chunk_text,  -- 실제 본문 내용 (청크)
                        dc.embedding <=> %s::vector AS distance
                    FROM document_chunks dc
                    JOIN announcements a ON dc.announcement_id = a.id
                    ORDER BY distance ASC
                    LIMIT 3
                """
                
                cur.execute(sql, (query_vector,))
                rows = cur.fetchall()

                if rows:
                    results = []
                    for i, row in enumerate(rows):
                        title, region, category, chunk_text, dist = row
                        # 유사도 (거리 0이 가장 가깝음)
                        similarity = 1 - dist 
                        
                        results.append(
                            f"[{i+1}] {title} ({category}/{region})\n"
                            f"   - 내용요약: {chunk_text[:200]}...\n"
                            f"   - 적합도: {similarity:.4f}"
                        )
                    vector_context = "\n\n".join(results)

            # -------------------------------------------------------
            # 3. 최종 결과 반환
            # -------------------------------------------------------
            return (
                f"--- [Real DB Search Result] ---\n"
                f"{rdb_context}\n\n"
                f"[추천 공고 리스트]\n"
                f"{vector_context}\n"
                f"-----------------------------"
            )

        except Exception as e:
            print(f"❌ DB 쿼리 실행 중 에러: {e}")
            return f"시스템 오류: 데이터 조회 실패 ({e})"

        finally:
            if cur: cur.close()
            if conn: conn.close()

    async def get_contextual_data(self, user_id: int, query: str) -> str:
        # 메인 메서드 (비동기 래퍼)
        query_vector = await self._get_embedding(query)
        
        if not query_vector:
            return "질문 내용을 분석하지 못했습니다."

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            self._fetch_from_db_sync, 
            user_id, 
            query_vector
        )
        return result