import os

def make_markdown(task_id: str, title: str, result: dict, script: str) -> str:
    output_dir = "markdowns"
    os.makedirs(output_dir, exist_ok=True)
    md_path = f"{output_dir}/{task_id}.md"

    chapters_md = ""
    for ch in result.get("chapters", []):
        chapters_md += f"### {ch['start_time']} — {ch['title']}\n{ch['summary']}\n\n"

    keywords_md = " ".join([f"`{kw}`" for kw in result.get("keywords", [])])

    content = f"""# {title}

> 영상 요약 서비스 · 자동 생성 문서

## 전체 요약
{result['summary']}

## 키워드
{keywords_md}

---

## 챕터별 요약
{chapters_md}
---

## 원본 스크립트
{script}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    return md_path
