from celery_app import celery
from database import get_db, query
from services.downloader import download_audio
from services.transcriber import transcribe
from services.subtitle_parser import parse_subtitle, subtitle_to_script
from services.summarizer import (
    summarize,
    summarize_with_youtube_chapters,
    summarize_with_subtitles,
    translate_to_korean
)
from services.pdf_maker import make_pdf
import json, os

def update_task(task_id, status, progress):
    conn = get_db()
    query(conn,
        "UPDATE tasks SET status=%s, progress=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s",
        (status, progress, task_id)
    )
    conn.commit()
    conn.close()

@celery.task(name="tasks.download")
def download_task(task_id, url):
    try:
        update_task(task_id, "PROCESSING", "오디오 추출 중")
        audio_path, meta = download_audio(url, task_id)
        meta["video_url"] = url
        celery.send_task("tasks.transcribe", args=[task_id, audio_path, meta])
    except Exception as e:
        update_task(task_id, "FAILED", f"다운로드 실패: {str(e)}")
        raise

@celery.task(name="tasks.transcribe")
def transcribe_task(task_id, audio_path, meta):
    try:
        subtitle_entries = []
        script = ""

        # 자막 있으면 자막 사용, 없으면 STT
        if meta.get("subtitle_path"):
            update_task(task_id, "PROCESSING", "자막 파싱 중")
            subtitle_entries = parse_subtitle(meta["subtitle_path"])
            script = subtitle_to_script(subtitle_entries)
        
        # STT 항상 실행 (자막 없을 때)
        if not script or len(script.strip()) < 10:
            update_task(task_id, "PROCESSING", "STT 변환 중")
            script = transcribe(audio_path)

        if not script or len(script.strip()) < 10:
            raise Exception("스크립트 생성 실패")

        celery.send_task("tasks.summarize", args=[task_id, script, meta, subtitle_entries])
    except Exception as e:
        update_task(task_id, "FAILED", f"STT 실패: {str(e)}")
        raise

@celery.task(name="tasks.summarize")
def summarize_task(task_id, script, meta, subtitle_entries=[]):
    try:
        update_task(task_id, "PROCESSING", "AI 요약 중")
        yt_chapters = meta.get("chapters", [])

        if yt_chapters:
            result = summarize_with_youtube_chapters(script, yt_chapters)
        elif subtitle_entries:
            result = summarize_with_subtitles(subtitle_entries)
        else:
            result = summarize(script)

        if result.get("language") != "한국어":
            update_task(task_id, "PROCESSING", "번역 중")
            result = translate_to_korean(result)

        update_task(task_id, "PROCESSING", "PDF 생성 중")
        pdf_path = make_pdf(task_id, meta.get("title"), result, script)

        conn = get_db()
        query(conn, """
            INSERT INTO results
            (task_id, video_url, video_title, thumbnail_url, duration,
             full_script, summary, chapters, keywords, pdf_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            task_id,
            meta.get("video_url"),
            meta.get("title"),
            meta.get("thumbnail"),
            meta.get("duration"),
            script,
            result.get("summary"),
            json.dumps(result.get("chapters", []), ensure_ascii=False),
            json.dumps(result.get("keywords", []), ensure_ascii=False),
            pdf_path
        ))
        conn.commit()
        conn.close()
        update_task(task_id, "DONE", "완료")

    except Exception as e:
        update_task(task_id, "FAILED", f"요약 실패: {str(e)}")
        raise
