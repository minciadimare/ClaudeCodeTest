from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.image_service import ImageService
from app.services.inference_service import InferenceService
from app.schemas.prediction import ClassifyResponse
from app.config import settings

router = APIRouter(prefix="/api", tags=["inference"])

image_service = ImageService()
inference_service = InferenceService()


@router.post("/classify", response_model=ClassifyResponse)
async def classify_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image and get armochromia classification."""

    # Read file
    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        # Save image
        image = await image_service.save_upload_image(
            file_bytes=file_bytes,
            filename=file.filename,
            db=db,
            source="manual_upload",
        )

        # Classify
        result = await inference_service.classify_image(
            image=image,
            db=db,
            storage_path=settings.storage_path,
        )

        return ClassifyResponse(
            prediction_uuid=image.uuid,
            season=result.get("season"),
            confidence=result.get("confidence", 0.0),
            probabilities=result.get("probabilities", {}),
            inference_method=result.get("inference_method", "rule_based"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
