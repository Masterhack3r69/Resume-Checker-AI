from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import shutil
import os

from pdf_processor import extract_text_from_pdf, clean_text, chunk_text
from vector_store import VectorStore
from fastapi.middleware.cors import CORSMiddleware
from analyzer import ResumeAnalyzer

app = FastAPI(title="Resume Checker AI", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Model (for documentation, though we use Form/File fields)
class AnalysisResponse(BaseModel):
    match_score: int
    analysis: dict
    recruiter_feedback: dict
    interview_prep: List[str]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    file: UploadFile,
    job_description: str = Form(...)
):
    try:
        # 1. Read and Process PDF
        content = await file.read()
        
        # Modified: Now returns tuple
        raw_text, page_count = extract_text_from_pdf(content)
        
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        # Prepare Metadata
        file_metadata = {
            "filename": file.filename,
            "page_count": page_count
        }

        # 2. Vector Store (Ephemeral)
        # Initialize VectorStore
        vs = VectorStore()
        collection, collection_name = vs.create_collection_from_chunks(chunks)
        
        try:
            # 3. Analyze
            analyzer = ResumeAnalyzer(vector_store=vs)
            
            # Modified: Passing full text and metadata
            result = await analyzer.analyze(job_description, collection, raw_text, file_metadata)
            
            return result
            
        finally:
            # Cleanup
            vs.delete_collection(collection_name)
            
    except Exception as e:
        # In production, log the full error
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount Frontend (After API routes to avoid conflicts)
# We expect the 'frontend/dist' directory to exist after we build the React app
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Allow API routes to pass through if they weren't caught above (though strictly they should be)
        if full_path.startswith("analyze"):
             return await analyze_resume() # Should not be hit via GET
             
        # Serve index.html for all other routes (SPA)
        if os.path.exists("frontend/dist/index.html"):
            return FileResponse("frontend/dist/index.html")
        return {"error": "Frontend not found. Did you run 'npm run build'?"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
