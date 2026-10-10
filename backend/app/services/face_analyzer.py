import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any, Tuple, Optional, List
import base64

class FaceAnalyzerService:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=3,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

    def decode_image(self, image_bytes: bytes) -> np.ndarray:
        """Decode image bytes to OpenCV BGR numpy array and validate dimensions."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid or corrupted image file format.")
        
        h, w, c = img.shape
        if h < 150 or w < 150:
            raise ValueError(f"Image resolution too low ({w}x{h} px). Please provide an image at least 150x150 pixels.")
        if h > 5000 or w > 5000:
            # Resize extremely large images for performance while preserving aspect ratio
            max_dim = 2500
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        return img

    def evaluate_lighting(self, img_bgr: np.ndarray) -> Dict[str, Any]:
        """Evaluate image brightness, contrast, and sharpness (blur detection)."""
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Mean brightness (0-255)
        brightness = float(np.mean(gray))
        
        # Contrast (standard deviation of grayscale values)
        contrast = float(np.std(gray))
        
        # Sharpness using Laplacian variance
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        is_valid = True
        warning = None
        
        if brightness < 35:
            is_valid = False
            warning = "Image is too dark. Please use natural or bright front lighting."
        elif brightness > 230:
            is_valid = False
            warning = "Image is overexposed. Avoid harsh direct flash or overexposure."
        elif blur_score < 25.0:
            warning = "Image appears slightly blurry. Landmark precision may be reduced."

        return {
            "is_valid": is_valid,
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "blur_score": round(blur_score, 2),
            "warning": warning
        }

    def process_face_landmarks(self, img_bgr: np.ndarray) -> Tuple[List[Dict[str, float]], np.ndarray, int, Optional[str]]:
        """
        Extract 468 3D facial landmarks using MediaPipe.
        Returns:
            (landmarks_list, annotated_bgr_image, num_faces_detected, detection_warning)
        """
        h, w, c = img_bgr.shape
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        
        if not results.multi_face_landmarks:
            return [], img_bgr, 0, None

        num_faces = len(results.multi_face_landmarks)
        detection_warning = None
        if num_faces > 1:
            detection_warning = f"Multiple faces ({num_faces}) detected. Analyzing the primary front-facing subject."

        # Select primary face
        face_landmarks = results.multi_face_landmarks[0]
        
        landmarks_list = []
        for lm in face_landmarks.landmark:
            landmarks_list.append({
                "x": lm.x * w,
                "y": lm.y * h,
                "z": lm.z * w,
                "norm_x": lm.x,
                "norm_y": lm.y
            })

        # Draw annotated landmarks & contours
        annotated_img = img_bgr.copy()
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        
        # Facemesh tessellation
        mp_drawing.draw_landmarks(
            image=annotated_img,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
        )
        
        # Facemesh contours
        mp_drawing.draw_landmarks(
            image=annotated_img,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
        )

        return landmarks_list, annotated_img, num_faces, detection_warning

    def encode_image_base64(self, img_bgr: np.ndarray) -> str:
        """Encode OpenCV image to base64 JPEG data URL."""
        success, buffer = cv2.imencode('.jpg', img_bgr)
        if not success:
            return ""
        encoded = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"

face_analyzer_service = FaceAnalyzerService()
