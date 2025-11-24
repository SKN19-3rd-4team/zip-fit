from typing import List, Dict, Any
import asyncio
import llm_handler
import gongo


# 1. 기본 RAG 프로세스 (Standard RAG)
async def rag_process(query: str, history: List[Dict], verbose: bool = True) -> Dict:
    """
    맥락과 관계없는 새로운 질문을 처리하는 표준 RAG 파이프라인
    순서: 재구성 -> 멀티쿼리 생성 -> 하이브리드 검색 -> 재순위화 -> 청크 병합 -> 컨텍스트 -> 답변 생성
    """
    # 1. 질문 재구성
    query_analysis = await llm_handler.rewrite_query(query, history)
    if verbose:
        print(f"[Log] 재구성된 질문: {query_analysis.get('rewritten_question')}")

    # 2. 멀티쿼리 생성
    multi_queries = await llm_handler.generate_multi_queries(query, query_analysis, num_queries=1)
    if verbose:
        print(f"[Log] 생성된 쿼리들: {multi_queries}")

    # 3. 멀티쿼리 하이브리드 검색 (Vector + Keyword)
    search_results = await gongo.multi_query_hybrid_search(query_analysis, multi_queries)

    if not search_results:
        return {
            'query': query,
            'answer': "죄송합니다. 요청하신 조건에 맞는 공고를 찾을 수 없습니다.",
            'sources': []
        }

    # 4. 재순위화 (Reranking)
    reranked = await gongo.rerank_results(query_analysis.get('rewritten_question', query), search_results)
    
    # 5. 청크 병합
    merged_results = await gongo.merge_chunks(reranked)

    # 6. 컨텍스트 구성
    context = gongo.build_context(merged_results)

    # 7. 답변 생성
    answer = await llm_handler.generate_answer(query_analysis.get('rewritten_question', query), context, history)

    # 결과 반환
    return {
        'query': query,
        'answer': answer,
        'sources': merged_results,
        'query_analysis': query_analysis
    }



# 2. 통합 채팅 서비스 (Context-Aware Service)
async def chat_service(query: str, history: List[Dict]) -> Dict:
    """
    API에서 호출하는 메인 진입점.
    질문이 이전 대화와 이어지는지(맥락 질문) 판단하여 처리 방식을 결정합니다.
    """
    
    # 1. 맥락 분석
    context_analysis = await llm_handler.analyze_context(query, history)
    is_context = context_analysis.get('is_context_question', False)
    context_type = context_analysis.get('context_type', 'new_question')

    # 2-1. 순수 대화 맥락 질문 (검색 불필요)
    if context_type == 'meta_conversation' and history:
        print(f"[Log] 대화 맥락 질문 감지: {context_analysis.get('reason')}")

        # 이전 대화 요약 컨텍스트 구성
        history_context = "\n\n".join([
            f"**질문 {i+1}**: {h.get('query', '')}\n**답변**: {h.get('answer', '')[:300]}..."
            for i, h in enumerate(history[-5:])
        ])

        answer = await llm_handler.generate_answer(
            query,
            f"이전 대화 내역:\n{history_context}",
            history
        )

        return {
            'query': query,
            'answer': answer,
            'sources': [],
            'metadata': {'context_type': 'meta_conversation'}
        }

    # 2-2. 공고 참조 질문인 경우
    if is_context and context_type == 'announcement_reference' and history:
        print(f"[Log] 공고 참조 질문 감지: {context_analysis.get('reason')}")

        # 이전 대화에서 언급된 공고 ID 추출
        prev_ids = []
        referenced_indices = context_analysis.get('referenced_announcement_indices', [0])
        
        # history 역순 탐색
        for idx in referenced_indices:
            if idx < len(history):
                # history는 {'query':.., 'answer':.., 'sources': [..]} 형태
                prev_turn = history[-(idx+1)]
                prev_sources = prev_turn.get('sources', [])
                
                # 상위 3개 공고만 참조 대상으로 설정
                for src in prev_sources[:3]:
                    # src가 딕셔너리인지 객체인지 확인 후 ID 추출
                    ann_id = src.get('announcement_id') if isinstance(src, dict) else getattr(src, 'announcement_id', None)
                    if ann_id and str(ann_id) not in prev_ids:
                        prev_ids.append(str(ann_id))
        
        if prev_ids:
            print(f"[Log] 참조 공고 ID: {prev_ids}")

            # 질문 재구성
            query_analysis = await llm_handler.rewrite_query(query, history)

            # 멀티쿼리 생성
            multi_queries = await llm_handler.generate_multi_queries(query, query_analysis, num_queries=1)

            # 우선 검색 (이전 공고 ID 범위 내에서 멀티쿼리 검색)
            context_tasks = []
            for q in multi_queries:
                context_tasks.append(gongo.vector_search(q, top_k=5, filter_ids=prev_ids))
            context_results_list = await asyncio.gather(*context_tasks)

            # 결과 병합 (중복 제거)
            seen = set()
            context_results = []
            for results in context_results_list:
                for r in results:
                    if r['chunk_id'] not in seen:
                        context_results.append(r)
                        seen.add(r['chunk_id'])

            # 일반 검색 (혹시 다른 공고일 수도 있으므로 넓게 검색)
            general_results = await gongo.multi_query_hybrid_search(query_analysis, multi_queries)

            # 전체 결과 병합 (중복 제거)
            combined = context_results + [r for r in general_results if r['chunk_id'] not in seen]

            # 재순위화
            reranked = await gongo.rerank_results(query_analysis.get('rewritten_question', query), combined)

            # 청크 병합
            merged_results = await gongo.merge_chunks(reranked)

            # 컨텍스트 구성 및 답변 생성
            context = gongo.build_context(merged_results)
            answer = await llm_handler.generate_answer(query_analysis.get('rewritten_question', query), context, history)

            return {
                'query': query,
                'answer': answer,
                'sources': merged_results,
                'query_analysis': query_analysis
            }

    # 3. 일반 질문인 경우
    print("[Log] 일반 질문으로 처리")
    return await rag_process(query, history)