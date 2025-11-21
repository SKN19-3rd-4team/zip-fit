"""
CSV 데이터를 PostgreSQL로 임포트하는 스크립트
- lh_sale_notices_eng.csv → announcements (category='sale')
- lh_lease_notices_eng.csv → announcements (category='lease')
- lh_sale_notices-download.csv → announcement_files
- lh_lease_notices-download.csv → announcement_files
"""

import pandas as pd
import asyncpg
import asyncio
from datetime import datetime
from pathlib import Path

# ====================================================================
# 설정
# ====================================================================

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'skn19_3rd_proj',  # 데이터베이스 이름
    'user': 'kimjm',  # PostgreSQL 사용자명 (macOS 기본값은 시스템 사용자명)
    'password': ''  # macOS Homebrew PostgreSQL은 기본적으로 비밀번호 없음
}

CSV_DIR = Path('3rd-proj/lab/김종민')

CSV_FILES = {
    'sale_announcements': CSV_DIR / 'lh_sale_notices_eng_core.csv',
    'lease_announcements': CSV_DIR / 'lh_lease_notices_eng_core.csv',
    'sale_files': CSV_DIR / 'lh_sale_notices-download_core.csv',
    'lease_files': CSV_DIR / 'lh_lease_notices-download_core.csv'
}

# ====================================================================
# 유틸리티 함수
# ====================================================================

def parse_date(date_str):
    """날짜 문자열을 date 객체로 변환"""
    if pd.isna(date_str):
        return None
    try:
        # '2024.11.04' → date(2024, 11, 4)
        return datetime.strptime(str(date_str), '%Y.%m.%d').date()
    except:
        return None


# file_category 제거로 인해 삭제됨


# ====================================================================
# 메인 임포트 함수
# ====================================================================

async def import_announcements(conn, csv_path: Path, category: str):
    """공고 데이터 임포트"""
    print(f"\n[1] {category} 공고 데이터 임포트 중...")

    df = pd.read_csv(csv_path)
    print(f"   - 총 {len(df)}건의 공고 발견")

    inserted_count = 0
    skipped_count = 0

    for _, row in df.iterrows():
        try:
            # 중복 체크
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM announcements WHERE id = $1)",
                row['ID']
            )

            if exists:
                skipped_count += 1
                continue

            # 삽입
            await conn.execute("""
                INSERT INTO announcements
                (id, notice_type, category, title, region,
                 posted_date, deadline_date, status, view_count, url)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            row['ID'],
            row['유형'],
            category,
            row['공고명'],
            row['지역'] if pd.notna(row['지역']) else None,
            parse_date(row['게시일']),
            parse_date(row['마감일']),
            row['상태'] if pd.notna(row['상태']) else None,
            int(row['조회수']) if pd.notna(row['조회수']) else 0,
            row['URL'] if pd.notna(row['URL']) else None
            )

            inserted_count += 1

        except Exception as e:
            print(f"   ✗ 오류 ({row['ID']}): {e}")
            continue

    print(f"   ✓ 완료: {inserted_count}건 삽입, {skipped_count}건 스킵")
    return inserted_count


async def import_files(conn, csv_path: Path):
    """첨부파일 데이터 임포트"""
    print(f"\n[2] 첨부파일 데이터 임포트 중...")

    df = pd.read_csv(csv_path)
    print(f"   - 총 {len(df)}건의 파일 발견")

    inserted_count = 0
    skipped_count = 0

    for _, row in df.iterrows():
        try:
            announcement_id = row['ID']
            file_name = row['파일명']

            # 공고 존재 확인
            announcement_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM announcements WHERE id = $1)",
                announcement_id
            )

            if not announcement_exists:
                print(f"   ⚠ 공고 없음: {announcement_id} (파일: {file_name})")
                skipped_count += 1
                continue

            # 파일 중복 체크
            file_exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM announcement_files
                    WHERE announcement_id = $1 AND file_name = $2
                )
            """, announcement_id, file_name)

            if file_exists:
                skipped_count += 1
                continue

            # 삽입
            await conn.execute("""
                INSERT INTO announcement_files
                (announcement_id, file_name)
                VALUES ($1, $2)
            """, announcement_id, file_name)

            inserted_count += 1

        except Exception as e:
            print(f"   ✗ 오류 ({announcement_id}/{file_name}): {e}")
            continue

    print(f"   ✓ 완료: {inserted_count}건 삽입, {skipped_count}건 스킵")
    return inserted_count


