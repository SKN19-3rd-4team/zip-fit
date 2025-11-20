    """
    db class get_connection 호출시 return conn
    """



from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from .config import settings

# 1. 데이터베이스 접속 URL 구성
# SQLAlchemy가 DB를 찾기 위한 주소입니다.
# - postgresql: 사용할 DB 종류
# - asyncpg: Python에서 PostgreSQL을 비동기로 가장 빠르게 연결해주는 드라이버
DATABASE_URL = f"postgresql+asyncpg://{settings.USER}:{settings.PASSWORD}@{settings.HOST}:{settings.PORT}/{settings.DATABASE}"
print(f"🔌 DB 연결 설정: {settings.HOST}:{settings.PORT}/{settings.DATABASE} (User: {settings.USER})")


# 2. 비동기 엔진(Engine) 생성 - "연결 관리자"
# 엔진은 실제 DB와의 연결(Connection)을 생성하고 관리하는 핵심 객체입니다.
engine = create_async_engine(
    DATABASE_URL,
    
    # [로그 설정]
    # True: 실행되는 모든 SQL 쿼리를 콘솔에 출력합니다. (개발 중 디버깅용)
    # False: 쿼리를 출력하지 않습니다. (운영 환경용)
    echo=True,

    # [커넥션 풀(Connection Pool) 설정]
    # 대기 없이 10명 까지는 접속 가능하게 끔 설정
    pool_size=10,

    # max_overflow=20: 10명이 다찼을 때 추가적으로 연결 가능한 인원 설정(pool_size 초과)
    # (즉, 최대 10 + 20 = 30명까지 동시 접속 가능)
    max_overflow=20,

    # [SQLAlchemy 버전 호환성]
    # True: SQLAlchemy 2.0 스타일(최신 표준, 엄격한 모드)을 강제합니다.
    # 비동기 기능을 안전하게 사용하기 위해 필수입니다.
    future=True
)


# 3. 세션 팩토리(Session Factory) - "세션 생성기"
# 실제 DB 작업(CRUD)을 할 때마다 이 공장에서 '세션'을 하나씩 찍어냅니다.
# 세션(Session) = DB와의 대화 창구 하나 (Transaction 단위)
AsyncSessionFactory = async_sessionmaker(
    # 위에서 만든 엔진을 연결합니다.
    bind=engine,
    
    # 비동기 세션 클래스를 사용한다고 명시합니다.
    class_=AsyncSession,
    
    # [중요] 커밋(commit) 후에도 객체 정보를 메모리에 유지할지 설정합니다.
    # False: 커밋 후에도 객체 속성에 접근할 수 있게 합니다. (비동기 환경에서 필수 권장)
    # True: 커밋하면 객체가 만료되어, 다시 접근할 때 DB 조회가 발생합니다. (비동기에서 에러 유발 가능)
    expire_on_commit=False
)


# 4. ORM 베이스 클래스
# models.py에서 정의할 모든 테이블 클래스는 이 'Base'를 상속받아야 합니다.
# 그래야 SQLAlchemy가 "아, 이게 테이블이구나" 하고 인식해서 생성해줍니다.
Base = declarative_base()


# 5. DB 초기화 함수 (서버 시작 시 1회 실행)
async def init_db():
    """
    서버가 시작될 때 main.py에서 호출되는 함수입니다.
    1. DB 연결을 테스트하고,
    2. 벡터 기능(pgvector)을 활성화하며,
    3. 정의된 테이블이 없으면 자동으로 생성합니다.
    """
    # 엔진을 통해 연결을 하나 엽니다.
    async with engine.begin() as conn:
        try:
            # 🌟 [벡터 확장 기능 활성화]
            # PostgreSQL에 벡터 기능이 설치되어 있어야 합니다.
            # 이 쿼리가 성공하면 DB 연결은 확실히 성공한 것입니다.
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # [테이블 자동 생성]
            # models.py에서 Base를 상속받아 정의한 모든 클래스(User, Notice 등)를
            # 실제 DB 테이블로 생성합니다. (이미 있으면 건너뜁니다)
            await conn.run_sync(Base.metadata.create_all)
            
            print("✅ DB 초기화 성공: 테이블 및 Vector Extension 준비 완료.")
            
        except Exception as e:
            print(f"❌ DB 초기화 실패: {e}")
            # DB 연결이 안 되면 서버를 켜도 의미가 없으므로 에러를 발생시켜 멈춥니다.
            raise e


# 6. 의존성 주입(Dependency Injection)용 함수
# FastAPI의 Router(API 엔드포인트)에서 DB 세션이 필요할 때 사용합니다.
# 사용법: db: AsyncSession = Depends(get_db)
async def get_db():
    """
    요청이 들어올 때 세션을 열고, 처리가 끝나면 자동으로 닫아주는 제너레이터입니다.
    """
    # 1. 세션 공장에서 세션을 하나 만듭니다.
    async with AsyncSessionFactory() as session:
        try:
            # 2. 요청을 처리하는 곳으로 세션을 빌려줍니다.
            yield session
        finally:
            # 3. 작업이 끝나거나 에러가 나면 반드시 세션을 닫습니다. (반납)
            await session.close()