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
            if filters.get('status') and filters['status'].strip():
                where_clauses.append(f"a.status = ${len(params)+1}")
                params.append(filters['status'])
        
        if filter_ids:
            where_clauses.append(f"a.id = ANY(${len(params)+1}::text[])")
            params.append(filter_ids)
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(top_k)
        
        sql = f"""
            SELECT dc.id as chunk_id, dc.announcement_id, a.title, a.category, a.region, a.notice_type,
                   a.posted_date, a.url, a.status, dc.chunk_text, dc.chunk_index, dc.metadata,
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


# 2. 키워드 검색 (Keyword Search)
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
            if filters.get('status') and filters['status'].strip():
                where_clauses.append(f"a.status = ${len(params)+1}")
                params.append(filters['status'])

        if filter_ids:
            where_clauses.append(f"a.id = ANY(${len(params)+1}::text[])")
            params.append(filter_ids)
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(top_k)
        
        sql = f"""
            SELECT DISTINCT ON (dc.id) dc.id as chunk_id, dc.announcement_id, a.title, a.category, a.region,
                   a.notice_type, a.posted_date, a.url, a.status, dc.chunk_text, dc.chunk_index, dc.metadata
            FROM document_chunks dc
            JOIN announcements a ON dc.announcement_id = a.id
            WHERE ({keyword_sql}) {where_sql}
            LIMIT ${len(params)}
        """
        
        rows = await conn.fetch(sql, *params)
        return [dict(row) for row in rows]
    finally:
        await conn.close()


# 3. 하이브리드 검색 (Hybrid Search)
async def multi_query_hybrid_search(
    query_analysis: Dict,
    multi_queries: List[str],
    vector_top_k: int = 10,
    keyword_top_k: int = 5
) -> List[Dict]:
    filters = {
        'region': query_analysis.get('region', ''),
        'notice_type': query_analysis.get('notice_type', ''),
        'category': query_analysis.get('category', ''),
        'status': query_analysis.get('status', '')
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
async def rerank_results(query: str, search_results: List[Dict], top_k: int = 25) -> List[Dict]:
    """
    Cross-Encoder를 사용하여 결과의 순위를 재조정합니다.
    """
    if not search_results:
        return []
    
    reranker = get_reranker()

    if reranker is None:
        sorted_results = sorted(search_results, key=lambda x: x.get('similarity', 0), reverse=True)
        return sorted_results[:top_k]

    try:
        pairs = [(query, r['chunk_text']) for r in search_results]
        scores = await asyncio.to_thread(reranker.predict, pairs)
        
        for i, result in enumerate(search_results):
            result['rerank_score'] = float(scores[i])
        
        reranked = sorted(search_results, key=lambda x: x['rerank_score'], reverse=True)
        return reranked[:top_k]
        
    except Exception as e:
        print(f"[Warning] Reranking 중 오류 발생: {e}")
        return search_results[:top_k]


# 5. 청크 병합 (Merge Chunks)
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
            'announcement_url': ann_chunks[0].get('url'),
            'announcement_status': ann_chunks[0].get('status'),
            'region': ann_chunks[0]['region'],
            'notice_type': ann_chunks[0]['notice_type'],
            'category': ann_chunks[0]['category'],
            'merged_content': merged_text,
            'rerank_score': max_score_chunk.get('rerank_score', 0),
            'num_chunks': len(ann_chunks)
        })
    
    merged_results.sort(key=lambda x: x['rerank_score'], reverse=True)
    return merged_results

# 6. 컨텍스트 구성 (Context Builder)
def build_context(merged_results: List[Dict]) -> str:
    if not merged_results:
        return "검색된 관련 정보가 없습니다."
    
    context_parts = []
    for i, result in enumerate(merged_results, 1):
        category_name = "임대" if result['category'] == 'lease' else "분양"
        url = result.get('announcement_url', '')

        context_parts.append(f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문서 {i}: {result['announcement_title']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[기본 정보]
- 분류: {category_name}
- 지역: {result['region']}
- 유형: {result['notice_type'] or 'N/A'}
- 상태: {result['announcement_status'] or '알수없음'}
- 공고 URL: {url if url else 'URL 정보 없음'}
- 관련도: {result['rerank_score']:.3f}

[문서 내용]
{result['merged_content']}""")
    
    return '\n\n'.join(context_parts)


# 7. DB 로그 관리 함수 (info.py에서 호출)
async def save_chat_log(user_id: str, query: str, answer: str, sources: List[Dict]):
    """
    대화 내용을 DB에 저장합니다.
    """
    conn = await asyncpg.connect(**get_db_config())
    try:
        # sources는 JSONB 형태로 저장
        await conn.execute("""
            INSERT INTO chat_logs (user_id, query, answer, sources)
            VALUES ($1, $2, $3, $4)
        """, user_id, query, answer, json.dumps(sources, ensure_ascii=False))
    except Exception as e:
        print(f"[Warning] 로그 저장 실패 (테이블 없음 등): {e}")
    finally:
        await conn.close()

async def get_chat_logs(limit: int = 50):
    """
    저장된 대화 로그를 조회합니다.
    """
    conn = await asyncpg.connect(**get_db_config())
    try:
        rows = await conn.fetch("""
            SELECT id, user_id, query, answer, sources, created_at
            FROM chat_logs
            ORDER BY created_at DESC
            LIMIT $1
        """, limit)
        results = []
        for row in rows:
            r = dict(row)
            # JSON string을 파이썬 객체로 변환
            if isinstance(r['sources'], str):
                r['sources'] = json.loads(r['sources'])
            # datetime을 문자열로 변환
            r['created_at'] = r['created_at'].isoformat()
            results.append(r)
        return results
    except Exception as e:
        print(f"[Warning] 로그 조회 실패: {e}")
        return []
    finally:
        await conn.close()


async def get_announcement_metadata(announcement_ids: List[str]) -> List[Dict]:
    """
    벡터 데이터가 없는 공고의 기본 정보를 RDB에서 가져옵니다.
    """
    if not announcement_ids:
        return []

    conn = await asyncpg.connect(**get_db_config())
    try:
        sql = """
            SELECT id, title, category, region, notice_type,
                   posted_date, url, status
            FROM announcements
            WHERE id = ANY($1::text[])
        """
        rows = await conn.fetch(sql, announcement_ids)

        results = []
        for row in rows:
            posted_date = row.get('posted_date')
            announcement_date = str(posted_date) if posted_date else None

            results.append({
                'announcement_id': row['id'],
                'announcement_title': row['title'],
                'announcement_date': announcement_date,
                'announcement_url': row.get('url'),
                'announcement_status': row.get('status'),
                'region': row['region'],
                'notice_type': row['notice_type'],
                'category': row['category'],
                'merged_content': '(상세 내용이 아직 처리되지 않았습니다. 공고 링크를 참고해주세요.)',
                'rerank_score': 0.0,
                'num_chunks': 0
            })

        return results
    finally:
        await conn.close()