import asyncpg
import asyncio
import json
from typing import List, Dict, Tuple, Any
import config
from dependencies import get_embedding_model, get_reranker, get_db_config


# 1. 벡터 검색 (Vector Search)
async def vector_search(query: str, top_k: int = 15, filters: dict = None, filter_ids: List[str] = None) -> List[Dict]:
    """
    임베딩 모델을 사용해 의미 기반 검색을 수행합니다.
    """
    # 임베딩 생성
    model = get_embedding_model()
    conn = await asyncpg.connect(**get_db_config())
    try:
        query_embedding = model.encode(query, normalize_embeddings=True)
        
        where_clauses = []
        params = [str(query_embedding.tolist())]
        
        if filters:
            if filters.get('region') and filters['region'].strip():
                where_clauses.append(f"a.region LIKE ${len(params)+1}")
                params.append(f"%{filters['region']}%")
            if filters.get('category') and filters['category'].strip():
                where_clauses.append(f"a.category = ${len(params)+1}")
                params.append(filters['category'])
            if filters.get('notice_type') and filters['notice_type'].strip():
                where_clauses.append(f"a.notice_type LIKE ${len(params)+1}")
                params.append(f"%{filters['notice_type']}%")
        
        if filter_ids:
            where_clauses.append(f"a.id = ANY(${len(params)+1}::text[])")
            params.append(filter_ids)
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(top_k)
        
        sql = f"""
            SELECT dc.id as chunk_id, dc.announcement_id, a.title, a.category, a.region, a.notice_type,
                   a.posted_date, dc.chunk_text, dc.chunk_index, dc.metadata, 
                   (1 - (dc.embedding <=> $1::vector)) as similarity
            FROM document_chunks dc
            JOIN announcements a ON dc.announcement_id = a.id
            WHERE 1=1 {where_sql}
            ORDER BY dc.embedding <=> $1::vector
            LIMIT ${len(params)}
        """
        
        rows = await conn.fetch(sql, *params)
        return [dict(row) for row in rows]
    finally:
        await conn.close()


# 키워드 검색 (Keyword Search)
async def keyword_search(keywords: List[str], top_k: int = 10, filters: dict = None, filter_ids: List[str] = None) -> List[Dict]:
    """
    정확한 단어 매칭을 위한 LIKE 검색을 수행합니다.
    """
    if not keywords:
        return []

    conn = await asyncpg.connect(**get_db_config())
    try:
        params, keyword_conditions = [], []
        for kw in keywords:
            keyword_conditions.append(f"dc.chunk_text LIKE ${len(params)+1}")
            params.append(f"%{kw}%")
        
        keyword_sql = " OR ".join(keyword_conditions) if keyword_conditions else "1=1"
        
        where_clauses = []
        if filters:
            if filters.get('region') and filters['region'].strip():
                where_clauses.append(f"a.region LIKE ${len(params)+1}")
                params.append(f"%{filters['region']}%")
            if filters.get('category') and filters['category'].strip():
                where_clauses.append(f"a.category = ${len(params)+1}")
                params.append(filters['category'])
            if filters.get('notice_type') and filters['notice_type'].strip():
                where_clauses.append(f"a.notice_type LIKE ${len(params)+1}")
                params.append(f"%{filters['notice_type']}%")
        
        if filter_ids:
            where_clauses.append(f"a.id = ANY(${len(params)+1}::text[])")
            params.append(filter_ids)
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(top_k)
        
        sql = f"""
            SELECT DISTINCT ON (dc.id) dc.id as chunk_id, dc.announcement_id, a.title, a.category, a.region,
                   a.notice_type, a.posted_date, dc.chunk_text, dc.chunk_index, dc.metadata
            FROM document_chunks dc
            JOIN announcements a ON dc.announcement_id = a.id
            WHERE ({keyword_sql}) {where_sql}
            LIMIT ${len(params)}
        """
        
        rows = await conn.fetch(sql, *params)
        return [dict(row) for row in rows]
    finally:
        await conn.close()


