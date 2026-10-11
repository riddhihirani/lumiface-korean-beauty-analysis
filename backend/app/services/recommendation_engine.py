import json
import os
import math
from typing import Dict, Any, List, Tuple

class RecommendationEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_dir = os.path.join(base_dir, "data")
        
        # Load JSON catalogs
        with open(os.path.join(data_dir, "color_palettes.json"), "r") as f:
            self.color_palettes = json.load(f)

        with open(os.path.join(data_dir, "makeup_shades.json"), "r") as f:
            self.makeup_shades = json.load(f)

        with open(os.path.join(data_dir, "eyewear_recommendations.json"), "r") as f:
            self.eyewear_catalog = json.load(f)

    def hex_to_lab(self, hex_code: str) -> Tuple[float, float, float]:
        """Convert HEX color string to CIE L*a*b* coordinates."""
        hex_clean = hex_code.lstrip("#")
        if len(hex_clean) != 6:
            return 50.0, 0.0, 0.0

        r = int(hex_clean[0:2], 16) / 255.0
        g = int(hex_clean[2:4], 16) / 255.0
        b = int(hex_clean[4:6], 16) / 255.0

        # Linearize sRGB
        r_lin = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
        g_lin = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
        b_lin = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4

        # RGB to XYZ (D65 illuminant)
        x = (r_lin * 0.4124564 + g_lin * 0.3575761 + b_lin * 0.1804375) / 0.95047
        y = (r_lin * 0.2126729 + g_lin * 0.7151522 + b_lin * 0.0721750) / 1.00000
        z = (r_lin * 0.0193339 + g_lin * 0.1191920 + b_lin * 0.9503041) / 1.08883

        fx = x ** (1/3) if x > 0.008856 else (7.787 * x) + (16 / 116)
        fy = y ** (1/3) if y > 0.008856 else (7.787 * y) + (16 / 116)
        fz = z ** (1/3) if z > 0.008856 else (7.787 * z) + (16 / 116)

        L = (116.0 * fy) - 16.0
        a = 500.0 * (fx - fy)
        b_val = 200.0 * (fy - fz)

        return L, a, b_val

    def calculate_delta_e(self, lab1: Tuple[float, float, float], lab2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean color distance Delta E in CIE L*a*b* space."""
        dL = lab1[0] - lab2[0]
        da = lab1[1] - lab2[1]
        db = lab1[2] - lab2[2]
        return math.sqrt(dL * dL + da * da + db * db)

    def get_color_palette(self, seasonal_key: str) -> Dict[str, Any]:
        key_map = {
            "Spring Light": "spring_light",
            "Summer Cool": "summer_cool",
            "Autumn Warm": "autumn_warm",
            "Winter Vivid": "winter_vivid"
        }
        json_key = key_map.get(seasonal_key, "spring_light")
        return self.color_palettes.get(json_key, self.color_palettes["spring_light"])

    def get_makeup_recommendations(self, undertone: str, season: str, skin_lab: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        Calculates Estimated Compatibility Score using continuous CIE L*a*b* color distance Delta E
        between skin sample and shade HEX code, combined with undertone/seasonal bonuses.
        Ranks shades dynamically with lowest Delta E tie-breaking to avoid flat identical scores.
        """
        user_lab = (skin_lab["L"], skin_lab["a"], skin_lab["b"]) if skin_lab else (65.0, 10.0, 14.0)

        matched = []
        for prod in self.makeup_shades:
            prod_lab = self.hex_to_lab(prod.get("hex_code", "#C86D7C"))
            delta_e = self.calculate_delta_e(user_lab, prod_lab)

            # Continuous color distance scoring:
            # Matches receive personal color harmony bonuses, modulated by continuous perceptual delta E
            undertone_bonus = 10.0 if undertone in prod.get("suitable_undertones", []) else 0.0
            season_bonus = 8.0 if season in prod.get("suitable_seasons", []) else 0.0

            base_score = 80.0 + undertone_bonus + season_bonus - (0.45 * delta_e)
            final_score = min(max(round(base_score, 1), 55.0), 98.0)

            item = dict(prod)
            item["match_score"] = final_score
            item["compatibility_label"] = "Estimated Compatibility Score (Lab Distance Matrix)"
            item["delta_e"] = round(delta_e, 2)
            matched.append(item)

        # Sort primarily by match_score descending, and break ties by delta_e ascending (closer perceptual match first)
        matched.sort(key=lambda x: (x["match_score"], -x["delta_e"]), reverse=True)
        return matched

    def get_eyewear_recommendations(
        self, 
        face_shape: str = None, 
        ratios: Dict[str, float] = None, 
        season: str = "Spring Light"
    ) -> List[Dict[str, Any]]:
        """
        Calculates dynamic eyewear compatibility scores based on facial geometry rules,
        continuous aspect ratios, jaw-to-cheek proportions, and personal seasonal color frame matches.
        Returns dynamically ranked recommendations with personalized geometric reasoning.
        """
        is_missing_shape = not face_shape or face_shape.lower() not in ["oval", "round", "square", "heart", "oblong", "diamond"]
        shape_clean = "neutral" if is_missing_shape else face_shape.lower()

        aspect_ratio = ratios.get("face_aspect_ratio", 1.35) if ratios else 1.35
        jaw_to_cheek = ratios.get("jaw_to_cheek_ratio", 0.78) if ratios else 0.78
        forehead_to_cheek = ratios.get("forehead_to_cheek_ratio", 0.80) if ratios else 0.80

        valid_seasons = ["Spring Light", "Summer Cool", "Autumn Warm", "Winter Vivid"]
        season_clean = season if season in valid_seasons else "Spring Light"

        recommendations = []
        for frame in self.eyewear_catalog:
            category = frame.get("category", "")
            base_score = 68.0

            # 1. Primary Face Shape & Proportion Rules
            if is_missing_shape:
                base_score += 8.0
                reason_text = f"Neutral compatibility for {frame.get('frame_style', 'frame')}. Face shape is unverified; provide a clear portrait image for custom geometric matching."
            else:
                if shape_clean in frame.get("suitable_face_shapes", []):
                    base_score += 15.0
                else:
                    base_score += 2.0

                # Category-Specific Geometric Rules & Custom Explanations
                if shape_clean == "round":
                    if category in ["rectangular", "square", "geometric"]:
                        base_score += 8.0
                        reason_text = f"Angular {category} frames add crisp structure and optical length to complement your round facial aspect ratio of {aspect_ratio}."
                    elif category in ["round", "oval"]:
                        base_score -= 8.0
                        reason_text = f"Curved {category} frames mirror your soft round cheek contours. Angular rectangular or geometric frames offer superior structural definition."
                    else:
                        reason_text = f"{frame.get('frame_style', 'Frame')} offers flattering accent proportions for your round facial contours."

                elif shape_clean == "square":
                    if category in ["round", "oval", "cat-eye"]:
                        base_score += 8.0
                        reason_text = f"Curved {category} frames contrast gracefully with your angular jawline structure (jaw-to-cheek ratio {jaw_to_cheek})."
                    elif category in ["square", "rectangular"]:
                        base_score -= 8.0
                        reason_text = f"Angular {category} frames double down on square jawline lines. Round or oval frames provide softer, more balanced visual harmony."
                    else:
                        reason_text = f"{frame.get('frame_style', 'Frame')} offers structured accent harmony for your square jawline."

                elif shape_clean == "heart":
                    if category in ["aviator", "oval", "round"]:
                        base_score += 8.0
                        reason_text = f"Bottom-heavy {category} frames broaden visual weight downward, balancing your tapering V-line chin (jaw-to-cheek ratio {jaw_to_cheek})."
                    elif category in ["rectangular", "square"]:
                        base_score -= 6.0
                        reason_text = f"Top-heavy {category} frames add width across your upper forehead. Aviator or oval styles offer better lower facial balance."
                    else:
                        reason_text = f"{frame.get('frame_style', 'Frame')} provides subtle framing for your heart-shaped chin taper."

                elif shape_clean == "oblong":
                    if category in ["square", "geometric", "round"]:
                        base_score += 8.0
                        reason_text = f"Oversized {category} frames break up your high facial aspect ratio of {aspect_ratio}, creating horizontal visual balance."
                    elif category in ["rectangular"]:
                        base_score -= 8.0
                        reason_text = f"Slim horizontal {category} frames emphasize vertical face length. Tall square or round frames shorten vertical proportions."
                    else:
                        reason_text = f"{frame.get('frame_style', 'Frame')} provides horizontal balance for your elongated facial proportions."

                elif shape_clean == "diamond":
                    if category in ["cat-eye", "oval", "aviator"]:
                        base_score += 8.0
                        reason_text = f"Uplifting {category} frames accentuate your stunning cheekbones (forehead-to-cheek ratio {forehead_to_cheek}) while softening sharp angles."
                    elif category in ["geometric"]:
                        base_score -= 6.0
                        reason_text = f"Sharp geometric frames compete with your prominent zygomatic cheekbones. Cat-eye or oval frames offer smoother harmony."
                    else:
                        reason_text = f"{frame.get('frame_style', 'Frame')} highlights high cheekbone symmetry."

                else: # oval
                    if category in ["oval", "round", "cat-eye", "rectangular", "geometric"]:
                        base_score += 6.0
                        reason_text = f"{frame.get('frame_style', 'Frame')} enhances your naturally balanced oval facial aspect ratio of {aspect_ratio}."
                    else:
                        reason_text = f"Flattering proportion fit for balanced oval geometry."

                # Continuous micro-proportion modulations (distinct per individual)
                if category in ["round", "oval"]:
                    base_score += (aspect_ratio - 1.35) * 6.0 - (jaw_to_cheek - 0.78) * 4.0
                elif category in ["rectangular", "geometric"]:
                    base_score += (1.35 - aspect_ratio) * 6.0 + (jaw_to_cheek - 0.78) * 4.0
                elif category in ["cat-eye"]:
                    base_score += (0.80 - jaw_to_cheek) * 5.0

            # 2. Seasonal Color Palette Match
            season_colors = frame.get("recommended_colors_by_season", {}).get(season_clean, ["Classic Metal"])
            if season_clean in frame.get("recommended_colors_by_season", {}):
                base_score += 4.0

            final_score = min(max(round(base_score, 1), 60.0), 98.0)

            if is_missing_shape:
                suitability = "General Recommendation"
                comp_label = "Estimated Compatibility Score (Neutral Baseline - Unverified Geometry)"
            else:
                if final_score >= 88.0:
                    suitability = "Highly Recommended"
                elif final_score >= 80.0:
                    suitability = "Flattering Accent"
                else:
                    suitability = "Selective Complement"
                comp_label = "Estimated Compatibility Score (Facial Geometry & Color Rules)"

            item = {
                "id": frame.get("id", "eye_01"),
                "frame_style": frame.get("frame_style", "Classic Frame"),
                "category": category,
                "description": frame.get("description", ""),
                "recommended_colors": season_colors,
                "color_hex_swatches": frame.get("color_hex_swatches", ["#2C2C2C"]),
                "match_score": final_score,
                "suitability": suitability,
                "compatibility_label": comp_label,
                "reasoning": reason_text
            }
            recommendations.append(item)

        # Dynamic ranking: sort by match_score descending, tie-break by ID
        recommendations.sort(key=lambda x: (x["match_score"], x["id"]), reverse=True)
        return recommendations

recommendation_engine = RecommendationEngine()
