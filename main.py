"""
Azerbaijani Court Case Sorter - Main Application
A comprehensive system for processing, indexing, and searching Azerbaijani court documents
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Import our modules
from app.document_processor import DocumentProcessor
from app.rag_system import RAGSystem
from app.ai_bot import AIBot
from app.database import DatabaseManager
from app.auth import AuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Azerbaijani Court Case Sorter",
    description="AI-powered system for processing and searching Azerbaijani court documents",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize components
document_processor = DocumentProcessor()
rag_system = RAGSystem()
ai_bot = AIBot()
db_manager = DatabaseManager()
auth_manager = AuthManager()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main application homepage"""
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload and process court documents"""
    try:
        # Verify user permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        processed_docs = []
        failed_docs = []

        for file in files:
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name

                # Process document
                if file.filename.endswith('.zip'):
                    # Handle ZIP files
                    with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                        zip_ref.extractall(tempfile.gettempdir())

                        for extracted_file in zip_ref.namelist():
                            if extracted_file.endswith('.pdf'):
                                extracted_path = os.path.join(tempfile.gettempdir(), extracted_file)
                                doc_data = document_processor.process_document(extracted_path)
                                if doc_data:
                                    doc_id = db_manager.store_document(doc_data)
                                    rag_system.add_document(doc_id, doc_data)
                                    processed_docs.append({"filename": extracted_file, "id": doc_id})
                                else:
                                    failed_docs.append(extracted_file)
                else:
                    # Handle single PDF files
                    doc_data = document_processor.process_document(temp_file_path)
                    if doc_data:
                        doc_id = db_manager.store_document(doc_data)
                        rag_system.add_document(doc_id, doc_data)
                        processed_docs.append({"filename": file.filename, "id": doc_id})
                    else:
                        failed_docs.append(file.filename)

                # Clean up temp file
                os.unlink(temp_file_path)

            except Exception as e:
                logger.error(f"Error processing {file.filename}: {str(e)}")
                failed_docs.append(file.filename)

        return {
            "message": "Upload completed",
            "processed": len(processed_docs),
            "failed": len(failed_docs),
            "processed_documents": processed_docs,
            "failed_documents": failed_docs
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_documents(
    query: str = None,
    judge: str = None,
    court: str = None,
    case_type: str = None,
    district: str = None,
    year: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Search documents using filters or natural language query"""
    try:
        # Verify user permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        if query:
            # Use AI bot for natural language queries
            results = ai_bot.search_documents(query)
        else:
            # Use structured filters
            filters = {
                "judge": judge,
                "court": court,
                "case_type": case_type,
                "district": district,
                "year": year
            }
            results = db_manager.search_documents(filters)

        return {"results": results, "total": len(results)}

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/filters")
async def get_filter_options(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get available filter options for dynamic dropdowns"""
    try:
        # Verify user permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        filters = db_manager.get_filter_options()
        return filters

    except Exception as e:
        logger.error(f"Filter options error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{doc_id}")
async def get_document(
    doc_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get specific document details"""
    try:
        # Verify user permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        document = db_manager.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return document

    except Exception as e:
        logger.error(f"Document retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_bot(
    message: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Chat with the AI bot"""
    try:
        # Verify user permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        response = ai_bot.chat(message)
        return {"response": response}

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """User login endpoint"""
    try:
        token = auth_manager.authenticate_user(username, password)
        if token:
            user = auth_manager.get_user(username)
            return {"token": token, "user": {"username": user["username"], "is_admin": user["is_admin"]}}
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        user = auth_manager.verify_token(credentials.credentials)
        if user:
            return user
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_system_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get system statistics"""
    try:
        # Verify user permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        # Get stats from database
        db_stats = db_manager.get_stats()

        # Get RAG system stats
        rag_stats = rag_system.get_stats()

        # Combine stats
        combined_stats = {
            **db_stats,
            **rag_stats
        }

        return combined_stats

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export")
async def export_results(
    format: str = "json",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export search results"""
    try:
        # Verify user permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        # This would implement export functionality
        # For now, return a placeholder
        return {"message": "Export functionality to be implemented"}

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoints
@app.delete("/admin/document/{doc_id}")
async def delete_document(
    doc_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a document (admin only)"""
    try:
        # Verify admin permissions
        user = auth_manager.verify_token(credentials.credentials)
        if not user or not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

        success = db_manager.delete_document(doc_id)
        if success:
            rag_system.remove_document(doc_id)
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
