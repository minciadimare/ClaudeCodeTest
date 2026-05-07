import json
import time
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Image, Prediction
from app.fallback.rule_based import RuleBasedClassifier


class InferenceService:
    def __init__(self):
        self.rule_based = RuleBasedClassifier()
        self.model = None
        self.model_version = None

    async def classify_image(self, image: Image, db: AsyncSession, storage_path: str) -> dict:
        """
        Classify image using priority cascade:
        1. PyTorch model (if loaded)
        2. Rule-based HSV classifier (always available)
        """
        start_time = time.time()

        # Full path to image file
        image_path = Path(storage_path) / image.storage_path

        # Try PyTorch model first
        if self.model is not None:
            try:
                result = self._classify_with_pytorch(image_path)
                inference_method = "pytorch"
            except Exception as e:
                print(f"PyTorch inference failed: {e}, falling back to rule-based")
                result = self.rule_based.classify(str(image_path))
                inference_method = "rule_based"
        else:
            # Use rule-based fallback
            result = self.rule_based.classify(str(image_path))
            inference_method = "rule_based"

        latency_ms = int((time.time() - start_time) * 1000)

        # Check for errors (no face detected)
        if "error" in result or result.get("season") is None:
            return {
                "season": None,
                "confidence": 0.0,
                "probabilities": result.get("probabilities", {}),
                "inference_method": inference_method,
                "error": result.get("error", "Could not classify image"),
            }

        # Store prediction in DB
        probabilities_json = json.dumps(result.get("probabilities", {}))
        prediction = Prediction(
            image_id=image.id,
            model_version=self.model_version or "rule_based_v1",
            predicted_season=result["season"],
            confidence=result["confidence"],
            probabilities=probabilities_json,
            inference_method=inference_method,
            latency_ms=latency_ms,
        )
        db.add(prediction)
        await db.commit()

        return {
            "season": result["season"],
            "confidence": result["confidence"],
            "probabilities": result.get("probabilities", {}),
            "inference_method": inference_method,
        }

    def _classify_with_pytorch(self, image_path: Path) -> dict:
        """Classify using PyTorch model (not yet implemented)."""
        raise NotImplementedError("PyTorch model not yet loaded")

    def load_model(self, checkpoint_path: str, device: str = "cpu"):
        """Load trained PyTorch model (Phase 5)."""
        # TODO: Implement model loading
        pass
