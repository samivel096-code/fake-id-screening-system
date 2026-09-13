import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.image_quality_service import ImageQualityService
from app.services.document_detection_service import DocumentDetectionService
from app.services.ocr_service import OCRService
from app.services.qr_service import QRService
from app.services.template_matching_service import TemplateMatchingService
from app.services.integrity_analysis_service import IntegrityAnalysisService
from app.services.comparison_service import ComparisonService
from app.providers.verification_provider import get_verification_provider

class VerificationService:
    def __init__(self):
        self.quality_service = ImageQualityService()
        self.detection_service = DocumentDetectionService()
        self.ocr_service = OCRService()
        self.qr_service = QRService()
        self.template_service = TemplateMatchingService()
        self.integrity_service = IntegrityAnalysisService()
        self.comparison_service = ComparisonService()

    def run_screening_pipeline(self,
                              doc_path: str,
                              doc_type: str,
                              template_profile: Dict[str, Any],
                              sample_image_path: Optional[str] = None,
                              output_dir: str = "uploads",
                              simulate_authoritative: bool = False) -> Dict[str, Any]:
        """
        Executes the end-to-end automated screening pipeline according to government spec.
        """
        validation_notes: List[str] = []
        flagged_issues: List[Dict[str, Any]] = []

        # Step 1: Strict Image Quality Analysis
        quality = self.quality_service.analyze(doc_path)
        if not quality["acceptable"]:
            validation_notes.append("❌ Image quality failed strict automated standards.")
            for r in quality["reasons"]:
                validation_notes.append(f"  • {r}")
                flagged_issues.append({
                    "id": f"quality_issue_{len(flagged_issues) + 1}",
                    "type": "QUALITY_WARNING",
                    "severity": "HIGH",
                    "title": "Unreadable Image Characteristic",
                    "description": r,
                    "region": None
                })
            
            return {
                "status": "UNABLE TO VERIFY",
                "screening_score": quality.get("overall_score", 30.0),
                "breakdown": {
                    "template_match": 0.0,
                    "ocr_consistency": 0.0,
                    "qr_consistency": 0.0,
                    "required_fields": 0.0,
                    "image_quality": quality.get("overall_score", 30.0),
                    "integrity_screening": 0.0,
                    "authorized_verification": "NOT AVAILABLE",
                    "template_details": {}
                },
                "validation_notes": validation_notes,
                "recommendation": "Reject upload. Prompt officer or applicant to upload a clear, complete, and un-cropped image.",
                "legal_disclaimer": "The uploaded document is not sufficiently visible for reliable analysis. Screening halted.",
                "flagged_issues": flagged_issues,
                "data_comparison": [],
                "extracted_fields": {},
                "qr_analysis": {"detected": False, "readable": False},
                "image_quality": quality,
                "integrity_screening": {},
                "normalized_image_url": None,
                "overlay_image_url": None,
                "sample_image_url": sample_image_path,
                "text_boxes": [],
                "qr_box": None,
                "manual_review_needed": True
            }

        validation_notes.append("✓ Document image quality acceptable (blur, lighting, resolution, and contrast validated).")

        # Step 2: Document Detection & Perspective Normalization
        detection = self.detection_service.process(doc_path, output_dir)
        working_image_path = detection["normalized_path"] if detection.get("success") else doc_path
        normalized_image_url = f"/uploads/{os.path.basename(working_image_path)}"

        if detection.get("detected_quad"):
            validation_notes.append("✓ Document boundaries detected and 4-point perspective correction applied.")
        else:
            validation_notes.append("ℹ Document boundary contour fell back to frame bounding box.")

        # Step 3: OCR Extraction
        ocr = self.ocr_service.extract(working_image_path, doc_type)
        extracted_fields = ocr.get("extracted_fields", {})
        text_boxes = ocr.get("text_boxes", [])

        if ocr.get("text") and len(ocr.get("text").strip()) > 15:
            validation_notes.append(f"✓ OCR text extraction completed successfully ({len(text_boxes)} text elements identified).")
            ocr_consistency = 96.0
        else:
            validation_notes.append("⚠ OCR text extraction returned sparse or unreadable text.")
            ocr_consistency = 40.0
            flagged_issues.append({
                "id": f"ocr_issue_{len(flagged_issues) + 1}",
                "type": "OCR_WARNING",
                "severity": "MEDIUM",
                "title": "Low OCR Confidence",
                "description": "Text extraction yielded low character count.",
                "region": None
            })

        # Step 4: Document Type Identification / Mismatch Check
        raw_text_lower = ocr.get("text", "").lower()
        type_mismatch = False
        if "aadhaar" in doc_type.lower() and ("income tax" in raw_text_lower or "permanent account" in raw_text_lower):
            type_mismatch = True
            mismatch_desc = "Selected document type is Aadhaar, but uploaded document contains PAN Card identifiers."
        elif "pan" in doc_type.lower() and ("unique identification" in raw_text_lower or "mera aadhaar" in raw_text_lower):
            type_mismatch = True
            mismatch_desc = "Selected document type is PAN Card, but uploaded document contains Aadhaar identifiers."
        
        if type_mismatch:
            validation_notes.append(f"⚠ DOCUMENT TYPE MISMATCH: {mismatch_desc}")
            flagged_issues.append({
                "id": f"type_mismatch_{len(flagged_issues) + 1}",
                "type": "TEMPLATE_MISMATCH",
                "severity": "HIGH",
                "title": "Document Type Mismatch",
                "description": mismatch_desc,
                "region": None
            })

        # Step 5: Template / Design Comparison
        template_res = self.template_service.compare_with_template(
            working_image_path,
            template_profile,
            sample_image_path,
            output_dir
        )
        template_match_score = template_res["overall_match"]
        if type_mismatch:
            template_match_score = min(35.0, template_match_score * 0.4)
            template_res["breakdown"]["layout"] = min(30.0, template_res["breakdown"]["layout"] * 0.4)

        if template_match_score >= 85:
            validation_notes.append(f"✓ Layout and visual design are consistent with reference template (Template Match: {template_match_score}%).")
        else:
            validation_notes.append(f"⚠ Layout differs from approved reference template (Template Match: {template_match_score}%).")
            flagged_issues.append({
                "id": f"template_issue_{len(flagged_issues) + 1}",
                "type": "TEMPLATE_MISMATCH",
                "severity": "HIGH" if template_match_score < 60 else "MEDIUM",
                "title": "Template Layout Deviation",
                "description": f"Overall template match score is {template_match_score}/100.",
                "region": None
            })

        # Step 6: QR Code Analysis
        qr = self.qr_service.decode(working_image_path)
        qr_detected = qr.get("detected", False)
        qr_readable = qr.get("readable", False)
        qr_box = qr.get("qr_box")
        qr_parsed = qr.get("parsed_data", {})
        qr_cross = {"match_status": "NOT AVAILABLE", "score": 100.0, "discrepancies": []}

        qr_consistency_score = 100.0
        if template_profile.get("has_qr_code", True):
            if qr_detected and qr_readable:
                validation_notes.append("✓ QR code detected and decoded successfully.")
                # Cross-check QR info against OCR info
                qr_cross = self.qr_service.cross_check(qr_parsed, extracted_fields)
                qr_consistency_score = qr_cross["score"]

                if qr_cross["match_status"] == "MATCH":
                    validation_notes.append("✓ QR code data matches corresponding visible document text.")
                elif qr_cross["match_status"] == "MISMATCH":
                    validation_notes.append("⚠ QR INFORMATION MISMATCH: Encoded QR payload differs from visible text.")
                    validation_notes.append("  • The information encoded in the QR code does not match the corresponding visible document information.")
                    for disc in qr_cross["discrepancies"]:
                        validation_notes.append(f"  • {disc}")
                        flagged_issues.append({
                            "id": f"qr_mismatch_{len(flagged_issues) + 1}",
                            "type": "QR_MISMATCH",
                            "severity": "HIGH",
                            "title": "QR Information Mismatch",
                            "description": disc,
                            "region": qr_box
                        })
            elif qr_detected and not qr_readable:
                validation_notes.append("⚠ QR code detected but unreadable or damaged.")
                qr_consistency_score = 45.0
                flagged_issues.append({
                    "id": f"qr_unreadable_{len(flagged_issues) + 1}",
                    "type": "QR_MISMATCH",
                    "severity": "MEDIUM",
                    "title": "QR Code Unreadable",
                    "description": "QR pattern is blurred, damaged, or unparseable.",
                    "region": qr_box
                })
            else:
                validation_notes.append("ℹ No QR code detected on document.")
                qr_consistency_score = 65.0
        else:
            validation_notes.append("ℹ QR code not required by this document profile.")
            qr_consistency_score = 100.0

        # Step 7: Required Fields Validation
        expected_fields = template_profile.get("expected_fields", [])
        missing_fields = []
        for ef in expected_fields:
            if ef.get("required", True) and ef.get("name") not in extracted_fields and ef.get("name") not in qr_parsed:
                missing_fields.append(ef.get("label", ef.get("name")))

        if not missing_fields:
            required_fields_score = 100.0
            validation_notes.append("✓ All expected mandatory document fields detected.")
        else:
            required_fields_score = max(30.0, 100.0 - len(missing_fields) * 25.0)
            validation_notes.append(f"⚠ Missing mandatory field(s): {', '.join(missing_fields)}")
            for mf in missing_fields:
                flagged_issues.append({
                    "id": f"missing_field_{len(flagged_issues) + 1}",
                    "type": "MISSING_FIELD",
                    "severity": "MEDIUM",
                    "title": f"Missing Expected Field: {mf}",
                    "description": f"Mandatory field '{mf}' was not located in OCR or QR data.",
                    "region": None
                })

        # Step 8: Document Integrity Analysis (ELA, Noise, Resaving)
        integrity = self.integrity_service.analyze(working_image_path, output_dir)
        integrity_score = integrity.get("integrity_score", 95.0)

        for susp in integrity.get("suspicious_regions", []):
            flagged_issues.append(susp)

        if integrity.get("indicator_count", 0) > 0:
            validation_notes.append(f"⚠ Document Integrity Screening: {integrity.get('indicator_count')} potential alteration indicator(s) detected.")
            for ind in integrity.get("indicators", []):
                validation_notes.append(f"  • {ind}")
        else:
            validation_notes.append("✓ Document Integrity Screening: No significant alteration indicators detected.")

        # Step 9: Data Cross-Check Table
        data_comparison = self.comparison_service.cross_check_data(
            extracted_fields,
            qr_parsed,
            template_profile
        )

        # Step 10: Authorized Verification Provider
        provider = get_verification_provider(doc_type)
        auth_status = "NOT AVAILABLE"
        provider_notice = "Official verification unavailable. AI screening completed."
        
        if simulate_authoritative:
            auth_status = "VERIFIED"
            provider_notice = "Authoritative government registry validated (SIMULATED FOR DEMO)."
            validation_notes.append("✓ Authoritative registry confirmation received.")
        else:
            validation_notes.append(f"ℹ {provider.provider_name}: Official authoritative source currently unavailable.")

        # Step 11: Final Screening Score Calculation (0-100)
        weights = {
            "template": 0.25,
            "ocr": 0.20,
            "qr": 0.20,
            "fields": 0.15,
            "quality": 0.10,
            "integrity": 0.10
        }
        raw_score = (
            template_match_score * weights["template"] +
            ocr_consistency * weights["ocr"] +
            qr_consistency_score * weights["qr"] +
            required_fields_score * weights["fields"] +
            quality.get("overall_score", 90.0) * weights["quality"] +
            integrity_score * weights["integrity"]
        )
        final_screening_score = round(max(15.0, min(99.0, raw_score)), 1)

        # Step 12: Final Result Classification
        # Rules strictly following user specification:
        # - VERIFIED: Only if authoritative verification confirms
        # - LIKELY AUTHENTIC: If template is highly consistent, OCR is consistent, QR matches, required fields exist, no significant alteration indicators, and authoritative verification is unavailable
        # - SUSPICIOUS / LIKELY ALTERED: If major template mismatch, QR mismatch, significant data mismatch, multiple alteration indicators, or missing required info
        # - UNABLE TO VERIFY: If image is unreadable, OCR fails, or verification cannot be completed reliably
        
        has_high_severity_flag = any(f.get("severity") == "HIGH" for f in flagged_issues)
        has_qr_mismatch = any(f.get("type") == "QR_MISMATCH" for f in flagged_issues)
        has_multiple_alterations = integrity.get("indicator_count", 0) >= 2

        if auth_status == "VERIFIED":
            status = "VERIFIED"
            recommendation = "Document confirmed through authoritative verification channel."
            manual_review_needed = False
        elif (template_match_score < 70 or
              has_qr_mismatch or
              has_multiple_alterations or
              type_mismatch or
              final_screening_score < 70.0):
            status = "SUSPICIOUS / LIKELY ALTERED"
            recommendation = "Manual officer review recommended due to detected risk indicators."
            manual_review_needed = True
        elif (final_screening_score >= 85.0 and
              template_match_score >= 80.0 and
              not has_high_severity_flag):
            status = "LIKELY AUTHENTIC"
            recommendation = "Manual review not required based on current automated screening checks."
            manual_review_needed = False
        else:
            status = "UNABLE TO VERIFY"
            recommendation = "Manual officer review recommended due to borderline consistency."
            manual_review_needed = True

        legal_disclaimer = (
            "IMPORTANT: Template and document checks are consistent, but design matching alone does not "
            "establish legal authenticity. Use an authorized verification source where available. "
            "NEVER claim a document is 100% genuine only because its design matches an approved sample."
        )

        sample_url = f"/uploads/{os.path.basename(sample_image_path)}" if sample_image_path else None

        return {
            "status": status,
            "screening_score": final_screening_score,
            "breakdown": {
                "template_match": round(template_match_score, 1),
                "ocr_consistency": round(ocr_consistency, 1),
                "qr_consistency": round(qr_consistency_score, 1),
                "required_fields": round(required_fields_score, 1),
                "image_quality": round(quality.get("overall_score", 90.0), 1),
                "integrity_screening": round(integrity_score, 1),
                "authorized_verification": auth_status,
                "template_details": template_res.get("breakdown", {})
            },
            "validation_notes": validation_notes,
            "recommendation": recommendation,
            "legal_disclaimer": legal_disclaimer,
            "flagged_issues": flagged_issues,
            "data_comparison": data_comparison,
            "extracted_fields": extracted_fields,
            "qr_analysis": {
                "detected": qr_detected,
                "readable": qr_readable,
                "data_available": bool(qr_parsed),
                "visible_data_match": qr_cross.get("match_status", "NOT AVAILABLE"),
                "authorized_verification": "VERIFIED (DEMO ONLY)" if simulate_authoritative else "NOT AVAILABLE",
                "discrepancies": qr_cross.get("discrepancies", []),
                "format": qr.get("format"),
                "raw_data": qr.get("raw_data"),
                "parsed_data": qr_parsed
            },
            "image_quality": quality,
            "integrity_screening": integrity,
            "normalized_image_url": normalized_image_url,
            "overlay_image_url": template_res.get("overlay_url"),
            "sample_image_url": sample_url,
            "text_boxes": text_boxes,
            "qr_box": qr_box,
            "manual_review_needed": manual_review_needed
        }
