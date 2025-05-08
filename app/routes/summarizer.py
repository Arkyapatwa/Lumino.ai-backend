from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


from models.summarizer_model import SummarizerModel
from services.summarizer_service import summarize_text, summarize_file

router = APIRouter(prefix="/summarizer")

@router.get("/text")
async def summarize_text(user_input: SummarizerModel, request: Request):
    try:
        result = summarize_text(user_input)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@router.get("/file")
async def summarize_file(user_input: SummarizerModel, request: Request):
    try:
        result = summarize_file(user_input, request)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)