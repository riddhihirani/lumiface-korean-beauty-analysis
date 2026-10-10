import cv2
import numpy as np
import math
from typing import List, Dict, Any, Tuple, Optional

class SkinToneAnalyzer:
    """
    Analyzes skin color in CIE L*a*b* space, calculates Individual Typology Angle (ITA°),
    evaluates lighting white-balance cast, and classifies undertone and personal seasonal color.
    """

    def extract_skin_roi_pixels(self, img_bgr: np.ndarray, landmarks: List[Dict[str, float]]) -> Tuple[np.ndarray, Optional[str]]:
        """
        Extract skin pixels strictly from inner cheek and forehead landmark polygons,
        filtering out hair, lips, eyebrows, eyes, and specular highlights.
        """
        h, w, c = img_bgr.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        warning = None

        if len(landmarks) >= 468:
            # Inner cheek center points (excluding mouth and outer contour)
            left_cheek_idx = [117, 118, 101, 205, 207, 187, 123]
            right_cheek_idx = [346, 347, 330, 425, 427, 411, 352]
            # Center forehead points (below hairline, above eyebrows)
            forehead_idx = [68, 104, 108, 151, 337, 333, 298]

            left_pts = np.array([[landmarks[i]["x"], landmarks[i]["y"]] for i in left_cheek_idx], dtype=np.int32)
            right_pts = np.array([[landmarks[i]["x"], landmarks[i]["y"]] for i in right_cheek_idx], dtype=np.int32)
            forehead_pts = np.array([[landmarks[i]["x"], landmarks[i]["y"]] for i in forehead_idx], dtype=np.int32)

            cv2.fillPoly(mask, [left_pts, right_pts, forehead_pts], 255)
        else:
            # Fallback center face oval mask
            center_x, center_y = w // 2, h // 2
            cv2.ellipse(mask, (center_x, center_y), (int(w * 0.15), int(h * 0.20)), 0, 0, 360, 255, -1)

        skin_pixels_bgr = img_bgr[mask == 255]
        if len(skin_pixels_bgr) < 30:
            skin_pixels_bgr = img_bgr.reshape(-1, 3)

        # Convert ROI to LAB to filter out dark hair shadows and specular highlights
        lab_pixels = cv2.cvtColor(skin_pixels_bgr.reshape(1, -1, 3), cv2.COLOR_BGR2LAB)[0]
        
        # Filter L* channel between 60 and 240 (out of 255)
        valid_mask = (lab_pixels[:, 0] >= 60) & (lab_pixels[:, 0] <= 240)
        filtered_bgr = skin_pixels_bgr[valid_mask]

        if len(filtered_bgr) < 20:
            filtered_bgr = skin_pixels_bgr

        # Check for lighting color cast (RGB channel balance)
        r_mean = float(np.mean(filtered_bgr[:, 2]))
        g_mean = float(np.mean(filtered_bgr[:, 1]))
        b_mean = float(np.mean(filtered_bgr[:, 0]))

        rg_ratio = r_mean / (g_mean if g_mean > 0 else 1.0)
        rb_ratio = r_mean / (b_mean if b_mean > 0 else 1.0)

        if rb_ratio > 1.75:
            warning = "Warm/yellow lighting cast detected. Undertone estimation marked as provisional."
        elif rb_ratio < 0.95 or (b_mean / (r_mean if r_mean > 0 else 1.0)) > 1.1:
            warning = "Cool/blue lighting cast detected. Undertone estimation marked as provisional."

        return filtered_bgr, warning

    def analyze(self, img_bgr: np.ndarray, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        skin_pixels_bgr, color_warning = self.extract_skin_roi_pixels(img_bgr, landmarks)

        # Mean BGR color of valid skin pixels
        bgr_mean = np.mean(skin_pixels_bgr, axis=0).reshape(1, 1, 3).astype(np.uint8)
        lab_pixel = cv2.cvtColor(bgr_mean, cv2.COLOR_BGR2LAB)[0, 0]

        # OpenCV L*a*b* conversion scaling:
        # L*: 0..255 -> 0..100
        # a*: 0..255 -> -128..+127
        # b*: 0..255 -> -128..+127
        L_val = float(lab_pixel[0]) * (100.0 / 255.0)
        a_val = float(lab_pixel[1]) - 128.0
        b_val = float(lab_pixel[2]) - 128.0

        # ITA° Calculation: arctan((L* - 50) / b*) * (180 / pi)
        b_safe = b_val if abs(b_val) > 0.001 else 0.001
        ita_angle = math.atan2(L_val - 50.0, b_safe) * (180.0 / math.pi)

        # 1. Skin Shade Classification by ITA°
        if ita_angle > 55.0:
            shade = "Very Light"
        elif ita_angle > 41.0:
            shade = "Fair / Light"
        elif ita_angle > 28.0:
            shade = "Medium"
        elif ita_angle > 10.0:
            shade = "Tan"
        else:
            shade = "Deep"

        # 2. Undertone Temperature Classification by CIE a* and b*
        b_a_ratio = b_val / (a_val if abs(a_val) > 0.001 else 0.001)

        if b_val > 11.5 and b_a_ratio > 1.35:
            undertone = "Warm"
        elif a_val > 9.5 and (b_a_ratio < 1.15 or b_val < 8.0):
            undertone = "Cool"
        else:
            undertone = "Neutral"

        # 3. Personal Seasonal Color Palette Assignment
        if undertone == "Warm":
            seasonal_palette = "Spring Light" if ita_angle > 40.0 else "Autumn Warm"
        elif undertone == "Cool":
            seasonal_palette = "Summer Cool" if ita_angle > 30.0 else "Winter Vivid"
        else:
            seasonal_palette = "Spring Light" if ita_angle > 42.0 else "Summer Cool"

        descriptions = {
            "Spring Light": "Bright, clear, warm complexion with delicate gold undertones. Complimented by peach, coral, and warm pastel hues.",
            "Summer Cool": "Soft, muted, luminous cool skin tone with subtle rosy undertones. Enhanced by lavender, dusty rose, and powder blue.",
            "Autumn Warm": "Rich, deep warm complexion with olive or golden undertones. Complimented by chili red, brick, and terracotta earth tones.",
            "Winter Vivid": "Striking, clear, high-contrast cool skin tone. Elevated by deep berry red, sapphire, emerald, and crisp white."
        }

        undertone_confidence = "Estimated (Single-Image Ambient Lighting)"
        if color_warning:
            undertone_confidence = "Provisional (Color Cast Detected)"

        return {
            "shade": shade,
            "undertone": undertone,
            "ita_angle": round(ita_angle, 2),
            "lab_values": {
                "L": round(L_val, 2),
                "a": round(a_val, 2),
                "b": round(b_val, 2)
            },
            "seasonal_palette": seasonal_palette,
            "description": descriptions.get(seasonal_palette, "Balanced radiant complexion."),
            "color_analysis_warning": color_warning,
            "undertone_confidence": undertone_confidence
        }

skin_tone_analyzer = SkinToneAnalyzer()
