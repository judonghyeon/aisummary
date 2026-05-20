from google import genai
from google.genai import types
import os, subprocess
from dotenv import load_dotenv

import shutil; FFMPEG = shutil.which("ffmpeg") or "/snap/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/snap/bin/ffmpeg.ffprobe"

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MAX_CHUNK_SEC = 10 * 60

def get_duration(audio_path: str) -> float:
    result = subprocess.run([
        FFPROBE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ], capture_output=True, text=True)
    return float(result.stdout.strip() or 0)

def split_audio(audio_path: str, chunk_dir: str) -> list:
    duration = get_duration(audio_path)
    chunk_paths = []
    start = 0
    i = 0
    while start < duration:
        chunk_path = f"{chunk_dir}/chunk_{i}.mp3"
        subprocess.run([
            FFMPEG, "-v", "error",
            "-ss", str(start),
            "-t", str(MAX_CHUNK_SEC),
            "-i", audio_path,
            "-acodec", "libmp3lame",
            "-y", chunk_path
        ], check=True)
        chunk_paths.append(chunk_path)
        start += MAX_CHUNK_SEC
        i += 1
    return chunk_paths

def transcribe(audio_path: str) -> str:
    chunk_dir = "temp_chunks"
    os.makedirs(chunk_dir, exist_ok=True)
    chunk_paths = split_audio(audio_path, chunk_dir)
    results = []
    for chunk_path in chunk_paths:
        with open(chunk_path, "rb") as f:
            audio_bytes = f.read()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3"),
                "이 오디오의 내용을 정확하게 텍스트로 변환해줘. 말한 내용만 출력하고 다른 설명은 하지 마."
            ]
        )
        results.append(response.text)
        os.remove(chunk_path)
    return " ".join(results)
