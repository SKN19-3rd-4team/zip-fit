# 단일 쿼리 실행 스크립트
import asyncio
import sys
from rag import RAGEngine


async def main():
    """쿼리 실행"""
    if len(sys.argv) < 2:
        print("사용법: python run_query.py '질문' [--no-llm] [--no-hybrid]")
        print("\n예시:")
        print("  python run_query.py '남양주시 국민임대주택 입주 자격은?'")
        print("  python run_query.py '수원시 행복주택은?' --no-llm")
        sys.exit(1)
    
    question = sys.argv[1]
    use_llm = '--no-llm' not in sys.argv
    use_hybrid = '--no-hybrid' not in sys.argv
    
    rag = RAGEngine()
    
    try:
        print(f"질문 처리 중: {question}")
        print("="*80)
        
        response = await rag.query(
            question=question,
            top_k=3,
            use_llm=use_llm,
            use_hybrid=use_hybrid
        )
        
        print(rag.format_response(response))
    
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    asyncio.run(main())
