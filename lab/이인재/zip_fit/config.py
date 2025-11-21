from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

# 현재 파일(config.py)이 위치한 폴더 경로
CURRENT_DIR = Path(__file__).parent
# 현재 폴더의 상위 폴더
PROJECT_ROOT = CURRENT_DIR.parent

class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리합니다.
    기본값이 없는 필드는 .env에 반드시 존재해야 합니다.
    Pydantic이 자동으로 값을 읽어옵니다.
    """
    
    # 1. R-DB 설정 (필수값 - .env에 없으면 에러 발생)
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # 2. OpenAI (필수값)
    OPENAI_API_KEY: str

    # 3. 선택값 (Optional)
    GOV_API_KEY: Optional[str] = None

    # Pydantic 설정
    model_config = SettingsConfigDict(
        # 1. 프로젝트 루트의 .env
        # 2. zip_fit 폴더 내의 .env (우선순위 낮음)
        env_file=[PROJECT_ROOT / ".env", CURRENT_DIR / ".env"],
        env_file_encoding='utf-8',
        extra='ignore' 
    )

# 설정 인스턴스 생성
settings = Settings()

# 로드 확인용
print(f"Config Loaded: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")