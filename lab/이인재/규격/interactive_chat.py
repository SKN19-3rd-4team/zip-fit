# 대화형 챗봇
import asyncio
from rag import RAGEngine


async def main():
    """대화형 챗봇 세션"""
    print("LH 공고 RAG 챗봇")
    print("="*80)
    print("명령어:")
    print("  'quit' 또는 'exit' - 종료")
    print("  'hybrid on/off' - 하이브리드 검색 토글")
    print("  'llm on/off' - LLM 생성 토글")
    print("="*80)
    
    rag = RAGEngine()
    use_hybrid = True
    use_llm = True
    
    while True:
        try:
            question = input("\n질문: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit']:
                print("종료합니다")
                break
            
            # 하이브리드 검색 토글
            if question.lower() == 'hybrid on':
                use_hybrid = True
                print("하이브리드 검색 활성화")
                continue
            elif question.lower() == 'hybrid off':
                use_hybrid = False
                print("하이브리드 검색 비활성화")
                continue
            
            # LLM 생성 토글
            if question.lower() == 'llm on':
                use_llm = True
                print("LLM 생성 활성화")
                continue
            elif question.lower() == 'llm off':
                use_llm = False
                print("LLM 생성 비활성화")
                continue
            
            print("\n검색 중...")
            response = await rag.query(
                question=question,
                top_k=3,
                use_llm=use_llm,
                use_hybrid=use_hybrid
            )
            
            print("\n" + rag.format_response(response))
        
        except KeyboardInterrupt:
            print("\n\n종료합니다")
            break
        except Exception as e:
            print(f"\n오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
