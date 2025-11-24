# **파일구조**
```
zip-fit/
├── .env                 # 환경 변수 (API Key, DB 설정, 모델 경로 등)
├── config.py            # 프로젝트 전역 설정 관리
├── main.py              # 서버 실행 진입점 (Lifespan 관리)
├── router.py            # API 엔드포인트 정의 (/chat)
├── models.py            # Pydantic 데이터 모델 (DTO)
├── dependencies.py      # AI 모델 로더 & 리소스 의존성 관리
├── gongo.py             # 핵심 검색 로직 (Vector/Keyword/Rerank)
├── llm_handler.py       # OpenAI LLM 인터페이스 (Query Rewrite, Answer Gen)
├── chatting.py          # RAG 파이프라인 및 대화 흐름 제어 (Controller)
├── model_cache          # 모델 저장 장소
└── docker_db/            # DB 초기화 파일 저장소
    └── db_dump.sql      # 초기 데이터 덤프 파일
```
# **핵심 기능**

### 파일별 기능 요약

* **`main.py` (실행 진입점)**
    * 서버를 켜고 끄는 스위치 역할입니다.
    * 앱이 시작될 때 AI 모델을 로드(`lifespan`)하고, 전체 API를 구동합니다.

* **`router.py` (API 연결 창구)**
    * 외부(프론트엔드)에서 들어오는 요청(`/chat`)을 받습니다.
    * 데이터 형식이 맞는지 검사하고, 핵심 로직(`chatting.py`)으로 넘겨줍니다.

* **`chatting.py` (관제탑 / 컨트롤러)**
    * RAG의 전체 흐름(질문 분석 → 검색 → 답변)을 지휘합니다.
    * "이전 대화 맥락"을 파악하여 검색 전략을 결정하는 로직이 들어있습니다.

* **`llm_handler.py` (AI 두뇌 / OpenAI)**
    * OpenAI API와 통신하는 전용 모듈입니다.
    * 질문을 검색하기 좋게 다듬거나(`Rewrite`), 최종 답변을 작성(`Generate`)합니다.

* **`gongo.py` (검색 및 데이터 조회)**
    * DB(PostgreSQL)에 접속하여 실제 데이터를 가져옵니다.
    * 벡터 검색, 키워드 검색, 그리고 **Reranking(재순위화)** 로직을 수행합니다.

* **`dependencies.py` (자원 관리소)**
    * 용량이 큰 AI 모델(Embedding, Reranker)을 서버 켤 때 미리 메모리에 올려둡니다.
    * 모델 캐싱 경로 설정 및 Reranker On/Off 처리를 담당합니다.

* **`models.py` (데이터 규격서)**
    * 데이터를 주고받을 때의 형식(문자열, 숫자 등)을 정의합니다.
    * DB의 ID가 문자열인지 숫자인지 등 데이터 타입을 강제합니다.

* **`config.py` (환경 설정)**
    * `.env` 파일의 내용을 불러와 코드에서 쓸 수 있게 변수로 관리합니다.
    * API 키, DB 접속 정보, 모델 경로 등 중요한 설정을 모아둡니다.

* **`docker-compose.yml` (인프라 설정)**
    * 벡터 검색이 가능한 DB(PostgreSQL + pgvector)를 가상 환경(Docker)에 띄웁니다.

* **`database/db_dump.sql` (초기 데이터)**
    * DB가 처음 생성될 때 자동으로 들어갈 LH 공고 데이터 파일입니다.
