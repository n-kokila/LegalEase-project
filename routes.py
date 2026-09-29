from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from ai_core.gemini_generator import generate_legal_document, DOCUMENT_TYPES
from utils.document_formatter import parse_document_sections, clean_text_for_export
from utils.docx_generator import create_docx
from utils.pdf_generator import create_pdf

router = APIRouter()

class DocumentGenerateRequest(BaseModel):
    document_type: str = Field(..., description="Type of legal document (e.g., NDA, Employment Contract, Lease Agreement)")
    parties: str = Field(..., description="Names, roles, and details of all parties involved")
    terms: str = Field(..., description="Key terms, covenants, compensation, duration, obligations")
    dates: Optional[str] = Field(None, description="Effective date or key dates")
    effective_date: Optional[str] = Field(None, description="Alias for effective date")
    jurisdiction: Optional[str] = Field(None, description="Governing state or country law")
    additional_clauses: Optional[str] = Field(None, description="Optional extra custom clauses")

    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "NDA",
                "parties": "Nexus Tech Inc. (Disclosing Party) and Jane Smith (Receiving Party)",
                "terms": "Confidential information covers source code, client lists, and financial roadmaps. 3-year confidentiality period.",
                "dates": "2026-10-01",
                "jurisdiction": "State of Delaware"
            }
        }


class DocumentGenerateResponse(BaseModel):
    status: str
    document_type: str
    generated_document: str
    document: str  # Convenient alias
    metadata: Dict[str, Any]
    created_at: str


class ExportRequest(BaseModel):
    document_text: str
    document_type: str = "Legal Document"
    effective_date: str = ""
    parties: str = ""


@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "service": "LegalEase API",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/document-types", tags=["Documents"])
async def get_document_types():
    """Returns list of supported legal document types."""
    return {
        "document_types": DOCUMENT_TYPES,
        "count": len(DOCUMENT_TYPES)
    }


@router.post("/generate", response_model=DocumentGenerateResponse, tags=["AI Generation"])
async def generate_document(payload: DocumentGenerateRequest):
    """
    Main endpoint to generate structured legal documents via Google Gemini AI.
    Accepts:
    - document_type
    - parties
    - terms
    - dates (or effective_date)
    - optional jurisdiction
    """
    effective_date = payload.dates or payload.effective_date
    if not effective_date or not effective_date.strip():
        effective_date = datetime.now().strftime("%B %d, %Y")

    # Validate required fields
    if not payload.document_type or not payload.document_type.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'document_type' cannot be empty."
        )
    if not payload.parties or not payload.parties.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'parties' cannot be empty."
        )
    if not payload.terms or not payload.terms.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'terms' cannot be empty."
        )

    try:
        result = generate_legal_document(
            document_type=payload.document_type,
            parties=payload.parties,
            terms=payload.terms,
            effective_date=effective_date,
            jurisdiction=payload.jurisdiction
        )

        doc_text = result["document"]
        stats = parse_document_sections(doc_text)

        metadata = {
            "mode": result.get("mode", "unknown"),
            "model": result.get("model", "standard_engine"),
            "message": result.get("message", ""),
            "word_count": stats["word_count"],
            "clause_count": stats["clause_count"],
            "estimated_reading_minutes": stats["estimated_reading_minutes"]
        }

        return DocumentGenerateResponse(
            status="success",
            document_type=payload.document_type,
            generated_document=doc_text,
            document=doc_text,
            metadata=metadata,
            created_at=datetime.utcnow().isoformat()
        )

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating the document: {str(e)}"
        )


@router.post("/export/pdf", tags=["Export"])
async def export_pdf(payload: ExportRequest):
    """Generates and downloads a binary PDF file."""
    try:
        buffer = create_pdf(
            document_text=payload.document_text,
            document_type=payload.document_type,
            effective_date=payload.effective_date,
            parties=payload.parties
        )
        filename = f"{payload.document_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/export/docx", tags=["Export"])
async def export_docx(payload: ExportRequest):
    """Generates and downloads a binary DOCX file."""
    try:
        buffer = create_docx(
            document_text=payload.document_text,
            document_type=payload.document_type,
            effective_date=payload.effective_date,
            parties=payload.parties
        )
        filename = f"{payload.document_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
        return Response(
            content=buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")
