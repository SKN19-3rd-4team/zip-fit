import os
import asyncio
import asyncpg
import json
import time
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, CrossEncoder
from openai import OpenAI

# API 키 로드
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_API_KEY_HERE":
    print("⚠️ OPENAI_API_KEY 환경변수를 설정하거나 코드에 직접 입력해 주세요.")

# DB 설정
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'skn19_3rd_proj',
    'user': 'rag_user',
    'password': 'skn19'
}

# 클라이언트 및 모델 로드
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
embedding_model = SentenceTransformer('BAAI/bge-m3')

# CrossEncoder('Dongjin-kr/ko-reranker', device='cpu') - 한국어 특화, 상대적으로 느림
# CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2') - 범용, 빠름
RERANKER = CrossEncoder('Dongjin-kr/ko-reranker', device='cpu')

print("환경 설정 완료")


# =============================================================================
# 멀티 쿼리 생성 함수
# =============================================================================
def generate_multi_queries(query: str, num_queries: int = 3) -> List[str]:
    """원본 질문을 여러 개의 다른 표현으로 변환합니다."""
    
    multi_query_prompt = """당신은 LH 공사 임대/분양 공고 검색을 돕는 AI 어시스턴트입니다.
사용자의 질문을 다양한 관점에서 재작성하여 검색 성능을 높이세요.

원본 질문에 대해 3개의 다른 버전을 생성하세요:
1. 동의어나 유사 표현을 사용한 버전
2. 더 구체적이거나 상세한 버전  
3. 더 일반적이거나 넓은 범위의 버전

규칙:
- 각 질문은 한 줄에 하나씩 작성
- 번호나 기호 없이 질문만 작성
- 원본 질문의 의도를 유지
- LH, 임대주택, 분양주택 관련 용어 활용

원본 질문: {question}

변환된 질문들:"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": multi_query_prompt.format(question=query)}],
            temperature=0.7,
            max_tokens=500
        )
        result = response.choices[0].message.content
        generated = [q.strip() for q in result.strip().split("\n") if q.strip()]
        return [query] + generated[:num_queries]
    except Exception as e:
        print(f"멀티 쿼리 생성 오류: {e}")
        return [query]


async def rewrite_query(query: str, conversation_history: List[Dict] = None) -> Dict:
    """LLM을 활용하여 질문을 재구성하고 확장"""
    
    context_str = ""
    if conversation_history:
        recent = conversation_history[-3:]
        context_str = "\n이전 대화:\n" + "\n".join([
            f"Q: {h['query']}\nA: {h['answer'][:100]}..." for h in recent
        ])
    
    system_prompt = """당신은 LH 공고 검색 시스템의 질문 분석 전문가입니다.
사용자의 질문을 분석하여 다음 정보를 JSON 형식으로 추출하세요:

1. rewritten: 완전한 문장으로 재구성된 질문 (대화 맥락 반영)
2. expanded: 검색 최적화를 위한 확장 쿼리 (유사어, 관련어 포함)
3. keywords: 핵심 키워드 리스트 (세부 지역명 포함)
4. filters: 메타데이터 필터
   - region: "경기도", "서울특별시", "서울특별시 외" 중 하나
   - notice_type: "국민임대", "행복주택", "영구임대" 등
   - category: "lease" 또는 "sale"

