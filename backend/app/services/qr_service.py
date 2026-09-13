import cv2
import json
import re
import numpy as np
from typing import Dict, Any, Optional

class QRService:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def decode(self, image_path: str) -> Dict[str, Any]:
        image = cv2.imread(image_path)
        if image is None:
            return {
                "detected": False,
                "readable": False,
                "data": None,
                "parsed_data": {},
                "qr_box": None,
                "visible_data_match": "NOT AVAILABLE",
                "discrepancies": []
            }

        # Attempt 1: Direct OpenCV QRCodeDetector
        data, points, _ = self.detector.detectAndDecode(image)
        
        # Attempt 2: If failed, try enhanced grayscale with CLAHE and thresholding
        if not data:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            data, points, _ = self.detector.detectAndDecode(enhanced)
            
        # Attempt 3: Try Otsu binarization
        if not data:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            data, points, _ = self.detector.detectAndDecode(thresh)

        detected = points is not None and len(points) > 0
        readable = bool(data and data.strip())
        
        qr_box = None
        if detected and points is not None:
            pts = points[0]
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
            qr_box = {
                "x": min(xs),
                "y": min(ys),
                "width": max(xs) - min(xs),
                "height": max(ys) - min(ys),
                "polygon": [[float(p[0]), float(p[1])] for p in pts]
            }

        parsed_data = {}
        if readable:
            parsed_data = self._parse_qr_payload(data)

        return {
            "detected": detected,
            "readable": readable,
            "raw_data": data if readable else None,
            "parsed_data": parsed_data,
            "qr_box": qr_box,
            "format": parsed_data.get("_format", "TEXT"),
            "authorized_verification": "NOT AVAILABLE"
        }

    def _parse_qr_payload(self, text: str) -> Dict[str, Any]:
        text_clean = text.strip()
        parsed: Dict[str, Any] = {}

        # 1. Try JSON
        if text_clean.startswith("{") and text_clean.endswith("}"):
            try:
                data = json.loads(text_clean)
                parsed = {k.lower(): v for k, v in data.items()}
                parsed["_format"] = "JSON"
                return self._normalize_keys(parsed)
            except Exception:
                pass

        # 2. Try XML (e.g. Aadhaar PrintLetterBarcodeData)
        if "<PrintLetterBarcodeData" in text_clean or "<?xml" in text_clean:
            parsed["_format"] = "XML_UIDAI"
            # Extract standard attributes: uid, name, dob, gender, co, yob, lm, loc, vtc, po, dist, subdist, state, pc
            uid_m = re.search(r'uid="([^"]+)"', text_clean)
            name_m = re.search(r'name="([^"]+)"', text_clean)
            dob_m = re.search(r'dob="([^"]+)"', text_clean)
            gender_m = re.search(r'gender="([^"]+)"', text_clean)
            
            if uid_m:
                parsed["document_id"] = uid_m.group(1)
            if name_m:
                parsed["name"] = name_m.group(1)
            if dob_m:
                parsed["dob"] = dob_m.group(1)
            if gender_m:
                parsed["gender"] = gender_m.group(1)
            return parsed

        # 3. Try Key: Value format
        kv_pairs = re.findall(r'([A-Za-z0-9_\s]+)[:=]\s*([^\n\r,;]+)', text_clean)
        if kv_pairs:
            for k, v in kv_pairs:
                clean_k = k.strip().lower().replace(" ", "_")
                parsed[clean_k] = v.strip()
            parsed["_format"] = "KEY_VALUE"
            return self._normalize_keys(parsed)

        # 4. Fallback text
        parsed["_format"] = "PLAIN_TEXT"
        parsed["content"] = text_clean
        return parsed

    def _normalize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        for k, v in data.items():
            if k in ["name", "full_name", "holder_name"]:
                normalized["name"] = str(v).title()
            elif k in ["dob", "date_of_birth", "birth_date"]:
                normalized["dob"] = str(v).replace("-", "/")
            elif k in ["gender", "sex"]:
                normalized["gender"] = str(v).upper()
            elif k in ["uid", "id", "pan", "document_id", "doc_no", "aadhaar", "passport_no"]:
                normalized["document_id"] = str(v)
            elif k in ["address", "addr"]:
                normalized["address"] = str(v)
            else:
                normalized[k] = v
        return normalized

    def cross_check(self, qr_parsed: Dict[str, Any], ocr_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-checks QR data against visible OCR extracted data."""
        if not qr_parsed:
            return {
                "match_status": "NOT AVAILABLE",
                "score": 50.0,
                "discrepancies": [],
                "comparison": []
            }

        discrepancies = []
        checks = []
        matches = 0
        total_checks = 0

        common_fields = ["name", "dob", "document_id", "gender"]
        for field in common_fields:
            qr_val = str(qr_parsed.get(field, "")).strip().lower()
            ocr_val = str(ocr_fields.get(field, "")).strip().lower()

            if qr_val and ocr_val:
                total_checks += 1
                # Clean spaces/punctuation for id comparison
                c_qr = re.sub(r'[\s\-_/]', '', qr_val)
                c_ocr = re.sub(r'[\s\-_/]', '', ocr_val)

                if c_qr == c_ocr or qr_val in ocr_val or ocr_val in qr_val:
                    matches += 1
                    checks.append({
                        "field": field.replace("_", " ").title(),
                        "qr_val": qr_parsed.get(field),
                        "ocr_val": ocr_fields.get(field),
                        "status": "MATCH"
                    })
                else:
                    discrepancies.append(
                        f"Visible document {field.replace('_', ' ').title()} '{ocr_fields.get(field)}' differs from QR encoded '{qr_parsed.get(field)}'"
                    )
                    checks.append({
                        "field": field.replace("_", " ").title(),
                        "qr_val": qr_parsed.get(field),
                        "ocr_val": ocr_fields.get(field),
                        "status": "MISMATCH"
                    })
            elif qr_val or ocr_val:
                checks.append({
                    "field": field.replace("_", " ").title(),
                    "qr_val": qr_parsed.get(field, "N/A"),
                    "ocr_val": ocr_fields.get(field, "N/A"),
                    "status": "PARTIAL"
                })

        if total_checks == 0:
            match_status = "NOT AVAILABLE"
            score = 70.0
        elif len(discrepancies) > 0:
            match_status = "MISMATCH"
            score = max(0.0, 30.0 - len(discrepancies) * 15.0)
        else:
            match_status = "MATCH"
            score = 100.0

        return {
            "match_status": match_status,
            "score": score,
            "discrepancies": discrepancies,
            "comparison": checks
        }