# 하이브리드 검색 (Hybrid Search)
async def multi_query_hybrid_search(
    query_analysis: Dict,
    multi_queries: List[str],
    vector_top_k: int = 10,
    keyword_top_k: int = 5
) -> List[Dict]:
    filters = {
        'region': query_analysis.get('region', ''),
        'notice_type': query_analysis.get('notice_type', ''),
        'category': query_analysis.get('category', '')
    }
    
    filter_ids = None
    if 'context_analysis' in query_analysis:
        context = query_analysis['context_analysis']
        if context.get('is_followup') and context.get('referenced_announcement_ids'):
            filter_ids = context['referenced_announcement_ids']
    
    
    tasks = []
    for q in multi_queries:
        tasks.append(vector_search(q, vector_top_k, filters, filter_ids))
        tasks.append(keyword_search(query_analysis.get('search_keywords', []), keyword_top_k, filters, filter_ids))
        
    results_list = await asyncio.gather(*tasks)
    
    all_results = {}
    for results in results_list:
        for r in results:
            chunk_id = r['chunk_id']
            if chunk_id not in all_results:
                all_results[chunk_id] = r
                
    return list(all_results.values())


# 4. 재순위화 (Reranking)
def rerank_results(query: str, search_results: List[Dict], top_k: int = 8) -> List[Dict]:
    """
    Cross-Encoder를 사용하여 결과의 순위를 재조정합니다.
    config.USE_RERANKER가 False면 단순 유사도 정렬을 수행합니다.
    """
    if not search_results:
        return []
    
    reranker = get_reranker() # 스위치가 꺼져있으면 None 반환

    # Reranker OFF 또는 모델 로드 실패 시
    if reranker is None:
        # 기존 similarity 점수(Vector 검색 결과) 기준으로 정렬
        sorted_results = sorted(search_results, key=lambda x: x.get('similarity', 0), reverse=True)
        return sorted_results[:top_k]

    # Reranker ON
    try:
        pairs = [(query, r['chunk_text']) for r in search_results]
        scores = reranker.predict(pairs)
        
        for i, result in enumerate(search_results):
            result['rerank_score'] = float(scores[i])
        
        # Rerank 점수 기준 정렬
        reranked = sorted(search_results, key=lambda x: x['rerank_score'], reverse=True)
        return reranked[:top_k]
        
    except Exception as e:
        print(f"[Warning] Reranking 중 오류 발생: {e}")
        return search_results[:top_k]


async def merge_chunks(chunks: List[Dict]) -> List[Dict]:
    if not chunks:
        return []
    
    announcement_chunks = {}
    for chunk in chunks:
        ann_id = chunk['announcement_id']
        if ann_id not in announcement_chunks:
            announcement_chunks[ann_id] = []
        announcement_chunks[ann_id].append(chunk)
    
    merged_results = []
    for ann_id, ann_chunks in announcement_chunks.items():
        ann_chunks.sort(key=lambda x: x.get('chunk_index', 999))
        
        merged_text = '\n\n'.join([c['chunk_text'] for c in ann_chunks])
        max_score_chunk = max(ann_chunks, key=lambda x: x.get('rerank_score', 0))
        
        posted_date = ann_chunks[0].get('posted_date')
        announcement_date = str(posted_date) if posted_date else None

        merged_results.append({
            'announcement_id': ann_id,
            'announcement_title': ann_chunks[0]['title'],
            'announcement_date': announcement_date,
            'region': ann_chunks[0]['region'],
            'notice_type': ann_chunks[0]['notice_type'],
            'category': ann_chunks[0]['category'],
            'merged_content': merged_text,
            'rerank_score': max_score_chunk.get('rerank_score', 0),
            'num_chunks': len(ann_chunks)
        })
    
    merged_results.sort(key=lambda x: x['rerank_score'], reverse=True)
    return merged_results

# 컨텍스트 구성 (Context Builder)
def build_context(merged_results: List[Dict]) -> str:
    if not merged_results:
        return "검색된 관련 정보가 없습니다."
    
    context_parts = []
    for i, result in enumerate(merged_results, 1):
        category_name = "임대" if result['category'] == 'lease' else "분양"
        
        context_parts.append(f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문서 {i}: {result['announcement_title']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[기본 정보]
- 분류: {category_name}
- 지역: {result['region']}
- 유형: {result['notice_type'] or 'N/A'}
- 관련도: {result['rerank_score']:.3f}

[문서 내용]
{result['merged_content']}""")
    
    return '\n\n'.join(context_parts)