중요: 세부 지역명(남양주, 수원)은 keywords에만, filters.region은 광역시/도만 사용"""

    user_prompt = f"{context_str}\n\n현재 질문: {query}\n\n위 질문을 분석하여 검색에 최적화된 형태로 재구성해주세요."

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        result['original'] = query
        return result
    except Exception as e:
        return {'original': query, 'rewritten': query, 'expanded': query, 'keywords': query.split(), 'filters': {}}


async def vector_search(query: str, top_k: int = 15, filters: dict = None, filter_ids: List[str] = None) -> List[Dict]:
    """벡터 유사도 검색 (의미 기반)"""
    query_embedding = embedding_model.encode(query, normalize_embeddings=True)
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        where_clauses, params = [], [str(query_embedding.tolist())]
        
        if filters:
            if 'region' in filters:
                where_clauses.append(f"a.region LIKE ${len(params)+1}")
                params.append(f"%{filters['region']}%")
            if 'category' in filters:
                where_clauses.append(f"a.category = ${len(params)+1}")
                params.append(filters['category'])
            if 'notice_type' in filters:
                where_clauses.append(f"a.notice_type LIKE ${len(params)+1}")
                params.append(f"%{filters['notice_type']}%")
        
        if filter_ids:
            where_clauses.append(f"a.id = ANY(${len(params)+1}::text[])")
            params.append(filter_ids)
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(top_k)
        
        sql = f"""
            SELECT dc.id as chunk_id, dc.announcement_id, a.title, a.category, a.region, a.notice_type,
                   dc.chunk_text, dc.metadata, (1 - (dc.embedding <=> $1::vector)) as similarity, 'vector' as search_type
            FROM document_chunks dc
            JOIN announcements a ON dc.announcement_id = a.id
            WHERE 1=1 {where_sql}
            ORDER BY dc.embedding <=> $1::vector
            LIMIT ${len(params)}
        """
        return [dict(r) for r in await conn.fetch(sql, *params)]
    finally:
        await conn.close()


async def keyword_search(keywords: List[str], top_k: int = 10, filters: dict = None) -> List[Dict]:
    """키워드 기반 검색 (LIKE 검색)"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        params, keyword_conditions = [], []
        for kw in keywords:
            keyword_conditions.append(f"dc.chunk_text LIKE ${len(params)+1}")
            params.append(f"%{kw}%")
        
        keyword_sql = " OR ".join(keyword_conditions) if keyword_conditions else "1=1"
        
        where_clauses = []
        if filters:
            if 'region' in filters:
                where_clauses.append(f"a.region LIKE ${len(params)+1}")
                params.append(f"%{filters['region']}%")
            if 'category' in filters:
                where_clauses.append(f"a.category = ${len(params)+1}")
                params.append(filters['category'])
            if 'notice_type' in filters:
                where_clauses.append(f"a.notice_type LIKE ${len(params)+1}")
                params.append(f"%{filters['notice_type']}%")
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(top_k)
        
        sql = f"""
            SELECT DISTINCT ON (dc.id) dc.id as chunk_id, dc.announcement_id, a.title, a.category, a.region,
                   a.notice_type, dc.chunk_text, dc.metadata, 0.5 as similarity, 'keyword' as search_type
            FROM document_chunks dc
            JOIN announcements a ON dc.announcement_id = a.id
            WHERE ({keyword_sql}) {where_sql}
            LIMIT ${len(params)}
        """
        return [dict(r) for r in await conn.fetch(sql, *params)]
    finally:
        await conn.close()


# =============================================================================
# 멀티 쿼리 하이브리드 검색
# =============================================================================
async def multi_query_hybrid_search(
    query_analysis: Dict, 
    use_multi_query: bool = True,
    vector_top_k: int = 10, 
    keyword_top_k: int = 5
) -> Tuple[List[Dict], List[str]]:
    """멀티 쿼리를 활용한 하이브리드 검색"""
    
    if use_multi_query:
        queries = generate_multi_queries(query_analysis.get('rewritten', query_analysis['original']))
        print(f"  📝 생성된 질의 ({len(queries)}개):")
        for i, q in enumerate(queries):
            prefix = "원본" if i == 0 else f"변환{i}"
            print(f"     [{prefix}] {q}")
    else:
        queries = [query_analysis.get('rewritten', query_analysis['original'])]
    
    all_results, seen_chunks = [], set()
    filters = query_analysis.get('filters', {})
    
    for q in queries:
        vector_results = await vector_search(q, top_k=vector_top_k, filters=filters)
        for r in vector_results:
            if r['chunk_id'] not in seen_chunks:
                seen_chunks.add(r['chunk_id'])
                all_results.append(r)
        
        if q == queries[0]:
            keyword_results = await keyword_search(query_analysis.get('keywords', []), top_k=keyword_top_k, filters=filters)
            for r in keyword_results:
                if r['chunk_id'] not in seen_chunks:
                    seen_chunks.add(r['chunk_id'])
                    all_results.append(r)
    
    return all_results, queries


async def hybrid_search(query_analysis: Dict, vector_top_k: int = 15, keyword_top_k: int = 10) -> List[Dict]:
    """하이브리드 검색 (단일 쿼리 버전, 호환성 유지)"""
    results, _ = await multi_query_hybrid_search(query_analysis, use_multi_query=False, vector_top_k=vector_top_k, keyword_top_k=keyword_top_k)
    return results


# =============================================================================
# 리랭킹 함수
# =============================================================================
def rerank_results(query: str, search_results: List[Dict], top_k: int = 8) -> List[Dict]:
    """Cross-Encoder를 사용한 정밀 재순위화"""
    if not search_results:
        return []
    
    pairs = [(query, r['chunk_text']) for r in search_results]
    scores = RERANKER.predict(pairs, show_progress_bar=False)
    
    for i, result in enumerate(search_results):
        result['rerank_score'] = float(scores[i])
    
    reranked = sorted(search_results, key=lambda x: x['rerank_score'], reverse=True)
    return reranked[:top_k]


def build_context(reranked_results: List[Dict]) -> Tuple[str, List[Dict]]:
    """청크 병합 및 구조화된 컨텍스트 구성"""
    
    announcement_chunks = {}
    for r in reranked_results:
        ann_id = r['announcement_id']
        if ann_id not in announcement_chunks:
            announcement_chunks[ann_id] = {
                'announcement_id': ann_id, 'title': r['title'], 'category': r['category'],
                'region': r['region'], 'notice_type': r['notice_type'], 'metadata': r['metadata'],
                'chunk_texts': [r['chunk_text']], 'rerank_score': r['rerank_score'], 'chunk_count': 1
            }
        else:
            announcement_chunks[ann_id]['chunk_texts'].append(r['chunk_text'])
            announcement_chunks[ann_id]['chunk_count'] += 1
            announcement_chunks[ann_id]['rerank_score'] = max(announcement_chunks[ann_id]['rerank_score'], r['rerank_score'])
    
    merged = sorted(announcement_chunks.values(), key=lambda x: x['rerank_score'], reverse=True)
    
    context_parts, sources = [], []
    for idx, m in enumerate(merged, 1):
        metadata = json.loads(m['metadata']) if isinstance(m['metadata'], str) else m['metadata']
        category_name = "임대" if m['category'] == 'lease' else "분양"
        merged_text = '\n\n'.join(m['chunk_texts'])
        
        context_parts.append(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문서 {idx}: {m['title']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[기본 정보]
- 분류: {category_name}
- 지역: {m['region']}
- 유형: {m['notice_type'] or 'N/A'}
- 관련도: {m['rerank_score']:.3f}

[문서 내용]
{merged_text}
        """.strip())
        
        # sources에 category, notice_type 추가
        sources.append({
            'announcement_id': m['announcement_id'],
            'title': m['title'],
            'category': m['category'],
            'region': m['region'],
            'notice_type': m['notice_type'],
            'score': m['rerank_score'],
            'chunk_count': m['chunk_count']
        })
    
    return "\n\n".join(context_parts), sources


def generate_answer(query: str, context: str, sources: List[Dict], queries_used: List[str] = None) -> Dict:
    """LLM으로 답변 생성"""
    
    system_prompt = """당신은 LH 공사의 임대/분양 공고 전문 상담사입니다.

# 답변 원칙
1. 제공된 문서만을 근거로 답변
2. 문서에 없는 내용은 "제공된 공고에서 확인할 수 없습니다" 명시
3. 표가 있으면 마크다운 표로 정리
4. 숫자, 날짜, 조건은 정확히 인용
5. 답변 끝에 [문서 1, 2 참조] 형태로 출처 표시"""

    user_prompt = f"# 제공된 문서\n\n{context}\n\n# 사용자 질문\n{query}\n\n위 문서를 바탕으로 정확하게 답변해주세요."

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        return {
            'answer': response.choices[0].message.content,
            'sources': sources,
            'queries_used': queries_used or [],
            'metadata': {'model': 'gpt-4o-mini', 'tokens': response.usage.total_tokens}
        }
    except Exception as e:
        return {'answer': f"답변 생성 오류: {str(e)}", 'sources': sources, 'queries_used': queries_used or [], 'metadata': {'error': str(e)}}


# =============================================================================
# 참고 문서 출력 함수
# =============================================================================
def print_source_documents(sources: List[Dict]):
    """참고 문서를 표 형식으로 출력"""
    print("\n" + "-"*80)
    confidence = "높음" if len(sources) >= 3 else "중간" if len(sources) >= 1 else "낮음"
    print(f"### 📚 참고 문서 ({len(sources)}건) | 신뢰도: {confidence} ###")
    print("-"*80 + "\n")
    
    if sources:
        print("| 순번 | 공고명 | 분류 | 지역 | 공고유형 | 관련도 |")
        print("|:---:|:---|:---:|:---:|:---:|:---:|")
        for i, doc in enumerate(sources, 1):
            title = doc['title'][:40] + "..." if len(doc['title']) > 40 else doc['title']
            category = "임대" if doc.get('category') == 'lease' else "분양"
            region = doc.get('region', 'N/A')
            notice_type = doc.get('notice_type', 'N/A') if doc.get('notice_type') else 'N/A'
            score = f"{doc.get('score', 0):.3f}"
            print(f"| {i} | {title} | {category} | {region} | {notice_type} | {score} |")
    else:
        print("참고 문서 없음")


# =============================================================================
# 통합 RAG 파이프라인 (멀티 쿼리 지원)
# =============================================================================
async def rag_chatbot(
    query: str, 
    conversation_history: List[Dict] = None, 
    verbose: bool = True,
    use_multi_query: bool = True
) -> Dict:
    """6단계 RAG 파이프라인 통합 함수"""
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*80}\n질문: {query}\n{'='*80}")
        print(f"🔄 Multi-Query: {'활성화' if use_multi_query else '비활성화'}")
    
    # 1. 질문 재구성
    step1_start = time.time()
    query_analysis = await rewrite_query(query, conversation_history)
    step1_time = time.time() - step1_start
    if verbose:
        print(f"\n[1/5] 질문 재구성: {query_analysis.get('rewritten', 'N/A')} ({step1_time:.2f}초)")
    
    # 2. 멀티 쿼리 하이브리드 검색
    step2_start = time.time()
    search_results, queries_used = await multi_query_hybrid_search(query_analysis, use_multi_query=use_multi_query, vector_top_k=10, keyword_top_k=5)
    step2_time = time.time() - step2_start
    if verbose:
        print(f"[2/5] 하이브리드 검색: {len(search_results)}개 결과 ({step2_time:.2f}초)")
    
    if not search_results:
        return {'query': query, 'answer': "관련 정보를 찾을 수 없습니다.", 'sources': [], 'queries_used': queries_used}
    
    # 3. 재순위화
    step3_start = time.time()
    reranked = rerank_results(query_analysis.get('rewritten', query), search_results, top_k=8)
    step3_time = time.time() - step3_start
    if verbose:
        print(f"[3/5] 재순위화: 상위 {len(reranked)}개 선정 (최고 점수: {reranked[0]['rerank_score']:.4f}) ({step3_time:.2f}초)")
    
    # 4. 컨텍스트 구성
    step4_start = time.time()
    context, sources = build_context(reranked)
    step4_time = time.time() - step4_start
    if verbose:
        print(f"[4/5] 컨텍스트 구성: {len(context)} 문자 ({step4_time:.2f}초)")
    
    # 5. 답변 생성
    step5_start = time.time()
    result = generate_answer(query_analysis.get('rewritten', query), context, sources, queries_used)
    step5_time = time.time() - step5_start
    
    total_time = time.time() - start_time
    
    if verbose:
        print(f"[5/5] 답변 생성 완료 ({step5_time:.2f}초)")
        print(f"\n⏱️ 총 소요 시간: {total_time:.2f}초")
        print(f"   - 질문 재구성: {step1_time:.2f}초")
        print(f"   - 검색: {step2_time:.2f}초")
        print(f"   - 재순위화: {step3_time:.2f}초")
        print(f"   - 컨텍스트: {step4_time:.2f}초")
        print(f"   - 답변 생성: {step5_time:.2f}초")
        print(f"\n{'='*80}\n{result['answer']}\n{'='*80}")
        
        # 참고 문서 출력
        print_source_documents(sources)
        
        # 사용된 검색 쿼리 출력
        if queries_used and len(queries_used) > 1:
            print(f"\n🔍 사용된 검색 쿼리:")
            for i, q in enumerate(queries_used):
                prefix = "원본" if i == 0 else f"변환{i}"
                print(f"   [{prefix}] {q}")
    
    return {
        'query': query, 
        'query_analysis': query_analysis, 
        'queries_used': queries_used,
        'timing': {'total': total_time, 'rewrite': step1_time, 'search': step2_time, 'rerank': step3_time, 'context': step4_time, 'generate': step5_time},
        **result
    }


# =============================================================================
# 대화 맥락 관리
# =============================================================================
conversation_history = []

async def analyze_context(query: str, history: List[Dict]) -> Dict:
    """LLM으로 맥락 참조 분석"""
    if not history:
        return {'is_context_question': False}
    
    history_str = "\n".join([f"Q: {h['query']}\nA: {h['answer'][:200]}..." for h in history[-2:]])
    
    system_prompt = """대화 맥락 분석 전문가입니다. 현재 질문이 이전 대화를 참조하는지 판단하세요.
JSON 응답: {"is_context_question": true/false, "reason": "판단 근거", "referenced_announcement_indices": [0, 1]}"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"이전 대화:\n{history_str}\n\n현재 질문: {query}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {'is_context_question': False}


async def chat(query: str, verbose: bool = True, use_multi_query: bool = True):
    """대화 맥락을 유지하는 챗봇"""
    
    context_analysis = await analyze_context(query, conversation_history)
    is_context = context_analysis.get('is_context_question', False)
    
    if is_context and conversation_history:
        if verbose:
            print(f"[맥락 인식] {context_analysis.get('reason', '')}")
        
        prev_ids = []
        for idx in context_analysis.get('referenced_announcement_indices', [0]):
            if idx < len(conversation_history):
                for src in conversation_history[-(idx+1)].get('sources', [])[:3]:
                    if src.get('announcement_id') and src['announcement_id'] not in prev_ids:
                        prev_ids.append(src['announcement_id'])
        
        if prev_ids:
            query_analysis = await rewrite_query(query, conversation_history)
            
            context_results = await vector_search(query_analysis.get('rewritten', query), top_k=5, filter_ids=prev_ids)
            general_results, queries_used = await multi_query_hybrid_search(query_analysis, use_multi_query=use_multi_query)
            
            seen = {r['chunk_id'] for r in context_results}
            combined = context_results + [r for r in general_results if r['chunk_id'] not in seen]
            
            reranked = rerank_results(query_analysis.get('rewritten', query), combined, top_k=8)
            context, sources = build_context(reranked)
            result = generate_answer(query_analysis.get('rewritten', query), context, sources, queries_used)
            result = {'query': query, 'query_analysis': query_analysis, **result}
            
            if verbose:
                print(f"\n{'='*80}\n{result['answer']}\n{'='*80}")
                # 참고 문서 출력
                print_source_documents(sources)
        else:
            result = await rag_chatbot(query, conversation_history, verbose, use_multi_query)
    else:
        result = await rag_chatbot(query, conversation_history, verbose, use_multi_query)
    
    conversation_history.append({
        'query': query,
        'answer': result['answer'],
        'sources': result.get('sources', [])
    })
    
    if len(conversation_history) > 10:
        conversation_history.pop(0)
    
    return result


# =============================================================================
# 테스트 실행
# =============================================================================
async def main():
    print("\n" + "="*80)
    print("📌 테스트 1: 멀티 쿼리 활성화")
    print("="*80)
    await chat("수원시 행복주택 알려줘", use_multi_query=True)
    
    print("\n" + "="*80)
    print("📌 테스트 2: 맥락 참조 질문")
    print("="*80)
    await chat("거기 청년 계층 출생자녀에 따른 소득 기준은?", use_multi_query=True)
    
    print("\n" + "="*80)
    print("📌 테스트 3: 멀티 쿼리 비활성화 (비교)")
    print("="*80)
    conversation_history.clear()
    await chat("LH 행복주택 청년 대상 조건은?", use_multi_query=False)


if __name__ == "__main__":
    asyncio.run(main())