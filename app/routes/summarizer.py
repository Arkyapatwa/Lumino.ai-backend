from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.models.summarizer_model import SummarizerModel
from app.services import summarizer_service

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/summarizer")

@router.get("/text")
@limiter.limit("2/minute")
async def summarize_text(user_input: SummarizerModel, request: Request):
    try:
        result = await summarizer_service.summarize_text(user_input=user_input, request=request)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@router.post("/file")
@limiter.limit("2/minute")
async def summarize_file(request: Request, file: UploadFile = File(...)):
    try:
        result = await summarizer_service.summarize_file(file=file, request=request)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)