import cv2
import numpy as np
import math
from typing import List, Dict, Any, Tuple, Optional

class SkinToneAnalyzer:
    """
    Analyzes skin color in CIE L*a*b* space, calculates Individual Typology Angle (ITA°),
    evaluates lighting white-balance cast, and classifies undertone and personal seasonal color.
    """

    def extract_zone_pixels(self, img_bgr: np.ndarray, landmarks: List[Dict[str, float]], indices: List[int]) -> Optional[Dict[str, Any]]:
        """
        Extract skin pixels from a specific facial landmark polygon,
        filtering out dark hair/shadows and specular highlights.
        """
        h, w, c = img_bgr.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        pts = np.array([[landmarks[i]["x"], landmarks[i]["y"]] for i in indices], dtype=np.int32)
        cv2.fillPoly(mask, [pts], 255)
        
        pixels = img_bgr[mask == 255]
        if len(pixels) == 0:
            return None
            
        lab_pixels = cv2.cvtColor(pixels.reshape(1, -1, 3), cv2.COLOR_BGR2LAB)[0]
        valid_mask = (lab_pixels[:, 0] >= 60) & (lab_pixels[:, 0] <= 240)
        filtered_bgr = pixels[valid_mask]
        
        if len(filtered_bgr) < 15:
            return None
            
        bgr_mean = np.mean(filtered_bgr, axis=0)
        lab_pixel = cv2.cvtColor(bgr_mean.reshape(1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2LAB)[0, 0]
        
        return {
            "bgr_mean": bgr_mean,
            "L": float(lab_pixel[0]) * (100.0 / 255.0),
            "a": float(lab_pixel[1]) - 128.0,
            "b": float(lab_pixel[2]) - 128.0,
            "pixel_count": len(filtered_bgr)
        }

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

        rb_ratio = r_mean / (b_mean if b_mean > 0 else 1.0)

        if rb_ratio > 1.75:
            warning = "Warm/yellow lighting cast detected. Undertone estimation marked as provisional."
        elif rb_ratio < 0.95 or (b_mean / (r_mean if r_mean > 0 else 1.0)) > 1.1:
            warning = "Cool/blue lighting cast detected. Undertone estimation marked as provisional."

        return filtered_bgr, warning

    def analyze(self, img_bgr: np.ndarray, landmarks: List[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Analyzes skin color in CIE L*a*b* space using multi-zone sampling (left cheek,
        right cheek, forehead) with illuminant cast compensation and ITA° classification.
        """
        landmarks = landmarks or []
        warning = None

        # 1. Multi-Zone Anatomical Sampling
        valid_zones = []
        if len(landmarks) >= 468:
            left_zone = self.extract_zone_pixels(img_bgr, landmarks, [117, 118, 101, 205, 207, 187, 123])
            right_zone = self.extract_zone_pixels(img_bgr, landmarks, [346, 347, 330, 425, 427, 411, 352])
            forehead_zone = self.extract_zone_pixels(img_bgr, landmarks, [68, 104, 108, 151, 337, 333, 298])
            valid_zones = [z for z in [left_zone, right_zone, forehead_zone] if z is not None]

        if not valid_zones:
            # Fallback to single ROI
            skin_pixels_bgr, warning = self.extract_skin_roi_pixels(img_bgr, landmarks)
            bgr_mean = np.mean(skin_pixels_bgr, axis=0)
            lab_pixel = cv2.cvtColor(bgr_mean.reshape(1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2LAB)[0, 0]
            valid_zones = [{
                "bgr_mean": bgr_mean,
                "L": float(lab_pixel[0]) * (100.0 / 255.0),
                "a": float(lab_pixel[1]) - 128.0,
                "b": float(lab_pixel[2]) - 128.0,
                "pixel_count": len(skin_pixels_bgr)
            }]

        # 2. Composite Multi-Zone Color Aggregation
        bgr_mean = np.mean([z["bgr_mean"] for z in valid_zones], axis=0)
        L_val = float(np.mean([z["L"] for z in valid_zones]))
        a_val = float(np.mean([z["a"] for z in valid_zones]))
        b_val = float(np.mean([z["b"] for z in valid_zones]))

        # Calculate lighting cast ratios
        b_mean = float(bgr_mean[0])
        g_mean = float(bgr_mean[1])
        r_mean = float(bgr_mean[2])

        rb_ratio = r_mean / (b_mean if b_mean > 0 else 1.0)
        br_ratio = b_mean / (r_mean if r_mean > 0 else 1.0)

        # 3. Illuminant Compensation for Ambient Color Casts
        b_comp = b_val
        is_extreme_cast = False
        if rb_ratio > 1.85:
            warning = f"Warm/yellow lighting cast detected. Severe ambient color bias (R/B ratio: {rb_ratio:.2f}). Evidence is insufficient for definitive undertone diagnosis; retake image in diffuse natural daylight."
            is_extreme_cast = True
            b_bias = min(8.0, (rb_ratio - 1.40) * 8.0)
            b_comp = b_val - b_bias
        elif rb_ratio > 1.75:
            warning = "Warm/yellow lighting cast detected. Undertone estimation marked as provisional."
            b_bias = min(5.0, (rb_ratio - 1.40) * 7.0)
            b_comp = b_val - b_bias
        elif rb_ratio > 1.50:
            b_bias = min(3.0, (rb_ratio - 1.40) * 5.0)
            b_comp = b_val - b_bias
        elif rb_ratio < 0.90 or br_ratio > 1.15:
            warning = f"Cool/blue lighting cast detected. Severe ambient color bias (B/R ratio: {br_ratio:.2f}). Evidence is insufficient for definitive undertone diagnosis; retake image in diffuse natural daylight."
            is_extreme_cast = True
            b_bias = min(6.0, (0.95 - rb_ratio) * 8.0)
            b_comp = b_val + b_bias
        elif rb_ratio < 0.95 or br_ratio > 1.10:
            warning = "Cool/blue lighting cast detected. Undertone estimation marked as provisional."
            b_bias = min(3.5, (0.95 - rb_ratio) * 6.5)
            b_comp = b_val + b_bias

        # 4. ITA° Calculation with compensated b* channel
        b_safe = b_comp if abs(b_comp) > 0.001 else 0.001
        ita_angle = math.atan2(L_val - 50.0, b_safe) * (180.0 / math.pi)

        # Skin Shade Classification by ITA°
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

        # 5. Undertone Classification using calibrated chromatic opponent ratios
        b_a_ratio = b_comp / (a_val if abs(a_val) > 0.001 else 0.001)

        if is_extreme_cast:
            undertone = "Neutral"
        elif b_comp > 11.5 and b_a_ratio > 1.35:
            undertone = "Warm"
        elif a_val > 9.5 and (b_a_ratio < 1.15 or b_comp < 8.0):
            undertone = "Cool"
        else:
            undertone = "Neutral"

        # 6. Personal Seasonal Color Palette Assignment
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

        # Check cross-zone uniformity for confidence
        std_L = float(np.std([z["L"] for z in valid_zones])) if len(valid_zones) > 1 else 0.0
        if is_extreme_cast:
            undertone_confidence = "Uncertain — Retake Image in Natural Daylight"
        elif warning:
            undertone_confidence = "Provisional (Color Cast Detected)"
        elif std_L > 10.0:
            undertone_confidence = "Moderate (Non-Uniform Facial Lighting)"
        elif len(valid_zones) >= 3:
            undertone_confidence = "High (Multi-Zone Calibrated)"
        else:
            undertone_confidence = "Estimated (Single-Image Ambient Lighting)"

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
            "color_analysis_warning": warning,
            "undertone_confidence": undertone_confidence
        }

skin_tone_analyzer = SkinToneAnalyzer()
