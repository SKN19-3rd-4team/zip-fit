# zip-fit 챗봇 API 개발자 가이드

## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처 구조](#아키텍처-구조)
3. [파일별 상세 설명](#파일별-상세-설명)
4. [데이터 흐름](#데이터-흐름)
5. [코드 수정 및 추가 가이드](#코드-수정-및-추가-가이드)
6. [의존성 주입 패턴](#의존성-주입-패턴)
7. [테스트 엔드포인트](#테스트-엔드포인트)
8. [환경 설정](#환경-설정)
9. [트러블슈팅](#트러블슈팅)

---

## 프로젝트 개요

zip-fit 챗봇 API는 FastAPI 기반의 LLM 챗봇 서비스입니다. 사용자의 질문을 받아 관계형 데이터베이스와 Vector DB에서 관련 정보를 조회하고, OpenAI API를 통해 지능형 응답을 생성합니다.

### 주요 기술 스택
- **FastAPI**: 비동기 웹 프레임워크
- **Pydantic**: 데이터 검증 및 설정 관리
- **OpenAI API**: LLM 응답 생성
- **의존성 주입 패턴**: 클린 아키텍처 구현

---

## 아키텍처 구조

```
사용자 요청 (HTTP POST)
    ↓
router.py (엔드포인트)
    ↓
chatting.py (비즈니스 로직)
    ↓
llm_engine.py (LLM 처리)
    ↓
gongo.py (데이터 조회)
    ↓
DB (RDB + Vector DB)
```

### 계층별 책임

1. **router.py**: HTTP 요청 라우팅 및 의존성 주입
2. **chatting.py**: 전체 서비스 로직 조율
3. **llm_engine.py**: LLM 호출 및 프롬프트 구성
4. **gongo.py**: 데이터베이스 조회 및 컨텍스트 제공
5. **models.py**: Pydantic 데이터 모델 정의
6. **config.py**: 환경 설정 및 .env 로드
7. **dependencies.py**: FastAPI 의존성 주입 관리
8. **main.py**: 애플리케이션 진입점 및 라이프사이클 관리

---

## 파일별 상세 설명

### 1. main.py
**역할**: 애플리케이션 시작점

```python
# 주요 기능
- FastAPI 앱 인스턴스 생성
- lifespan 컨텍스트 매니저로 앱 시작/종료 관리
- 의존성 주입 초기화 순서:
  1. Gongo (DB 연결)
  2. LlmEngine (Gongo 주입)
  3. Chatting (LlmEngine 주입)
  4. dependencies에 Chatting 인스턴스 저장
```

**수정 시 주의사항**:
- 의존성 주입 순서를 반드시 지켜야 합니다
- lifespan의 yield 이전: 시작 로직
- lifespan의 yield 이후: 종료 로직

**코드 위치**:
- FastAPI 앱 생성: `main.py:34-39`
- 의존성 초기화: `main.py:12-24`
- 라우터 등록: `main.py:42`

---

### 2. config.py
**역할**: 환경 변수 관리

```python
# 필수 설정
OPENAI_API_KEY: OpenAI API 키 (필수)

# 선택 설정
GOV_API_KEY: 정부 API 키 (선택)

# 향후 추가 가능
DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
VECTOR_DB_PATH_OR_URL
```

**수정 방법**:
1. 새로운 환경 변수를 `Settings` 클래스에 추가
2. 타입 힌트와 기본값 설정
3. .env 파일에 실제 값 추가

```python
# 예시: 새로운 API 키 추가
class Settings(BaseSettings):
    # 기존 설정들...
    NEW_API_KEY: Optional[str] = None
```

---

### 3. models.py
**역할**: API 요청/응답 데이터 모델 정의

```python
# ChatRequest: 사용자 입력 모델
- user_input: 사용자 질문 (필수)
- user_id: 사용자 ID (기본값: 0)

# ChatResponse: API 응답 모델
- response: 챗봇 응답 (필수)
- status: 처리 상태 (기본값: "success")
- processed_by: 처리 컴포넌트 정보
```

**새로운 필드 추가 방법**:
```python
class ChatRequest(BaseModel):
    user_input: str
    user_id: int = 0
    session_id: Optional[str] = None  # 새 필드 추가
    language: str = "ko"  # 기본값 포함
```

---

### 4. dependencies.py
**역할**: FastAPI 의존성 주입 관리

```python
# 전역 변수로 Chatting 인스턴스 저장
_CHAT_SERVICE_INSTANCE: Optional[Chatting] = None

# setter: main.py에서 호출
set_chatting_service_instance(instance)

# getter: router.py에서 Depends로 사용
get_chatting_service() -> Chatting
```

**확장 방법**:
다른 서비스도 의존성 주입하려면:
```python
_ANOTHER_SERVICE_INSTANCE: Optional[AnotherService] = None

def set_another_service(instance: AnotherService):
    global _ANOTHER_SERVICE_INSTANCE
    _ANOTHER_SERVICE_INSTANCE = instance

def get_another_service() -> AnotherService:
    if _ANOTHER_SERVICE_INSTANCE is None:
        raise Exception("Service not initialized")
    return _ANOTHER_SERVICE_INSTANCE
```

---

### 5. gongo.py
**역할**: 데이터베이스 조회 및 컨텍스트 제공

```python
# 주요 메서드
async def get_contextual_data(user_id: int, query: str) -> str
```

**현재 상태**: Mock 데이터 반환
**향후 구현 필요**:
1. PostgreSQL 연결 풀 초기화
2. Vector DB (ChromaDB/FAISS/Pinecone) 클라이언트 초기화
3. 실제 데이터 쿼리 로직

**실제 DB 연결 추가 예시**:
```python
class Gongo:
    def __init__(self):
        # PostgreSQL 연결 풀
        self.db_pool = None
        # Vector DB 클라이언트
        self.vector_client = None

    async def initialize_db_pool(self):
        # asyncpg로 PostgreSQL 연결
        self.db_pool = await asyncpg.create_pool(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )

    async def get_contextual_data(self, user_id: int, query: str) -> str:
        # 실제 DB 조회
        async with self.db_pool.acquire() as conn:
            user_data = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1", user_id
            )

        # Vector DB 검색
        vector_results = self.vector_client.search(query, top_k=5)

        return f"사용자 정보: {user_data}\n관련 문서: {vector_results}"
```

**코드 위치**:
- Mock 데이터 반환: `gongo.py:26-42`

---

### 6. llm_engine.py
**역할**: LLM 호출 및 프롬프트 구성

```python
# 주요 메서드
1. generate_response(request) -> Dict
   - 전체 처리 흐름 조율

2. _get_llm_input_text(request) -> str
   - Gongo에서 컨텍스트 조회
   - 프롬프트 텍스트 구성

3. _call_llm_api(prompt_text) -> Dict
   - OpenAI API 호출
   - 응답 파싱 및 반환
```

**OpenAI 설정 변경**:
```python
# llm_engine.py:63-66
response = await self.openai_client.chat.completions.create(
    model="gpt-4o-mini",  # 모델 변경
    messages=messages,
    temperature=0.3,  # 온도 조절 (0.0-2.0)
    max_tokens=1000,  # 최대 토큰 수 제한 (선택)
)
```

**시스템 프롬프트 수정**:
```python
# llm_engine.py:54
system_prompt = "당신은 최고의 분석가이자 조언자입니다. 정확하게 답변하세요"
# ↓ 변경
system_prompt = "당신은 zip-fit 서비스의 전문 상담원입니다. 친절하고 정확하게 답변하세요."
```

**코드 위치**:
- OpenAI 클라이언트 초기화: `llm_engine.py:19`
- 프롬프트 구성: `llm_engine.py:25-42`
- LLM API 호출: `llm_engine.py:47-83`

---

### 7. chatting.py
**역할**: 비즈니스 로직 조율

```python
# 주요 메서드
1. get_chat_response(request) -> ChatResponse
   - LlmEngine 호출
   - 최종 응답 가공

2. get_llm_engine() -> LlmEngine
   - LlmEngine 인스턴스 반환

3. get_gongo_service() -> Gongo
   - Gongo 인스턴스 반환
```

**응답 가공 수정**:
```python
# chatting.py:39-43
return ChatResponse(
    response=f"[LLM 엔진 처리 결과] {final_response}",
    # ↓ 변경: 접두사 제거
    response=final_response,
    status="success",
    processed_by="zip-fit Chatbot"
)
```

**코드 위치**:
- LLM 호출: `chatting.py:34`
- 응답 가공: `chatting.py:36-43`

---

### 8. router.py
**역할**: HTTP 엔드포인트 정의

```python
# 메인 엔드포인트
POST /api/v1/chat/
- 일반 사용자 요청 처리

# 테스트 엔드포인트
POST /api/v1/chat/test/llm-only
- LlmEngine까지만 테스트

POST /api/v1/chat/test/gongo-only
- Gongo까지만 테스트
```

**새로운 엔드포인트 추가**:
```python
@router.post("/custom-endpoint", response_model=ChatResponse)
async def custom_endpoint(
    request: ChatRequest,
    chat_service: Chatting = Depends(get_chatting_service)
):
    """
    커스텀 처리 로직
    """
    # 원하는 로직 구현
    result = await chat_service.some_method(request)
    return result
```

**코드 위치**:
- 메인 엔드포인트: `router.py:14-25`
- LLM 테스트: `router.py:31-50`
- Gongo 테스트: `router.py:56-79`

---

## 데이터 흐름

### 일반 요청 처리 흐름

```
1. 사용자가 POST /api/v1/chat/ 호출
   ↓
2. router.chat_endpoint()가 요청 수신
   - ChatRequest 모델로 검증
   - Depends로 Chatting 인스턴스 주입
   ↓
3. chatting.get_chat_response() 호출
   ↓
4. llm_engine.generate_response() 호출
   ↓
5. llm_engine._get_llm_input_text() 호출
   - gongo.get_contextual_data() 호출
   - DB에서 컨텍스트 조회
   - 프롬프트 텍스트 구성
   ↓
6. llm_engine._call_llm_api() 호출
   - OpenAI API 호출
   - 응답 파싱
   ↓
7. Chatting이 최종 응답 가공
   ↓
8. ChatResponse 모델로 반환
   ↓
9. 사용자에게 JSON 응답
```

---

## 코드 수정 및 추가 가이드

### 시나리오 1: 새로운 LLM 모델 추가

**목표**: OpenAI 외에 다른 LLM 추가 (예: Anthropic Claude)

**수정 파일**: `llm_engine.py`, `config.py`

```python
# 1. config.py에 API 키 추가
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None  # 새로 추가

# 2. llm_engine.py에 클라이언트 추가
class LlmEngine:
    def __init__(self, gongo_service: Gongo):
        self.gongo_service = gongo_service
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Anthropic 클라이언트 추가
        if settings.ANTHROPIC_API_KEY:
            from anthropic import AsyncAnthropic
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

# 3. 새로운 호출 메서드 추가
    async def _call_anthropic_api(self, prompt_text: str) -> Dict[str, Any]:
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt_text}]
            )
            return {
                "llm_output": response.content[0].text,
                "prompt_used": prompt_text,
                "usage_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        except Exception as e:
            return {
                "llm_output": f"Anthropic 호출 오류: {str(e)}",
                "prompt_used": prompt_text,
                "usage_tokens": 0
            }
```

---

### 시나리오 2: 대화 히스토리 저장 기능 추가

**목표**: 사용자별 대화 히스토리 관리

**수정 파일**: `models.py`, `gongo.py`, `llm_engine.py`

```python
# 1. models.py에 히스토리 모델 추가
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatRequest(BaseModel):
    user_input: str
    user_id: int = 0
    conversation_history: List[ChatMessage] = []  # 새로 추가

# 2. gongo.py에 히스토리 저장 메서드 추가
class Gongo:
    async def save_chat_history(self, user_id: int, message: ChatMessage):
        """대화 히스토리를 DB에 저장"""
        # DB INSERT 로직
        pass

    async def get_chat_history(self, user_id: int, limit: int = 10) -> List[ChatMessage]:
        """최근 대화 히스토리 조회"""
        # DB SELECT 로직
        pass

# 3. llm_engine.py에서 히스토리 활용
    async def _get_llm_input_text(self, request: ChatRequest) -> str:
        # 히스토리 조회
        history = await self.gongo_service.get_chat_history(request.user_id)

        # 컨텍스트 데이터 조회
        context_data = await self.gongo_service.get_contextual_data(
            user_id=request.user_id,
            query=request.user_input
        )

        # 히스토리를 포함한 프롬프트 구성
        history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in history])

        llm_input_text = (
            f"대화 히스토리:\n{history_text}\n\n"
            f"컨텍스트:\n{context_data}\n\n"
            f"사용자 질문: {request.user_input}"
        )

        return llm_input_text
```

---

### 시나리오 3: 커스텀 전처리 로직 추가

**목표**: 사용자 입력을 필터링하거나 전처리

**수정 파일**: `chatting.py`

```python
class Chatting:
    def _preprocess_user_input(self, user_input: str) -> str:
        """
        사용자 입력 전처리
        - 욕설 필터링
        - 특수문자 제거
        - 공백 정리 등
        """
        # 욕설 필터링
        bad_words = ["욕설1", "욕설2"]
        for word in bad_words:
            user_input = user_input.replace(word, "***")

        # 공백 정리
        user_input = " ".join(user_input.split())

        return user_input

    async def get_chat_response(self, request: ChatRequest) -> ChatResponse:
        # 전처리 적용
        request.user_input = self._preprocess_user_input(request.user_input)

        # 기존 로직 계속
        llm_result = await self.llm_engine.generate_response(request)
        # ...
```

---

### 시나리오 4: 새로운 데이터 소스 추가

**목표**: Vector DB 외에 외부 API 데이터 추가

**수정 파일**: `gongo.py`

```python
class Gongo:
    def __init__(self):
        print("💡 Gongo Data Engine Initialized!")
        # HTTP 클라이언트 추가
        import httpx
        self.http_client = httpx.AsyncClient()

    async def get_external_api_data(self, query: str) -> str:
        """외부 API에서 추가 데이터 조회"""
        try:
            response = await self.http_client.get(
                "https://api.example.com/search",
                params={"q": query}
            )
            return response.json()["result"]
        except Exception as e:
            return f"외부 API 오류: {str(e)}"

    async def get_contextual_data(self, user_id: int, query: str) -> str:
        # 기존 데이터 조회
        rdb_data = "..."
        vector_data = "..."

        # 외부 API 데이터 추가
        external_data = await self.get_external_api_data(query)

        # 모든 데이터 결합
        context_string = (
            "--- SYSTEM DATA START ---\n"
            f"RDB Context: {rdb_data}\n"
            f"VectorDB Context: {vector_data}\n"
            f"External API Context: {external_data}\n"
            "--- SYSTEM DATA END ---\n"
        )

        return context_string
```

---

## 의존성 주입 패턴

이 프로젝트는 **의존성 주입(Dependency Injection)** 패턴을 사용합니다.

### 장점
1. **테스트 용이성**: Mock 객체로 쉽게 교체 가능
2. **결합도 감소**: 각 클래스가 독립적으로 동작
3. **유지보수성**: 코드 수정이 다른 부분에 영향 없음

### 주입 흐름
```python
# main.py에서 초기화 (앱 시작 시 한 번만)
gongo = Gongo()
llm_engine = LlmEngine(gongo_service=gongo)  # Gongo 주입
chatting = Chatting(llm_engine=llm_engine)   # LlmEngine 주입

# dependencies.py에 저장
set_chatting_service_instance(chatting)

# router.py에서 사용 (매 요청마다)
def chat_endpoint(chat_service: Chatting = Depends(get_chatting_service)):
    # chat_service 사용
```

### 새로운 서비스 추가 시 패턴 따르기

```python
# 1. 새 서비스 클래스 생성
class NewService:
    def __init__(self, dependency: SomeDependency):
        self.dependency = dependency

# 2. main.py에서 초기화 및 주입
new_service = NewService(dependency=some_instance)

# 3. dependencies.py에 등록
_NEW_SERVICE_INSTANCE = None

def set_new_service(instance: NewService):
    global _NEW_SERVICE_INSTANCE
    _NEW_SERVICE_INSTANCE = instance

def get_new_service() -> NewService:
    if _NEW_SERVICE_INSTANCE is None:
        raise Exception("NewService not initialized")
    return _NEW_SERVICE_INSTANCE

# 4. router.py에서 사용
@router.post("/new-endpoint")
async def new_endpoint(service: NewService = Depends(get_new_service)):
    # service 사용
```

---

## 테스트 엔드포인트

### 1. Gongo만 테스트
```bash
POST /api/v1/chat/test/gongo-only
{
  "user_input": "환불 정책이 궁금해요",
  "user_id": 123
}

# 응답
{
  "status": "gongo_service_mocked",
  "processed_by": "Gongo only test",
  "gongo_raw_output": "--- SYSTEM DATA START ---\nRDB Context: ...",
  "context_length": 256
}
```

**용도**:
- DB 연결 테스트
- 데이터 조회 로직 검증
- Vector DB 검색 결과 확인

---

### 2. LlmEngine만 테스트
```bash
POST /api/v1/chat/test/llm-only
{
  "user_input": "안녕하세요",
  "user_id": 123
}

# 응답
{
  "response": "**LlmEngine Mock 호출 성공.** (사용 프롬프트: 245자)",
  "status": "llm_engine_mocked",
  "processed_by": "LlmEngine only test"
}
```

**용도**:
- LLM API 호출 테스트
- 프롬프트 구성 검증
- 토큰 사용량 확인

---

### 3. 전체 플로우 테스트
```bash
POST /api/v1/chat/
{
  "user_input": "서비스 정책에 대해 알려주세요",
  "user_id": 123
}

# 응답
{
  "response": "[LLM 엔진 처리 결과] zip-fit 서비스의 환불 정책은...",
  "status": "llm_mock_processed",
  "processed_by": "Chatting -> LlmEngine (Used Tokens: 285)"
}
```

**용도**:
- 전체 파이프라인 검증
- 실제 사용자 요청 시뮬레이션

---

## 환경 설정

### .env 파일 설정
```bash
# 프로젝트 루트에 .env 파일 생성
# 경로: C:\Users\Playdata\Documents\GitHub\zip-fit\lab\이인재\zip_fit\.env

# 필수
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx

# 선택
GOV_API_KEY=your_government_api_key_here

# 향후 추가 예정
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_NAME=zipfit_db
# VECTOR_DB_PATH_OR_URL=./vector_store
```

### 서버 실행
```bash
# 개발 모드 (hot reload)
uvicorn main:app --reload --port 8000

# 프로덕션 모드
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API 문서 접근
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 트러블슈팅

### 문제 1: "Chatting Service가 초기화되지 않았습니다"

**원인**: main.py의 lifespan이 제대로 실행되지 않음

**해결**:
```python
# main.py:38 확인
app = FastAPI(lifespan=lifespan)  # lifespan 파라미터 누락 확인
```

---

### 문제 2: OpenAI API 호출 실패

**원인**: API 키 미설정 또는 잘못된 키

**해결**:
1. .env 파일 확인
2. `OPENAI_API_KEY=sk-proj-...` 형식 확인
3. 키 유효성 확인 (OpenAI 대시보드)

---

### 문제 3: Import 오류

**원인**: 상대 경로 import 문제

**해결**:
```python
# 올바른 import (패키지 내부에서)
from .chatting import Chatting
from .models import ChatRequest

# 올바른 import (외부에서)
from zip_fit.chatting import Chatting
from zip_fit.models import ChatRequest
```

---

### 문제 4: Pydantic 검증 오류

**원인**: 요청 데이터가 모델 스키마와 불일치

**해결**:
```python
# 요청 JSON이 ChatRequest 모델과 일치하는지 확인
{
  "user_input": "문자열이어야 함",  # str 타입
  "user_id": 123  # int 타입, 선택사항
}
```

---

## 코딩 컨벤션

### 네이밍 규칙
- 클래스: PascalCase (예: `Chatting`, `LlmEngine`)
- 함수/메서드: snake_case (예: `get_chat_response`)
- 상수: UPPER_SNAKE_CASE (예: `OPENAI_API_KEY`)
- Private 메서드: 앞에 `_` (예: `_call_llm_api`)

### 타입 힌팅
모든 함수는 타입 힌트를 포함해야 합니다:
```python
async def get_contextual_data(self, user_id: int, query: str) -> str:
    pass
```

### Docstring
공개 메서드는 docstring을 포함해야 합니다:
```python
def get_contextual_data(self, user_id: int, query: str) -> str:
    """
    사용자 ID와 쿼리를 기반으로 컨텍스트 데이터를 조회합니다.

    Args:
        user_id: 현재 채팅 중인 사용자 ID.
        query: 사용자의 현재 질문.

    Returns:
        LLM 프롬프트에 삽입할 준비가 된 텍스트 문자열.
    """
```

---

## 다음 단계

### 구현 필요 기능
1. **실제 DB 연결**: gongo.py에 PostgreSQL, Vector DB 연동
2. **인증/권한**: 사용자 인증 미들웨어 추가
3. **로깅**: 구조화된 로그 시스템 (loguru 등)
4. **에러 핸들링**: 전역 예외 핸들러
5. **캐싱**: Redis를 통한 응답 캐싱
6. **모니터링**: Prometheus, Grafana 연동

### 추천 학습 자료
- FastAPI 공식 문서: https://fastapi.tiangolo.com
- Pydantic 문서: https://docs.pydantic.dev
- OpenAI API 문서: https://platform.openai.com/docs
- Python 비동기 프로그래밍: asyncio, aiohttp

---

## 연락처 및 지원

문제가 발생하거나 질문이 있으면:
1. 코드 내 주석 확인
2. 이 가이드의 트러블슈팅 섹션 참조
3. API 문서 확인 (/docs 엔드포인트)
4. 팀 슬랙/이메일로 문의

**작성자**: 이인재
**마지막 업데이트**: 2025-01-18
**버전**: 1.0.0
