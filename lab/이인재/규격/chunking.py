# 텍스트 청킹 (문맥 보존)
import re
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import MIN_CHUNK_SIZE, OPTIMAL_CHUNK_SIZE, MAX_CHUNK_SIZE, MAX_TABLE_SIZE, CHUNK_OVERLAP


class SmartChunker:
    """문맥 보존 텍스트 청킹"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=OPTIMAL_CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def chunk_markdown(self, md_text: str) -> List[Dict[str, Any]]:
        """마크다운 텍스트 청킹"""
        blocks = re.split(r'\n\n+', md_text)
        chunks = []
        current_chunk = []
        current_length = 0
        current_section = None
        previous_context = ""
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            # 섹션 헤더 감지
            section = self._extract_section_name(block)
            if section:
                current_section = section
            
            # 테이블 처리
            if self._is_table(block):
                if current_chunk:
                    chunk_info = self._create_chunk('\n\n'.join(current_chunk), current_section, False, previous_context)
                    if chunk_info:
                        chunks.append(chunk_info)
                        previous_context = self._get_context(chunk_info['text'])
                    current_chunk = []
                    current_length = 0
                
                # 큰 테이블 분할
                if len(block) > MAX_TABLE_SIZE:
                    table_chunks = self._split_table(block)
                    for tc in table_chunks:
                        chunk_info = self._create_chunk(tc, current_section, True, previous_context)
                        if chunk_info:
                            chunks.append(chunk_info)
                            previous_context = self._get_context(tc)
                else:
                    chunk_info = self._create_chunk(block, current_section, True, previous_context)
                    if chunk_info:
                        chunks.append(chunk_info)
                        previous_context = self._get_context(block)
            
            # 일반 텍스트 처리
            else:
                block_length = len(block)
                
                if current_length + block_length > OPTIMAL_CHUNK_SIZE and current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunk_info = self._create_chunk(chunk_text, current_section, False, previous_context)
                    if chunk_info:
                        chunks.append(chunk_info)
                        previous_context = self._get_context(chunk_text)
                    current_chunk = [block]
                    current_length = block_length
                
                elif current_length + block_length > MAX_CHUNK_SIZE:
                    if current_chunk:
                        chunk_text = '\n\n'.join(current_chunk)
                        chunk_info = self._create_chunk(chunk_text, current_section, False, previous_context)
                        if chunk_info:
                            chunks.append(chunk_info)
                            previous_context = self._get_context(chunk_text)
                    
                    if block_length > MAX_CHUNK_SIZE:
                        split_chunks = self.text_splitter.split_text(block)
                        for sc in split_chunks:
                            chunk_info = self._create_chunk(sc, current_section, False, previous_context)
                            if chunk_info:
                                chunks.append(chunk_info)
                                previous_context = self._get_context(sc)
                    else:
                        current_chunk = [block]
                        current_length = block_length
                
                else:
                    current_chunk.append(block)
                    current_length += block_length
        
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunk_info = self._create_chunk(chunk_text, current_section, False, previous_context)
            if chunk_info:
                chunks.append(chunk_info)
        
        return chunks
    
    def _create_chunk(self, text: str, section: str, has_table: bool, context: str) -> Dict[str, Any]:
        """청크 생성"""
        if not self._is_meaningful(text):
            return None
        
        enriched_text = f"[{section}]\n{text}" if context and section else text
        
        return {
            'text': text,
            'enriched_text': enriched_text,
            'section': section,
            'has_table': has_table,
            'length': len(text)
        }
    
    def _get_context(self, text: str, max_length: int = 100) -> str:
        """컨텍스트 추출"""
        return text[:max_length] if len(text) > max_length else text
    
    def _extract_section_name(self, text_chunk: str) -> str:
        """섹션 이름 추출"""
        patterns = [
            r'^\s*#+\s*(.+)',
            r'^\s*【(.+?)】',
            r'^\s*\*\*(.+?)\*\*',
            r'^\s*■\s*(.+)',
            r'^\s*[0-9]+\.\s*(.+)',
        ]
        for line in text_chunk.split('\n')[:3]:
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    section_title = match.group(1).strip()
                    if len(section_title) > 5:
                        return section_title
        return None
    
    def _is_table(self, text_chunk: str) -> bool:
        """테이블 여부 확인"""
        lines = text_chunk.split('\n')
        pipe_lines = [line for line in lines if '|' in line]
        return len(pipe_lines) >= 3 and len(pipe_lines) / len(lines) > 0.5
    
    def _is_meaningful(self, text_chunk: str) -> bool:
        """의미 있는 청크인지 확인"""
        content = text_chunk.strip()
        
        if len(content) < MIN_CHUNK_SIZE:
            return False
        
        if re.match(r'^[-\s\|\d\.]+$', content):
            return False
        
        if self._is_table(content):
            lines = [line for line in content.split('\n') if line.strip()]
            if len(lines) <= 3:
                return False
        
        words = re.findall(r'[가-힣a-zA-Z]{2,}', content)
        if len(words) < 5:
            return False
        
        return True
    
    def _split_table(self, table_text: str, max_size: int = MAX_TABLE_SIZE) -> List[str]:
        """큰 테이블 분할 (헤더 유지)"""
        lines = table_text.split('\n')
        header_lines = []
        data_lines = []
        
        for i, line in enumerate(lines):
            if '|' not in line:
                continue
            if i < 3 or '---' in line:
                header_lines.append(line)
            else:
                data_lines.append(line)
        
        if not data_lines:
            return [table_text] if len(table_text) < max_size else []
        
        header_text = '\n'.join(header_lines)
        header_size = len(header_text)
        
        chunks = []
        current_rows = []
        current_size = header_size
        
        for row in data_lines:
            row_size = len(row) + 1
            
            if current_size + row_size > max_size and current_rows:
                chunk = header_text + '\n' + '\n'.join(current_rows)
                chunks.append(chunk)
                current_rows = [row]
                current_size = header_size + row_size
            else:
                current_rows.append(row)
                current_size += row_size
        
        if current_rows:
            chunk = header_text + '\n' + '\n'.join(current_rows)
            chunks.append(chunk)
        
        return chunks
