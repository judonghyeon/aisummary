from fastapi import APIRouter, Request, Form
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db, query
from services.md_maker import make_markdown
from services.summarizer import summarize
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/result/{task_id}")
async def result_page(request: Request, task_id: str):
    conn = get_db()
    cur = query(conn, "SELECT * FROM results WHERE task_id = %s", (task_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return RedirectResponse(f"/status/{task_id}")

    result = dict(result)
    result["chapters"] = json.loads(result["chapters"] or "[]")
    result["keywords"] = json.loads(result["keywords"] or "[]")

    return templates.TemplateResponse(
        "result.html",
        {"request": request, "result": result}
    )

@router.get("/result/{task_id}/pdf")
async def download_pdf(task_id: str):
    conn = get_db()
    cur = query(conn, "SELECT pdf_path, video_title FROM results WHERE task_id = %s", (task_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result or not result["pdf_path"]:
        return {"error": "PDF가 없습니다"}

    filename = f"{result['video_title'] or task_id}_요약.pdf"
    return FileResponse(path=result["pdf_path"], media_type="application/pdf", filename=filename)

@router.get("/result/{task_id}/markdown")
async def download_markdown(task_id: str):
    conn = get_db()
    cur = query(conn, "SELECT * FROM results WHERE task_id = %s", (task_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return {"error": "결과가 없습니다"}

    result = dict(result)
    md_path = make_markdown(
        task_id,
        result["video_title"] or "",
        {
            "summary":  result["summary"],
            "chapters": json.loads(result["chapters"] or "[]"),
            "keywords": json.loads(result["keywords"] or "[]"),
        },
        result["full_script"] or ""
    )
    filename = f"{result['video_title'] or task_id}_요약.md"
    return FileResponse(path=md_path, media_type="text/markdown", filename=filename)

@router.post("/result/{task_id}/resummarize")
async def resummarize(task_id: str, style: str = Form("normal")):
    conn = get_db()
    cur = query(conn, "SELECT full_script FROM results WHERE task_id = %s", (task_id,))
    result = cur.fetchone()
    cur.close()

    if not result:
        conn.close()
        return {"error": "결과가 없습니다"}

    new_result = summarize(result["full_script"], style)

    query(conn, """
        UPDATE results SET summary=%s, chapters=%s, keywords=%s WHERE task_id=%s
    """, (
        new_result["summary"],
        json.dumps(new_result["chapters"], ensure_ascii=False),
        json.dumps(new_result["keywords"], ensure_ascii=False),
        task_id
    ))
    conn.commit()
    conn.close()

    return RedirectResponse(f"/result/{task_id}", status_code=303)
