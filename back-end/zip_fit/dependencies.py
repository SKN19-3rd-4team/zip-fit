import os
from typing import Optional, Dict
from sentence_transformers import SentenceTransformer, CrossEncoder
from openai import AsyncOpenAI
from huggingface_hub import snapshot_download
import config


# 전역 변수
_embedding_model: Optional[SentenceTransformer] = None
_reranker_model: Optional[CrossEncoder] = None
_openai_client: Optional[AsyncOpenAI] = None

def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client

def load_models():
    """
    앱 시작 시 AI 모델을 로드합니다.
    지정된 폴더에 모델이 없으면 자동으로 다운로드합니다.
    """
    global _embedding_model, _reranker_model
    
    # 기본 저장 경로
    base_path = os.path.abspath(config.MODEL_CACHE_DIR)
    os.environ['HF_HOME'] = base_path # 안전장치
    
    print(f"\n[System] 모델 저장소 경로: {base_path}")
    

    # 1. 임베딩 모델 로드 (자동 다운로드 포함)
    if _embedding_model is None:
        print(f"[System] 임베딩 모델 확인 중... ({config.EMBEDDING_MODEL_NAME})")
        try:
            # SentenceTransformer는 cache_folder를 주면 알아서 다운로드하지만,
            # 명시적으로 경로를 지정합니다.
            _embedding_model = SentenceTransformer(
                config.EMBEDDING_MODEL_NAME, 
                cache_folder=base_path
            )
            print("[System] 임베딩 모델 준비 완료")
        except Exception as e:
            print(f"[Critical] 임베딩 모델 로딩 실패: {e}")
            raise e


    # 2. Reranker 모델 로드
    if config.USE_RERANKER:
        if _reranker_model is None:
            rerank_model_name = config.RERANKER_MODEL_NAME
            # 우리가 원하는 최종 경로: .../model_cache/ko-reranker
            local_rerank_path = os.path.join(base_path, "ko-reranker")
            
            print(f"[System] 2Reranker 모델 확인 중... ({rerank_model_name})")
            
            # 폴더가 비어있거나 없으면 -> 강제 다운로드 실행
            if not os.path.exists(local_rerank_path) or not os.listdir(local_rerank_path):
                print(f"[System] 모델 파일이 없습니다. 다운로드를 시작합니다... (대상: {local_rerank_path})")
                try:
                    snapshot_download(
                        repo_id=rerank_model_name,
                        local_dir=local_rerank_path,
                        local_dir_use_symlinks=False # 실제 파일로 저장
                    )
                    print("[System] 다운로드 완료!")
                except Exception as e:
                    print(f"[Error] 다운로드 실패: {e}")
            
            # 이제 파일이 있다고 확신하고 로드
            try:
                # 로컬 경로가 있으면 경로를, 다운로드 실패했으면 온라인 ID를 사용
                model_source = local_rerank_path if os.path.exists(local_rerank_path) else rerank_model_name
                
                print(f"[System] 모델을 메모리로 올리는 중... (Source: {model_source})")
                _reranker_model = CrossEncoder(
                    model_source, 
                    device='cpu'
                )
                print("[System] Reranker 모델 로딩 완료")
            except Exception as e:
                print(f"[Error] Reranker 모델 로딩 실패: {e}")
                print("[System] Reranker 기능이 비활성화됩니다.")
    else:
        print("[System] Reranker 로딩 건너뜀 (설정 OFF)")

    print("[System] 모든 시스템 준비 완료\n")

def get_embedding_model() -> SentenceTransformer:
    if _embedding_model is None: load_models()
    return _embedding_model

def get_reranker() -> Optional[CrossEncoder]:
    if not config.USE_RERANKER: return None
    if _reranker_model is None: load_models()
    return _reranker_model

def get_db_config() -> Dict:
    return config.DB_CONFIG