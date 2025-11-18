from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
BASE_DIR = Path(__file__).parent

class Settings(BaseSettings):
    """
    .env 파일을 읽어와 애플리케이션 설정을 관리합니다.
    """
    
    # 1. R-DB 설정 (Gongo가 사용)
    # DB_HOST: str = "localhost"
    # DB_PORT: int = 5432
    # DB_USER: str
    # DB_PASSWORD: str
    # DB_NAME: str

    # 2. Vector DB 설정 (Gongo가 사용)
    # (예: ChromaDB/FAISS의 로컬 경로 또는 Pinecone/Weaviate URL)
    # VECTOR_DB_PATH_OR_URL: str = "./vector_store" 

    # 3. LLM - OpenAI (LLM 관리가 사용)
    OPENAI_API_KEY: str

    # 4. LLM - Runpod/Fine-tuning (LLM 관리가 사용)
    # (선택 사항일 수 있으므로 Optional/None 허용)
    # RUNPOD_API_ENDPOINT: Optional[str] = None
    # RUNPOD_API_KEY: Optional[str] = None

    # 5. 데이터 수집 API 키 (데이터 수집 봇이 사용)
    # (백엔드 서버가 아닌 별도 스크립트에서 사용하더라도 설정은 통합 관리)
    GOV_API_KEY: Optional[str] = None

    # Pydantic 설정
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", # .env 파일 위치 (프로젝트 루트)
        env_file_encoding='utf-8',
        extra='ignore' # .env에 정의된 다른 변수는 무시
    )

# 이 settings 객체를 다른 파일(main.py)에서 import하여 사용합니다.
settings = Settings()