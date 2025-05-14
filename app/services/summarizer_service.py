from utils.llm import LLM
from models.summarizer_model import SummarizerModel
from fastapi import Request, File, UploadFile
import json
import logging

from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
# from langchain.document_loaders import PyPDFLoader, TextLoader
import tempfile
import os
import io
from PyPDF2 import PdfReader

# Setup logger
logger = logging.getLogger("summarizer_service")

async def summarize_text(user_input: SummarizerModel, request: Request):
    try:
        # Generate cache key
        u_id = request.state.user["uid"]
        cache_key = f"summary:{u_id}:{hash(user_input.text)}"
        
        # Try to fetch from cache
        try:
            cached_summary = await request.app.state.redis.get(cache_key)
            if cached_summary:
                logger.info(f"Cache hit for key: {cache_key}")
                return {
                    "status": "success",
                    "message": json.loads(cached_summary),
                    "source": "cache"
                }
        except Exception as redis_error:
            logger.error(f"Redis error: {str(redis_error)}")
            # Continue with generation if cache fails
            
        # Generate new summary
        llm = LLM()
        model = llm.get_openai_model()
        
        content_type = file.content_type
        file_content = await file.read()

        if content_type == "application/pdf":
            pdf_reader = PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Create document from extracted text
            docs = [Document(page_content=text)]
        elif content_type == "text/plain":
            text = file_content.decode("utf-8")
            docs = [Document(page_content=text)]
        else:
            result = {
                "status": "error",
                "message": "Unsupported file format. Please upload a PDF or TXT file."
            }
            return result
        
        # Split text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        split_docs = text_splitter.split_documents(docs)

        # Use map_reduce for batch processing
        chain = load_summarize_chain(
            llm=model,
            chain_type="map_reduce",  # Changed from "stuff" to "map_reduce"
            verbose=False
        )
        
        # Process in batches
        summary = await chain.arun(split_docs)
        
        # Cache the result
        try:
            await request.app.state.redis.set(
                cache_key,
                json.dumps(summary),
                ex=3600  # Cache for 1 hour
            )
            logger.info(f"Cached summary for key: {cache_key}")
        except Exception as redis_error:
            logger.error(f"Failed to cache summary: {str(redis_error)}")
        
        return {
            "status": "success",
            "message": summary,
            "source": "generated"
        }
        
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

async def summarize_file(request: Request, file: UploadFile = File(...)):
    try:
        # Generate cache key from file content
        file_content = await file.read()
        cache_key = f"file_summary:{request.state.user['uid']}:{hash(file_content)}"
        
        # Try to fetch from cache
        try:
            cached_summary = await request.app.state.redis.get(cache_key)
            if cached_summary:
                logger.info(f"Cache hit for file summary: {cache_key}")
                return {
                    "status": "success",
                    "message": json.loads(cached_summary),
                    "source": "cache"
                }
        except Exception as redis_error:
            logger.error(f"Redis error: {str(redis_error)}")
            
        # Reset file position after reading
        await file.seek(0)
        
        llm = LLM()
        model = llm.get_openai_model()
        
        content_type = file.content_type
        file_content = await file.read()

        if content_type == "application/pdf":
            pdf_reader = PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Create document from extracted text
            docs = [Document(page_content=text)]
        elif content_type == "text/plain":
            text = file_content.decode("utf-8")
            docs = [Document(page_content=text)]
        else:
            result = {
                "status": "error",
                "message": "Unsupported file format. Please upload a PDF or TXT file."
            }
            return result
        
        # Split text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        split_docs = text_splitter.split_documents(docs)

        # Use map_reduce for batch processing
        chain = load_summarize_chain(
            llm=model,
            chain_type="map_reduce",  # Changed from "stuff" to "map_reduce"
            verbose=False
        )
        
        # Process in batches
        summary = await chain.arun(split_docs)
        
        # Cache the result
        try:
            await request.app.state.redis.set(
                cache_key,
                json.dumps(summary),
                ex=3600  # Cache for 1 hour
            )
            logger.info(f"Cached file summary: {cache_key}")
        except Exception as redis_error:
            logger.error(f"Failed to cache file summary: {str(redis_error)}")
            
        return {
            "status": "success",
            "message": summary,
            "source": "generated"
        }
        
    except Exception as e:
        logger.error(f"File summarization error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }