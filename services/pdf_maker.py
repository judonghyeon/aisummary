import pdfkit
import os

def make_pdf(task_id: str, title: str, result: dict, script: str) -> str:
    output_dir = "pdfs"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = f"{output_dir}/{task_id}.pdf"

    chapters_html = ""
    for ch in result.get("chapters", []):
        chapters_html += f"""
        <div class="chapter">
            <span class="time">{ch['start_time']}</span>
            <div>
                <div class="chapter-title">{ch['title']}</div>
                <div class="chapter-summary">{ch['summary']}</div>
            </div>
        </div>
        """

    keywords_html = "".join(
        f'<span class="keyword">{kw}</span>'
        for kw in result.get("keywords", [])
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8">
    <style>
        @font-face {{
            font-family: 'NanumGothic';
            src: local('NanumGothic');
        }}
        body {{ font-family: 'NanumGothic', 'Malgun Gothic', sans-serif;
                padding: 40px; color: #1A1A2E; }}
        h1 {{ font-size: 22px; margin-bottom: 8px; }}
        .meta {{ color: #94A3B8; font-size: 13px; margin-bottom: 32px; }}
        .section-title {{ font-size: 11px; font-weight: bold; color: #94A3B8;
                          letter-spacing: 2px; text-transform: uppercase;
                          margin-bottom: 10px; }}
        .summary {{ background: #F8FAFC; border-radius: 8px; padding: 16px;
                    font-size: 14px; line-height: 1.8; margin-bottom: 28px; }}
        .keywords {{ margin-bottom: 28px; }}
        .keyword {{ display: inline-block; background: #EFF6FF; color: #3B82F6;
                    padding: 4px 12px; border-radius: 20px; font-size: 12px;
                    margin: 3px; }}
        .chapter {{ display: flex; gap: 14px; margin-bottom: 14px;
                    background: #F8FAFC; border-radius: 8px; padding: 14px; }}
        .time {{ color: #3B82F6; font-weight: bold; font-size: 12px;
                 background: #EFF6FF; padding: 3px 8px; border-radius: 6px;
                 white-space: nowrap; }}
        .chapter-title {{ font-size: 14px; font-weight: bold; margin-bottom: 4px; }}
        .chapter-summary {{ font-size: 13px; color: #475569; line-height: 1.6; }}
        .script {{ background: #F8FAFC; border-radius: 8px; padding: 16px;
                   font-size: 12px; line-height: 1.8; color: #64748B; }}
        .divider {{ height: 1px; background: #E2E8F0; margin: 24px 0; }}
    </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="meta">영상 요약 서비스 · 자동 생성 문서</div>

        <div class="section-title">전체 요약</div>
        <div class="summary">{result['summary']}</div>

        <div class="section-title">키워드</div>
        <div class="keywords">{keywords_html}</div>

        <div class="divider"></div>

        <div class="section-title">챕터별 요약</div>
        {chapters_html}

        <div class="divider"></div>

        <div class="section-title">원본 스크립트</div>
        <div class="script">{script}</div>
    </body>
    </html>
    """

    config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
    options = {
        "encoding": "UTF-8",
        "enable-local-file-access": "",
        "quiet": "",
    }
    pdfkit.from_string(html, pdf_path, configuration=config, options=options)
    return pdf_path
