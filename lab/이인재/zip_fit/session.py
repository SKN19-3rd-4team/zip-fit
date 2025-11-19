import json
import os
from threading import Lock
from typing import Any, Dict, Optional

# 세션 데이터가 저장될 로컬 파일 경로
SESSION_FILE = "sessions.json"

# 여러 요청이 동시에 파일을 쓰려고 할 때 파일이 깨지는 것을 방지하는 잠금 장치
_file_lock = Lock()

def _load_json() -> Dict[str, Any]:
    """
    내부 함수: JSON 파일을 읽어서 파이썬 딕셔너리로 반환합니다.
    파일이 없거나 깨져있으면 빈 딕셔너리를 반환합니다.
    """
    if not os.path.exists(SESSION_FILE):
        return {}
    try:
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_json(data: Dict[str, Any]) -> None:
    """
    내부 함수: 파이썬 딕셔너리를 JSON 파일로 저장합니다.
    ensure_ascii=False 옵션으로 한글이 깨지지 않게 저장합니다.
    """
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_session(session_name: str, variable: str = None) -> Any:
    """
    세션명(User ID 등)과 변수명(키)을 받아 저장된 값을 반환합니다.
    
    Args:
        session_name (str): 세션 식별자 (예: 'messages_userid_1')
        variable (str): 가져올 데이터의 키 (예: 'conversation'). None이면 세션 통째로 반환.
    
    Returns:
        Any: 저장된 값 또는 None
    """
    with _file_lock:
        data = _load_json()
        
        # 세션 자체가 없으면 None 반환
        if session_name not in data:
            return None
            
        # 변수명이 지정되었으면 해당 값만, 아니면 전체 세션 데이터 반환
        if variable:
            return data[session_name].get(variable)
        else:
            return data[session_name]

def set_session(session_name: str, variable: str, value: Any) -> None:
    """
    세션명과 변수명을 지정하여 값을 저장합니다.
    
    Args:
        session_name (str): 세션 식별자
        variable (str): 저장할 데이터의 키
        value (Any): 저장할 값 (List, Dict, Str 등)
    """
    with _file_lock:
        data = _load_json()
        
        # 해당 세션이 없으면 빈 딕셔너리로 초기화
        if session_name not in data:
            data[session_name] = {}
            
        # 값 업데이트
        data[session_name][variable] = value
        
        _save_json(data)

def clear_session(session_name: str) -> None:
    """
    특정 세션 데이터를 완전히 삭제합니다.
    (대화 초기화 등에 사용)
    """
    with _file_lock:
        data = _load_json()
        
        if session_name in data:
            del data[session_name]
            _save_json(data)
            print(f"🧹 Session cleared: {session_name}")