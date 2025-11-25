# ZIPFIT (집핏) - 나에게 딱 맞는 집

**SK네트웍스 Family AI 캠프 19기 3차 프로젝트**

> LLM과 RAG 기술을 활용한 공공주택 공고 기반 맞춤형 주거 정보 제공 AI 에이전트 서비스


<img width="1671" alt="home" src="https://github.com/user-attachments/assets/4f488cb9-28f7-4d72-a380-6c51172ea71e" />

**상세 문서**: [프로젝트 산출물](./docs/00_프로젝트_산출물.md)

---

## 1. 팀 소개

**팀명**: A.J.C

**팀원**:

| <img src="https://github.com/user-attachments/assets/4fef2723-f298-406e-8e18-dfe06c61c174" width="200" height="200" /> | <img src="https://github.com/user-attachments/assets/f58d5e52-fa84-4745-affd-472ac458912b" width="200" height="200" /> | <img src="https://github.com/user-attachments/assets/86647741-f153-49da-89c2-d2922872665d" width="200" height="200" /> | <img src="https://github.com/user-attachments/assets/b7972497-13b2-458a-a013-4c9568428645" width="200" height="200" /> | <img src="https://github.com/user-attachments/assets/b3c747f8-4497-4136-bc4a-426c2b16c808" width="200" height="200" /> |
|---|---|---|---|---|
| 김범섭 | 김종민 | 오흥재 | 이상혁 | 이인재 |
| [@WhatSupYap](https://github.com/WhatSupYap) | [@jongminkim-KR1](https://github.com/jongminkim-KR1) | [@vfxpedia](https://github.com/vfxpedia) | [@sangpiri](https://github.com/sangpiri) | [@distecter](https://github.com/distecter) |

---

## 2. 프로젝트 개요

### 프로젝트 명
ZIPFIT (집핏) - 나에게 딱 맞는 집

### 프로젝트 소개
ZIPFIT은 LH(한국토지주택공사), SH(서울주택도시공사), GH(경기주택도시공사) 등 공공주택 공고를 통합하여, LLM과 RAG 기술을 활용해 사용자 맞춤형 주거 정보를 제공하는 AI 에이전트 서비스입니다.

복잡하고 이해하기 어려운 공공주택 공고문을 분석하여, 사용자의 조건에 맞는 공고를 추천하고, 공고 정보를 쉽게 이해할 수 있도록 안내합니다.

**현재 프로토타입 범위**:
- **데이터 범위**: LH 공고 중 서울/경기 지역 공고만 대상
- **핵심 서비스 흐름**: AI 상담 → 공고 비교/추천 → 신청 안내
- **제외된 기능** (향후 확장 예정): 자격 진단, 계약 지원, 대출 정보 제공

**최종 목표 서비스 흐름**: AI 상담 → 자격 진단 → 공고 비교/추천 → 신청 안내 → 계약 지원 → 대출 정보 제공

### 프로젝트 필요성 (배경)

공공주택(LH, SH, GH)은 청년, 신혼부부, 저소득층 등 주거 취약계층에게 매우 중요한 주거 안정 수단입니다. 그러나 현재 공공주택 공고는 다음과 같은 문제점이 있습니다:

1. **복잡한 공고 구조**: 각 기관(LH, SH, GH)마다 공고 형식과 용어가 달라, 통합적으로 비교하기 어렵습니다.

2. **전문 용어의 범람**: "선계약후검증", "묵시적갱신", "계약보증금" 등 일반인이 이해하기 어려운 전문 용어가 많습니다.

3. **산재된 정보**: 자격 요건, 신청 방법, 대출 정보 등이 각각 다른 문서와 웹사이트에 흩어져 있어 정보 수집에 많은 시간이 소요됩니다.

4. **자격 판단의 어려움**: 본인이 해당 공고에 신청할 자격이 되는지 판단하기 위해서는 복잡한 소득 기준, 거주 요건 등을 일일이 확인해야 합니다.

이러한 문제로 인해 많은 국민들이 자신에게 적합한 공공주택 기회를 놓치거나, 부적격 신청으로 시간을 낭비하는 경우가 발생하고 있습니다.

### 프로젝트 목표

1. **LLM 기반 비정형 문서 이해**: 공공주택 공고문의 맥락을 이해하고, 사용자의 질문에 맞춰 필요한 정보를 추출하여 쉽게 설명합니다.

2. **사용자 맞춤형 정보 제공**: 사용자의 나이, 소득, 가족 구성 등을 고려하여 맞춤형 공고를 추천하고, 자격 요건을 자동으로 확인합니다.

3. **원스톱 서비스 제공**: 공고 검색부터 신청, 계약, 대출까지 여러 단계를 하나의 대화 창에서 처리할 수 있도록 지원합니다.

4. **사회적 가치 실현**: 모든 국민이 공평하게 공공주택 정보에 접근하고, 자신에게 맞는 주거 기회를 찾을 수 있도록 지원함으로써 주거 불평등 해소에 기여합니다.

---

## 3. 기술 스택 & 사용한 모델

| 구분 | 상세 구분 | 기술/도구 | 버전/모델명 | 용도 |
| :---: | :---: | :--- | :--- | :--- |
| **Backend** | API | <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/> | 0.121.3 | RESTful API 프레임워크 |
| | 언어 | <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> | 3.12 | 백엔드 개발 언어 |
| | 비동기 | <img src="https://img.shields.io/badge/Asyncio-007ACC?style=for-the-badge&logo=asyncapi&logoColor=white"/> | 4.11.0 | 비동기 처리 |
| | DB 연결 | <img src="https://img.shields.io/badge/asyncpg-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/> | 0.30.0 | PostgreSQL 비동기 연결 |
| | LLM 클라이언트 | <img src="https://img.shields.io/badge/OpenAI_SDK-412991?style=for-the-badge&logo=openai&logoColor=white"/> | 1.57.2 | OpenAI API 클라이언트 |
| | 서버 | <img src="https://img.shields.io/badge/Uvicorn-010101?style=for-the-badge&logo=uvicorn&logoColor=white"/> | 0.38.0 | ASGI 서버 |
| **Frontend** | 프레임워크 | <img src="https://img.shields.io/badge/Vue-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white"/> | 3.5.22 | 프론트엔드 프레임워크 |
| | 빌드 | <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white"/> | 7.1.11 | 빌드 도구 |
| | 언어 | <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white"/> | 5.9.0 | 타입 안전성 보장 |
| | 상태 관리 | <img src="https://img.shields.io/badge/Pinia-FFDC3D?style=for-the-badge&logo=pinia&logoColor=black"/> | 3.0.3 | 상태 관리 |
| | 라우팅 | <img src="https://img.shields.io/badge/Vue_Router-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white"/> | 4.6.3 | 라우팅 |
| | 런타임 | <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white"/> | ^20.19.0+ | 런타임 환경 |
| **데이터베이스** | RDB | <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/> | 14.20 | 관계형 데이터베이스 |
| | 벡터 확장 | <img src="https://img.shields.io/badge/pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/> | 0.4.1 | 벡터 확장 |
| | DB 연결 | <img src="https://img.shields.io/badge/asyncpg-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/> | 0.30.0 | 비동기 DB 연결 라이브러리 |
| **AI 모델** | 임베딩 | <img src="https://img.shields.io/badge/BAAI%2Fbge--m3-010101?style=for-the-badge&logo=huggingface&logoColor=white"/> | - | 문서 및 질문 임베딩 생성 (1024차원) |
| | 임베딩 라이브러리 | <img src="https://img.shields.io/badge/Sentence--Transformers-FF6347?style=for-the-badge&logo=pytorch&logoColor=white"/> | 3.3.1 | 임베딩 모델 라이브러리 |
| | Reranker | <img src="https://img.shields.io/badge/Ko--Reranker-010101?style=for-the-badge&logo=huggingface&logoColor=white"/> | - | 검색 결과 재순위화 (Cross-Encoder) |
| | LLM | <img src="https://img.shields.io/badge/GPT--4o--mini-000000?style=for-the-badge&logo=openai&logoColor=white"/> | OpenAI | 질문 재구성, 답변 생성, 맥락 분석 |
| **데이터 처리** | PDF 추출 | <img src="https://img.shields.io/badge/PyMuPDF4LLM-B31B1B?style=for-the-badge&logo=pdf&logoColor=white"/> | 0.0.17 | PDF 텍스트 추출 |
| | 청킹 | <img src="https://img.shields.io/badge/Langchain--Splitter-181818?style=for-the-badge&logo=langchain&logoColor=white"/> | 0.3.2 | 텍스트 청킹 |
| | HTTP | <img src="https://img.shields.io/badge/requests-010101?style=for-the-badge&logo=html5&logoColor=white"/> | 2.32.5 | HTTP 요청 |
| | 파싱 | <img src="https://img.shields.io/badge/BeautifulSoup4-010101?style=for-the-badge&logo=html5&logoColor=white"/> | 4.14.2 | HTML 파싱 |
| | 데이터 분석 | <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/> | 2.2.3 | 데이터 분석 및 처리 |
| | 딥러닝 | <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"/> | >=2.6.0 | 딥러닝 프레임워크 |
| | 수치 연산 | <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white"/> | >=1.24.0 | 수치 연산 라이브러리 |
| **개발 환경** | 컨테이너 | <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/> | 4.41.0.210443 | 컨테이너화 및 배포 |
| | 패키지 관리 | <img src="https://img.shields.io/badge/Pip%2FConda-010101?style=for-the-badge&logo=anaconda&logoColor=white"/> | - | 패키지 관리 |
| | 환경 변수 | <img src="https://img.shields.io/badge/python--dotenv-3776AB?style=for-the-badge&logo=python&logoColor=white"/> | 1.0.1 | 환경 변수 관리 |

---

## 4. 시스템 아키텍처

자세한 내용은 [시스템 아키텍처 문서](./docs/03_시스템_아키텍처.md)를 참조하세요.

![SKN_3차_ZIPFIT - 시스템 아키텍쳐](https://github.com/user-attachments/assets/91d8e81f-7320-4d7e-87f7-4fd3dcfe049a)

---

## 5. WBS

<table style="width:100%; border-collapse: collapse; text-align: center;">
    <thead>
        <tr>
            <th style="width:10%; padding: 8px; border-bottom: 2px solid #ddd;">분류</th>
            <th style="width:30%; padding: 8px; border-bottom: 2px solid #ddd; text-align: left;">상세업무</th>
            <th style="width:20%; padding: 8px; border-bottom: 2px solid #ddd;">담당자</th>
            <th style="width:40%; padding: 8px; border-bottom: 2px solid #ddd;">Date</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="background-color: #e0f7fa; padding: 6px;">✨ 기획</td>
            <td style="text-align: left; padding: 6px;">📄 기획</td>
            <td>ALL</td>
            <td>2025년 11월 12일 → 11월 14일</td>
        </tr>
        <tr>
            <td style="background-color: #e0f7fa; padding: 6px;">✨ 기획</td>
            <td style="text-align: left; padding: 6px;">📄 프로토타입 설계</td>
            <td>김범섭</td>
            <td>2025년 11월 14일</td>
        </tr>
        <tr>
            <td style="background-color: #fff9c4; padding: 6px;">📊 데이터</td>
            <td style="text-align: left; padding: 6px;">📄 데이터 조사</td>
            <td>이상혁, 오흥재, 이인재</td>
            <td>2025년 11월 18일 → 11월 19일</td>
        </tr>
        <tr>
            <td style="background-color: #fff9c4; padding: 6px;">📊 데이터</td>
            <td style="text-align: left; padding: 6px;">📄 데이터 수집</td>
            <td>이상혁</td>
            <td>2025년 11월 16일 → 11월 18일</td>
        </tr>
        <tr>
            <td style="background-color: #ffccbc; padding: 6px;">🗄️ DB설계</td>
            <td style="text-align: left; padding: 6px;">📄 DB 조사</td>
            <td>ALL</td>
            <td>2025년 11월 17일</td>
        </tr>
        <tr>
            <td style="background-color: #ffccbc; padding: 6px;">🗄️ DB설계</td>
            <td style="text-align: left; padding: 6px;">📄 전처리 및 벡터DB 구축</td>
            <td>김종민</td>
            <td>2025년 11월 19일 → 11월 20일</td>
        </tr>
        <tr>
            <td style="background-color: #ffccbc; padding: 6px;">🗄️ DB설계</td>
            <td style="text-align: left; padding: 6px;">📄 DB 구축 인프라 설정</td>
            <td>김종민</td>
            <td>2025년 11월 18일 → 11월 20일</td>
        </tr>
        <tr>
            <td style="background-color: #e1bee7; padding: 6px;">🗣️ RAG</td>
            <td style="text-align: left; padding: 6px;">📄 RAG 파이프라인 구축</td>
            <td>김종민, 이상혁</td>
            <td>2025년 11월 20일 → 11월 23일</td>
        </tr>
        <tr>
            <td style="background-color: #f8bbd0; padding: 6px;">💻 설계</td>
            <td style="text-align: left; padding: 6px;">📄 백엔드 기초 작업</td>
            <td>김범섭</td>
            <td>2025년 11월 20일</td>
        </tr>
        <tr>
            <td style="background-color: #f8bbd0; padding: 6px;">💻 설계</td>
            <td style="text-align: left; padding: 6px;">📄 프론트엔드 기초 작업</td>
            <td>김범섭</td>
            <td>2025년 11월 20일</td>
        </tr>
        <tr>
            <td style="background-color: #f8bbd0; padding: 6px;">💻 설계</td>
            <td style="text-align: left; padding: 6px;">📄 최종 설계안</td>
            <td>김범섭</td>
            <td></td>
        </tr>
        <tr>
            <td style="background-color: #ffe0b2; padding: 6px;">🔨 개발</td>
            <td style="text-align: left; padding: 6px;">📄 백엔드 개발</td>
            <td>이인재</td>
            <td>2025년 11월 21일 → 11월 24일</td>
        </tr>
        <tr>
            <td style="background-color: #ffe0b2; padding: 6px;">🔨 개발</td>
            <td style="text-align: left; padding: 6px;">📄 프론트엔드 개발</td>
            <td>김범섭</td>
            <td>2025년 11월 21일 → 11월 24일</td>
        </tr>
        <tr>
            <td style="background-color: #b3e5fc; padding: 6px;">🧪 테스트</td>
            <td style="text-align: left; padding: 6px;">📄 기능 테스트</td>
            <td>ALL</td>
            <td>2025년 11월 24일 → 11월 25일</td>
        </tr>
        <tr>
            <td style="background-color: #b3e5fc; padding: 6px;">🧪 테스트</td>
            <td style="text-align: left; padding: 6px;">📄 프롬프트 최적화</td>
            <td>김종민, 이상혁, 오흥재</td>
            <td>2025년 11월 24일 → 11월 25일</td>
        </tr>
        <tr>
            <td style="background-color: #c8e6c9; padding: 6px;">📢 발표</td>
            <td style="text-align: left; padding: 6px;">📄 README 작성</td>
            <td>오흥재, 이상혁</td>
            <td>2025년 11월 24일 → 11월 25일</td>
        </tr>
        <tr>
            <td style="background-color: #c8e6c9; padding: 6px;">📢 발표</td>
            <td style="text-align: left; padding: 6px;">📄 발표 준비</td>
            <td>김범섭</td>
            <td>2025년 11월 24일 → 11월 25일</td>
        </tr>
    </tbody>
</table>

---

## 6. 요구사항 명세서

자세한 내용은 [요구사항 명세서 문서](./docs/08_요구사항_명세서.md)를 참조하세요.

### 프로젝트 범위

| 구분 | 프로토타입 (현재 구현) | 최종 목표 |
|------|---------------------|----------|
| **데이터** | LH 공고 중 서울/경기 지역만 | 전국 지역, GH/SH 공고 포함 |
| **핵심 기능** | AI 상담 → 공고 비교/추천 → 신청 안내 | AI 상담 → 자격 진단 → 공고 비교/추천 → 신청 안내 → 계약 지원 → 대출 정보 제공 |
| **제외 기능** | 자격 진단, 계약 지원, 대출 정보 제공 | - |

### 기능 요구사항 요약

| 기능 ID | 기능명 | 프로토타입 상태 | 우선순위 |
|---------|--------|----------------|---------|
| FR-001 | AI 상담 (대화형 인터페이스) | ✅ 구현 완료 | 높음 |
| FR-002 | 질문 재구성 및 분석 | ✅ 구현 완료 | 높음 |
| FR-003 | RAG 기반 문서 검색 | ✅ 구현 완료 | 높음 |
| FR-004 | 공고 비교 및 추천 | ✅ 구현 완료 | 높음 |
| FR-005 | 신청 안내 | ✅ 구현 완료 | 높음 |
| FR-006 | 자격 진단 | ❌ 미구현 (향후 확장) | 중간 |
| FR-007 | 계약 지원 | ❌ 미구현 (향후 확장) | 낮음 |
| FR-008 | 대출 정보 제공 | ❌ 미구현 (향후 확장) | 중간 |
| FR-009 | 용어 설명 (Glossary) | ✅ 구현 완료 | 중간 |
| FR-010 | 세션 관리 | ✅ 구현 완료 | 높음 |
| FR-011 | 공고 통계 대시보드 | ✅ 구현 완료 | 중간 |
| FR-012 | 공고 목록 조회 | ⚠️ 구조만 구현 | 중간 |

### 비기능 요구사항 요약

| 항목 | 요구사항 | 현재 상태 |
|------|----------|----------|
| **응답 시간** | 평균 3초 이내 | 측정 필요 |
| **동시 접속자** | 최소 10명 동시 처리 | ✅ 지원 (비동기 처리) |
| **확장성** | Stateless API 설계 | ✅ 지원 |
| **보안** | 입력 검증, CORS 설정, API 키 관리 | ✅ 구현 완료 |
| **호환성** | 최신 브라우저 지원, Python 3.12, Node.js ^20.19.0 | ✅ 지원 |

### 주요 제약사항

| 제약사항 | 설명 |
|----------|------|
| **데이터 범위** | 프로토타입은 LH 서울/경기 지역만 대상 |
| **LLM API 비용** | OpenAI API 사용으로 인한 비용 발생 |
| **세션 저장** | 인메모리 저장으로 서버 재시작 시 데이터 손실 가능 |
| **공고 업데이트** | 수동 크롤링으로 실시간 업데이트 어려움 |

### 향후 확장 계획

- **Phase 2**: 자격 진단, GH/SH 공고 통합, 공고 목록 완성
- **Phase 3**: 대출 정보 제공, 계약 지원, 알림 기능

**상세 내용**: [요구사항 명세서 문서](./docs/08_요구사항_명세서.md)

---

## 7. 수집한 데이터 및 전처리 요약

자세한 내용은 다음 문서를 참조하세요:
- [수집된 데이터](./docs/01_수집된_데이터.md)
- [데이터 전처리 문서](./docs/02_데이터_전처리_문서.md)

### 데이터 수집

#### LH (한국토지주택공사) 공고 데이터
- **수집 기간**: 2024년 11월 1일 이후 공고
- **수집 방법**: 웹 크롤링 (POST 방식)
- **프로토타입 범위**: 서울/경기 지역 공고만 대상
- **수집 항목**: 공고번호, 유형, 공고명, 지역, 게시일, 마감일, 상태, 조회수, 상세 URL
- **유형 분류**:

| 구분 | 유형 | 설명 |
|------|------|------|
| **임대** | 통합공공임대 | 통합된 공공 임대주택 |
| | 통합공공임대(신혼희망) | 신혼부부 우선 공급 |
| | 국민임대 | 국민임대주택 |
| | 공공임대 | 공공임대주택 |
| | 영구임대 | 영구임대주택 |
| | 행복주택 | 행복주택 |
| | 행복주택(신혼희망) | 신혼부부 우선 공급 |
| | 장기전세 | 장기전세주택 |
| | 신축다세대매입임대 | 신축 다세대 매입 임대 |
| | 가정어린이집 | 가정어린이집 |
| | 매입임대 | 매입임대주택 |
| | 전세임대 | 전세임대주택 |
| | 집주인임대 | 집주인임대주택 |
| | 6년 공공임대주택 | 6년 공공임대주택 |
| **분양** | 분양주택 | 분양주택 |
| | 공공분양(신혼희망) | 신혼부부 우선 공급 |
- **저장 형식**: CSV (lh_lease_notices_F.csv, lh_sale_notices_F.csv)

#### GH (경기주택도시공사) 공고 데이터
- **수집 상태**: 크롤링 완료 (프로토타입에서는 미사용)

#### SH (서울주택도시공사) 공고 데이터
- **수집 상태**: 크롤링 완료 (프로토타입에서는 미사용)

### 데이터 전처리

#### PDF 문서 처리
- **도구**: pymupdf4llm (0.0.17)
- **처리 과정**: PDF 다운로드 → 텍스트 추출 → 마크다운 변환
- **구조 보존**: 섹션 헤더, 테이블 구조 유지

#### 텍스트 청킹 (Chunking)
- **구현 위치**: `lab/이인재/규격/chunking.py`
- **기반 문서**: PDF에서 추출한 텍스트를 마크다운 형식으로 변환한 문서
- **클래스**: `SmartChunker`
- **청킹 파라미터**:
  - 최소 청크 크기: 100자
  - 최적 청크 크기: 600자
  - 최대 청크 크기: 1200자
  - 최대 테이블 크기: 3000자
  - 청크 오버랩: 150자
- **방법**: RecursiveCharacterTextSplitter 활용, 섹션 헤더 및 테이블 구조 보존
- **주요 기능**: 
  - 섹션 헤더 자동 감지 (마크다운 헤더, 한글 섹션 표시)
  - 테이블 구조 인식 및 처리
  - 문맥 보존을 위한 오버랩 처리
  - 의미 있는 청크 필터링 (최소 단어 수 확인)

#### 임베딩 생성
- **구현 위치**: `lab/이인재/규격/vectorizer.py`
- **모델**: BAAI/bge-m3 (sentence-transformers 3.3.1)
- **차원**: 1024차원
- **처리 과정**:
  1. 각 청크 텍스트를 모델에 입력
  2. 정규화된 임베딩 벡터 생성 (`normalize_embeddings=True`)
  3. PostgreSQL pgvector 확장을 사용하여 벡터 저장 (`vector(1024)` 타입)
- **메타데이터**: JSONB 형식으로 섹션 정보, 파일명, 테이블 포함 여부, 청크 길이 저장

#### 용어집 (Glossary) 구축
- 공공주택 관련 전문 용어 1,000개 이상 수집 및 정리
- 용어별 쉬운 설명, 상세 설명, 사용 예시, 관련 용어 포함
- RAG 시스템에서 용어 설명 제공에 활용

---

## 8. DB 연동 구현 코드

자세한 내용은 [DB 연동 구현 코드 문서](./docs/05_DB_연동_구현_코드.md)를 참조하세요.

### 개요
PostgreSQL과 pgvector 확장을 활용하여 공고 메타데이터, PDF 파일 정보, 문서 청크 및 임베딩 벡터를 저장하고 검색합니다. RDB와 VectorDB의 역할을 동시에 수행하는 하이브리드 데이터베이스 구조를 채택했습니다.

### 데이터베이스 스키마

PostgreSQL에서 총 3개의 테이블을 사용합니다.

#### announcements 테이블
웹 크롤링을 통해 수집한 공고 메타데이터를 저장하는 테이블입니다.

**주요 컬럼**:
- `id`: 공고 고유 ID
- `notice_type`: 공고 유형 (국민임대, 행복주택 등)
- `category`: 카테고리 (lease/sale)
- `title`: 공고 제목
- `region`: 지역
- `posted_date`: 게시일
- `deadline_date`: 마감일
- `status`: 상태
- `view_count`: 조회수
- `url`: 공고 URL
- `is_vectorized`: 벡터화 완료 여부
- `vectorized_at`: 벡터화 완료 시각
- `created_at`, `updated_at`: 생성/수정 시각

#### announcement_files 테이블
각 공고에 해당하는 PDF 문서 다운로드 정보를 저장하는 테이블입니다.

**주요 컬럼**:
- `id`: 파일 고유 ID
- `announcement_id`: 공고 ID (외래키)
- `file_name`: 파일명
- `file_path`: 파일 경로
- `is_vectorized`: 벡터화 완료 여부
- `vectorized_at`: 벡터화 완료 시각
- `created_at`: 생성 시각

#### document_chunks 테이블
공고 PDF 문서를 청킹하고 임베딩한 벡터를 저장하는 테이블입니다. RDB와 VectorDB의 역할을 동시에 수행합니다.

**주요 컬럼**:
- `id`: 청크 고유 ID
- `announcement_id`: 공고 ID (외래키)
- `file_id`: 파일 ID (외래키)
- `chunk_text`: 청크 텍스트
- `chunk_index`: 청크 인덱스
- `page_number`: 페이지 번호 (NULL 가능)
- `embedding`: 임베딩 벡터 (pgvector 타입, 1024차원)
- `metadata`: 메타데이터 (JSONB)
  - `section`: 섹션 정보
  - `file_name`: 파일명
  - `has_table`: 테이블 포함 여부
  - `chunk_length`: 청크 길이

### 주요 구현 파일

#### Backend
- `back-end/zip_fit/gongo.py`: 벡터 검색, 키워드 검색, 하이브리드 검색, 재순위화 구현
- `back-end/zip_fit/config.py`: 데이터베이스 연결 설정 및 RAG 파라미터 설정
- `back-end/zip_fit/dependencies.py`: 데이터베이스 연결 및 모델 로딩 관리
- `back-end/zip_fit/chatting.py`: RAG 챗봇 서비스 로직
- `back-end/zip_fit/llm_handler.py`: LLM 처리 (질문 재구성, 답변 생성)
- `back-end/zip_fit/router.py`: API 라우터 및 세션 관리
- `back-end/zip_fit/info.py`: 통계 정보 제공

#### 데이터베이스 관리
- `lab/이인재/규격/database.py`: 데이터베이스 관리 클래스 (벡터화 진행 상황 추적, 청크 저장 등)

### 벡터 검색 구현

#### 벡터 유사도 검색
pgvector의 cosine distance 연산자 (`<=>`)를 활용한 의미 기반 검색:

```python
# back-end/zip_fit/gongo.py
async def vector_search(query: str, top_k: int = 15, filters: dict = None):
    query_embedding = model.encode(query, normalize_embeddings=True)
    # pgvector cosine distance 연산자 사용
    sql = """
        SELECT ..., (1 - (dc.embedding <=> $1::vector)) as similarity
        FROM document_chunks dc
        JOIN announcements a ON dc.announcement_id = a.id
        ORDER BY dc.embedding <=> $1::vector
        LIMIT $2
    """
```

#### 하이브리드 검색
벡터 검색과 키워드 검색 결과를 병합하여 검색 정확도 향상:

```python
# back-end/zip_fit/gongo.py
async def multi_query_hybrid_search(query_analysis, multi_queries):
    # 벡터 검색과 키워드 검색 병렬 수행 후 결과 병합
    vector_results = await vector_search(...)
    keyword_results = await keyword_search(...)
    # 중복 제거 및 병합
```

#### 재순위화
Cross-Encoder 기반 Reranker로 검색 결과 재정렬:

```python
# back-end/zip_fit/gongo.py
def rerank_results(query: str, search_results: List[Dict], top_k: int = 8):
    reranker = get_reranker()  # Dongjin-kr/ko-reranker
    pairs = [(query, r['chunk_text']) for r in search_results]
    scores = reranker.predict(pairs)
    # Rerank 점수 기준 정렬
```

#### 필터링
지역, 유형, 카테고리별 필터링 지원으로 검색 범위 최적화.

### RAG 파이프라인 흐름

자세한 내용은 [개발된 소프트웨어 문서](./docs/04_개발된_소프트웨어.md)를 참조하세요.

RAG 시스템은 다음과 같은 단계로 사용자 질문에 대한 답변을 생성합니다:

1. **질문 재구성** (`llm_handler.py`): 사용자 질문을 분석하여 지역, 유형, 카테고리 등 검색 필터 추출
2. **멀티쿼리 생성** (`llm_handler.py`): 원본 질문을 다양한 표현으로 변환하여 검색 범위 확대
3. **하이브리드 검색** (`gongo.py`): 벡터 검색과 키워드 검색을 병렬 수행 후 결과 병합
4. **재순위화** (`gongo.py`): Cross-Encoder 기반 Reranker로 검색 결과 재정렬
5. **청크 병합** (`gongo.py`): 동일 공고의 여러 청크를 문맥 순서대로 병합
6. **컨텍스트 구성** (`gongo.py`): 검색된 공고 정보를 구조화된 형식으로 구성
7. **답변 생성** (`llm_handler.py`): 제공된 컨텍스트를 바탕으로 GPT-4o-mini가 답변 생성

### API 엔드포인트

| 메서드 | 엔드포인트 | 기능 | 요청 형식 | 응답 형식 |
|--------|-----------|------|----------|----------|
| POST | `/api/v1/chat` | RAG 챗봇 메인 엔드포인트 | `ChatRequest` (user_id, query) | `ChatResponse` (query, answer, sources) |
| POST | `/api/v1/session/reset` | 세션 초기화 | `ResetRequest` (user_id) | 상태 메시지 |
| GET | `/api/v1/stats` | 대시보드 통계 조회 | - | 공고 통계 정보 |
| GET | `/` | 헬스 체크 | - | 서비스 상태 및 설정 정보 |

#### API 사용 예시

**채팅 요청**:
```json
POST /api/v1/chat
{
  "user_id": "user123",
  "query": "서울 행복주택 신청할 수 있어?"
}
```

**채팅 응답**:
```json
{
  "query": "서울 행복주택 신청할 수 있어?",
  "answer": "네, 서울 지역 행복주택 신청이 가능합니다...",
  "sources": [
    {
      "announcement_id": "LH_lease_1",
      "announcement_title": "서울시 강남구 행복주택 모집공고",
      "region": "서울",
      "notice_type": "행복주택",
      "category": "lease",
      "rerank_score": 0.95,
      "num_chunks": 3
    }
  ],
  "metadata": {
    "query_analysis": {...}
  }
}
```

---

## 9. 테스트 계획 및 결과 보고서

자세한 내용은 [테스트 계획 및 결과 보고서](./docs/06_테스트_계획_및_결과_보고서.md)를 참조하세요.

### 테스트 계획

#### 기능 테스트
- [ ] RAG 파이프라인 테스트
- [ ] 벡터 검색 정확도 테스트
- [ ] 세션 관리 테스트
- [ ] API 엔드포인트 테스트

#### 성능 테스트
- [ ] 응답 시간 측정
- [ ] 동시 접속자 처리 테스트
- [ ] 벡터 검색 성능 테스트

#### 사용자 테스트
- [ ] 실제 사용자 시나리오 테스트
- [ ] 답변 정확도 평가

### 테스트 결과
(추후 작성 예정)

---

## 10. 진행 과정 중 프로그램 개선 노력

본 프로젝트에서는 기본 RAG 시스템의 한계를 극복하기 위해 다양한 고급 RAG 기법을 단계적으로 도입하고 개선했습니다.

자세한 내용은 [진행 과정 중 프로그램 개선 노력 문서](./docs/07_진행_과정_중_프로그램_개선_노력.md)를 참조하세요.

### RAG 파이프라인 단계별 문제점 및 해결 방안

```
[사용자 질문]
    ↓
[1. 컨텍스트 분석] → 이전 대화 참조 여부 판단
    ↓
[2. 질문 재구성] → 검색 최적화된 형태로 변환
    ↓
[3. 멀티쿼리 생성] → 다양한 표현으로 변환
    ↓
[4. 하이브리드 검색] → 벡터 검색 + 키워드 검색
    ↓
[5. 재순위화 (Reranking)] → 관련도 기준 재정렬
    ↓
[6. 청크 병합] → 동일 공고의 청크 통합
    ↓
[7. 답변 생성] → LLM 기반 답변 생성
```

---

## 11. 수행 결과 (테스트/시연 페이지)

### 시연 페이지
(추후 작성 예정)

### 주요 기능 시연
(추후 작성 예정)

---

## 12. 한 줄 회고

| 팀원 | 역할 | 한 줄 회고 |
|------|------|-----------|
| 김범섭 | 시스템 아키텍처 설계, 프로젝트 총괄, 프론트엔드 개발 | (작성 예정) |
| 김종민 | LLM 파이프라인 구성 (RAG, 임베딩, 청킹 등) | (작성 예정) |
| 이상혁 | 데이터 수집 및 크롤링, RAG 파이프라인 구성, 프롬프팅 설계 | (작성 예정) |
| 이인재 | 백엔드 아키텍처 구성 및 데이터베이스 관리 | (작성 예정) |
| 오흥재 | 공공주택 용어집(Glossary) 구축 및 프로젝트 지원 | (작성 예정) |

---

## 개발 환경 설정

### Backend 설정

#### 필수 요구사항
- Python 3.12
- PostgreSQL (pgvector 확장 설치 필요)
- OpenAI API Key

#### 설치 방법

```bash
# Conda 환경 생성
conda create -n zf_back python=3.12
conda activate zf_back

# 필수 패키지 설치
pip install fastapi uvicorn "pydantic[email]"
pip install mysql-connector-python aiomysql langchain openai
pip install sentence-transformers python-dotenv asyncpg
pip install pymupdf4llm langchain-text-splitters pandas torch
```

#### 환경 변수 설정 (.env 파일)
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_DATABASE=your_database
OPENAI_API_KEY=your_openai_api_key
GOV_API_KEY=your_gov_api_key
MODEL_CACHE_DIR=./model_cache
USE_RERANKER=true
```

#### 서버 실행
```bash
cd back-end/zip_fit
uvicorn main:app --reload
```

### Frontend 설정

#### 필수 요구사항
- Node.js (^20.19.0 || >=22.12.0)

#### 설치 방법
```bash
cd front-end/zf_front
npm install
```

#### 개발 서버 실행
```bash
npm run dev
```

### 데이터베이스 설정

#### Docker를 사용한 데이터베이스 설정 (권장)
프로젝트에서 Docker를 사용하여 데이터베이스를 설정할 수 있습니다. `docker-compose.yml` 파일이 있는 경우 다음 명령어로 실행합니다:

```bash
docker-compose up -d
```

#### PostgreSQL pgvector 확장 설치
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 테이블 생성
(스키마 파일 참조)

#### 버전 확인 방법
PostgreSQL 및 pgvector 버전은 다음 SQL 명령어로 확인할 수 있습니다:
```sql
-- PostgreSQL 버전 확인
SELECT version();

-- pgvector 확장 확인
SELECT * FROM pg_extension WHERE extname = 'vector';

-- pgvector 버전 확인
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

또는 psql 명령어로 확인:
```bash
psql -U your_username -d your_database -c "SELECT version();"
psql -U your_username -d your_database -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

---

## 프로젝트 구조

```
zip-fit-main/
├── back-end/              # Backend 서버 코드
│   └── zip_fit/          # FastAPI 애플리케이션
│       ├── main.py       # FastAPI 앱 진입점
│       ├── router.py     # API 라우터 및 세션 관리
│       ├── chatting.py   # RAG 챗봇 서비스 로직
│       ├── llm_handler.py # LLM 처리 (질문 재구성, 답변 생성)
│       ├── gongo.py      # 벡터 검색 및 DB 연동
│       ├── config.py     # 설정 파일
│       ├── dependencies.py # 의존성 주입 (모델 로딩)
│       ├── models.py     # Pydantic 모델 정의
│       └── info.py       # 통계 정보 제공
├── front-end/            # Frontend 클라이언트 코드
│   └── zf_front/        # Vue 3 애플리케이션
│       ├── src/
│       │   ├── views/    # 페이지 컴포넌트 (AiView, HomeView, ListView)
│       │   ├── components/ # 재사용 컴포넌트
│       │   ├── router/   # 라우팅 설정
│       │   └── stores/   # Pinia 상태 관리
│       └── package.json
├── crawler/              # 크롤러 코드
├── lab/                  # 팀원별 실험 및 개발 코드
│   ├── 김범섭/          # 시스템 아키텍처 설계, 프로젝트 총괄, 프론트엔드 개발
│   ├── 김종민/          # LLM 파이프라인 구성 (RAG, 임베딩, 청킹 등)
│   ├── 이상혁/          # 데이터 수집 및 크롤링, RAG 파이프라인 구성, 프롬프팅 설계
│   ├── 이인재/          # 백엔드 아키텍처 구성 및 데이터베이스 관리
│   └── 오흥재/          # 공공주택 용어집(Glossary) 구축 및 프로젝트 지원
└── docs/                 # 프로젝트 문서
    ├── 00_프로젝트_산출물.md
    ├── 01_수집된_데이터.md
    ├── 02_데이터_전처리_문서.md
    ├── 03_시스템_아키텍처.md
    ├── 04_개발된_소프트웨어.md
    ├── 05_DB_연동_구현_코드.md
    └── 06_테스트_계획_및_결과_보고서.md
```

---

## 라이선스

(추후 결정 예정)

---

## 참고 자료

### 공공 API
- [LH 공고 API](https://www.data.go.kr/data/15058530/openapi.do)
- [GH 공고 API](https://www.data.go.kr/data/15119414/fileData.do)

### 기술 문서
- [OpenAI API 문서](https://platform.openai.com/docs)
- [pgvector 문서](https://github.com/pgvector/pgvector)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Vue 3 문서](https://vuejs.org/)

### 프로젝트 문서
- [프로젝트 산출물](./docs/00_프로젝트_산출물.md)
- [수집된 데이터](./docs/01_수집된_데이터.md)
- [데이터 전처리 문서](./docs/02_데이터_전처리_문서.md)
- [시스템 아키텍처](./docs/03_시스템_아키텍처.md)
- [개발된 소프트웨어](./docs/04_개발된_소프트웨어.md)
- [DB 연동 구현 코드](./docs/05_DB_연동_구현_코드.md)
- [테스트 계획 및 결과 보고서](./docs/06_테스트_계획_및_결과_보고서.md)
- [진행 과정 중 프로그램 개선 노력](./docs/07_진행_과정_중_프로그램_개선_노력.md)
- [요구사항 명세서](./docs/08_요구사항_명세서.md)
