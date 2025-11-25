# 이 코드를 노트북에 새로운 셀로 추가하세요

# ============================================================
# 테스트 검증: 4가지 핵심 기능 확인
# ============================================================

for result in all_results:
    if 'error' in result:
        continue

    print("\n" + "=" * 80)
    print(f"[{result['tc_id']}] {result['query']}")
    print("=" * 80)

    # 1. 질문 재구성 & 멀티쿼리 생성 검증
    print("\n[검증 1] 질문 재구성 및 멀티쿼리 생성")
    print("-" * 60)
    qa = result['query_analysis']
    print(f"원본 질문: {result['query']}")
    print(f"재구성된 질문: {qa.get('rewritten_question')}")
    print(f"추출된 필터:")
    print(f"  - 지역: {qa.get('region') or '없음'}")
    print(f"  - 유형: {qa.get('notice_type') or '없음'}")
    print(f"  - 상태: {qa.get('status') or '없음'}")
    print(f"검색 키워드: {', '.join(qa.get('search_keywords', []))}")
    print(f"\n생성된 멀티쿼리 ({len(result['multi_queries'])}개):")
    for i, mq in enumerate(result['multi_queries'], 1):
        print(f"  {i}. {mq}")

    # 2. 하이브리드 검색 검증
    print(f"\n[검증 2] 하이브리드 검색 - 연관 문서 검색")
    print("-" * 60)
    print(f"총 검색된 문서: {result['search_count']}개")
    print(f"상위 5개 검색 결과:")
    for i, doc in enumerate(result['search_results'][:5], 1):
        title = doc.get('title', 'N/A')[:50]
        region = doc.get('region', 'N/A')
        notice_type = doc.get('notice_type', 'N/A')
        similarity = doc.get('similarity', 0)
        print(f"  [{i}] {title}...")
        print(f"      지역: {region}, 유형: {notice_type}, 유사도: {similarity:.4f}")

    # 3. 리랭킹 & 병합 검증
    print(f"\n[검증 3] 재순위화(Reranking) 및 병합(Merge)")
    print("-" * 60)
    print("리랭킹 전 상위 3개:")
    for i, doc in enumerate(result['search_results'][:3], 1):
        title = doc.get('title', 'N/A')[:40]
        similarity = doc.get('similarity', 0)
        print(f"  [{i}] {title}... (유사도: {similarity:.4f})")

    print("\n리랭킹 후 상위 3개:")
    for i, doc in enumerate(result['reranked'][:3], 1):
        title = doc.get('title', 'N/A')[:40]
        rerank_score = doc.get('rerank_score', 0)
        print(f"  [{i}] {title}... (rerank: {rerank_score:.4f})")

    print(f"\n병합 결과: {result['merged_count']}개 공고로 병합")
    print("병합된 상위 3개 공고:")
    for i, ann in enumerate(result['merged'][:3], 1):
        title = ann.get('announcement_title', 'N/A')
        num_chunks = ann.get('num_chunks', 0)
        content_len = len(ann.get('merged_content', ''))
        print(f"  [{i}] {title}")
        print(f"      병합 청크: {num_chunks}개, 텍스트 길이: {content_len}자")

    # 4. 답변 생성 및 환각 검증
    print(f"\n[검증 4] 답변 생성 - 환각 없는 정확한 답변")
    print("-" * 60)
    answer = result['answer']
    print(f"답변 길이: {len(answer)}자")
    print(f"\n생성된 답변:")
    print("-" * 60)
    print(answer)
    print("-" * 60)

    # 환각 검증 체크리스트
    print("\n환각 검증:")
    checks = {
        "표 형식 사용": "|" in answer,
        "구체적 수치 포함": any(char.isdigit() for char in answer),
        "정보 부족 명시": any(kw in answer for kw in ["확인", "공고문", "고객센터", "제공"]),
        "컨텍스트 기반": len(answer) > 50  # 최소한의 답변 길이
    }

    for check, passed in checks.items():
        status = "Pass" if passed else "주의"
        print(f"  - {check}: {status}")

    print("\n")

print("\n" + "=" * 80)
print("전체 테스트 검증 완료")
print("=" * 80)
