import cv2
import re
import numpy as np
from typing import Dict, Any, List, Optional

class BaseOCRProvider:
    def extract_words_and_lines(self, image: np.ndarray) -> Dict[str, Any]:
        raise NotImplementedError

class WinOCRProvider(BaseOCRProvider):
    def __init__(self):
        try:
            import winocr
            self.winocr = winocr
            self.available = True
        except ImportError:
            self.available = False

    def extract_words_and_lines(self, image: np.ndarray) -> Dict[str, Any]:
        if not self.available:
            return {"lines": [], "text": "", "words": []}
        try:
            res = self.winocr.recognize_cv2_sync(image, 'en')
            line_texts = [line_obj.get('text', '') for line_obj in res.get('lines', [])]
            raw_text = "\n".join(line_texts) if line_texts else res.get('text', '')
            lines_data = []
            all_words = []
            
            for line_obj in res.get('lines', []):
                line_text = line_obj.get('text', '')
                words_list = []
                for w in line_obj.get('words', []):
                    b = w.get('bounding_rect', {})
                    word_dict = {
                        "text": w.get('text', ''),
                        "box": {
                            "x": float(b.get('x', 0)),
                            "y": float(b.get('y', 0)),
                            "width": float(b.get('width', 0)),
                            "height": float(b.get('height', 0))
                        }
                    }
                    words_list.append(word_dict)
                    all_words.append(word_dict)
                lines_data.append({
                    "text": line_text,
                    "words": words_list
                })
            return {
                "text": raw_text,
                "lines": lines_data,
                "words": all_words,
                "provider": "WinOCR"
            }
        except Exception as e:
            print(f"WinOCR error: {e}")
            return {"lines": [], "text": "", "words": [], "provider": "WinOCR"}

class TesseractOCRProvider(BaseOCRProvider):
    def __init__(self):
        try:
            import pytesseract
            self.pytesseract = pytesseract
            # Verify availability
            self.pytesseract.get_tesseract_version()
            self.available = True
        except Exception:
            self.available = False

    def extract_words_and_lines(self, image: np.ndarray) -> Dict[str, Any]:
        if not self.available:
            return {"lines": [], "text": "", "words": []}
        try:
            data = self.pytesseract.image_to_data(image, output_type=self.pytesseract.Output.DICT)
            raw_text = self.pytesseract.image_to_string(image)
            words = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 30 and data['text'][i].strip():
                    words.append({
                        "text": data['text'][i],
                        "box": {
                            "x": float(data['left'][i]),
                            "y": float(data['top'][i]),
                            "width": float(data['width'][i]),
                            "height": float(data['height'][i])
                        },
                        "conf": float(data['conf'][i])
                    })
            return {
                "text": raw_text,
                "words": words,
                "provider": "Tesseract"
            }
        except Exception as e:
            print(f"Tesseract error: {e}")
            return {"lines": [], "text": "", "words": [], "provider": "Tesseract"}

