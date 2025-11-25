-- ====================================================================
-- LH 공고 데이터베이스 스키마
-- RAG 프로젝트용 - 공고 및 첨부파일 관리
-- ====================================================================

-- pgvector 확장 설치 (벡터 검색용)
CREATE EXTENSION IF NOT EXISTS vector;

-- ====================================================================
-- 1. 공고 테이블 (announcements)
-- ====================================================================
CREATE TABLE announcements (
    -- 기본키 (CSV의 ID 컬럼)
    id VARCHAR(50) PRIMARY KEY,  -- 'LH_sale_1', 'LH_lease_1', ...

    -- 공고 기본 정보
    notice_type VARCHAR(100),  -- '공공분양(신혼희망)', '국민임대', '영구임대'
    category VARCHAR(20) NOT NULL CHECK (category IN ('sale', 'lease')),  -- 분양/임대 구분
    title TEXT NOT NULL,  -- 공고명
    region VARCHAR(100),  -- 지역

    -- 날짜 정보
    posted_date DATE,  -- 게시일
    deadline_date DATE,  -- 마감일

    -- 상태 정보
    status VARCHAR(20),  -- '접수마감', '공고중'
    view_count INTEGER DEFAULT 0,  -- 조회수

    -- URL
    url TEXT,  -- 원본 공고 URL

    -- 벡터화 상태 추적
    is_vectorized BOOLEAN DEFAULT FALSE,  -- 임베딩 생성 완료 여부
    vectorized_at TIMESTAMP,  -- 벡터화 완료 시각

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ====================================================================
-- 2. 공고 첨부파일 테이블 (announcement_files)
-- ====================================================================
CREATE TABLE announcement_files (
    -- 기본키
    id SERIAL PRIMARY KEY,

    -- 외래키 (어떤 공고의 파일인지)
    announcement_id VARCHAR(50) NOT NULL REFERENCES announcements(id) ON DELETE CASCADE,

    -- 파일 정보
    file_name TEXT NOT NULL,  -- PDF 파일명
    file_path TEXT,  -- 실제 저장 경로 (PDF 다운로드 후 업데이트)

    -- 벡터화 상태 추적
    is_vectorized BOOLEAN DEFAULT FALSE,  -- 이 파일의 임베딩 생성 완료 여부
    vectorized_at TIMESTAMP,  -- 벡터화 완료 시각

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),

    -- 제약조건: 같은 공고에 같은 파일명 중복 방지
    CONSTRAINT unique_announcement_file UNIQUE (announcement_id, file_name)
);

-- ====================================================================
-- 3. 인덱스 생성 (검색 성능 향상)
-- ====================================================================

-- 공고 검색용 인덱스
CREATE INDEX idx_announcements_category ON announcements(category);
CREATE INDEX idx_announcements_notice_type ON announcements(notice_type);
CREATE INDEX idx_announcements_region ON announcements(region);
CREATE INDEX idx_announcements_status ON announcements(status);
CREATE INDEX idx_announcements_dates ON announcements(posted_date, deadline_date);
CREATE INDEX idx_announcements_vectorized ON announcements(is_vectorized);  -- 벡터화 상태

-- 공고 제목 전문 검색 (한국어는 나중에 추가)
-- CREATE INDEX idx_announcements_title_fulltext ON announcements
--     USING gin(to_tsvector('korean', title));

-- 첨부파일 검색용 인덱스
CREATE INDEX idx_files_announcement ON announcement_files(announcement_id);
CREATE INDEX idx_files_vectorized ON announcement_files(is_vectorized);  -- 벡터화 상태

-- ====================================================================
-- 4. 트리거 (자동 업데이트)
-- ====================================================================

-- updated_at 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- announcements 테이블 업데이트 시 자동으로 updated_at 갱신
CREATE TRIGGER trigger_update_announcements_timestamp
    BEFORE UPDATE ON announcements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ====================================================================
-- 5. 뷰 (편리한 조회용)
-- ====================================================================

-- 공고별 첨부파일 수 조회
CREATE VIEW announcement_file_counts AS
SELECT
    a.id,
    a.title,
    a.category,
    a.region,
    a.status,
    COUNT(f.id) as file_count
FROM announcements a
LEFT JOIN announcement_files f ON a.id = f.announcement_id
GROUP BY a.id, a.title, a.category, a.region, a.status;

-- 벡터화 진행 상황
CREATE VIEW vectorization_progress AS
SELECT
    category,
    COUNT(*) as total_announcements,
    SUM(CASE WHEN is_vectorized THEN 1 ELSE 0 END) as vectorized_count,
    ROUND(100.0 * SUM(CASE WHEN is_vectorized THEN 1 ELSE 0 END) / COUNT(*), 2) as progress_pct
FROM announcements
GROUP BY category;

-- ====================================================================
-- 6. 문서 청크 테이블 (RAG 핵심)
-- ====================================================================
CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,

    -- 어떤 공고의 어떤 파일에서 추출되었는지
    announcement_id VARCHAR(50) REFERENCES announcements(id) ON DELETE CASCADE,
    file_id INTEGER REFERENCES announcement_files(id) ON DELETE CASCADE,

    -- 청크 정보
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,  -- 파일 내 청크 순서
    page_number INTEGER,

    -- 임베딩 벡터
    embedding VECTOR(1024) NOT NULL,

    -- 메타데이터
    metadata JSONB,
    /* 예시:
    {
        "file_name": "공고문.pdf",
        "section": "임대조건",
        "has_table": true
    }
    */

    created_at TIMESTAMP DEFAULT NOW(),

    -- 제약조건: 같은 파일 내에서 chunk_index 중복 방지
    CONSTRAINT unique_file_chunk UNIQUE (file_id, chunk_index)
);

-- ====================================================================
-- 7. 추가 인덱스 (document_chunks)
-- ====================================================================

-- 청크 검색용 인덱스
CREATE INDEX idx_chunks_announcement ON document_chunks(announcement_id);
CREATE INDEX idx_chunks_file ON document_chunks(file_id);

-- Vector 검색 인덱스 (HNSW - 빠른 ANN 검색)
CREATE INDEX idx_chunks_embedding ON document_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- 메타데이터 검색
CREATE INDEX idx_chunks_metadata ON document_chunks USING gin(metadata);

-- ====================================================================
-- 완료
-- ====================================================================
-- 스키마 생성 완료!
-- 다음 단계: CSV 데이터 임포트 → PDF 다운로드 → 벡터화
