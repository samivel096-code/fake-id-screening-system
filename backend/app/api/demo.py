import os
import shutil
import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.document import Document
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter()
DEMO_DIR = os.path.join("uploads", "demo_docs")
DOC_DIR = os.path.join("uploads", "documents")

@router.get("/documents")
def list_demo_documents():
    """Returns pre-packaged synthetic test documents for demonstration and verification testing."""
    return [
        {
            "id": "demo-valid-aadhaar",
            "title": "Authentic Sample Aadhaar",
            "document_type": "Aadhaar",
            "filename": "demo_aadhaar_valid.png",
            "expected_outcome": "LIKELY AUTHENTIC",
            "description": "Fictional Aadhaar card with matching QR code, crisp typography, and full layout alignment.",
            "url": "/uploads/demo_docs/demo_aadhaar_valid.png"
        },
        {
            "id": "demo-tampered-aadhaar",
            "title": "Tampered / Altered Aadhaar (QR & Splicing Anomaly)",
            "document_type": "Aadhaar",
            "filename": "demo_aadhaar_altered.png",
            "expected_outcome": "SUSPICIOUS / LIKELY ALTERED",
            "description": "Spliced text over visible name while QR code contains original holder name. Triggers QR mismatch and integrity alerts.",
            "url": "/uploads/demo_docs/demo_aadhaar_altered.png"
        },
        {
            "id": "demo-valid-pan",
            "title": "Authentic Sample PAN Card",
            "document_type": "PAN Card",
            "filename": "demo_pan_valid.png",
            "expected_outcome": "LIKELY AUTHENTIC",
            "description": "Synthetic PAN card with valid 10-digit PAN format, QR code, and correct aspect ratio.",
            "url": "/uploads/demo_docs/demo_pan_valid.png"
        },
        {
            "id": "demo-blurry",
            "title": "Blurry Low-Quality Document",
            "document_type": "Aadhaar",
            "filename": "demo_blurry_unreadable.png",
            "expected_outcome": "DOCUMENT NOT CLEAR",
            "description": "Heavy blur and low sharpness. Triggers strict Image Quality check failure.",
            "url": "/uploads/demo_docs/demo_blurry_unreadable.png"
        }
    ]

@router.post("/load/{demo_id}")
def load_demo_document_for_screening(
    demo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Copies a demo synthetic document into the active documents table for immediate screening."""
    demo_map = {
        "demo-valid-aadhaar": ("demo_aadhaar_valid.png", "Aadhaar"),
        "demo-tampered-aadhaar": ("demo_aadhaar_altered.png", "Aadhaar"),
        "demo-valid-pan": ("demo_pan_valid.png", "PAN Card"),
        "demo-blurry": ("demo_blurry_unreadable.png", "Aadhaar"),
    }
    if demo_id not in demo_map:
        raise HTTPException(404, "Demo document not found")

    filename, doc_type = demo_map[demo_id]
    src_path = os.path.join(DEMO_DIR, filename)
    if not os.path.exists(src_path):
        raise HTTPException(404, f"Demo file {filename} not generated on disk")

    doc_id = str(uuid.uuid4())
    dest_path = os.path.join(DOC_DIR, f"{doc_id}_{filename}")
    os.makedirs(DOC_DIR, exist_ok=True)
    shutil.copyfile(src_path, dest_path)

    doc = Document(
        id=doc_id,
        original_filename=filename,
        file_path=dest_path,
        file_type="PNG",
        document_type=doc_type,
        uploaded_by_user_id=current_user.user_id if current_user else "OFFICER",
        status="READY_FOR_SCREENING"
    )
    db.add(doc)
    db.commit()

    return {
        "document_id": doc.id,
        "filename": doc.original_filename,
        "document_type": doc.document_type,
        "file_url": f"/uploads/documents/{os.path.basename(dest_path)}",
        "status": doc.status
    }
