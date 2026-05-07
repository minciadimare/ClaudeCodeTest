import hashlib
import uuid
from pathlib import Path
from datetime import datetime
from PIL import Image as PILImage
import mediapipe as mp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Image, Label
from app.config import settings


class ImageService:
    def __init__(self):
        self.storage_path = Path(settings.storage_path)
        self.images_path = self.storage_path / "images"
        self.thumbnails_path = self.images_path / "thumbnails"
        self.images_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)

        # Initialize mediapipe face detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )

    async def save_upload_image(
        self,
        file_bytes: bytes,
        filename: str,
        db: AsyncSession,
        source: str = "manual_upload",
        original_url: str = None,
        label_season: str = None,
    ) -> Image:
        """Save uploaded image, check for duplicates, detect face, generate thumbnail."""

        # Compute SHA-256 hash for deduplication
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # Check if image already exists
        stmt = select(Image).where(Image.file_hash == file_hash)
        existing = await db.execute(stmt)
        existing_image = existing.scalars().first()
        if existing_image:
            return existing_image

        # Create Image record
        image_uuid = str(uuid.uuid4())
        now = datetime.utcnow()
        date_path = now.strftime("%Y-%m")

        # Determine storage path based on source
        if source.startswith("scraped_"):
            storage_subdir = f"scraped/{source.replace('scraped_', '')}/{date_path}"
        else:
            storage_subdir = f"uploads/{date_path}"

        storage_dir = self.images_path / storage_subdir
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Determine file extension
        try:
            pil_img = PILImage.open(__import__("io").BytesIO(file_bytes))
            file_format = pil_img.format or "JPEG"
            ext = file_format.lower()
            if ext == "jpg":
                ext = "jpeg"
        except Exception:
            file_format = "JPEG"
            ext = "jpeg"

        # Save original image
        filename_with_uuid = f"{image_uuid}.{ext}"
        file_path = storage_dir / filename_with_uuid
        file_path.write_bytes(file_bytes)

        # Get image dimensions and detect face
        try:
            pil_img = PILImage.open(file_path)
            width, height = pil_img.size

            # Face detection
            import cv2
            import numpy as np

            img_array = cv2.imread(str(file_path))
            if img_array is not None:
                results = self.face_detector.process(
                    cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                )
                is_face_detected = results.detections is not None and len(results.detections) > 0
                face_count = len(results.detections) if results.detections else 0
            else:
                is_face_detected = False
                face_count = 0

            # Generate thumbnail (224x224)
            thumb_path = self.thumbnails_path / f"{image_uuid}_thumb.jpg"
            pil_img.thumbnail((224, 224), PILImage.Resampling.LANCZOS)
            pil_img.save(thumb_path, "JPEG", quality=85)
            thumbnail_path = f"thumbnails/{image_uuid}_thumb.jpg"

        except Exception as e:
            width = None
            height = None
            is_face_detected = False
            face_count = 0
            thumbnail_path = None

        # Create Image record
        image = Image(
            uuid=image_uuid,
            filename=filename,
            original_url=original_url,
            source=source,
            file_hash=file_hash,
            file_size_bytes=len(file_bytes),
            width=width,
            height=height,
            format=file_format,
            is_face_detected=is_face_detected,
            face_count=face_count,
            storage_path=f"{storage_subdir}/{filename_with_uuid}",
            thumbnail_path=thumbnail_path,
        )

        db.add(image)

        # Auto-label if keyword-inferred
        if label_season:
            label = Label(
                image=image,
                season=label_season,
                confidence=None,
                label_source="keyword_inferred",
                is_verified=False,
            )
            db.add(label)

        await db.commit()
        await db.refresh(image)
        return image

    async def get_image_by_uuid(self, uuid: str, db: AsyncSession) -> Image:
        """Fetch image by UUID."""
        stmt = select(Image).where(Image.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete_image(self, image_uuid: str, db: AsyncSession) -> bool:
        """Delete image file and DB record."""
        image = await self.get_image_by_uuid(image_uuid, db)
        if not image:
            return False

        # Delete file
        file_path = self.images_path / image.storage_path
        if file_path.exists():
            file_path.unlink()

        # Delete thumbnail
        if image.thumbnail_path:
            thumb_path = self.images_path / image.thumbnail_path
            if thumb_path.exists():
                thumb_path.unlink()

        # Delete DB record (cascades to labels, predictions)
        await db.delete(image)
        await db.commit()
        return True

    def get_file_url(self, image: Image) -> str:
        """Return the media URL for an image."""
        return f"/media/{image.storage_path}"

    def get_thumbnail_url(self, image: Image) -> str:
        """Return the media URL for a thumbnail."""
        if image.thumbnail_path:
            return f"/media/{image.thumbnail_path}"
        return self.get_file_url(image)
