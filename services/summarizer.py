from google import genai
import os, json
from dotenv import load_dotenv

load_dotenv('/mnt/c/Users/jujdh/OneDrive/바탕 화면/캡스톤/.env')
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def seconds_to_timestamp(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def summarize_with_youtube_chapters(script: str, yt_chapters: list, length: str = "normal") -> dict:
    """1순위: YouTube 챕터 정보 기반 요약"""
    length_prompt = {
        "short":  "1~2문장으로 아주 짧게 요약",
        "normal": "3~5문장으로 요약",
        "detail": "7~10문장으로 상세하게 요약"
    }
    summary_guide = length_prompt.get(length, length_prompt["normal"])

    chapters_info = "\n".join([
        f"- {seconds_to_timestamp(ch['start_time'])} ~ {seconds_to_timestamp(ch['end_time'])}: {ch['title']}"
        for ch in yt_chapters
    ])

    prompt = f"""
다음은 영상의 전체 스크립트와 YouTube에서 제공하는 정확한 챕터 정보야.

[챕터 정보 - 정확한 타임스탬프]
{chapters_info}

[전체 스크립트]
{script}

챕터 정보의 타임스탬프를 그대로 사용해서 아래 JSON만 출력해줘:

{{
  "summary": "{summary_guide}",
  "chapters": [
    {{
      "title": "챕터 제목 (위 챕터 정보의 제목 사용)",
      "start_time": "MM:SS (위 챕터 정보의 정확한 시작 시간 사용)",
      "summary": "해당 챕터 내용 1~2문장 요약"
    }}
  ],
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
  "language": "영상의 언어 (한국어/영어/기타)",
  "timestamp_source": "youtube_chapters"
}}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return _parse_json(response.text)

def summarize_with_subtitles(subtitle_entries: list, length: str = "normal") -> dict:
    """2순위: 자막 기반 타임스탬프 요약"""
    length_prompt = {
        "short":  "1~2문장으로 아주 짧게 요약",
        "normal": "3~5문장으로 요약",
        "detail": "7~10문장으로 상세하게 요약"
    }
    summary_guide = length_prompt.get(length, length_prompt["normal"])

    # 자막을 30초 단위로 묶어서 전달
    grouped = []
    current_group = []
    current_start = 0

    for entry in subtitle_entries:
        if not current_group:
            current_start = entry["seconds"]
        current_group.append(entry["text"])

        if entry["seconds"] - current_start >= 30:
            grouped.append({
                "time": seconds_to_timestamp(current_start),
                "text": " ".join(current_group)
            })
            current_group = []

    if current_group:
        grouped.append({
            "time": seconds_to_timestamp(current_start),
            "text": " ".join(current_group)
        })

    subtitle_text = "\n".join([f"[{g['time']}] {g['text']}" for g in grouped])

    prompt = f"""
다음은 타임스탬프가 포함된 영상 자막이야. 각 줄의 [MM:SS]가 정확한 시작 시간이야.

[타임스탬프 자막]
{subtitle_text}

자막의 정확한 타임스탬프를 사용해서 아래 JSON만 출력해줘:

{{
  "summary": "{summary_guide}",
  "chapters": [
    {{
      "title": "챕터 제목",
      "start_time": "MM:SS (자막에서 해당 내용이 시작되는 정확한 시간)",
      "summary": "해당 챕터 내용 1~2문장 요약"
    }}
  ],
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
  "language": "영상의 언어 (한국어/영어/기타)",
  "timestamp_source": "subtitles"
}}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return _parse_json(response.text)

def summarize(script: str, length: str = "normal") -> dict:
    """3순위: AI 추정 타임스탬프 요약"""
    length_prompt = {
        "short":  "1~2문장으로 아주 짧게 요약",
        "normal": "3~5문장으로 요약",
        "detail": "7~10문장으로 상세하게 요약"
    }
    summary_guide = length_prompt.get(length, length_prompt["normal"])

    prompt = f"""
다음은 영상 강의의 전체 스크립트야.

[스크립트]
{script}

아래 형식의 JSON만 출력해줘:

{{
  "summary": "{summary_guide}",
  "chapters": [
    {{
      "title": "챕터 제목",
      "start_time": "MM:SS (내용 흐름상 추정한 시작 시간)",
      "summary": "이 챕터의 핵심 내용 1~2문장"
    }}
  ],
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
  "language": "영상의 언어 (한국어/영어/기타)",
  "timestamp_source": "ai_estimated"
}}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return _parse_json(response.text)

def translate_to_korean(result: dict) -> dict:
    if result.get("language") == "한국어":
        return result
    prompt = f"""
아래 JSON의 summary, chapters의 title과 summary, keywords를 한국어로 번역해줘.
JSON 형식 그대로 유지하고 번역된 JSON만 출력해줘:

{json.dumps(result, ensure_ascii=False)}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return _parse_json(response.text)

def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
