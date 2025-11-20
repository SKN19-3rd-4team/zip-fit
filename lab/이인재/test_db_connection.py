import sys
import os

# 현재 폴더를 모듈 검색 경로에 추가 (zip_fit 패키지를 찾기 위함)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 작성하신 DB 클래스 임포트
    from zip_fit.db import DB
except ImportError as e:
    print(f"❌ 임포트 에러: {e}")
    print("폴더 구조가 zip_fit/db.py 형태로 되어있는지 확인해주세요.")
    sys.exit(1)

def run_test():
    print("🚀 [테스트] DB 연결 및 pgvector 기능 검증 시작...")
    
    # 1. DB 클래스 인스턴스 생성
    try:
        db = DB()
        print("✅ DB 인스턴스 생성 완료 (설정 로드됨)")
    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
        return

    conn = None
    cur = None

    try:
        # 2. 연결 가져오기
        conn = db.get_connection()
        cur = conn.cursor()
        
        # 3. 테스트 테이블 생성 (movies)
        print("\n🛠️ 테스트용 테이블(movies) 생성 중...")
        cur.execute("DROP TABLE IF EXISTS movies")
        cur.execute("CREATE TABLE movies (id bigserial PRIMARY KEY, title text, summary text, embedding vector(3))")
        
        # 4. 데이터 입력
        print("📥 데이터 삽입 중...")
        movie_data = [
            ('미션 임파서블', '액션 영화', [1.0, 0.1, 0.2]),
            ('러브 액츄얼리', '로맨스 영화', [0.1, 0.9, 0.7]),
            ('나 홀로 집에', '코미디 영화', [0.3, 0.1, 1.0]),
        ]
        
        for title, summary, embedding in movie_data:
            cur.execute("INSERT INTO movies (title, summary, embedding) VALUES (%s, %s, %s)", 
                        (title, summary, embedding))
        
        print(f"✅ {len(movie_data)}개 데이터 저장 완료.")

        # 5. 벡터 검색 테스트
        query_vec = [0.7, 0.7, 0.0] # 액션+로맨스 섞인 취향
        print(f"\n🔍 벡터 검색 테스트 (Query: {query_vec})")
        
        cur.execute("""
            SELECT title, summary, embedding <=> %s::vector as distance
            FROM movies
            ORDER BY distance ASC
            LIMIT 1
        """, (query_vec,))
        
        row = cur.fetchone()
        
        if row:
            print(f"🎉 검색 성공! 가장 유사한 영화: {row[0]}")
            print(f"   - 설명: {row[1]}")
            print(f"   - 거리: {row[2]:.4f}")
        else:
            print("⚠️ 검색 결과가 없습니다.")

    except Exception as e:
        print(f"\n❌ 테스트 실패 (에러 발생): {e}")
        import traceback
        traceback.print_exc()

    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("\n🔒 연결 종료.")

if __name__ == "__main__":
    run_test()