async def print_statistics(conn):
    """데이터 통계 출력"""
    print("\n" + "=" * 60)
    print("데이터베이스 통계")
    print("=" * 60)

    # 공고 통계
    total_announcements = await conn.fetchval("SELECT COUNT(*) FROM announcements")
    sale_count = await conn.fetchval("SELECT COUNT(*) FROM announcements WHERE category = 'sale'")
    lease_count = await conn.fetchval("SELECT COUNT(*) FROM announcements WHERE category = 'lease'")

    print(f"\n📋 공고 총 {total_announcements}건")
    print(f"   - 분양: {sale_count}건")
    print(f"   - 임대: {lease_count}건")

    # 공고 유형별 통계
    print("\n📊 공고 유형별 분포:")
    type_stats = await conn.fetch("""
        SELECT notice_type, COUNT(*) as count
        FROM announcements
        GROUP BY notice_type
        ORDER BY count DESC
        LIMIT 10
    """)
    for row in type_stats:
        print(f"   - {row['notice_type']}: {row['count']}건")

    # 파일 통계
    total_files = await conn.fetchval("SELECT COUNT(*) FROM announcement_files")
    print(f"\n📎 첨부파일 총 {total_files}건")

    # 벡터화 진행 상황
    print("\n🔄 벡터화 진행 상황:")
    vec_progress = await conn.fetch("""
        SELECT * FROM vectorization_progress
    """)
    for row in vec_progress:
        print(f"   - {row['category']}: {row['vectorized_count']}/{row['total_announcements']} ({row['progress_pct']}%)")

    # 공고별 평균 파일 수
    avg_files = await conn.fetchval("""
        SELECT AVG(file_count)::NUMERIC(10,2)
        FROM (
            SELECT announcement_id, COUNT(*) as file_count
            FROM announcement_files
            GROUP BY announcement_id
        ) sub
    """)
    print(f"\n📊 공고당 평균 첨부파일 수: {avg_files}개")

    print("\n" + "=" * 60)


# ====================================================================
# 메인 실행
# ====================================================================

async def main():
    print("=" * 60)
    print("LH 공고 데이터 임포트 시작")
    print("=" * 60)

    # DB 연결
    print("\n🔌 데이터베이스 연결 중...")
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("   ✓ 연결 성공")
    except Exception as e:
        print(f"   ✗ 연결 실패: {e}")
        print("\n💡 PostgreSQL 설정 확인:")
        print("   1. PostgreSQL이 실행 중인지 확인")
        print("   2. DB_CONFIG의 host, port, database, user, password 확인")
        print("   3. 데이터베이스 생성: CREATE DATABASE lh_announcements;")
        return

    try:
        # 1. 분양 공고 임포트
        await import_announcements(
            conn,
            CSV_FILES['sale_announcements'],
            'sale'
        )

        # 2. 임대 공고 임포트
        await import_announcements(
            conn,
            CSV_FILES['lease_announcements'],
            'lease'
        )

        # 3. 분양 첨부파일 임포트
        await import_files(
            conn,
            CSV_FILES['sale_files']
        )

        # 4. 임대 첨부파일 임포트
        await import_files(
            conn,
            CSV_FILES['lease_files']
        )

        # 5. 통계 출력
        await print_statistics(conn)

        print("\n✅ 임포트 완료!")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()
        print("\n🔌 데이터베이스 연결 종료")


if __name__ == "__main__":
    asyncio.run(main())
