# PDF 벡터화 엔진
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import pymupdf4llm
from sentence_transformers import SentenceTransformer

from config import PDF_BASE_PATH, EMBEDDING_MODEL, BATCH_SIZE, MAX_WORKERS
from chunking import SmartChunker
from database import DatabaseManager


class Vectorizer:
    """PDF 처리 및 벡터화 (병렬 처리)"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.chunker = SmartChunker()
        self.db = DatabaseManager()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    
    def find_pdf_file(self, file_name: str, category: str) -> Optional[Path]:
        """PDF 파일 찾기 (공고 or 공고문만, 팸플릿 제외)"""
        # 팸플릿 제외
        if '팸플릿' in file_name or '팜플렛' in file_name:
            return None

        # 공고 또는 공고문만 처리
        if '공고문' not in file_name and '공고' not in file_name:
            return None
        
        folder = 'LH_sale_서울.경기' if category == 'sale' else 'LH_lease_서울.경기'
        search_path = PDF_BASE_PATH / folder
        
        for pdf_path in search_path.rglob('*.pdf'):
            if pdf_path.name == file_name:
                return pdf_path
        return None
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """PDF에서 마크다운 추출"""
        return pymupdf4llm.to_markdown(str(pdf_path))
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩 생성"""
        embeddings = self.model.encode(
            texts, normalize_embeddings=True,
            show_progress_bar=False, batch_size=BATCH_SIZE
        )
        return [emb.tolist() for emb in embeddings]
    
    async def process_pdf(self, file_record: Dict[str, Any], announcement_category: str) -> Dict[str, Any]:
        """PDF 파일 처리"""
        file_id = file_record['id']
        file_name = file_record['file_name']
        announcement_id = file_record['announcement_id']
        
        pdf_path = self.find_pdf_file(file_name, announcement_category)
        
        if not pdf_path or not pdf_path.exists():
            return {'success': False, 'file_name': file_name, 'error': 'PDF not found'}
        
        try:
            loop = asyncio.get_event_loop()
            
            # PDF 텍스트 추출 (병렬 처리)
            md_text = await loop.run_in_executor(self.executor, self.extract_text_from_pdf, pdf_path)
            
            # 텍스트 청킹
            chunk_infos = self.chunker.chunk_markdown(md_text)
            
            if not chunk_infos:
                return {'success': False, 'file_name': file_name, 'error': 'No meaningful chunks'}
            
            # 배치 임베딩 생성
            enriched_texts = [chunk['enriched_text'] for chunk in chunk_infos]
            embeddings = await loop.run_in_executor(self.executor, self.create_embeddings_batch, enriched_texts)
            
            # DB 저장
            for idx, (chunk_info, embedding) in enumerate(zip(chunk_infos, embeddings)):
                metadata = {
                    'file_name': file_name,
                    'section': chunk_info['section'],
                    'has_table': chunk_info['has_table'],
                    'chunk_length': chunk_info['length']
                }
                
                await self.db.insert_chunk(
                    announcement_id=announcement_id,
                    file_id=file_id,
                    chunk_text=chunk_info['text'],
                    chunk_index=idx,
                    embedding=embedding,
                    metadata=metadata
                )
            
            await self.db.mark_file_vectorized(file_id)
            
            return {'success': True, 'file_name': file_name, 'chunks_count': len(chunk_infos)}
        
        except Exception as e:
            return {'success': False, 'file_name': file_name, 'error': str(e)}
    
    async def process_announcement(self, announcement: Dict[str, Any]) -> Dict[str, Any]:
        """공고의 모든 파일 처리"""
        announcement_id = announcement['id']
        category = announcement['category']
        
        files = await self.db.get_announcement_files(announcement_id)
        
        if not files:
            return {
                'success': True, 'announcement_id': announcement_id,
                'files_processed': 0, 'total_chunks': 0
            }
        
        results = []
        for file_record in files:
            result = await self.process_pdf(file_record, category)
            results.append(result)

        success_count = sum(1 for r in results if r['success'])
        total_chunks = sum(r.get('chunks_count', 0) for r in results if r['success'])

        # Always mark as vectorized after processing
        # This prevents infinite loops for announcements with no processable files
        await self.db.mark_announcement_vectorized(announcement_id)
        
        return {
            'success': success_count == len(files),
            'announcement_id': announcement_id,
            'title': announcement['title'],
            'files_processed': success_count,
            'total_files': len(files),
            'total_chunks': total_chunks,
            'results': results
        }
    
    async def vectorize_batch(self, limit: int = 10) -> List[Dict[str, Any]]:
        """배치 벡터화"""
        announcements = await self.db.get_unvectorized_announcements(limit)
        
        if not announcements:
            return []
        
        results = []
        for announcement in announcements:
            result = await self.process_announcement(announcement)
            results.append(result)
        
        return results
    
    async def vectorize_all(self, batch_size: int = 10):
        """전체 벡터화"""
        while True:
            results = await self.vectorize_batch(batch_size)
            if not results:
                break
            
            for result in results:
                if result['success']:
                    print(f"완료: {result['announcement_id']} "
                          f"({result['files_processed']}/{result['total_files']} 파일, "
                          f"{result['total_chunks']} 청크)")
                else:
                    print(f"부분: {result['announcement_id']} "
                          f"({result['files_processed']}/{result['total_files']} 파일)")
                    # Show errors for failed files
                    for file_result in result.get('results', []):
                        if not file_result['success']:
                            print(f"  실패: {file_result['file_name']} - {file_result.get('error', 'Unknown')}")
        
        progress = await self.db.get_vectorization_progress()
        return progress
    
    def close(self):
        """리소스 정리"""
        self.executor.shutdown(wait=True)
