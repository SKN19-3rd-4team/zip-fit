# RAG 챗봇 설정
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# DB 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'skn19_3rd_proj'),
    'user': os.getenv('DB_USER', 'kimjm'),
    'password': os.getenv('DB_PASSWORD', '')
}

# 경로 설정 (수정됨)
BASE_DIR = Path(__file__).parent.parent.parent
PDF_BASE_PATH = BASE_DIR

# 임베딩 모델
EMBEDDING_MODEL = 'BAAI/bge-m3'
EMBEDDING_DIMENSION = 1024

# 청킹 설정
MIN_CHUNK_SIZE = 100
OPTIMAL_CHUNK_SIZE = 600
MAX_CHUNK_SIZE = 1200
MAX_TABLE_SIZE = 3000
CHUNK_OVERLAP = 150

# 검색 설정
DEFAULT_TOP_K = 5
SIMILARITY_THRESHOLD = 0.6

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = 'gpt-4o-mini'
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 1500

# 처리 설정
BATCH_SIZE = 10
MAX_WORKERS = 4
