"""OCR abstraction layer for text recognition in images."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """A single OCR text detection."""

    text: str
    confidence: float
    bbox: tuple[int, int, int, int] | None = None  # x, y, w, h


class OCREngine(Protocol):
    """Protocol for OCR backends."""

    def recognize(self, image: np.ndarray) -> list[OCRResult]:
        """Run OCR on an image and return detected text regions.

        Args:
            image: BGR or grayscale image as a NumPy array.

        Returns:
            List of OCRResult with text, confidence, and optional bounding box.
        """
        ...


class TesseractEngine:
    """OCR engine backed by pytesseract + Tesseract."""

    def __init__(self, lang: str = "eng") -> None:
        self.lang = lang

    def recognize(self, image: np.ndarray) -> list[OCRResult]:
        """Run Tesseract OCR on an image.

        Args:
            image: BGR or grayscale image as a NumPy array.

        Returns:
            List of OCRResult for each detected text block.
        """
        import pytesseract

        data = pytesseract.image_to_data(image, lang=self.lang, output_type=pytesseract.Output.DICT)

        results = []
        for i, text in enumerate(data["text"]):
            text = text.strip()
            if not text:
                continue

            conf = float(data["conf"][i])
            if conf < 0:
                continue

            bbox = (
                int(data["left"][i]),
                int(data["top"][i]),
                int(data["width"][i]),
                int(data["height"][i]),
            )
            results.append(OCRResult(text=text, confidence=conf, bbox=bbox))

        logger.debug("Tesseract found %d text regions", len(results))
        return results
