import yt_dlp
import os
import shutil
import base64
import tempfile

FFMPEG = shutil.which("ffmpeg") or "/snap/bin/ffmpeg"

def get_cookie_file():
    cookies_b64 = os.getenv("YOUTUBE_COOKIES", "")
    if not cookies_b64:
        return None
    try:
        cookies_data = base64.b64decode(cookies_b64).decode("utf-8")
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        tmp.write(cookies_data)
        tmp.close()
        return tmp.name
    except:
        return None

def download_audio(url: str, task_id: str) -> tuple[str, dict]:
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{task_id}.%(ext)s"
    cookie_file = get_cookie_file()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "ffmpeg_location": FFMPEG,
        # 자막 다운로드 실패해도 계속 진행
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["ko", "en"],
        "ignoreerrors": True,  # 자막 오류 무시
        "quiet": True,
    }

    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        chapters = info.get("chapters", []) if info else []

        subtitle_path = None
        for ext in ["ko.vtt", "en.vtt", "ko.srt", "en.srt"]:
            candidate = f"{output_dir}/{task_id}.{ext}"
            if os.path.exists(candidate):
                subtitle_path = candidate
                break

        meta = {
            "title":         info.get("title", "") if info else "",
            "thumbnail":     info.get("thumbnail", "") if info else "",
            "duration":      info.get("duration", 0) if info else 0,
            "chapters":      chapters,
            "subtitle_path": subtitle_path,
        }

    if cookie_file and os.path.exists(cookie_file):
        os.remove(cookie_file)

    audio_path = f"{output_dir}/{task_id}.mp3"
    return audio_path, meta
