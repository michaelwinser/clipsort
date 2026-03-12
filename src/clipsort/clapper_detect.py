"""Clapper board detection via visual analysis and OCR."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import numpy as np

from clipsort.ocr import OCREngine, OCRResult
from clipsort.parser import ClipInfo

logger = logging.getLogger(__name__)

# Patterns to extract scene/take from OCR text (applied to joined text)
_SCENE_PATTERNS = [
    re.compile(r"SCENE\s*:?\s*(\d+)", re.I),
    re.compile(r"SC\s*:?\s*(\d+)", re.I),
    re.compile(r"\bS(\d+)", re.I),
]
_TAKE_PATTERNS = [
    re.compile(r"TAKE\s*:?\s*(\d+)", re.I),
    re.compile(r"TK\s*:?\s*(\d+)", re.I),
    re.compile(r"\bT(\d+)", re.I),
]
# Combined short forms: "S3T2", "S3 T2"
_COMBINED_PATTERN = re.compile(r"S(\d+)\s*T(\d+)", re.I)


class ClapperDetector:
    """Detect clapper boards in video frames and extract scene/take via OCR."""

    def __init__(
        self,
        ocr_engine: OCREngine,
        scan_seconds: int = 10,
        sample_rate: int = 2,
        min_confidence: float = 30.0,
    ) -> None:
        self.ocr_engine = ocr_engine
        self.scan_seconds = scan_seconds
        self.sample_rate = sample_rate
        self.min_confidence = min_confidence

    def detect_frame(self, frame: np.ndarray) -> ClipInfo | None:
        """Detect clapper board in a single frame.

        Args:
            frame: BGR image as a NumPy array.

        Returns:
            ClipInfo if a clapper board with readable text is found, None otherwise.
        """
        region = self._find_slate_region(frame)
        if region is None:
            return None

        preprocessed = self._preprocess_slate(region)
        ocr_results = self.ocr_engine.recognize(preprocessed)
        return self._parse_ocr_results(ocr_results)

    def detect(self, video_path: Path) -> ClipInfo | None:
        """Scan video for a clapper board and extract scene/take info.

        Args:
            video_path: Path to the video file.

        Returns:
            ClipInfo if a clapper board with readable text is found, None otherwise.
        """
        import cv2

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.warning("Cannot open video: %s", video_path)
            return None

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        max_frame = min(total_frames, int(fps * self.scan_seconds))
        frame_interval = max(1, int(fps / self.sample_rate))

        best_result: ClipInfo | None = None
        best_confidence = 0.0

        for frame_idx in range(0, max_frame, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            info = self.detect_frame(frame)

            if info is not None and info.confidence > best_confidence:
                best_result = info
                best_confidence = info.confidence
                if best_confidence >= 80.0:
                    # Good enough — stop early
                    break

        cap.release()

        if best_result is not None:
            logger.debug("Clapper detected in %s: scene=%d", video_path.name, best_result.scene)

        return best_result

    def _find_slate_region(self, frame: np.ndarray) -> np.ndarray | None:
        """Find the best rectangular slate-like region in a frame.

        Uses edge detection and contour analysis to find high-contrast
        rectangular regions that could be clapper boards.

        Returns:
            Cropped image of the best candidate region, or None.
        """
        import cv2

        h, w = frame.shape[:2]
        min_area = h * w * 0.02  # Slate must be at least 2% of frame
        max_area = h * w * 0.9  # And at most 90%

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Dilate to close gaps in edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_score = 0.0
        best_rect = None

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area or area > max_area:
                continue

            # Approximate the contour to a polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

            if len(approx) != 4:
                continue

            x, y, rw, rh = cv2.boundingRect(approx)
            if rh == 0:
                continue

            aspect = rw / rh
            # Clapper boards are wider than tall, roughly 4:3 to 2:1
            if aspect < 0.8 or aspect > 2.5:
                continue

            # Score by area (bigger is likely more prominent) and aspect ratio
            aspect_score = 1.0 - abs(aspect - 1.33) / 1.33  # Ideal ~4:3
            area_score = area / (h * w)

            # Check internal contrast — slates are high-contrast
            roi = gray[y : y + rh, x : x + rw]
            contrast = float(np.std(roi))
            contrast_score = min(contrast / 80.0, 1.0)

            score = aspect_score * 0.3 + area_score * 0.3 + contrast_score * 0.4

            if score > best_score:
                best_score = score
                best_rect = (x, y, rw, rh)

        if best_rect is None:
            return None

        x, y, rw, rh = best_rect
        return frame[y : y + rh, x : x + rw]

    def _preprocess_slate(self, region: np.ndarray) -> np.ndarray:
        """Preprocess a slate region for better OCR accuracy.

        Applies CLAHE contrast enhancement and converts to grayscale.
        """
        import cv2

        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if len(region.shape) == 3 else region

        # CLAHE for adaptive contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        return enhanced

    def _parse_ocr_results(self, results: list[OCRResult]) -> ClipInfo | None:
        """Parse OCR results to extract scene and take numbers.

        Looks for patterns like "SCENE 3", "SC 3", "TAKE 2", "TK 2",
        "S3T2", etc.

        Args:
            results: OCR results from the engine.

        Returns:
            ClipInfo if scene info is found, None otherwise.
        """
        if not results:
            return None

        # Filter low-confidence results
        good_results = [r for r in results if r.confidence >= self.min_confidence]
        if not good_results:
            return None

        # Join all text for pattern matching
        full_text = " ".join(r.text for r in good_results)
        avg_confidence = sum(r.confidence for r in good_results) / len(good_results)

        # Try combined pattern first (S3T2)
        m = _COMBINED_PATTERN.search(full_text)
        if m:
            return ClipInfo(
                scene=int(m.group(1)),
                take=int(m.group(2)),
                confidence=avg_confidence,
                method="ocr",
            )

        # Try separate scene and take patterns
        scene = None
        take = None

        for pattern in _SCENE_PATTERNS:
            m = pattern.search(full_text)
            if m:
                scene = int(m.group(1))
                break

        for pattern in _TAKE_PATTERNS:
            m = pattern.search(full_text)
            if m:
                take = int(m.group(1))
                break

        if scene is not None:
            return ClipInfo(
                scene=scene,
                take=take,
                confidence=avg_confidence,
                method="ocr",
            )

        return None
