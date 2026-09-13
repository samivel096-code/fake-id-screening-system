import cv2
import numpy as np
import os
from typing import Tuple, Optional, Dict, Any

class DocumentDetectionService:
    def __init__(self, target_width: int = 1000, target_height: int = 650):
        self.target_width = target_width
        self.target_height = target_height

    def process(self, image_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Detects document corners, applies perspective transform (deskew/dewarp),
        normalizes the canvas dimensions, and saves normalized and thumbnail images.
        """
        os.makedirs(output_dir, exist_ok=True)
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Could not read image file."}

        orig_h, orig_w = img.shape[:2]
        
        # 1. Edge detection for finding document contours
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 30, 150)
        
        # Dilate edges slightly to close gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edged, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        doc_contour = None
        min_area = orig_w * orig_h * 0.20  # Document must take at least 20% of image
        
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4 and cv2.contourArea(c) > min_area:
                doc_contour = approx
                break

        if doc_contour is not None:
            warped = self._four_point_transform(img, doc_contour.reshape(4, 2))
            detected_quad = True
        else:
            # Fallback: find bounding box of largest component or use full image if already cropped
            detected_quad = False
            warped = img.copy()

        # Resize to standardized normalized dimensions for consistent template comparison
        h_w, w_w = warped.shape[:2]
        # Decide orientation based on aspect ratio
        if h_w > w_w:
            # Vertical document (e.g. portrait certificate)
            normalized = cv2.resize(warped, (self.target_height, self.target_width), interpolation=cv2.INTER_AREA)
        else:
            # Horizontal card/certificate
            normalized = cv2.resize(warped, (self.target_width, self.target_height), interpolation=cv2.INTER_AREA)

        # Save normalized image
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        norm_filename = f"{base_name}_normalized.png"
        norm_path = os.path.join(output_dir, norm_filename)
        cv2.imwrite(norm_path, normalized)

        # Generate thumbnail
        thumb = cv2.resize(normalized, (300, int(300 * (normalized.shape[0] / normalized.shape[1]))))
        thumb_filename = f"{base_name}_thumb.png"
        thumb_path = os.path.join(output_dir, thumb_filename)
        cv2.imwrite(thumb_path, thumb)

        return {
            "success": True,
            "detected_quad": detected_quad,
            "normalized_path": norm_path,
            "thumbnail_path": thumb_path,
            "normalized_width": normalized.shape[1],
            "normalized_height": normalized.shape[0],
            "aspect_ratio": round(normalized.shape[1] / float(normalized.shape[0]), 3)
        }

    def _four_point_transform(self, image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        rect = self._order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return warped

    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
