import json
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.verification import VerificationRecord
from app.models.document import Document
from app.models.template import DocumentTemplate
from app.models.user import User
from app.schemas.verification import VerificationRunRequest, OfficerReviewRequest
from app.services.verification_service import VerificationService
from app.utils.security import get_current_user, require_role
from app.utils.logging import log_audit

router = APIRouter()
screening_service = VerificationService()

@router.post("/run")
def run_verification(
    req: VerificationRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    # Load matching template
    template = None
    if req.template_id:
        template = db.query(DocumentTemplate).filter(DocumentTemplate.id == req.template_id).first()
    if not template:
        template = db.query(DocumentTemplate).filter(
            DocumentTemplate.document_type == req.document_type,
            DocumentTemplate.status == "ACTIVE"
        ).first()

    template_profile = {}
    sample_path = None
    if template:
        try:
            template_profile = json.loads(template.template_profile_json)
        except Exception:
            pass
        sample_path = template.sample_image_path

    # Execute full multi-stage screening pipeline
    result = screening_service.run_screening_pipeline(
        doc_path=doc.file_path,
        doc_type=req.document_type,
        template_profile=template_profile,
        sample_image_path=sample_path,
        output_dir="uploads",
        simulate_authoritative=req.allow_demo_authoritative_provider
    )

    # Save verification record
    record_id = str(uuid.uuid4())
    record = VerificationRecord(
        id=record_id,
        document_id=doc.id,
        document_type=req.document_type,
        template_id=template.id if template else None,
        officer_id=current_user.user_id if current_user else "SYSTEM",
        officer_name=current_user.full_name if current_user else "Screening Officer",
        status=result["status"],
        screening_score=result["screening_score"],
        template_match_score=result["breakdown"]["template_match"],
        ocr_consistency_score=result["breakdown"]["ocr_consistency"],
        qr_consistency_score=result["breakdown"]["qr_consistency"],
        required_fields_score=result["breakdown"]["required_fields"],
        image_quality_score=result["breakdown"]["image_quality"],
        integrity_score=result["breakdown"]["integrity_screening"],
        authorized_verification_status=result["breakdown"]["authorized_verification"],
        breakdown_json=json.dumps(result["breakdown"]),
        validation_notes_json=json.dumps(result["validation_notes"]),
        flagged_issues_json=json.dumps(result["flagged_issues"]),
        data_comparison_json=json.dumps(result["data_comparison"]),
        extracted_fields_json=json.dumps(result["extracted_fields"]),
        qr_data_json=json.dumps(result["qr_analysis"]),
        text_boxes_json=json.dumps(result["text_boxes"]),
        qr_box_json=json.dumps(result["qr_box"]),
        overlay_image_path=result["overlay_image_url"],
        manual_review_needed=result["manual_review_needed"]
    )
    db.add(record)

    # Update document status
    doc.status = result["status"]
    db.commit()

    log_audit(
        db,
        user_id=current_user.user_id if current_user else "SYSTEM",
        user_name=current_user.full_name if current_user else "Officer",
        action="VERIFICATION_SCREENING",
        document_id=doc.id,
        result=result["status"],
        details={"score": result["screening_score"], "flags": len(result["flagged_issues"])}
    )

    return {
        "id": record.id,
        "document_id": doc.id,
        "document_type": req.document_type,
        "template_id": template.id if template else None,
        "template_name": template.template_name if template else "Default Heuristic Profile",
        "officer_id": record.officer_id,
        "officer_name": record.officer_name,
        "status": result["status"],
        "screening_score": result["screening_score"],
        "breakdown": result["breakdown"],
        "validation_notes": result["validation_notes"],
        "recommendation": result["recommendation"],
        "legal_disclaimer": result["legal_disclaimer"],
        "flagged_issues": result["flagged_issues"],
        "data_comparison": result["data_comparison"],
        "extracted_fields": result["extracted_fields"],
        "qr_analysis": result["qr_analysis"],
        "image_quality": result["image_quality"],
        "integrity_screening": result["integrity_screening"],
        "normalized_image_url": result["normalized_image_url"],
        "overlay_image_url": result["overlay_image_url"],
        "sample_image_url": result["sample_image_url"],
        "text_boxes": result["text_boxes"],
        "qr_box": result["qr_box"],
        "manual_review_needed": result["manual_review_needed"],
        "officer_review_decision": None,
        "officer_notes": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "created_at": record.created_at
    }

@router.get("/history")
def get_verification_history(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(VerificationRecord)
    if status:
        query = query.filter(VerificationRecord.status == status)
    if document_type:
        query = query.filter(VerificationRecord.document_type == document_type)
    if search:
        query = query.filter(
            (VerificationRecord.document_id.contains(search)) |
            (VerificationRecord.officer_name.contains(search)) |
            (VerificationRecord.document_type.contains(search))
        )

    records = query.order_by(VerificationRecord.created_at.desc()).limit(limit).all()
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "document_id": r.document_id,
            "document_type": r.document_type,
            "status": r.status,
            "screening_score": r.screening_score,
            "template_match_score": r.template_match_score,
            "qr_consistency_score": r.qr_consistency_score,
            "officer_name": r.officer_name,
            "manual_review_needed": r.manual_review_needed,
            "officer_review_decision": r.officer_review_decision,
            "created_at": r.created_at
        })
    return results

