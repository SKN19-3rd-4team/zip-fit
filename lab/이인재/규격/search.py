# 검색 엔진
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, DEFAULT_TOP_K, SIMILARITY_THRESHOLD
from database import DatabaseManager


class SearchEngine:
    """벡터 및 하이브리드 검색"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.db = DatabaseManager()
    
    def extract_keywords(self, query: str) -> str:
        """키워드 추출 (불용어 제거)"""
        stop_words = ['은', '는', '이', '가', '을', '를', '의', '에', '에서', '과', '와']
        words = query.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        return ' '.join(keywords)
    
    def extract_filters(self, query: str) -> Dict[str, Any]:
        """쿼리에서 필터 자동 추출"""
        filters = {}
        
        # 지역 추출
        regions = ['서울', '경기', '인천', '남양주', '수원', '화성', '용인', '고양', '성남',
                  '부천', '안산', '안양', '평택', '시흥', '파주', '의정부', '김포']
        for region in regions:
            if region in query:
                filters['region'] = region
                break
        
        # 카테고리 추출
        if any(word in query for word in ['분양', '공공분양', '신혼희망타운']):
            filters['category'] = 'sale'
        elif any(word in query for word in ['임대', '국민임대', '영구임대', '행복주택']):
            filters['category'] = 'lease'
        
        return filters
    
    async def vector_search(self, query: str, top_k: int = DEFAULT_TOP_K, **filters) -> List[Dict[str, Any]]:
        """벡터 유사도 검색"""
        query_embedding = self.model.encode(query, normalize_embeddings=True)
        embedding_list = query_embedding.tolist()
        
        results = await self.db.search_chunks(
            query_embedding=embedding_list, top_k=top_k, **filters
        )
        
        return [r for r in results if r['similarity'] >= SIMILARITY_THRESHOLD]
    
    async def hybrid_search(self, query: str, top_k: int = DEFAULT_TOP_K, vector_weight: float = 0.7) -> List[Dict[str, Any]]:
        """하이브리드 검색 (벡터 + 키워드)"""
        query_embedding = self.model.encode(query, normalize_embeddings=True)
        embedding_list = query_embedding.tolist()
        keywords = self.extract_keywords(query)
        
        results = await self.db.hybrid_search(
            query_embedding=embedding_list,
            keywords=keywords,
            top_k=top_k,
            vector_weight=vector_weight
        )
        
        return results
    
    async def smart_search(self, query: str, top_k: int = DEFAULT_TOP_K, use_hybrid: bool = True) -> List[Dict[str, Any]]:
        """자동 필터 검색"""
        filters = self.extract_filters(query)
        
        if use_hybrid and not filters:
            return await self.hybrid_search(query, top_k)
        else:
            return await self.vector_search(query, top_k, **filters)
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """검색 결과 포맷팅"""
        if not results:
            return "검색 결과 없음"
        
        output = []
        for idx, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            output.append(
                f"[{idx}] {result['title']}\n"
                f"    지역: {result['region']} | 카테고리: {result['category']} | "
                f"유사도: {result['similarity']:.2%}\n"
                f"    파일: {metadata.get('file_name', 'N/A')}\n"
                f"    섹션: {metadata.get('section', 'N/A')}\n"
                f"    미리보기: {result['chunk_text'][:200]}...\n"
            )
        
        return "\n".join(output)
