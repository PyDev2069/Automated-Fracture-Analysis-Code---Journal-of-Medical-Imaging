
import numpy as np
import cv2
import sys, types

_ai_doctor = types.ModuleType("utils.ai_doctor")
_ai_doctor.clean_text = lambda text: text
sys.modules.setdefault("utils.ai_doctor", _ai_doctor)

_pdf_styles = types.ModuleType("utils.pdf_styles")
_pdf_styles.register_fonts = lambda: None
from reportlab.lib.styles import getSampleStyleSheet
_pdf_styles.get_styles = getSampleStyleSheet
sys.modules.setdefault("utils.pdf_styles", _pdf_styles)
from utils.image_processing import canny_on_gray, analyze_contours


class TestCannyOnGray:
    def test_output_shapes(self):       
        roi = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        gray, edges = canny_on_gray(roi)
        assert gray.shape == (100, 100)
        assert edges.shape == (100, 100)

    def test_edges_binary(self):
        
        roi = np.random.randint(0, 255, (80, 80, 3), dtype=np.uint8)
        _, edges = canny_on_gray(roi)
        unique_vals = set(np.unique(edges))
        assert unique_vals.issubset({0, 255})


class TestAnalyzeContours:
    def _make_dummy_image(self, h=200, w=200):
        return np.zeros((h, w, 3), dtype=np.uint8)

    def test_returns_required_keys(self):        
        roi = np.zeros((50, 50, 3), dtype=np.uint8)
        img_detail = self._make_dummy_image()
        result = analyze_contours(roi, 0, 0, 50, 50, img_detail, 0.2646)
        for key in ("Shift (px)", "Shift (mm)", "Shape Diff"):
            assert key in result

    def test_fallback_when_no_contours(self):        
        roi = np.zeros((60, 60, 3), dtype=np.uint8)  
        img_detail = self._make_dummy_image()
        result = analyze_contours(roi, 10, 10, 70, 70, img_detail, 0.2646)        
        assert result["Shift (px)"] is not None
        assert result["Shift (mm)"] is not None
        assert result["Shape Diff"] == "N/A"

    def test_mm_conversion(self):        
        roi = np.zeros((60, 60, 3), dtype=np.uint8)
        img_detail = self._make_dummy_image()
        px_to_mm = 0.2646
        result = analyze_contours(roi, 0, 0, 60, 60, img_detail, px_to_mm)
        if result["Shift (px)"] is not None:
            expected_mm = round(result["Shift (px)"] * px_to_mm, 2)
            assert abs(result["Shift (mm)"] - expected_mm) < 0.01
