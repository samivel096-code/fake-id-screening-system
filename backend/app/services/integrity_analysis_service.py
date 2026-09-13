import cv2
import numpy as np
import os
from typing import Dict, Any, List, Optional

class IntegrityAnalysisService:
    def __init__(self, ela_quality: int = 90, ela_scale: int = 15):
        self.ela_quality = ela_quality
        self.ela_scale = ela_scale

    def analyze(self, image_path: str, output_dir: str = "uploads") -> Dict[str, Any]:
        img = cv2.imread(image_path)
        if img is None:
            return {
                "integrity_score": 0.0,
                "indicator_count": 1,
                "indicators": ["Unable to perform integrity analysis on corrupt or unreadable image."],
                "suspicious_regions": []
            }

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        indicators: List[str] = []
        suspicious_regions: List[Dict[str, Any]] = []

        # 1. Error Level Analysis (ELA)
        # Resave as JPEG with fixed quality and compare difference
        ela_diff = self._compute_ela(img)
        ela_gray = cv2.cvtColor(ela_diff, cv2.COLOR_BGR2GRAY)
        
        # High contrast spots in ELA signify differing compression histories (tampering/copy-paste)
        # Suppress normal graphic lines, text glyphs, and borders by morphological edge dilation
        edges = cv2.Canny(gray, 50, 150)
        kernel_text = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        edges_dilated = cv2.dilate(edges, kernel_text, iterations=2)
        
        # Suppress edge ringing on normal text
        ela_clean = ela_gray.copy()
        ela_clean[edges_dilated > 0] = 0

        _, ela_thresh = cv2.threshold(ela_clean, 50, 255, cv2.THRESH_BINARY)
        # Remove small noise specks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        ela_morph = cv2.morphologyEx(ela_thresh, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(ela_morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        tamper_clusters = 0
        for c in contours:
            area = cv2.contourArea(c)
            # Filter out thin border lines and tiny noise
            bx, by, bw, bh = cv2.boundingRect(c)
            aspect = bw / float(bh) if bh > 0 else 1.0
            
            # Skip horizontal or vertical lines (borders / dividers)
            if aspect > 7.0 or aspect < 0.14 or bw < 25 or bh < 18:
                continue

            # Significant compact patch with anomalous compression
            if (w * h * 0.005) < area < (w * h * 0.25):
                tamper_clusters += 1
                
                # Check location semantics: top (header/photo), middle (name/date), bottom (id/signature)
                region_type = "Critical Text Field"
                if bx > w * 0.60 and by < h * 0.5:
                    region_type = "Photograph / Emblem Region"
                elif by < h * 0.22:
                    region_type = "Header / Organization Label"
                elif by > h * 0.65:
                    region_type = "Identifier / Signature Region"

                suspicious_regions.append({
                    "id": f"integrity_anomaly_{len(suspicious_regions) + 1}",
                    "type": "INTEGRITY_ANOMALY",
                    "severity": "HIGH" if area > (w * h * 0.015) else "MEDIUM",
                    "title": f"Unusual image compression in {region_type}",
                    "description": f"Potential alteration indicators detected in {region_type}. Manual review recommended.",
                    "region": {
                        "x": float(bx),
                        "y": float(by),
                        "width": float(bw),
                        "height": float(bh),
                        "x_ratio": round(bx / float(w), 3),
                        "y_ratio": round(by / float(h), 3),
                        "w_ratio": round(bw / float(w), 3),
                        "h_ratio": round(bh / float(h), 3)
                    }
                })

        # Also detect any colored bounding splice boxes (such as [SPLICED PATCH])
        # In tampered document, check for rectangular patches in the middle demographic zone
        demographic_zone = img[int(h * 0.25):int(h * 0.65), int(w * 0.25):int(w * 0.75)]
        if demographic_zone.size > 0:
            # Check for localized contrast box borders
            d_gray = cv2.cvtColor(demographic_zone, cv2.COLOR_BGR2GRAY)
            d_edges = cv2.Canny(d_gray, 50, 150)
            d_contours, _ = cv2.findContours(d_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for dc in d_contours:
                d_area = cv2.contourArea(dc)
                if (w * h * 0.008) < d_area < (w * h * 0.08):
                    peri = cv2.arcLength(dc, True)
                    approx = cv2.approxPolyDP(dc, 0.04 * peri, True)
                    if len(approx) == 4:
                        dx, dy, dw, dh = cv2.boundingRect(dc)
                        real_x = int(w * 0.25) + dx
                        real_y = int(h * 0.25) + dy
                        # Check if not already covered
                        already_flagged = any(abs(sr["region"]["x"] - real_x) < 30 and abs(sr["region"]["y"] - real_y) < 30 for sr in suspicious_regions)
                        if not already_flagged:
                            tamper_clusters += 1
                            suspicious_regions.append({
                                "id": f"integrity_anomaly_{len(suspicious_regions) + 1}",
                                "type": "INTEGRITY_ANOMALY",
                                "severity": "HIGH",
                                "title": "Spliced text box detected in Demographic Information",
                                "description": "Bounding box border discrepancy indicates inserted or replaced text patch. Manual review recommended.",
                                "region": {
                                    "x": float(real_x),
                                    "y": float(real_y),
                                    "width": float(dw),
                                    "height": float(dh),
                                    "x_ratio": round(real_x / float(w), 3),
                                    "y_ratio": round(real_y / float(h), 3),
                                    "w_ratio": round(dw / float(w), 3),
                                    "h_ratio": round(dh / float(h), 3)
                                }
                            })

        if tamper_clusters > 0:
            indicators.append(f"Detected {tamper_clusters} region(s) with compression or structural discrepancies consistent with digital editing.")

        # 2. Local Noise Inconsistency / Resolution Inconsistency
        grid_rows, grid_cols = 4, 4
        cell_h, cell_w = h // grid_rows, w // grid_cols
        variances = []
        
        for r in range(grid_rows):
            for c in range(grid_cols):
                cell = gray[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w]
                var = float(cv2.Laplacian(cell, cv2.CV_64F).var())
                variances.append(var)

        std_of_variances = float(np.std(variances))
        mean_variance = float(np.mean(variances)) + 1e-5
        noise_inconsistency_ratio = std_of_variances / mean_variance

        if noise_inconsistency_ratio > 2.5:
            indicators.append("Significant local sharpness/noise inconsistency across document zones (potential copy-paste insertion).")
            max_idx = int(np.argmax(variances))
            mr = max_idx // grid_cols
            mc = max_idx % grid_cols
            suspicious_regions.append({
                "id": f"noise_anomaly_{len(suspicious_regions) + 1}",
                "type": "INTEGRITY_ANOMALY",
                "severity": "MEDIUM",
                "title": "Abnormal sharpness contrast in document section",
                "description": "This sub-section has sharpness levels inconsistent with neighboring document areas.",
                "region": {
                    "x": float(mc * cell_w),
                    "y": float(mr * cell_h),
                    "width": float(cell_w),
                    "height": float(cell_h),
                    "x_ratio": round((mc * cell_w) / float(w), 3),
                    "y_ratio": round((mr * cell_h) / float(h), 3),
                    "w_ratio": round(cell_w / float(w), 3),
                    "h_ratio": round(cell_h / float(h), 3)
                }
            })

        # Calculate integrity score
        penalty = (len(suspicious_regions) * 22.0)
        integrity_score = round(max(20.0, min(99.0, 98.0 - penalty)), 1)

        if len(indicators) == 0:
            indicators.append("No significant alteration indicators detected.")

        return {
            "integrity_score": integrity_score,
            "indicator_count": len(suspicious_regions),
            "indicators": indicators,
            "suspicious_regions": suspicious_regions,
            "noise_inconsistency_ratio": round(noise_inconsistency_ratio, 2)
        }

    def _compute_ela(self, image: np.ndarray) -> np.ndarray:
        """Computes Error Level Analysis (ELA) image difference."""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.ela_quality]
        _, encimg = cv2.imencode('.jpg', image, encode_param)
        resaved = cv2.imdecode(encimg, 1)
        
        diff = cv2.absdiff(image, resaved)
        # Scale difference so subtle variations are clearly visible
        scaled_diff = cv2.convertScaleAbs(diff, alpha=self.ela_scale, beta=0)
        return scaled_diff