@router.get("/{verification_id}")
def get_verification_details(verification_id: str, db: Session = Depends(get_db)):
    r = db.query(VerificationRecord).filter(VerificationRecord.id == verification_id).first()
    if not r:
        raise HTTPException(404, "Verification record not found")

    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == r.template_id).first() if r.template_id else None
    doc = db.query(Document).filter(Document.id == r.document_id).first()

    return {
        "id": r.id,
        "document_id": r.document_id,
        "document_type": r.document_type,
        "template_id": r.template_id,
        "template_name": template.template_name if template else "Default Heuristic Profile",
        "officer_id": r.officer_id,
        "officer_name": r.officer_name,
        "status": r.status,
        "screening_score": r.screening_score,
        "breakdown": json.loads(r.breakdown_json) if r.breakdown_json else {},
        "validation_notes": json.loads(r.validation_notes_json) if r.validation_notes_json else [],
        "recommendation": "Manual review recommended." if r.manual_review_needed else "Automated checks consistent.",
        "legal_disclaimer": "Template and document checks are consistent, but design matching alone does not establish legal authenticity. Use an authorized verification source where available.",
        "flagged_issues": json.loads(r.flagged_issues_json) if r.flagged_issues_json else [],
        "data_comparison": json.loads(r.data_comparison_json) if r.data_comparison_json else [],
        "extracted_fields": json.loads(r.extracted_fields_json) if r.extracted_fields_json else {},
        "qr_analysis": json.loads(r.qr_data_json) if r.qr_data_json else {},
        "text_boxes": json.loads(r.text_boxes_json) if r.text_boxes_json else [],
        "qr_box": json.loads(r.qr_box_json) if r.qr_box_json else None,
        "normalized_image_url": f"/uploads/documents/{os.path.basename(doc.normalized_path)}" if (doc and doc.normalized_path) else (f"/uploads/documents/{os.path.basename(doc.file_path)}" if doc else None),
        "overlay_image_url": r.overlay_image_path,
        "sample_image_url": f"/uploads/templates/{os.path.basename(template.sample_image_path)}" if (template and template.sample_image_path) else None,
        "manual_review_needed": r.manual_review_needed,
        "officer_review_decision": r.officer_review_decision,
        "officer_notes": r.officer_notes,
        "reviewed_by": r.reviewed_by,
        "reviewed_at": r.reviewed_at,
        "created_at": r.created_at
    }

@router.post("/{verification_id}/review")
def submit_officer_review(
    verification_id: str,
    req: OfficerReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("OFFICER", "REVIEWER", "ADMIN"))
):
    r = db.query(VerificationRecord).filter(VerificationRecord.id == verification_id).first()
    if not r:
        raise HTTPException(404, "Verification record not found")

    r.officer_review_decision = req.decision
    r.officer_notes = req.notes
    r.reviewed_by = current_user.full_name
    r.reviewed_at = datetime.utcnow()
    
    if req.new_status:
        r.status = req.new_status
    elif req.decision == "APPROVED" and r.status == "SUSPICIOUS / LIKELY ALTERED":
        r.status = "LIKELY AUTHENTIC"

    db.commit()

    log_audit(
        db,
        user_id=current_user.user_id,
        user_name=current_user.full_name,
        action="OFFICER_MANUAL_REVIEW",
        document_id=r.document_id,
        result=r.status,
        details={"decision": req.decision, "notes": req.notes}
    )

    return {
        "success": True,
        "status": r.status,
        "officer_review_decision": r.officer_review_decision,
        "reviewed_by": r.reviewed_by,
        "reviewed_at": r.reviewed_at
    }