class OCRService:
    def __init__(self):
        # Register providers
        self.providers: List[BaseOCRProvider] = []
        win_p = WinOCRProvider()
        if win_p.available:
            self.providers.append(win_p)
        tess_p = TesseractOCRProvider()
        if tess_p.available:
            self.providers.append(tess_p)

    def extract(self, image_path: str, doc_type: str = "Aadhaar") -> Dict[str, Any]:
        image = cv2.imread(image_path)
        if image is None:
            return {"text": "", "fields": {}, "text_boxes": [], "provider": "None"}

        ocr_result = {"text": "", "lines": [], "words": [], "provider": "None"}
        
        for provider in self.providers:
            res = provider.extract_words_and_lines(image)
            if res.get("text") and len(res.get("text").strip()) > 10:
                ocr_result = res
                break

        full_text = ocr_result.get("text", "")
        text_boxes = ocr_result.get("words", [])
        
        # Parse document fields based on type
        extracted_fields = self._parse_fields(full_text, doc_type, text_boxes)

        return {
            "text": full_text,
            "provider": ocr_result.get("provider", "Fallback"),
            "extracted_fields": extracted_fields,
            "text_boxes": text_boxes
        }

    def _parse_fields(self, text: str, doc_type: str, words: List[Dict[str, Any]]) -> Dict[str, Any]:
        fields: Dict[str, Any] = {}
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Common regular expressions
        dob_pattern = r'(?:DOB|Date of Birth|D\.O\.B|Birth)[\s:]*([0-9]{2}[/-][0-9]{2}[/-][0-9]{4})'
        date_general_pattern = r'\b([0-9]{2}[/-][0-9]{2}[/-][0-9]{4})\b'
        gender_pattern = r'\b(MALE|FEMALE|TRANSGENDER|पुरुष|महिला)\b'

        # 1. Date of birth
        dob_match = re.search(dob_pattern, text, re.IGNORECASE)
        if dob_match:
            fields["dob"] = dob_match.group(1).replace("-", "/")
        else:
            dates = re.findall(date_general_pattern, text)
            if dates:
                fields["dob"] = dates[0].replace("-", "/")

        # 2. Gender
        gender_match = re.search(gender_pattern, text, re.IGNORECASE)
        if gender_match:
            fields["gender"] = gender_match.group(1).upper()

        # Specific document parsers
        if "aadhaar" in doc_type.lower():
            # 12-digit UID
            uid_match = re.search(r'\b([0-9]{4}[\s-][0-9]{4}[\s-][0-9]{4})\b', text)
            if uid_match:
                fields["document_id"] = uid_match.group(1).replace("-", " ")
            else:
                # Continuous 12 digits
                c_match = re.search(r'\b([0-9]{12})\b', text)
                if c_match:
                    num = c_match.group(1)
                    fields["document_id"] = f"{num[:4]} {num[4:8]} {num[8:]}"

            # Name heuristic: line before DOB or after Government of India / Unique Identification
            name = self._find_name_near_dob(lines)
            if name:
                fields["name"] = name
                
            # Address heuristic
            addr = self._find_address(lines)
            if addr:
                fields["address"] = addr

        elif "pan" in doc_type.lower():
            # 10-character PAN: 5 letters, 4 digits, 1 letter
            pan_match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', text)
            if pan_match:
                fields["document_id"] = pan_match.group(1)

            # Name and Father's Name on PAN
            name = self._find_pan_names(lines)
            if name.get("name"):
                fields["name"] = name["name"]
            if name.get("father_name"):
                fields["father_name"] = name["father_name"]

        elif "driving" in doc_type.lower():
            # DL number pattern e.g. DL-1420110012345 or similar
            dl_match = re.search(r'\b([A-Z]{2}[-\s]?[0-9]{2,3}[-\s]?[0-9]{7,11})\b', text)
            if dl_match:
                fields["document_id"] = dl_match.group(1)
            name = self._find_name_near_dob(lines)
            if name:
                fields["name"] = name

        elif "passport" in doc_type.lower():
            # Passport number: 1 letter + 7 digits
            p_match = re.search(r'\b([A-Z][0-9]{7})\b', text)
            if p_match:
                fields["document_id"] = p_match.group(1)
            name = self._find_name_near_dob(lines)
            if name:
                fields["name"] = name

        elif "voter" in doc_type.lower():
            epic_match = re.search(r'\b([A-Z]{3}[0-9]{7})\b', text)
            if epic_match:
                fields["document_id"] = epic_match.group(1)
            name = self._find_name_near_dob(lines)
            if name:
                fields["name"] = name

        elif "certificate" in doc_type.lower():
            cert_match = re.search(r'(?:Certificate\s*(?:No|Number)|Reg\s*No)[\s.:]*([A-Z0-9/-]+)', text, re.IGNORECASE)
            if cert_match:
                fields["document_id"] = cert_match.group(1)
            name = self._find_name_near_dob(lines)
            if name:
                fields["name"] = name

        else:
            # Generic fallback
            name = self._find_name_near_dob(lines)
            if name:
                fields["name"] = name
            # Any alphanumeric id
            id_match = re.search(r'\b([A-Z0-9]{8,14})\b', text)
            if id_match:
                fields["document_id"] = id_match.group(1)

        return fields

    def _find_name_near_dob(self, lines: List[str]) -> Optional[str]:
        ignore_keywords = [
            "government", "india", "unique", "identification", "authority", "enrollment",
            "income", "tax", "department", "permanent", "account", "republic", "driving",
            "licence", "transport", "certificate", "date", "birth", "gender", "male",
            "female", "download", "issue", "help", "www", "father", "signature"
        ]
        for idx, line in enumerate(lines):
            if re.search(r'(?:DOB|Date of Birth|Birth)', line, re.IGNORECASE):
                # Name is very often on the preceding non-empty line
                if idx > 0:
                    candidate = lines[idx - 1].strip()
                    cand_lower = candidate.lower()
                    if not any(k in cand_lower for k in ignore_keywords) and len(candidate) > 2:
                        return candidate.title()
        # Fallback: first capitalized alphabetic line without header words
        for line in lines:
            cand = line.strip()
            cand_lower = cand.lower()
            if re.match(r'^[A-Za-z\s\.\'-]{3,35}$', cand):
                if not any(k in cand_lower for k in ignore_keywords):
                    return cand.title()
        return None

    def _find_pan_names(self, lines: List[str]) -> Dict[str, str]:
        res = {}
        for idx, line in enumerate(lines):
            if "name" in line.lower() and idx + 1 < len(lines):
                candidate = lines[idx + 1].strip()
                if not res.get("name") and len(candidate) > 2:
                    res["name"] = candidate.title()
            if "father" in line.lower() and idx + 1 < len(lines):
                cand = lines[idx + 1].strip()
                if len(cand) > 2:
                    res["father_name"] = cand.title()
        return res

    def _find_address(self, lines: List[str]) -> Optional[str]:
        addr_lines = []
        capturing = False
        for line in lines:
            if "address" in line.lower() or "s/o" in line.lower() or "w/o" in line.lower() or "c/o" in line.lower():
                capturing = True
            if capturing:
                addr_lines.append(line)
                if len(addr_lines) >= 3:
                    break
        if addr_lines:
            return ", ".join(addr_lines)
        return None
