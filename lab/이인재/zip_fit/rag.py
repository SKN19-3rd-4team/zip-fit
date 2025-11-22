import json
from typing import List, Dict, Any, Tuple
from search import SearchEngine
from llm_engine import LLMEngine
import session 

class RAGEngine:
    def __init__(self):
        self.search_engine = SearchEngine()
        self.llm_engine = LLMEngine()
    
    async def retrieve(self,
                        question: str,
                        top_k: int = 5,
                        use_hybrid: bool = True) -> Tuple[str, List[Dict[str, Any]]]:

        results = await self.search_engine.smart_search(question, top_k=top_k, use_hybrid=use_hybrid)
        if not results: return "", []
        
        context_parts = []
        for idx, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            if isinstance(metadata, str): metadata = json.loads(metadata)
            context_parts.append(
                f"[문서 {idx}]\n제목: {result['title']}\n지역: {result['region']}\n"
                f"내용: {result['chunk_text']}\n"
            )
        return "\n" + "="*80 + "\n".join(context_parts), results
    
    # user_id 파라미터 추가
    async def query(self,
                    user_id: int,
                    question: str,
                    top_k: int = 3,
                    use_llm: bool = True,
                    use_hybrid: bool = True) -> Dict[str, Any]:
        
        # 1. 검색 (Retrieve)
        context, results = await self.retrieve(question, top_k, use_hybrid)
        
        if not results:
            # 검색 실패 시에도 대화 맥락상 답변이 가능할 수 있으므로(예: 인사), Context 없이 진행할 수도 있지만
            # 현재는 안전하게 종료합니다.
            return {
                'question': question,
                'answer': "죄송합니다. 관련 공고를 찾을 수 없습니다.",
                'context': "", 'results': [], 'metadata': {}
            }
        
        answer = None
        if use_llm:
            # 2-1. 과거 대화 가져오기
            history = await session.get_history(user_id)
            
            # 2-2. LLM 생성 (히스토리 전달)
            answer = await self.llm_engine.generate_answer(question, context, history)
            
            # 2-3. 새로운 대화 저장 (비동기로 수행하여 응답 속도 저하 방지)
            # await session.add_turn(user_id, question, answer) 
            # 여기서는 순차 실행하지만, 필요 시 asyncio.create_task로 백그라운드 처리 가능
            await session.add_turn(user_id, question, answer)
        
        metadata = {
            'num_documents': len(results),
            'search_type': 'hybrid' if use_hybrid else 'vector'
        }
        
        return {
            'question': question,
            'answer': answer,
            'context': context,
            'results': results,
            'metadata': metadata
        }