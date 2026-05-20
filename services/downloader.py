import yt_dlp
import os

FFMPEG = "/snap/bin/ffmpeg"

def download_audio(url, task_id):
    task_dir = os.path.join("downloads", task_id)
    os.makedirs(task_dir, exist_ok=True)

    base_opts = {
        "ffmpeg_location": FFMPEG,
        "cookiefile": "cookies.txt",
        "sleep_interval": 2,
        "max_sleep_interval": 5,
        "retries": 3,
        "fragment_retries": 3,
        "quiet": True,
        "no_warnings": True,
    }

    # 🔥 메타 (fallback 포함)
    info = None
    try:
        with yt_dlp.YoutubeDL({**base_opts, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except:
        pass

    if not info:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

    if not info:
        raise Exception("영상 정보 추출 실패")

    title = info.get("title", "Unknown")
    thumbnail = info.get("thumbnail", "")
    duration = info.get("duration", 0)
    chapters = info.get("chapters", [])
    video_id = info.get("id")

    # 🔥 자막 완전 제거 (429 방지 핵심)
    subtitle_path = None

    # 🔥 오디오
    with yt_dlp.YoutubeDL({
        **base_opts,
        "format": "bestaudio/best",
        "outtmpl": os.path.join(task_dir, f"{video_id}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
    }) as ydl:
        ydl.download([url])

    audio_path = os.path.join(task_dir, f"{video_id}.mp3")

    if not os.path.exists(audio_path):
        raise Exception("오디오 다운로드 실패")

    return audio_path, {
        "title": title,
        "thumbnail": thumbnail,
        "duration": duration,
        "chapters": chapters,
        "subtitle_path": None,
    }