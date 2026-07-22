"""Loss-aware conversion of OCR geometry into LayoutLMv3's 0..1000 space."""

from __future__ import annotations

from typing import Sequence


def layoutlm_bbox(quad: Sequence[float], page_width: int, page_height: int) -> list[int]:
    """Convert an OCR quadrilateral to clamped LayoutLMv3 axis-aligned bbox.

    Original quadrilaterals must remain in the evidence record. This projection
    is model input only and must never replace source geometry.
    """
    if len(quad) != 8:
        raise ValueError("quad must contain 8 coordinates")
    if page_width <= 0 or page_height <= 0:
        raise ValueError("page dimensions must be positive")
    xs, ys = quad[0::2], quad[1::2]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)

    def scale(value: float, size: int) -> int:
        return max(0, min(1000, round(value * 1000 / size)))

    return [scale(left, page_width), scale(top, page_height), scale(right, page_width), scale(bottom, page_height)]
