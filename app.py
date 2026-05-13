import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from config import UPLOAD_DIR
from routes import router
from engine import rag_engine 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print("[시스템] 서버 가동을 감지했습니다. 초기 문서 인덱싱을 시작합니다.")
    try:
        rag_engine.setup_engine()
        print("[시스템] 초기 문서 로드 완료! 챗봇이 준비되었습니다.")
    except Exception as e:
        print(f"[시스템] 서버 시작 중 문서 로드 오류 발생: {e}")
    print("="*60 + "\n")
    
    yield
    
    print("\n[시스템] 서버를 종료합니다.")
    pass

def create_app():
    app = FastAPI(
        title="AI PDF Analyzer",
        description="PDF 분석 및 RAG 기반 대화 시스템",
        lifespan=lifespan
    )
    
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/pdf_files", StaticFiles(directory=UPLOAD_DIR), name="pdf_files")
    
    app.include_router(router)
    
    return app

app = create_app()