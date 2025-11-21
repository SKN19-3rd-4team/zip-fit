# RAG 엔진 (검색 + 생성)
import json
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS
from search import SearchEngine


class RAGEngine:
    """RAG (검색 증강 생성) 엔진"""
    
    def __init__(self, api_key: str = OPENAI_API_KEY):
        self.search_engine = SearchEngine()
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    async def retrieve(self, question: str, top_k: int = 5, use_hybrid: bool = True) -> Tuple[str, List[Dict[str, Any]]]:
        """관련 문서 검색"""
        results = await self.search_engine.smart_search(question, top_k=top_k, use_hybrid=use_hybrid)
        
        if not results:
            return "", []
        
        context_parts = []
        for idx, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            context_parts.append(
                f"[문서 {idx}]\n"
                f"제목: {result['title']}\n"
                f"지역: {result['region']}\n"
                f"카테고리: {'임대' if result['category'] == 'lease' else '분양'}\n"
                f"출처: {metadata.get('file_name', 'N/A')}\n"
                f"유사도: {result['similarity']:.2%}\n\n"
                f"{result['chunk_text']}\n"
            )
        
        context = "\n" + "="*80 + "\n".join(context_parts)
        return context, results
    
    def generate_answer(self, question: str, context: str, model: str = OPENAI_MODEL) -> Optional[str]:
        """LLM 답변 생성"""
        if not self.client:
            return None
        
        system_prompt = """당신은 LH 공사 임대/분양 공고 전문가입니다.
제공된 문서를 바탕으로 정확하게 답변하세요.

지침:
1. 제공된 문서의 정보만 사용
2. 정보가 부족하면 명확히 언급
3. 숫자, 날짜, 조건을 정확히 인용
4. 여러 공고를 비교할 때는 각 공고명을 명시
5. 전문 용어는 쉽게 설명
6. 표와 목록은 읽기 쉽게 포맷"""
        
        user_prompt = f"""다음은 LH 공고 문서입니다:

{context}

질문: {question}

위 문서를 바탕으로 답변해주세요."""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"답변 생성 오류: {e}")
            return None
    
    async def query(self, question: str, top_k: int = 3, use_llm: bool = True, use_hybrid: bool = True) -> Dict[str, Any]:
        """전체 RAG 파이프라인"""
        # 문서 검색
        context, results = await self.retrieve(question, top_k, use_hybrid)
        
        if not results:
            return {
                'question': question,
                'answer': "관련 정보를 찾을 수 없습니다.",
                'context': "",
                'results': [],
                'metadata': {}
            }
        
        # LLM 답변 생성
        answer = None
        if use_llm and self.client:
            answer = self.generate_answer(question, context)
        
        # 메타데이터
        metadata = {
            'num_documents': len(results),
            'num_announcements': len(set(r['announcement_id'] for r in results)),
            'avg_similarity': sum(r['similarity'] for r in results) / len(results),
            'top_similarity': results[0]['similarity'] if results else 0,
            'search_type': 'hybrid' if use_hybrid else 'vector'
        }
        
        return {
            'question': question,
            'answer': answer,
            'context': context,
            'results': results,
            'metadata': metadata
        }
    
    def format_response(self, response: Dict[str, Any]) -> str:
        """RAG 응답 포맷팅"""
        output = []
        
        output.append(f"질문: {response['question']}\n")
        
        if response['answer']:
            output.append("="*80)
            output.append("답변:")
            output.append("="*80)
            output.append(response['answer'])
            output.append("")
        
        output.append("="*80)
        output.append("참조 문서:")
        output.append("="*80)
        
        for idx, result in enumerate(response['results'], 1):
            output.append(f"{idx}. {result['title']}")
            output.append(f"   지역: {result['region']}")
            output.append(f"   유사도: {result['similarity']:.2%}")
        
        metadata = response['metadata']
        output.append("")
        output.append(f"메타데이터:")
        output.append(f"  문서 수: {metadata['num_documents']}")
        output.append(f"  공고 수: {metadata['num_announcements']}")
        output.append(f"  평균 유사도: {metadata['avg_similarity']:.2%}")
        output.append(f"  검색 방식: {metadata['search_type']}")
        
        return "\n".join(output)
