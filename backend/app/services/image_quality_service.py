import cv2
import numpy as np
from typing import Dict, Any, List

class ImageQualityService:
    def __init__(self,
                 min_width: int = 600,
                 min_height: int = 400,
                 min_blur_score: float = 85.0,
                 min_brightness: float = 40.0,
                 max_brightness: float = 230.0,
                 min_contrast: float = 25.0,
                 max_glare_ratio: float = 0.12):
        self.min_width = min_width
        self.min_height = min_height
        self.min_blur_score = min_blur_score
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_contrast = min_contrast
        self.max_glare_ratio = max_glare_ratio

    def analyze(self, image_path: str) -> Dict[str, Any]:
        image = cv2.imread(image_path)
        if image is None:
            return {
                "acceptable": False,
                "summary": "The uploaded document could not be decoded as a valid image.",
                "blur_score": 0.0,
                "brightness": 0.0,
                "contrast": 0.0,
                "width": 0,
                "height": 0,
                "aspect_ratio": 0.0,
                "reasons": ["Unreadable image file or corrupt format."],
                "checks": {}
            }

        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Blur Analysis using Laplacian Variance
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        # 2. Brightness & Contrast
        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))
        
        # 3. Glare Analysis (percentage of overexposed pixels > 250)
        glare_pixels = np.sum(gray >= 250)
        glare_ratio = float(glare_pixels / (h * w))
        
        # 4. Shadow Analysis (percentage of underexposed pixels < 20)
        shadow_pixels = np.sum(gray <= 20)
        shadow_ratio = float(shadow_pixels / (h * w))
        
        # 5. Aspect ratio
        aspect_ratio = round(w / float(h), 3) if h > 0 else 1.0

        # 6. Edge / Cropping density near borders
        border_thickness = max(5, int(min(h, w) * 0.02))
        top_b = gray[:border_thickness, :]
        bottom_b = gray[-border_thickness:, :]
        left_b = gray[:, :border_thickness]
        right_b = gray[:, -border_thickness:]
        
        border_edge_std = float(np.mean([np.std(top_b), np.std(bottom_b), np.std(left_b), np.std(right_b)]))
        
        # 7. Rotation estimation via Hough lines
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=max(50, w // 8), maxLineGap=10)
        estimated_tilt = 0.0
        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines[:20]:
                pts = np.array(line).flatten()
                if len(pts) == 4:
                    x1, y1, x2, y2 = pts
                    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                    angle_norm = (angle + 45) % 90 - 45
                    angles.append(angle_norm)
            if angles:
                estimated_tilt = float(np.median(angles))


        reasons: List[str] = []
        checks: Dict[str, Any] = {}

        # Evaluate checks
        # Resolution
        res_pass = (w >= self.min_width and h >= self.min_height) or (h >= self.min_width and w >= self.min_height)
        checks["resolution"] = {
            "status": "PASS" if res_pass else "FAIL",
            "score": round(min(100.0, ((w * h) / (800 * 500)) * 100), 1),
            "detail": f"{w}x{h} px"
        }
        if not res_pass:
            reasons.append("Resolution is too low (minimum 600x400 required)")

        # Blur
        blur_pass = laplacian_var >= self.min_blur_score
        blur_quality = min(100.0, round((laplacian_var / 250.0) * 100, 1))
        checks["blur"] = {
            "status": "PASS" if blur_pass else "FAIL",
            "score": round(laplacian_var, 1),
            "detail": f"Sharpness score {round(laplacian_var, 1)}"
        }
        if not blur_pass:
            reasons.append("Image is blurry; text is not sufficiently crisp")

        # Lighting / Brightness
        bright_pass = self.min_brightness <= brightness <= self.max_brightness
        checks["brightness"] = {
            "status": "PASS" if bright_pass else "FAIL",
            "score": round(brightness, 1),
            "detail": f"Mean luma {round(brightness, 1)}"
        }
        if brightness < self.min_brightness:
            reasons.append("Lighting is insufficient (image is too dark)")
        elif brightness > self.max_brightness:
            reasons.append("Image is overexposed (excessive lighting)")

        # Contrast
        contrast_pass = contrast >= self.min_contrast
        checks["contrast"] = {
            "status": "PASS" if contrast_pass else "FAIL",
            "score": round(contrast, 1),
            "detail": f"Standard deviation {round(contrast, 1)}"
        }
        if not contrast_pass:
            reasons.append("Contrast is too low for reliable OCR reading")

        # Glare
        glare_pass = glare_ratio <= self.max_glare_ratio
        checks["glare"] = {
            "status": "PASS" if glare_pass else "FAIL",
            "score": round((1.0 - glare_ratio) * 100, 1),
            "detail": f"{round(glare_ratio * 100, 1)}% specular reflection"
        }
        if not glare_pass:
            reasons.append("Excessive glare detected obscuring document areas")

        # Orientation / Rotation
        tilt_pass = abs(estimated_tilt) < 18.0
        checks["orientation"] = {
            "status": "PASS" if tilt_pass else "WARN",
            "score": round(max(0.0, 100 - abs(estimated_tilt) * 3), 1),
            "detail": f"Tilt ~{round(estimated_tilt, 1)}°"
        }
        if not tilt_pass and abs(estimated_tilt) > 35.0:
            reasons.append("Document is rotated or skewed excessively")

        acceptable = len(reasons) == 0

        # Calculate overall quality score (0-100)
        q_scores = [
            min(100.0, (w * h) / (800 * 500) * 100),
            min(100.0, (laplacian_var / 150.0) * 100),
            100.0 - abs(brightness - 128) * 0.7,
            min(100.0, (contrast / 50.0) * 100),
            max(0.0, (1.0 - glare_ratio) * 100),
            max(0.0, 100 - abs(estimated_tilt) * 2)
        ]
        overall_score = round(max(10.0, min(100.0, float(np.mean(q_scores)))), 1) if acceptable else round(max(10.0, min(55.0, float(np.mean(q_scores)))), 1)

        summary = "IMAGE QUALITY ACCEPTABLE" if acceptable else "DOCUMENT NOT CLEAR: The uploaded document is not sufficiently visible for reliable analysis."

        return {
            "acceptable": acceptable,
            "summary": summary,
            "overall_score": overall_score,
            "blur_score": round(laplacian_var, 2),
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "glare_ratio": round(glare_ratio, 3),
            "shadow_ratio": round(shadow_ratio, 3),
            "estimated_tilt": round(estimated_tilt, 2),
            "width": w,
            "height": h,
            "aspect_ratio": aspect_ratio,
            "reasons": reasons,
            "checks": checks
        }
