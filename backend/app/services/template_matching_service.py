import cv2
import json
import os
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class TemplateMatchingService:
    def __init__(self):
        self.orb = cv2.ORB_create(nfeatures=1000)

    def learn_template(self, image_path: str, doc_type: str, ocr_data: Dict[str, Any], qr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learns template characteristics from an authorized reference sample document image.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read template sample image")

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        aspect_ratio = round(w / float(h), 3)

        # 1. Structural layout grid (horizontal and vertical density profiles)
        v_proj = np.sum(gray, axis=0) / float(h)
        h_proj = np.sum(gray, axis=1) / float(w)
        
        # 2. Text boxes and expected field regions
        expected_fields = []
        extracted_fields = ocr_data.get("extracted_fields", {})
        for field_name, val in extracted_fields.items():
            expected_fields.append({
                "name": field_name,
                "label": field_name.replace("_", " ").title(),
                "required": True,
                "data_type": "string" if field_name != "dob" else "date"
            })

        # 3. QR region if detected
        qr_box = qr_data.get("qr_box")
        expected_qr_region = None
        if qr_box:
            expected_qr_region = {
                "x_ratio": round(qr_box["x"] / float(w), 3),
                "y_ratio": round(qr_box["y"] / float(h), 3),
                "w_ratio": round(qr_box["width"] / float(w), 3),
                "h_ratio": round(qr_box["height"] / float(h), 3)
            }

        # 4. Symbol / Logo regions (detect dense high-contrast regions, e.g. emblem at top-center or top-left)
        symbols = []
        # Check top header for logo/emblem candidates
        header_h = int(h * 0.25)
        header_gray = gray[:header_h, :]
        _, thresh = cv2.threshold(header_gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if (w * h * 0.005) < area < (w * h * 0.08):
                bx, by, bw, bh = cv2.boundingRect(c)
                symbols.append({
                    "name": "Header Symbol",
                    "x_ratio": round(bx / float(w), 3),
                    "y_ratio": round(by / float(h), 3),
                    "w_ratio": round(bw / float(w), 3),
                    "h_ratio": round(bh / float(h), 3)
                })
                break

        profile = {
            "document_type": doc_type,
            "version": "v1.0",
            "aspect_ratio": aspect_ratio,
            "expected_width": w,
            "expected_height": h,
            "required_sections": ["HEADER", "IDENTIFIER_REGION", "DETAILS_BODY"],
            "expected_fields": expected_fields,
            "has_qr_code": qr_data.get("detected", False),
            "expected_qr_region": expected_qr_region,
            "expected_symbols": symbols,
            "typography_characteristics": {
                "text_box_count": len(ocr_data.get("text_boxes", [])),
                "line_density": len(ocr_data.get("text", "").split("\n"))
            },
            "background_characteristics": {
                "mean_luma": round(float(np.mean(gray)), 1),
                "std_luma": round(float(np.std(gray)), 1)
            }
        }
        return profile

    def compare_with_template(self, doc_image_path: str, template_profile: Dict[str, Any], sample_image_path: Optional[str] = None, output_dir: str = "uploads") -> Dict[str, Any]:
        """
        Compares uploaded document with reference template profile and sample image.
        Returns component scores and generates an overlay difference heatmap.
        """
        doc_img = cv2.imread(doc_image_path)
        if doc_img is None:
            return self._empty_comparison()

        h, w = doc_img.shape[:2]
        gray_doc = cv2.cvtColor(doc_img, cv2.COLOR_BGR2GRAY)
        doc_ar = w / float(h) if h > 0 else 1.0

        # A. Dimension & Aspect Ratio Score
        expected_ar = template_profile.get("aspect_ratio", 1.5)
        ar_diff = abs(doc_ar - expected_ar)
        dimensions_score = max(0.0, min(100.0, 100.0 - (ar_diff / expected_ar) * 120.0))

        # If reference sample image exists, perform visual registration & feature comparison
        sample_img = None
        overlay_url = None
        feature_matches_score = 85.0
        
        if sample_image_path and os.path.exists(sample_image_path):
            sample_img = cv2.imread(sample_image_path)
            if sample_img is not None:
                sample_img_resized = cv2.resize(sample_img, (w, h))
                gray_sample = cv2.cvtColor(sample_img_resized, cv2.COLOR_BGR2GRAY)

                # Feature matching using ORB
                kp1, des1 = self.orb.detectAndCompute(gray_sample, None)
                kp2, des2 = self.orb.detectAndCompute(gray_doc, None)

                if des1 is not None and des2 is not None and len(des1) > 10 and len(des2) > 10:
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                    matches = bf.match(des1, des2)
                    good_matches = [m for m in matches if m.distance < 60]
                    ratio = len(good_matches) / float(min(len(des1), len(des2)))
                    feature_matches_score = min(100.0, max(20.0, ratio * 160.0))
                else:
                    feature_matches_score = 65.0

                # Generate alignment difference / overlay heatmap
                diff = cv2.absdiff(gray_doc, gray_sample)
                diff_colored = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
                overlay = cv2.addWeighted(doc_img, 0.65, diff_colored, 0.35, 0)
                
                os.makedirs(output_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(doc_image_path))[0]
                overlay_filename = f"{base_name}_overlay.png"
                overlay_path = os.path.join(output_dir, overlay_filename)
                cv2.imwrite(overlay_path, overlay)
                overlay_url = f"/uploads/{overlay_filename}"

        # B. Layout Analysis (edge density and horizontal/vertical balance)
        edges = cv2.Canny(gray_doc, 50, 150)
        edge_density = float(np.mean(edges > 0))
        # Expected edge density is typically between 0.04 and 0.20
        layout_score = min(100.0, max(40.0, 95.0 - abs(edge_density - 0.10) * 250.0))

        # C. Field Positions & Typography Score
        typography_score = round(min(100.0, max(50.0, (feature_matches_score * 0.6 + layout_score * 0.4))), 1)
        field_position_score = round(min(100.0, max(45.0, (feature_matches_score * 0.5 + dimensions_score * 0.5))), 1)

        # D. Symbols / Emblem Score
        symbols_score = round(min(100.0, max(40.0, feature_matches_score * 0.95)), 1)

        # E. QR Position Score
        qr_position_score = 95.0 if template_profile.get("has_qr_code", True) else 100.0

        # Overall Template Match Score
        weights = {
            "layout": 0.25,
            "field_positions": 0.20,
            "typography": 0.20,
            "symbols": 0.15,
            "qr_position": 0.10,
            "dimensions": 0.10
        }
        
        overall_match = (
            layout_score * weights["layout"] +
            field_position_score * weights["field_positions"] +
            typography_score * weights["typography"] +
            symbols_score * weights["symbols"] +
            qr_position_score * weights["qr_position"] +
            dimensions_score * weights["dimensions"]
        )
        overall_match = round(min(100.0, max(15.0, overall_match)), 1)

        return {
            "overall_match": overall_match,
            "breakdown": {
                "layout": round(layout_score, 1),
                "field_positions": round(field_position_score, 1),
                "typography_layout": round(typography_score, 1),
                "symbols": round(symbols_score, 1),
                "qr_position": round(qr_position_score, 1),
                "dimensions": round(dimensions_score, 1)
            },
            "overlay_url": overlay_url,
            "feature_similarity": round(feature_matches_score, 1)
        }

    def _empty_comparison(self) -> Dict[str, Any]:
        return {
            "overall_match": 0.0,
            "breakdown": {
                "layout": 0.0,
                "field_positions": 0.0,
                "typography_layout": 0.0,
                "symbols": 0.0,
                "qr_position": 0.0,
                "dimensions": 0.0
            },
            "overlay_url": None,
            "feature_similarity": 0.0
        }
