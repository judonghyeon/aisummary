import re

def seconds_to_timestamp(seconds: float) -> str:
    """초를 MM:SS 형식으로 변환"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def parse_vtt(path: str) -> list:
    """VTT 자막 파일 파싱 → [{time, text}] 반환"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    # VTT 타임스탬프 패턴: 00:00:00.000 --> 00:00:00.000
    pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d+)\s*-->\s*[\d:.]+\n(.*?)(?=\n\n|\Z)",
        re.DOTALL
    )

    for match in pattern.finditer(content):
        time_str = match.group(1)  # 00:00:05.000
        text = match.group(2).strip()
        text = re.sub(r"<[^>]+>", "", text)  # HTML 태그 제거
        if text:
            # HH:MM:SS.ms → 초로 변환
            h, m, s = time_str.split(":")
            total_seconds = int(h) * 3600 + int(m) * 60 + float(s)
            entries.append({
                "seconds": total_seconds,
                "time":    seconds_to_timestamp(total_seconds),
                "text":    text
            })

    return entries

def parse_srt(path: str) -> list:
    """SRT 자막 파일 파싱 → [{time, text}] 반환"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    pattern = re.compile(
        r"\d+\n(\d{2}:\d{2}:\d{2}),\d+ --> [\d:,]+\n(.*?)(?=\n\n|\Z)",
        re.DOTALL
    )

    for match in pattern.finditer(content):
        time_str = match.group(1)  # 00:00:05
        text = match.group(2).strip()
        if text:
            h, m, s = time_str.split(":")
            total_seconds = int(h) * 3600 + int(m) * 60 + int(s)
            entries.append({
                "seconds": total_seconds,
                "time":    seconds_to_timestamp(total_seconds),
                "text":    text
            })

    return entries

def parse_subtitle(path: str) -> list:
    """자막 파일 자동 감지 후 파싱"""
    if path.endswith(".vtt"):
        return parse_vtt(path)
    elif path.endswith(".srt"):
        return parse_srt(path)
    return []

def subtitle_to_script(entries: list) -> str:
    """자막 엔트리 → 전체 스크립트 텍스트"""
    return " ".join([e["text"] for e in entries])
