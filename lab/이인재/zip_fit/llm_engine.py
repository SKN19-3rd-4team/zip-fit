from openai import AsyncOpenAI
from typing import List, Dict
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class LLMEngine:
    """OpenAI API 호출 전담 (히스토리 지원)"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.model = OPENAI_MODEL

    async def generate_answer(self,
                                question: str,
                                context: str,
                                history: List[Dict[str, str]]) -> str:
        """
        [Context] + [History] + [Current Question] -> Answer
        """
        if not self.client:
            return "오류: OpenAI API 키가 설정되지 않았습니다."

        try:
            # 1. 현재 질문 메시지 구성 (RAG Context 포함)
            current_user_message = {
                "role": "user", 
                "content": USER_PROMPT_TEMPLATE.format(context=context, question=question)
            }
            
            # 2. 메시지 체인 조립
            # 순서: [시스템 프롬프트] -> [과거 대화(History)] -> [현재 질문+문서(User)]
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [current_user_message]

            # 3. API 호출
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"LLM 생성 오류: {e}")
            return f"죄송합니다. 답변을 생성하는 중 오류가 발생했습니다. ({e})"