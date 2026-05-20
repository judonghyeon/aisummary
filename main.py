from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from database import init_db
from routers import video, result, status
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 필요한 폴더 자동 생성
    for folder in ["static", "uploads", "downloads", "pdfs", "markdowns", "temp_chunks"]:
        os.makedirs(folder, exist_ok=True)
    init_db()
    yield

app = FastAPI(title="영상 요약 서비스", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(video.router)
app.include_router(status.router)
app.include_router(result.router)
