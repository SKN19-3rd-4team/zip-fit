from fastapi import FastAPI
from contextlib import asynccontextmanager

from .chatting import Chatting 
from . import router           
from .dependencies import set_chatting_service_instance 
from .llm_engine import LlmEngine
# 🌟 Gongo 임포트
from .gongo import Gongo 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🏃‍♂️ 1. Gongo 인스턴스 생성 (DB 연결 등 가장 먼저 초기화)
    gongo_instance = Gongo()
    # NOTE: 여기에 await gongo_instance.initialize_db_pool() 코드가 들어갑니다.
    
    # 🏃‍♂️ 2. LlmEngine 인스턴스를 만들 때 Gongo 인스턴스를 주입!
    llm_engine_instance = LlmEngine(gongo_service=gongo_instance) 
    
    # 🏃‍♂️ 3. Chatting 인스턴스를 만들 때 LlmEngine을 주입!
    chat_instance = Chatting(llm_engine=llm_engine_instance)
    
    # 🏃‍♂️ 4. dependencies에 Chatting 인스턴스를 저장
    set_chatting_service_instance(chat_instance)
    print("🚀 App Startup: All core services initialized and wired up!")
    
    yield # 앱 실행

    # 🛑 종료 시점: 정리 로직
    # NOTE: 여기에 await gongo_instance.close_db_pool() 코드가 들어갑니다.
    print("🛑 App Shutdown: Cleaning up.")


app = FastAPI(
    title="zip-fit Chatbot API",
    version="1.0.0",
    description="LLM을 활용한 zip-fit 챗봇 API 서비스",
    lifespan=lifespan 
)

# 🌟 라우터 등록: main.py의 유일한 역할 중 하나!
app.include_router(router.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "zip-fit API Service Running! Check /docs for endpoints."}