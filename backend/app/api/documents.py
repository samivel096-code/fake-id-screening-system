import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.document import Document
from app.models.user import User
from app.services.image_quality_service import ImageQualityService
from app.services.document_detection_service import DocumentDetectionService
from app.utils.security import get_current_user
from app.utils.logging import log_audit

router = APIRouter()
UPLOAD_DIR = os.path.join("uploads", "documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)

quality_service = ImageQualityService()
detection_service = DocumentDetectionService()

ALLOWED_MIME = {
    "image/jpeg", "image/jpg", "image/png", "application/pdf"
}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("Aadhaar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_MIME and not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
        raise HTTPException(400, "Only JPG, PNG, and PDF documents are supported.")

    data = await file.read()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "Document size exceeds 20MB limit.")

    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower() or ".png"
    if ext == ".pdf":
        # Save as pdf
        saved_name = f"{doc_id}.pdf"
    else:
        saved_name = f"{doc_id}{ext}"
        
    saved_path = os.path.join(UPLOAD_DIR, saved_name)
    with open(saved_path, "wb") as f:
        f.write(data)

    # If PDF, in standard production pdf2image converts page 1; for now if image format, analyze directly
    quality = quality_service.analyze(saved_path)

    # Perform perspective normalization if acceptable
    normalized_path = None
    thumb_path = None
    if quality["acceptable"]:
        det = detection_service.process(saved_path, UPLOAD_DIR)
        if det.get("success"):
            normalized_path = det.get("normalized_path")
            thumb_path = det.get("thumbnail_path")

    doc = Document(
        id=doc_id,
        original_filename=file.filename,
        file_path=saved_path,
        normalized_path=normalized_path,
        thumbnail_path=thumb_path,
        file_type=ext.replace(".", "").upper(),
        document_type=document_type,
        uploaded_by_user_id=current_user.user_id if current_user else "SYSTEM",
        status="QUALITY_CHECK_FAILED" if not quality["acceptable"] else "READY_FOR_SCREENING"
    )
    db.add(doc)
    db.commit()

    log_audit(
        db,
        user_id=current_user.user_id if current_user else "SYSTEM",
        user_name=current_user.full_name if current_user else "Officer",
        action="DOCUMENT_UPLOAD",
        document_id=doc_id,
        result="IMAGE_QUALITY_ACCEPTABLE" if quality["acceptable"] else "DOCUMENT_NOT_CLEAR",
        details={"quality_score": quality.get("overall_score"), "reasons": quality.get("reasons")}
    )

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "document_type": document_type,
        "status": doc.status,
        "quality": quality,
        "file_url": f"/uploads/documents/{saved_name}",
        "normalized_url": f"/uploads/documents/{os.path.basename(normalized_path)}" if normalized_path else None,
        "thumbnail_url": f"/uploads/documents/{os.path.basename(thumb_path)}" if thumb_path else None
    }

@router.post("/batch-upload")
async def batch_upload_documents(
    files: List[UploadFile] = File(...),
    document_type: str = Form("Aadhaar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = []
    for file in files:
        data = await file.read()
        doc_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1].lower() or ".png"
        saved_name = f"{doc_id}{ext}"
        saved_path = os.path.join(UPLOAD_DIR, saved_name)
        with open(saved_path, "wb") as f:
            f.write(data)

        quality = quality_service.analyze(saved_path)
        normalized_path = None
        thumb_path = None
        if quality["acceptable"]:
            det = detection_service.process(saved_path, UPLOAD_DIR)
            if det.get("success"):
                normalized_path = det.get("normalized_path")
                thumb_path = det.get("thumbnail_path")

        doc = Document(
            id=doc_id,
            original_filename=file.filename,
            file_path=saved_path,
            normalized_path=normalized_path,
            thumbnail_path=thumb_path,
            file_type=ext.replace(".", "").upper(),
            document_type=document_type,
            uploaded_by_user_id=current_user.user_id if current_user else "SYSTEM",
            status="QUALITY_CHECK_FAILED" if not quality["acceptable"] else "READY_FOR_SCREENING"
        )
        db.add(doc)
        results.append({
            "document_id": doc_id,
            "filename": file.filename,
            "document_type": document_type,
            "acceptable": quality["acceptable"],
            "quality_score": quality.get("overall_score", 0),
            "status": doc.status,
            "reasons": quality.get("reasons", [])
        })

    db.commit()
    return {"total": len(files), "results": results}

@router.get("/")
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(50).all()
    return docs

@router.get("/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc
