from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid, shutil, os
import yt_dlp

from database import get_db
from celery_app import celery   # 🔥 핵심

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# =========================================
def estimate_time(url: str) -> str:
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
            estimated = max(1, int(duration / 60 * 0.5))
            return f"약 {estimated}분 소요 예정"
    except:
        return "처리 시간 계산 중..."


# =========================================
@router.get("/")
async def index(request: Request):
    conn = get_db()
    recent = conn.execute("""
        SELECT t.id, r.video_title, r.thumbnail_url, t.created_at
        FROM tasks t
        LEFT JOIN results r ON t.id = r.task_id
        WHERE t.status = 'DONE'
        ORDER BY t.created_at DESC
        LIMIT 5
    """).fetchall()
    conn.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "recent": [dict(r) for r in recent]
    })


# =========================================
# 🔥 URL 입력
# =========================================
@router.post("/submit/url")
async def submit_url(url: str = Form(...), summary_length: str = Form("normal")):
    if not url.startswith("http"):
        return RedirectResponse("/?error=invalid_url", status_code=303)

    task_id = str(uuid.uuid4())
    estimated_time = estimate_time(url)

    conn = get_db()
    conn.execute(
        "INSERT INTO tasks (id, status, progress, video_url, summary_length, estimated_time) VALUES (?, ?, ?, ?, ?, ?)",
        (task_id, "PENDING", "대기 중", url, summary_length, estimated_time)
    )
    conn.commit()
    conn.close()

    # 🔥 Celery 시작 (정석 방식)
    celery.send_task("tasks.download", args=[task_id, url])

    return RedirectResponse(f"/status/{task_id}", status_code=303)


# =========================================
# 🔥 파일 업로드
# =========================================
@router.post("/submit/file")
async def submit_file(file: UploadFile = File(...), summary_length: str = Form("normal")):
    if not file.filename.endswith(".mp4"):
        return RedirectResponse("/?error=invalid_file", status_code=303)

    task_id = str(uuid.uuid4())

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{task_id}.mp4"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    conn = get_db()
    conn.execute(
        "INSERT INTO tasks (id, status, progress, video_url, summary_length, estimated_time) VALUES (?, ?, ?, ?, ?, ?)",
        (task_id, "PENDING", "대기 중", file.filename, summary_length, "파일 처리 중")
    )
    conn.commit()
    conn.close()

    # 🔥 파일은 download_task가 아니라 바로 STT로 넘김
    celery.send_task("tasks.transcribe", args=[task_id, file_path, {
        "title": file.filename,
        "thumbnail": "",
        "duration": 0,
        "chapters": [],
        "video_url": file.filename
    }])

    return RedirectResponse(f"/status/{task_id}", status_code=303)