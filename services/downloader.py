import yt_dlp
import os
import shutil

# 환경에 따라 ffmpeg 경로 자동 감지
FFMPEG = shutil.which("ffmpeg") or "/snap/bin/ffmpeg"

def download_audio(url: str, task_id: str) -> tuple[str, dict]:
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{task_id}.%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "ffmpeg_location": FFMPEG,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["ko", "en"],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        chapters = info.get("chapters", [])

        subtitle_path = None
        for ext in ["ko.vtt", "en.vtt", "ko.srt", "en.srt"]:
            candidate = f"{output_dir}/{task_id}.{ext}"
            if os.path.exists(candidate):
                subtitle_path = candidate
                break

        meta = {
            "title":         info.get("title", ""),
            "thumbnail":     info.get("thumbnail", ""),
            "duration":      info.get("duration", 0),
            "chapters":      chapters,
            "subtitle_path": subtitle_path,
        }

    audio_path = f"{output_dir}/{task_id}.mp3"
    return audio_path, meta
