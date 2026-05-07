from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Image, Label
from app.services.label_service import LabelService
from app.services.image_service import ImageService
from app.schemas.image import ImageResponse, ImageDetailResponse
from app.schemas.label import LabelCreate, LabelResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])

label_service = LabelService()
image_service = ImageService()


@router.get("/images", response_model=list[ImageResponse])
async def get_images(
    db: AsyncSession = Depends(get_db),
    unlabeled: bool = Query(True),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Get paginated list of images, optionally filtered to unlabeled only."""

    offset = (page - 1) * per_page

    if unlabeled:
        stmt = (
            select(Image)
            .outerjoin(Label)
            .where(Label.id == None)
            .order_by(Image.created_at.desc())
            .limit(per_page)
            .offset(offset)
        )
    else:
        stmt = select(Image).order_by(Image.created_at.desc()).limit(per_page).offset(offset)

    result = await db.execute(stmt)
    images = result.scalars().all()

    return [
        ImageResponse(
            id=img.id,
            uuid=img.uuid,
            filename=img.filename,
            source=img.source,
            is_face_detected=img.is_face_detected,
            face_count=img.face_count,
            storage_path=img.storage_path,
            thumbnail_path=img.thumbnail_path,
            created_at=img.created_at,
        )
        for img in images
    ]


@router.get("/images/{uuid}", response_model=ImageDetailResponse)
async def get_image_detail(
    uuid: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed info about a single image including label."""

    image = await image_service.get_image_by_uuid(uuid, db)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    label = await label_service.get_label_by_image_uuid(uuid, db)

    labels_data = []
    if label:
        labels_data.append({
            "id": label.id,
            "season": label.season,
            "confidence": label.confidence,
            "label_source": label.label_source,
            "is_verified": label.is_verified,
        })

    return ImageDetailResponse(
        id=image.id,
        uuid=image.uuid,
        filename=image.filename,
        source=image.source,
        is_face_detected=image.is_face_detected,
        face_count=image.face_count,
        storage_path=image.storage_path,
        thumbnail_path=image.thumbnail_path,
        created_at=image.created_at,
        labels=labels_data,
        predictions=[],
    )


@router.post("/images/{uuid}/label", response_model=LabelResponse)
async def label_image(
    uuid: str,
    label_data: LabelCreate,
    db: AsyncSession = Depends(get_db),
):
    """Assign or update label for an image."""

    image = await image_service.get_image_by_uuid(uuid, db)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    label = await label_service.create_or_update_label(
        image_uuid=uuid,
        season=label_data.season.value,
        db=db,
        confidence=label_data.confidence,
        label_source=label_data.label_source,
        labeled_by=label_data.labeled_by,
        notes=label_data.notes,
        is_verified=label_data.is_verified,
    )

    return LabelResponse(
        id=label.id,
        image_id=label.image_id,
        season=label.season,
        confidence=label.confidence,
        label_source=label.label_source,
        labeled_by=label.labeled_by,
        notes=label.notes,
        is_verified=label.is_verified,
    )


@router.delete("/images/{uuid}")
async def delete_image(
    uuid: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete an image and its DB record."""

    success = await image_service.delete_image(uuid, db)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")

    return {"status": "deleted"}


@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics on images and labels."""

    total_images = await db.execute(select(func.count(Image.id)))
    total_images = total_images.scalar()

    labeled = await db.execute(select(func.count(Label.id)))
    labeled = labeled.scalar()

    verified = await db.execute(select(func.count(Label.id)).where(Label.is_verified == True))
    verified = verified.scalar()

    return {
        "total_images": total_images,
        "labeled": labeled,
        "unlabeled": total_images - labeled,
        "verified": verified,
        "unverified": labeled - verified,
    }
