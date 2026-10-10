import math
from typing import List, Dict, Any

class FaceShapeEstimator:
    """
    Estimates facial shape based on 3D facial landmark geometry measurements and documented ratio rules.
    
    MediaPipe FaceMesh Landmark Point Index Map:
    - Landmark 10: Top forehead / hairline midpoint (trichion)
    - Landmark 152: Bottom chin (menton)
    - Landmark 234: Left cheekbone outer contour (zygoma left)
    - Landmark 454: Right cheekbone outer contour (zygoma right)
    - Landmark 103: Left forehead boundary (temple left)
    - Landmark 332: Right forehead boundary (temple right)
    - Landmark 172: Left jaw angle (gonion left)
    - Landmark 397: Right jaw angle (gonion right)
    - Landmark 33: Left eye outer corner
    - Landmark 263: Right eye outer corner
    - Landmark 1: Nose tip
    """
    
    SHAPE_DESCRIPTIONS = {
        "oval": {
            "description": "Proportional and balanced facial contours with cheekbones slightly wider than forehead and jawline. Widely considered the harmonious ideal in classic Korean aesthetics.",
            "styling_tips": [
                "Versatile face shape that flatters almost all eyewear styles.",
                "Soft gradient MLBB lip colors highlight natural balanced proportions.",
                "Gentle curtain bangs or soft waves complement your soft cheek contours."
            ]
        },
        "round": {
            "description": "Soft rounded jawline with equal face length and cheekbone width. Youthful and approachable Korean 'Baby Face' aesthetic.",
            "styling_tips": [
                "Rectangular, square, or geometric eyewear frames add elegant structural definition.",
                "Apply blush diagonally along the upper cheekbones to visually elongate the face.",
                "Gradient lip tints with slightly emphasized Cupid's bow add vertical focus."
            ]
        },
        "square": {
            "description": "Strong, well-defined angular jawline with forehead and cheekbones of nearly equal width. Exudes chic, structured confidence.",
            "styling_tips": [
                "Round, oval, or soft cat-eye glasses soften angular jawline contours.",
                "Apply soft pink blush on the apples of cheeks in circular blending strokes.",
                "Soft, layered haircuts and curtain bangs create romantic framing."
            ]
        },
        "heart": {
            "description": "Wider forehead and cheekbones gracefully tapering to a delicate, pointed chin. Emblematic of the coveted Korean V-line facial aesthetic.",
            "styling_tips": [
                "Lightweight rimless, oval, or bottom-heavy glasses balance forehead width.",
                "Concentrate blush lower on cheekbones and blend upward toward the temples.",
                "Soft, dewy berry and peach lip colors draw harmonious focus to the lips."
            ]
        },
        "oblong": {
            "description": "Elongated facial structure with straight cheekline and jawline. Elegant, refined, and noble impression.",
            "styling_tips": [
                "Oversized square or tall round frames break up facial length for horizontal balance.",
                "Apply blush horizontally across the cheeks to create a widening visual optical illusion.",
                "Full straight bangs or side-swept bangs shorten vertical face length."
            ]
        },
        "diamond": {
            "description": "High, prominent cheekbones tapering to both a narrower forehead and a refined narrow chin. Highly photogenic and striking geometry.",
            "styling_tips": [
                "Cat-eye or oval frames accentuate stunning cheekbones while balancing forehead width.",
                "Apply soft blush directly on cheekbone highlights to celebrate natural high contours.",
                "Soft glossy lip tints complement dramatic cheek symmetry."
            ]
        }
    }

    def estimate_shape(self, landmarks: List[Dict[str, float]], blur_score: float = 100.0) -> Dict[str, Any]:
        """
        Estimate face shape using geometric landmark ratio calculations.
        Returns detailed measurements, geometry reasoning, limitations, and uncertainty assessment.
        """
        if len(landmarks) < 468:
            return {
                "face_shape": "oval",
                "ratios": {"face_aspect_ratio": 1.35, "jaw_to_cheek_ratio": 0.78, "forehead_to_cheek_ratio": 0.80},
                "measurements": {"face_length_px": 0.0, "forehead_width_px": 0.0, "cheekbone_width_px": 0.0, "jaw_width_px": 0.0},
                "reasoning": "Standard proportional fallback applied due to insufficient facial landmark coordinates.",
                "description": self.SHAPE_DESCRIPTIONS["oval"]["description"],
                "styling_tips": self.SHAPE_DESCRIPTIONS["oval"]["styling_tips"],
                "limitations": "Heuristic shape estimation based on projected landmark geometry. Hair, lighting, or face angle may influence ratio precision.",
                "uncertainty_level": "High"
            }

        # Documented Landmark Extractions
        top_forehead = landmarks[10]    # Hairline / trichion point (10)
        bottom_chin = landmarks[152]   # Chin menton point (152)
        left_cheek = landmarks[234]    # Left zygomatic arch (234)
        right_cheek = landmarks[454]   # Right zygomatic arch (454)
        left_forehead = landmarks[103] # Left forehead boundary (103)
        right_forehead = landmarks[332]# Right forehead boundary (332)
        left_jaw = landmarks[172]      # Left jaw gonion angle (172)
        right_jaw = landmarks[397]     # Right jaw gonion angle (397)
        left_eye = landmarks[33]       # Left eye outer corner (33)
        right_eye = landmarks[263]     # Right eye outer corner (263)
        nose_tip = landmarks[1]        # Nose tip (1)

        # Calculate pixel Euclidean distances
        face_length_px = math.hypot(bottom_chin["x"] - top_forehead["x"], bottom_chin["y"] - top_forehead["y"])
        cheekbone_width_px = math.hypot(right_cheek["x"] - left_cheek["x"], right_cheek["y"] - left_cheek["y"])
        forehead_width_px = math.hypot(right_forehead["x"] - left_forehead["x"], right_forehead["y"] - left_forehead["y"])
        jaw_width_px = math.hypot(right_jaw["x"] - left_jaw["x"], right_jaw["y"] - left_jaw["y"])

        if cheekbone_width_px == 0:
            cheekbone_width_px = 1.0

        # Compute key geometric ratios (resolution-independent)
        face_aspect_ratio = face_length_px / cheekbone_width_px
        jaw_to_cheek = jaw_width_px / cheekbone_width_px
        forehead_to_cheek = forehead_width_px / cheekbone_width_px

        measurements = {
            "face_length_px": round(face_length_px, 1),
            "forehead_width_px": round(forehead_width_px, 1),
            "cheekbone_width_px": round(cheekbone_width_px, 1),
            "jaw_width_px": round(jaw_width_px, 1),
            "aspect_ratio": round(face_aspect_ratio, 3),
            "jaw_to_cheek_ratio": round(jaw_to_cheek, 3),
            "forehead_to_cheek_ratio": round(forehead_to_cheek, 3)
        }

        ratios = {
            "face_aspect_ratio": round(face_aspect_ratio, 3),
            "jaw_to_cheek_ratio": round(jaw_to_cheek, 3),
            "forehead_to_cheek_ratio": round(forehead_to_cheek, 3)
        }

        # Pose Estimation (Head Roll & Yaw asymmetry)
        eye_dx = right_eye["x"] - left_eye["x"]
        eye_dy = right_eye["y"] - left_eye["y"]
        roll_angle_deg = abs(math.degrees(math.atan2(eye_dy, eye_dx if eye_dx != 0 else 1.0)))
        
        yaw_offset = (nose_tip["x"] - left_cheek["x"]) / cheekbone_width_px # Ideal frontal pose ~0.50

        # Rule-based scoring engine for 6 face shapes
        scores = {
            "oval": 0.0,
            "round": 0.0,
            "square": 0.0,
            "heart": 0.0,
            "oblong": 0.0,
            "diamond": 0.0
        }

        # 1. Face Aspect Ratio rules
        if face_aspect_ratio > 1.44:
            scores["oblong"] += 3.5
            scores["oval"] += 2.0
        elif face_aspect_ratio < 1.25:
            scores["round"] += 3.5
            scores["square"] += 2.5
        else:
            scores["oval"] += 2.8
            scores["heart"] += 2.0
            scores["diamond"] += 1.8

        # 2. Jaw to Cheek Ratio rules
        if jaw_to_cheek > 0.84:
            scores["square"] += 3.5
            scores["oblong"] += 1.5
        elif jaw_to_cheek < 0.72:
            scores["heart"] += 3.2
            scores["diamond"] += 2.8
            scores["oval"] += 1.5
        else:
            scores["round"] += 2.2
            scores["oval"] += 2.0

        # 3. Forehead to Cheek Ratio rules
        if forehead_to_cheek < 0.74:
            scores["diamond"] += 3.5
        elif forehead_to_cheek > 0.84:
            scores["heart"] += 3.0
            scores["square"] += 1.8
        else:
            scores["oval"] += 2.2

        # Select highest scoring face shape
        best_shape = max(scores, key=scores.get)

        # Build documented geometric reasoning string
        reasonings = {
            "oval": f"Aspect ratio of {ratios['face_aspect_ratio']} indicates balanced height with cheekbone width ({measurements['cheekbone_width_px']}px) slightly exceeding forehead ({measurements['forehead_width_px']}px) and jaw ({measurements['jaw_width_px']}px).",
            "round": f"Aspect ratio of {ratios['face_aspect_ratio']} (< 1.28) with jaw-to-cheek ratio of {ratios['jaw_to_cheek_ratio']} indicates equal facial width and height with soft jawline contours.",
            "square": f"Jaw-to-cheek ratio of {ratios['jaw_to_cheek_ratio']} (> 0.84) and forehead-to-cheek ratio of {ratios['forehead_to_cheek_ratio']} reflect angular jawline and balanced forehead width.",
            "heart": f"Forehead-to-cheek ratio of {ratios['forehead_to_cheek_ratio']} with tapering jaw-to-cheek ratio of {ratios['jaw_to_cheek_ratio']} (< 0.72) indicates wider upper face tapering to a V-line chin.",
            "oblong": f"High face aspect ratio of {ratios['face_aspect_ratio']} (> 1.44) indicates vertical facial length exceeding cheekbone width ({measurements['cheekbone_width_px']}px).",
            "diamond": f"Cheekbone width ({measurements['cheekbone_width_px']}px) significantly exceeds narrow forehead ({measurements['forehead_width_px']}px, ratio {ratios['forehead_to_cheek_ratio']}) and jaw width ({measurements['jaw_width_px']}px)."
        }

        # Calculate honest uncertainty indicator
        uncertainty_level = "Low"
        uncertainty_notes = []
        
        if roll_angle_deg > 6.0:
            uncertainty_level = "Moderate"
            uncertainty_notes.append("Head tilt detected (roll > 6°).")
        if abs(yaw_offset - 0.50) > 0.10:
            uncertainty_level = "Moderate"
            uncertainty_notes.append("Off-center face angle (yaw asymmetry).")
        if blur_score < 25.0:
            uncertainty_level = "Moderate"
            uncertainty_notes.append("Subtle image blur detected.")

        limitations_text = "Heuristic shape estimation based on 2D projection of MediaPipe 3D face mesh. "
        if uncertainty_notes:
            limitations_text += f"Note: {' '.join(uncertainty_notes)} "
        limitations_text += "Factors such as head tilt, expression, and hair framing may alter pixel ratio precision."

        shape_data = self.SHAPE_DESCRIPTIONS.get(best_shape, self.SHAPE_DESCRIPTIONS["oval"])

        return {
            "face_shape": best_shape,
            "ratios": ratios,
            "measurements": measurements,
            "reasoning": reasonings.get(best_shape, reasonings["oval"]),
            "description": shape_data["description"],
            "styling_tips": shape_data["styling_tips"],
            "limitations": limitations_text,
            "uncertainty_level": uncertainty_level
        }

face_shape_estimator = FaceShapeEstimator()
