from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

# Import the existing scraping function
from .models import AnalyzeRequest, FinalOSDDResult
from .scraper import perform_osdd_searches
from .settings import BASE_DIR
from .logger import logger
from .pipeline import run_osdd_pipeline

ANALYST_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

app = FastAPI(title="AML OSDD Helper")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(request = request, name = "index.html",
        context={
            "request": request,
            "model": ANALYST_MODEL,
        },
    )


@app.post("/api/analyze", response_model=FinalOSDDResult)
async def analyze_entity(payload: AnalyzeRequest):
    """Executes full AML OSDD analysis for a designated entity and optional address."""
    entity_name = payload.entity_name.strip()
    if not entity_name:
        logger.warning("Rejected /api/analyze request: entity_name is empty.")
        raise HTTPException(status_code=400, detail="entity_name is required.")

    logger.info(f"Incoming /api/analyze request: entity='{entity_name}', address='{payload.address}'")
    try:
        report = await run_osdd_pipeline(entity=entity_name, address=payload.address)
        return report
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unhandled failure in /api/analyze: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OSDD processing failure: {str(exc)}")


if __name__ == "__main__":
    import uvicorn

    logger.info("Launching AML OSDD API server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)