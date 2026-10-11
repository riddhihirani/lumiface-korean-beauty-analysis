import math
from typing import List, Dict, Any, Tuple

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

        # 1. Head Roll Normalization (Rotate landmarks to eliminate head-tilt distortion)
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        eye_dx = right_eye["x"] - left_eye["x"]
        eye_dy = right_eye["y"] - left_eye["y"]
        roll_angle_rad = math.atan2(eye_dy, eye_dx if eye_dx != 0 else 1.0)
        roll_angle_deg = abs(math.degrees(roll_angle_rad))

        cx = (left_eye["x"] + right_eye["x"]) / 2.0
        cy = (left_eye["y"] + right_eye["y"]) / 2.0
        cos_a = math.cos(-roll_angle_rad)
        sin_a = math.sin(-roll_angle_rad)

        def rotate_pt(pt: Dict[str, float]) -> Tuple[float, float]:
            tx = pt["x"] - cx
            ty = pt["y"] - cy
            rx = tx * cos_a - ty * sin_a + cx
            ry = tx * sin_a + ty * cos_a + cy
            return rx, ry

        # 2. Extract Verified Anthropometric Facial Landmark Coordinates
        top_x, top_y = rotate_pt(landmarks[10])       # Hairline / trichion (10)
        chin_x, chin_y = rotate_pt(landmarks[152])    # Chin / menton (152)
        l_cheek_x, l_cheek_y = rotate_pt(landmarks[234]) # Left zygomatic arch (234)
        r_cheek_x, r_cheek_y = rotate_pt(landmarks[454]) # Right zygomatic arch (454)
        l_temple_x, l_temple_y = rotate_pt(landmarks[54]) # Left bitemporal forehead boundary (54)
        r_temple_x, r_temple_y = rotate_pt(landmarks[284]) # Right bitemporal forehead boundary (284)
        l_jaw_x, l_jaw_y = rotate_pt(landmarks[58])      # Left mandibular gonion angle (58)
        r_jaw_x, r_jaw_y = rotate_pt(landmarks[288])     # Right mandibular gonion angle (288)
        nose_x, nose_y = rotate_pt(landmarks[1])         # Nose tip (1)

        # Calculate aligned Euclidean span measurements
        face_length_px = abs(chin_y - top_y)
        cheekbone_width_px = abs(r_cheek_x - l_cheek_x)
        forehead_width_px = abs(r_temple_x - l_temple_x)
        jaw_width_px = abs(r_jaw_x - l_jaw_x)

        if cheekbone_width_px == 0:
            cheekbone_width_px = 1.0

        # Compute resolution-independent geometric ratios
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

        # Yaw asymmetry offset (ideal frontal pose ~0.50)
        yaw_offset = (nose_x - l_cheek_x) / cheekbone_width_px

        # 3. Continuous Multi-Feature Distance Classification (Anthropometric Norms)
        # Vector: [Aspect Ratio, Jaw-to-Cheek, Forehead-to-Cheek]
        PROTOTYPES = {
            "oval":    {"target": [1.36, 0.80, 0.85], "weights": [2.5, 2.0, 1.5]},
            "round":   {"target": [1.14, 0.82, 0.85], "weights": [3.5, 1.5, 1.5]},
            "square":  {"target": [1.22, 0.90, 0.89], "weights": [2.0, 3.5, 2.0]},
            "heart":   {"target": [1.32, 0.70, 0.88], "weights": [1.5, 3.0, 2.5]},
            "oblong":  {"target": [1.52, 0.81, 0.84], "weights": [3.5, 1.5, 1.5]},
            "diamond": {"target": [1.35, 0.72, 0.76], "weights": [1.5, 2.5, 3.5]},
        }

        distances = {}
        for shape, proto in PROTOTYPES.items():
            tgt = proto["target"]
            w = proto["weights"]
            d = math.sqrt(
                ((face_aspect_ratio - tgt[0]) ** 2) * w[0] +
                ((jaw_to_cheek - tgt[1]) ** 2) * w[1] +
                ((forehead_to_cheek - tgt[2]) ** 2) * w[2]
            )
            distances[shape] = d

        # Convert distance to normalized similarity probabilities
        similarities = {shape: 1.0 / (1.0 + 4.0 * d) for shape, d in distances.items()}
        total_sim = sum(similarities.values())
        probabilities = {shape: sim / total_sim for shape, sim in similarities.items()}

        sorted_shapes = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        best_shape, best_prob = sorted_shapes[0]
        second_shape, second_prob = sorted_shapes[1]
        margin = best_prob - second_prob

        # Documented geometric reasoning
        reasonings = {
            "oval": f"Aspect ratio of {ratios['face_aspect_ratio']} with harmonious cheekbone width ({measurements['cheekbone_width_px']}px) tapering gently to jawline (ratio {ratios['jaw_to_cheek_ratio']}) indicates classic balanced proportions.",
            "round": f"Compact aspect ratio of {ratios['face_aspect_ratio']} with balanced width ({measurements['cheekbone_width_px']}px) indicates soft, equal facial dimensions characteristic of a youthful round face contour.",
            "square": f"Broad jawline width of {measurements['jaw_width_px']}px (jaw-to-cheek ratio {ratios['jaw_to_cheek_ratio']}) paired with strong forehead width ({measurements['forehead_width_px']}px) establishes structured angular geometry.",
            "heart": f"Broad forehead width ({measurements['forehead_width_px']}px, ratio {ratios['forehead_to_cheek_ratio']}) tapering downward to a delicate jaw width of {measurements['jaw_width_px']}px (ratio {ratios['jaw_to_cheek_ratio']}) reflects classic V-line proportions.",
            "oblong": f"Elongated aspect ratio of {ratios['face_aspect_ratio']} with vertical face length ({measurements['face_length_px']}px) distinctly exceeding width reflects elegant elongated facial structure.",
            "diamond": f"Cheekbone width ({measurements['cheekbone_width_px']}px) distinctly exceeds both narrow forehead ({measurements['forehead_width_px']}px, ratio {ratios['forehead_to_cheek_ratio']}) and tapered jawline (ratio {ratios['jaw_to_cheek_ratio']})."
        }

        # Calculate calibrated uncertainty indicator
        uncertainty_level = "Low"
        uncertainty_notes = []

        if roll_angle_deg > 6.0:
            uncertainty_level = "Moderate"
            uncertainty_notes.append(f"Head tilt detected ({roll_angle_deg:.1f}° roll normalized).")
        if abs(yaw_offset - 0.50) > 0.10:
            uncertainty_level = "Moderate"
            uncertainty_notes.append("Off-center face angle (yaw asymmetry).")
        if blur_score < 25.0:
            uncertainty_level = "Moderate"
            uncertainty_notes.append("Subtle image blur detected.")
        if margin < 0.05:
            uncertainty_level = "High"
            uncertainty_notes.append(f"Intermediate boundary between {best_shape} and {second_shape} (margin: {margin*100:.1f}%).")

        limitations_text = "Continuous geometric classification normalized for 2D head tilt. "
        if uncertainty_notes:
            limitations_text += f"Note: {' '.join(uncertainty_notes)} "
        limitations_text += "Subtle facial expressions, camera perspective distance, and hairstyle may influence measured ratios."

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
