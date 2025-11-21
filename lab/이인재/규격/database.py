# 데이터베이스 관리
import asyncpg
import json
from typing import List, Dict, Any, Optional
from config import DB_CONFIG


class DatabaseManager:
    """DB 연결 및 쿼리 관리"""
    
    def __init__(self):
        self.config = DB_CONFIG
    
    async def get_connection(self):
        """DB 연결"""
        return await asyncpg.connect(**self.config)
    
    async def execute_query(self, query: str, *args):
        """쿼리 실행 및 결과 반환"""
        conn = await self.get_connection()
        try:
            return await conn.fetch(query, *args)
        finally:
            await conn.close()
    
    async def execute_single(self, query: str, *args):
        """단일 값 반환"""
        conn = await self.get_connection()
        try:
            return await conn.fetchval(query, *args)
        finally:
            await conn.close()
    
    async def execute_command(self, query: str, *args):
        """쿼리 실행 (반환값 없음)"""
        conn = await self.get_connection()
        try:
            await conn.execute(query, *args)
        finally:
            await conn.close()
    
    async def get_vectorization_progress(self) -> Dict[str, Any]:
        """벡터화 진행 상황"""
        results = await self.execute_query("SELECT * FROM vectorization_progress")
        return {
            row['category']: {
                'vectorized': row['vectorized_count'],
                'total': row['total_announcements'],
                'percentage': row['progress_pct']
            }
            for row in results
        }
    
    async def get_unvectorized_announcements(self, limit: int = 10) -> List[Dict[str, Any]]:
        """미벡터화 공고 조회"""
        query = """
            SELECT DISTINCT a.id, a.title, a.category
            FROM announcements a
            JOIN announcement_files af ON a.id = af.announcement_id
            WHERE a.is_vectorized = FALSE
            ORDER BY a.id LIMIT $1
        """
        results = await self.execute_query(query, limit)
        return [dict(row) for row in results]
    
    async def get_announcement_files(self, announcement_id: str) -> List[Dict[str, Any]]:
        """공고의 파일 목록 조회"""
        query = """
            SELECT id, announcement_id, file_name
            FROM announcement_files
            WHERE announcement_id = $1 AND is_vectorized = FALSE
        """
        results = await self.execute_query(query, announcement_id)
        return [dict(row) for row in results]
    
    async def mark_file_vectorized(self, file_id: int):
        """파일 벡터화 완료 표시"""
        query = """
            UPDATE announcement_files
            SET is_vectorized = TRUE, vectorized_at = NOW()
            WHERE id = $1
        """
        await self.execute_command(query, file_id)
    
    async def mark_announcement_vectorized(self, announcement_id: str):
        """공고 벡터화 완료 표시"""
        query = """
            UPDATE announcements
            SET is_vectorized = TRUE, vectorized_at = NOW()
            WHERE id = $1
        """
        await self.execute_command(query, announcement_id)
    
    async def insert_chunk(self, announcement_id: str, file_id: int,
                          chunk_text: str, chunk_index: int,
                          embedding: List[float], metadata: Dict[str, Any]):
        """청크 및 임베딩 저장"""
        query = """
            INSERT INTO document_chunks
            (announcement_id, file_id, chunk_text, chunk_index, embedding, metadata)
            VALUES ($1, $2, $3, $4, $5::vector, $6::jsonb)
            ON CONFLICT (file_id, chunk_index) DO NOTHING
        """
        await self.execute_command(
            query, announcement_id, file_id, chunk_text, chunk_index,
            str(embedding), json.dumps(metadata)
        )
    
    async def search_chunks(self, query_embedding: List[float], top_k: int = 5,
                           announcement_id: Optional[str] = None,
                           category: Optional[str] = None,
                           region: Optional[str] = None) -> List[Dict[str, Any]]:
        """벡터 유사도 검색 (필터 옵션)"""
        embedding_str = str(query_embedding)
        where_clauses = []
        params = [embedding_str]
        param_idx = 2
        
        if announcement_id:
            where_clauses.append(f"dc.announcement_id = ${param_idx}")
            params.append(announcement_id)
            param_idx += 1
        
        if category:
            where_clauses.append(f"a.category = ${param_idx}")
            params.append(category)
            param_idx += 1
        
        if region:
            where_clauses.append(f"a.region LIKE ${param_idx}")
            params.append(f"%{region}%")
            param_idx += 1
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(top_k)
        
        query = f"""
            SELECT
                dc.announcement_id, a.title, a.category, a.region,
                dc.chunk_text, dc.metadata,
                1 - (dc.embedding <=> $1::vector) as similarity
            FROM document_chunks dc
            JOIN announcements a ON dc.announcement_id = a.id
            WHERE 1=1 {where_sql}
            ORDER BY dc.embedding <=> $1::vector
            LIMIT ${param_idx}
        """
        
        results = await self.execute_query(query, *params)
        return [dict(row) for row in results]
    
    async def hybrid_search(self, query_embedding: List[float], keywords: str,
                           top_k: int = 5, vector_weight: float = 0.7) -> List[Dict[str, Any]]:
        """하이브리드 검색 (벡터 + 키워드)"""
        embedding_str = str(query_embedding)
        keyword_weight = 1.0 - vector_weight
        
        query = """
            WITH vector_search AS (
                SELECT
                    dc.announcement_id, a.title, a.category, a.region,
                    dc.chunk_text, dc.metadata,
                    1 - (dc.embedding <=> $1::vector) as vector_similarity
                FROM document_chunks dc
                JOIN announcements a ON dc.announcement_id = a.id
                ORDER BY dc.embedding <=> $1::vector LIMIT 20
            ),
            keyword_search AS (
                SELECT
                    dc.announcement_id, a.title, a.category, a.region,
                    dc.chunk_text, dc.metadata,
                    ts_rank(to_tsvector('simple', dc.chunk_text),
                            plainto_tsquery('simple', $2)) as keyword_score
                FROM document_chunks dc
                JOIN announcements a ON dc.announcement_id = a.id
                WHERE to_tsvector('simple', dc.chunk_text) @@ plainto_tsquery('simple', $2)
                ORDER BY keyword_score DESC LIMIT 20
            )
            SELECT DISTINCT ON (vs.announcement_id, vs.chunk_text)
                vs.announcement_id, vs.title, vs.category, vs.region,
                vs.chunk_text, vs.metadata,
                (vs.vector_similarity * $3 + COALESCE(ks.keyword_score, 0) * $4) as combined_score
            FROM vector_search vs
            LEFT JOIN keyword_search ks ON vs.chunk_text = ks.chunk_text
            ORDER BY combined_score DESC LIMIT $5
        """
        
        results = await self.execute_query(
            query, embedding_str, keywords, vector_weight, keyword_weight, top_k
        )
        return [dict(row) for row in results]
