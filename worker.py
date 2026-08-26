from celery_app import celery
from database import get_db
from services.downloader import download_audio
from services.transcriber import transcribe
from services.summarizer import (
    summarize,
    summarize_with_youtube_chapters,
    summarize_with_subtitles,
    translate_to_korean
)
from services.subtitle_parser import parse_subtitle, subtitle_to_script
from services.pdf_maker import make_pdf
import json, os, subprocess

def update_task(task_id: str, status: str, progress: str):
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET status=?, progress=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (status, progress, task_id)
    )
    conn.commit()
    conn.close()

@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 2})
def process_video(self, task_id: str, url: str = None, file_path: str = None, summary_length: str = "normal"):
    try:
        # =========================================
        # 다운로드
        # =========================================
        update_task(task_id, "PROCESSING", "오디오 추출 중")

        if url:
            audio_path, meta = download_audio(url, task_id)

            # meta None 방어
            if not meta:
                raise Exception("영상 메타데이터 수집 실패")
        else:
            audio_path = f"downloads/{task_id}.mp3"
            os.makedirs("downloads", exist_ok=True)

            subprocess.run([
                "/snap/bin/ffmpeg", "-i", file_path,
                "-acodec", "libmp3lame", "-y", audio_path
            ], check=True)

            meta = {
                "title": os.path.basename(file_path),
                "thumbnail": "",
                "duration": 0,
                "chapters": [],
                "subtitle_path": None
            }

        # meta 안전 접근
        title = meta.get("title", "Unknown")
        thumbnail = meta.get("thumbnail", "")
        duration = meta.get("duration", 0)
        yt_chapters = meta.get("chapters", []) or []
        subtitle_path = meta.get("subtitle_path")

        # =========================================
        # 스크립트 생성
        # =========================================
        script = ""
        subtitle_entries = []

        if subtitle_path and os.path.exists(subtitle_path):
            try:
                update_task(task_id, "PROCESSING", "자막 파싱 중")
                subtitle_entries = parse_subtitle(subtitle_path)
                script = subtitle_to_script(subtitle_entries)
            except Exception:
                subtitle_entries = []
                script = ""

        # 자막 실패 or 없음 → STT
        if not script:
            update_task(task_id, "PROCESSING", "STT 변환 중")
            script = transcribe(audio_path)

        # STT 실패 방어
        if not script or len(script.strip()) < 10:
            raise Exception("스크립트 생성 실패")

        # =========================================
        # 요약
        # =========================================
        try:
            if yt_chapters:
                update_task(task_id, "PROCESSING", "AI 요약 중 (YouTube 챕터 기반)")
                result = summarize_with_youtube_chapters(script, yt_chapters, summary_length)

            elif subtitle_entries:
                update_task(task_id, "PROCESSING", "AI 요약 중 (자막 기반)")
                result = summarize_with_subtitles(subtitle_entries, summary_length)

            else:
                update_task(task_id, "PROCESSING", "AI 요약 중 (AI 추정)")
                result = summarize(script, summary_length)

        except Exception:
            # 요약 실패 fallback
            result = summarize(script, summary_length)

        # =========================================
        # 번역
        # =========================================
        try:
            if result.get("language") != "한국어":
                update_task(task_id, "PROCESSING", "한국어로 번역 중")
                result = translate_to_korean(result)
        except Exception:
            pass  # 번역 실패해도 계속 진행

        # =========================================
        # PDF
        # =========================================
        update_task(task_id, "PROCESSING", "PDF 생성 중")
        pdf_path = make_pdf(task_id, title, result, script)

        # =========================================
        # 저장
        # =========================================
        conn = get_db()
        conn.execute("""
            INSERT INTO results
            (task_id, video_url, video_title, thumbnail_url, duration,
             full_script, summary, chapters, keywords, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            url or file_path,
            title,
            thumbnail,
            duration,
            script,
            result.get("summary", ""),
            json.dumps(result.get("chapters", []), ensure_ascii=False),
            json.dumps(result.get("keywords", []), ensure_ascii=False),
            pdf_path
        ))
        conn.commit()
        conn.close()

        update_task(task_id, "DONE", "완료")

    except Exception as e:
        update_task(task_id, "FAILED", f"오류: {str(e)}")
        raise
