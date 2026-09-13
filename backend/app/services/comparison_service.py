import re
from typing import Dict, Any, List
from app.utils.masking import mask_identifier

class ComparisonService:
    def cross_check_data(self, ocr_fields: Dict[str, Any], qr_parsed: Dict[str, Any], template_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates a data cross-check table comparing visible OCR extracted values
        against QR-encoded values and template requirements. Sensitive values are safely masked.
        """
        comparison_rows: List[Dict[str, Any]] = []

        # Standard list of fields to check
        fields_to_check = [
            ("name", "Name"),
            ("dob", "Date of Birth"),
            ("document_id", "Document ID / Number"),
            ("gender", "Gender"),
            ("address", "Address"),
            ("father_name", "Father's Name"),
            ("issue_date", "Issue Date"),
            ("expiry_date", "Expiry Date")
        ]

        expected_fields_meta = {f.get("name"): f for f in template_profile.get("expected_fields", [])}

        for key, label in fields_to_check:
            ocr_val = ocr_fields.get(key)
            qr_val = qr_parsed.get(key) if qr_parsed else None
            is_expected = key in expected_fields_meta or key in ["name", "document_id", "dob"]

            if not ocr_val and not qr_val:
                if is_expected and template_profile.get("expected_fields"):
                    # Check if template explicitly marked it required
                    field_cfg = expected_fields_meta.get(key, {})
                    if field_cfg.get("required", False):
                        comparison_rows.append({
                            "field": label,
                            "extracted_value": "NOT DETECTED",
                            "reference_or_qr_value": "NOT DETECTED",
                            "result": "NOT FOUND",
                            "details": "Expected mandatory field was not located in visible document or QR."
                        })
                continue

            # Format and mask values
            display_ocr = mask_identifier(str(ocr_val)) if ocr_val else "NOT FOUND"
            display_qr = mask_identifier(str(qr_val)) if qr_val else "NOT AVAILABLE"

            # Determine match status
            if ocr_val and qr_val:
                clean_ocr = self._normalize(ocr_val)
                clean_qr = self._normalize(qr_val)

                if clean_ocr == clean_qr:
                    result = "MATCH"
                    details = "Exact match between visible document text and QR code payload."
                elif clean_ocr in clean_qr or clean_qr in clean_ocr:
                    result = "PARTIAL MATCH"
                    details = "Substantial overlap between visible text and QR data."
                else:
                    result = "MISMATCH"
                    details = f"Discrepancy detected between visible value and QR value."
            elif ocr_val and not qr_val:
                result = "MATCH" if not template_profile.get("has_qr_code", True) else "PARTIAL MATCH"
                details = "Visible text extracted; QR code did not encode this specific field."
            else:
                result = "NOT FOUND"
                details = "Encoded in QR code but not detected in visible text."

            comparison_rows.append({
                "field": label,
                "extracted_value": display_ocr,
                "reference_or_qr_value": display_qr,
                "result": result,
                "details": details
            })

        return comparison_rows

    def _normalize(self, val: Any) -> str:
        s = str(val).strip().lower()
        # Remove separators, spaces, punctuation
        return re.sub(r'[\s\-_\/,\.:]', '', s)
