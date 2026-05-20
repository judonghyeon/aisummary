# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from database import init_db
from routers import video, result, status

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()       # 앱 시작 시 DB 테이블 생성
    yield

app = FastAPI(
    title="영상 요약 서비스",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 라우터 등록
app.include_router(video.router)    # 영상 입력 관련
app.include_router(status.router)   # 처리 상태 관련
app.include_router(result.router)   # 결과 페이지 관련