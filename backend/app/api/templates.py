import os
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.template import DocumentTemplate
from app.models.user import User
from app.services.image_quality_service import ImageQualityService
from app.services.document_detection_service import DocumentDetectionService
from app.services.ocr_service import OCRService
from app.services.qr_service import QRService
from app.services.template_matching_service import TemplateMatchingService
from app.utils.security import get_current_user, require_role
from app.utils.logging import log_audit

router = APIRouter()
TEMPLATE_UPLOAD_DIR = os.path.join("uploads", "templates")
os.makedirs(TEMPLATE_UPLOAD_DIR, exist_ok=True)

quality_service = ImageQualityService()
detection_service = DocumentDetectionService()
ocr_service = OCRService()
qr_service = QRService()
template_service = TemplateMatchingService()

@router.get("/")
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(DocumentTemplate).order_by(DocumentTemplate.document_type.asc()).all()
    results = []
    for t in templates:
        profile = {}
        try:
            profile = json.loads(t.template_profile_json)
        except Exception:
            pass
        results.append({
            "id": t.id,
            "document_type": t.document_type,
            "template_name": t.template_name,
            "version": t.version,
            "issuing_org": t.issuing_org,
            "status": t.status,
            "is_default": t.is_default,
            "aspect_ratio": t.aspect_ratio,
            "expected_width": t.expected_width,
            "expected_height": t.expected_height,
            "sample_image_url": f"/uploads/templates/{os.path.basename(t.sample_image_path)}" if t.sample_image_path else None,
            "profile": profile,
            "created_by": t.created_by,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        })
    return results

@router.post("/learn-from-sample")
async def learn_template_from_sample(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    template_name: str = Form(...),
    version: str = Form("v1.0"),
    issuing_org: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "OFFICER"))
):
    """
    Administrator feature: Uploads an authorized reference sample and runs the
    complete automated template learning workflow to build a Document Template Profile.
    """
    data = await file.read()
    tmpl_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower() or ".png"
    sample_filename = f"{tmpl_id}_sample{ext}"
    sample_path = os.path.join(TEMPLATE_UPLOAD_DIR, sample_filename)
    
    with open(sample_path, "wb") as f:
        f.write(data)

    # 1. Image quality check
    quality = quality_service.analyze(sample_path)
    if not quality["acceptable"]:
        raise HTTPException(400, f"Template reference sample failed quality check: {', '.join(quality['reasons'])}")

    # 2. Document detection & normalization
    detection = detection_service.process(sample_path, TEMPLATE_UPLOAD_DIR)
    norm_path = detection["normalized_path"] if detection.get("success") else sample_path

    # 3. OCR extraction & text regions
    ocr = ocr_service.extract(norm_path, document_type)

    # 4. QR detection & decoding
    qr = qr_service.decode(norm_path)

    # 5. Build template profile
    profile = template_service.learn_template(norm_path, document_type, ocr, qr)
    profile["issuing_org"] = issuing_org
    profile["version"] = version

    # Save to database
    tmpl = DocumentTemplate(
        id=tmpl_id,
        document_type=document_type,
        template_name=template_name,
        version=version,
        issuing_org=issuing_org,
        status="ACTIVE",
        is_default=True,
        aspect_ratio=profile.get("aspect_ratio"),
        expected_width=profile.get("expected_width"),
        expected_height=profile.get("expected_height"),
        sample_image_path=sample_path,
        template_profile_json=json.dumps(profile),
        created_by=current_user.user_id if current_user else "ADMIN"
    )
    db.add(tmpl)
    db.commit()

    log_audit(
        db,
        user_id=current_user.user_id if current_user else "ADMIN",
        user_name=current_user.full_name if current_user else "Admin",
        action="TEMPLATE_CREATED",
        result="SUCCESS",
        details={"document_type": document_type, "template_name": template_name}
    )

    return {
        "id": tmpl.id,
        "document_type": tmpl.document_type,
        "template_name": tmpl.template_name,
        "version": tmpl.version,
        "status": tmpl.status,
        "profile": profile,
        "sample_image_url": f"/uploads/templates/{sample_filename}"
    }

@router.put("/{template_id}/status")
def toggle_template_status(
    template_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    tmpl = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not tmpl:
        raise HTTPException(404, "Template not found")
    
    tmpl.status = status.upper()
    db.commit()
    return {"id": tmpl.id, "status": tmpl.status}

@router.delete("/{template_id}")
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    tmpl = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not tmpl:
        raise HTTPException(404, "Template not found")
    db.delete(tmpl)
    db.commit()
    return {"success": True, "message": "Template deleted"}
