from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db, query

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/status/{task_id}")
async def status_page(request: Request, task_id: str):
    conn = get_db()
    cur = query(conn, "SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()

    if not task:
        return RedirectResponse("/")

    if task["status"] == "DONE":
        return RedirectResponse(f"/result/{task_id}")

    return templates.TemplateResponse(
        "status.html",
        {"request": request, "task": dict(task)}
    )

@router.get("/api/status/{task_id}")
async def status_api(task_id: str):
    conn = get_db()
    cur = query(conn, "SELECT status, progress FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()

    if not task:
        return JSONResponse({"error": "not found"}, status_code=404)

    return JSONResponse({
        "status":   task["status"],
        "progress": task["progress"],
    })
