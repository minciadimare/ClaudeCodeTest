from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Image, Label, SeasonEnum


class LabelService:
    async def create_or_update_label(
        self,
        image_uuid: str,
        season: str,
        db: AsyncSession,
        confidence: float = None,
        label_source: str = "human",
        labeled_by: str = None,
        notes: str = None,
        is_verified: bool = False,
    ) -> Label:
        """Create or update label for an image."""

        # Get image
        stmt = select(Image).where(Image.uuid == image_uuid)
        result = await db.execute(stmt)
        image = result.scalars().first()
        if not image:
            raise ValueError(f"Image {image_uuid} not found")

        # Check if label already exists
        label_stmt = select(Label).where(Label.image_id == image.id)
        label_result = await db.execute(label_stmt)
        label = label_result.scalars().first()

        if label:
            # Update existing label
            label.season = season
            label.confidence = confidence
            label.label_source = label_source
            label.labeled_by = labeled_by
            label.notes = notes
            label.is_verified = is_verified
        else:
            # Create new label
            label = Label(
                image_id=image.id,
                season=season,
                confidence=confidence,
                label_source=label_source,
                labeled_by=labeled_by,
                notes=notes,
                is_verified=is_verified,
            )
            db.add(label)

        await db.commit()
        await db.refresh(label)
        return label

    async def get_label_by_image_uuid(self, image_uuid: str, db: AsyncSession) -> Label:
        """Get label for an image."""
        stmt = (
            select(Label)
            .join(Image)
            .where(Image.uuid == image_uuid)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_unlabeled_images(self, db: AsyncSession, limit: int = 20, offset: int = 0):
        """Get images without labels (or with unverified labels)."""
        stmt = (
            select(Image)
            .outerjoin(Label)
            .where(Label.id == None)  # No label at all
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_unlabeled_images(self, db: AsyncSession) -> int:
        """Count unlabeled images."""
        stmt = (
            select(Image)
            .outerjoin(Label)
            .where(Label.id == None)
        )
        result = await db.execute(stmt)
        return len(result.scalars().all())
