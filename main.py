import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from routes import router

app = FastAPI(
    title="LegalEase API",
    description="AI-Powered Legal Document Generator Backend powered by Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit frontend and local clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "LegalEase – AI-Powered Legal Document Generator",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "generate": "POST /generate",
            "document_types": "GET /document-types",
            "health": "GET /health",
            "export_pdf": "POST /export/pdf",
            "export_docx": "POST /export/docx"
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 8000))
    print(f"🚀 Starting LegalEase Backend on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
