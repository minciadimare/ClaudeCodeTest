import colorsys
from pathlib import Path
from PIL import Image as PILImage
import mediapipe as mp
import cv2
import numpy as np
from app.models.label import SeasonEnum


class RuleBasedClassifier:
    """
    Simple HSV-based skin tone analyzer.
    Samples skin pixels from face region and classifies based on warm/cool + depth + chroma.
    """

    # Mapping: (undertone, depth, chroma) -> season
    SEASON_MAP = {
        ("cool", "light", "clear"): SeasonEnum.BRIGHT_WINTER,
        ("cool", "light", "muted"): SeasonEnum.LIGHT_SUMMER,
        ("cool", "medium", "clear"): SeasonEnum.BRIGHT_WINTER,
        ("cool", "medium", "muted"): SeasonEnum.TRUE_SUMMER,
        ("cool", "dark", "clear"): SeasonEnum.COOL_WINTER,
        ("cool", "dark", "muted"): SeasonEnum.COOL_SUMMER,
        ("warm", "light", "clear"): SeasonEnum.BRIGHT_SPRING,
        ("warm", "light", "muted"): SeasonEnum.LIGHT_SPRING,
        ("warm", "medium", "clear"): SeasonEnum.TRUE_SPRING,
        ("warm", "medium", "muted"): SeasonEnum.SOFT_AUTUMN,
        ("warm", "dark", "clear"): SeasonEnum.WARM_AUTUMN,
        ("warm", "dark", "muted"): SeasonEnum.DEEP_AUTUMN,
        ("neutral", "light", "clear"): SeasonEnum.BRIGHT_SPRING,
        ("neutral", "light", "muted"): SeasonEnum.LIGHT_SPRING,
        ("neutral", "medium", "clear"): SeasonEnum.TRUE_SPRING,
        ("neutral", "medium", "muted"): SeasonEnum.SOFT_AUTUMN,
    }

    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )

    def classify(self, image_path: str) -> dict:
        """
        Classify image by analyzing skin tone.
        Returns: {season, confidence, undertone, contrast, value}
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return self._no_face_response("Could not read image")

            # Detect face
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.face_detector.process(rgb_img)

            if not results.detections or len(results.detections) == 0:
                return self._no_face_response("No face detected")

            # Extract skin region from largest face
            h, w, _ = img.shape
            largest_detection = max(
                results.detections,
                key=lambda d: (d.location_data.relative_bounding_box.width *
                               d.location_data.relative_bounding_box.height)
            )

            bbox = largest_detection.location_data.relative_bounding_box
            x_min = max(0, int((bbox.xmin - 0.1) * w))
            y_min = max(0, int((bbox.ymin - 0.1) * h))
            x_max = min(w, int((bbox.xmin + bbox.width + 0.1) * w))
            y_max = min(h, int((bbox.ymin + bbox.height + 0.1) * h))

            face_roi = img[y_min:y_max, x_min:x_max]

            # Sample skin-tone pixels from center region (avoiding eyes, mouth)
            center_y_start = int(y_max * 0.2)
            center_y_end = int(y_max * 0.5)
            center_x_start = int(x_max * 0.25)
            center_x_end = int(x_max * 0.75)

            skin_region = face_roi[center_y_start:center_y_end, center_x_start:center_x_end]
            if skin_region.size == 0:
                skin_region = face_roi

            # Convert to HSV and compute average
            hsv_img = cv2.cvtColor(skin_region, cv2.COLOR_BGR2HSV).astype(np.float32)
            avg_h = np.mean(hsv_img[:, :, 0])  # Hue: 0-180 in OpenCV
            avg_s = np.mean(hsv_img[:, :, 1])  # Saturation: 0-255
            avg_v = np.mean(hsv_img[:, :, 2])  # Value: 0-255

            # Normalize for analysis
            undertone = self._classify_undertone(avg_h)
            depth = self._classify_depth(avg_v)
            chroma = self._classify_chroma(avg_s)

            # Look up season
            season = self.SEASON_MAP.get(
                (undertone, depth, chroma),
                SeasonEnum.TRUE_SPRING  # fallback
            )

            return {
                "season": season,
                "confidence": 0.5,  # Always 0.5 for rule-based (uncertainty)
                "undertone": undertone,
                "depth": depth,
                "chroma": chroma,
                "probabilities": self._uniform_probs(),
            }

        except Exception as e:
            return self._no_face_response(f"Error: {str(e)}")

    def _classify_undertone(self, hue: float) -> str:
        """Classify undertone from hue (0-180 in OpenCV)."""
        # Red/Pink: 0-15 or 165-180 (cool)
        # Yellow: 20-40 (warm)
        # Green: 50-90 (cool, but rare in skin)
        # Blue: 100-130 (cool)
        if (hue < 15 or hue > 165) or (100 < hue < 130):
            return "cool"
        elif 20 < hue < 40:
            return "warm"
        else:
            return "neutral"

    def _classify_depth(self, value: float) -> str:
        """Classify skin depth from value (0-255)."""
        normalized_v = value / 255.0
        if normalized_v < 0.4:
            return "dark"
        elif normalized_v < 0.7:
            return "medium"
        else:
            return "light"

    def _classify_chroma(self, saturation: float) -> str:
        """Classify chroma (clarity) from saturation (0-255)."""
        normalized_s = saturation / 255.0
        if normalized_s > 0.4:
            return "clear"
        else:
            return "muted"

    def _no_face_response(self, reason: str) -> dict:
        """Return response when face cannot be detected."""
        return {
            "season": None,
            "confidence": 0.0,
            "error": reason,
            "probabilities": {},
        }

    def _uniform_probs(self) -> dict:
        """Return uniform probabilities across all 16 seasons."""
        prob = 1.0 / 16
        return {
            "Cool Winter": prob,
            "Deep Winter": prob,
            "Bright Winter": prob,
            "True Winter": prob,
            "Bright Spring": prob,
            "Light Spring": prob,
            "Warm Spring": prob,
            "True Spring": prob,
            "Warm Autumn": prob,
            "Deep Autumn": prob,
            "Soft Autumn": prob,
            "True Autumn": prob,
            "Soft Summer": prob,
            "Light Summer": prob,
            "Cool Summer": prob,
            "True Summer": prob,
        }
