from .chatting import Chatting
from typing import Optional

# 전역 변수를 사용하기 위해 인스턴스 변수를 정의합니다.
_CHAT_SERVICE_INSTANCE: Optional[Chatting] = None

def set_chatting_service_instance(instance: Chatting):
    """
    main.py의 lifespan에서 생성된 Chatting 인스턴스를 저장합니다.
    """
    global _CHAT_SERVICE_INSTANCE
    _CHAT_SERVICE_INSTANCE = instance
    print("Dependencies: Chatting 인스턴스가 주입 준비 완료되었습니다.")

def get_chatting_service() -> Chatting:
    """
    라우터 함수에서 의존성 주입(Depends)을 통해 사용될 함수입니다.
    """
    if _CHAT_SERVICE_INSTANCE is None:
        raise Exception("Chatting Service가 초기화되지 않았습니다. main.py의 lifespan을 확인하세요.")
    return _CHAT_SERVICE_INSTANCE