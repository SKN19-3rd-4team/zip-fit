import psycopg2
from pgvector.psycopg2 import register_vector
# config.py에서 settings 객체를 가져옵니다.
from .config import settings

class DB:
    def __init__(self):
        # config.py의 설정값을 사용합니다.
        self.db_config = {
            "host": settings.HOST,
            "port": settings.PORT,
            "database": settings.DATABASE,
            "user": settings.USER,
            "password": settings.PASSWORD
        }

    def get_connection(self):
        """
        config.py 설정으로 DB에 연결하고, 
        pgvector 확장을 등록한 뒤 conn 객체를 반환합니다.
        """
        try:
            # 1. 연결 생성
            conn = psycopg2.connect(**self.db_config)
            
            # 2. 설정 적용 (Auto Commit)
            conn.autocommit = True 
            
            # 3. pgvector 확장 기능 등록 (업로드해주신 코드 반영)
            register_vector(conn)
            
            print(f"🔌 DB 연결 성공: {settings.HOST}:{settings.PORT}/{settings.DATABASE}")
            
            # 4. 연결 객체 반환
            return conn
            
        except Exception as e:
            print(f"❌ DB 연결 실패: {e}")
            raise e