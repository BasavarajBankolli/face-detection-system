from typing import List
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.roi import ROIDetection

router = APIRouter(prefix="/api", tags=["ROI"])


class ROIDetectionSchema(BaseModel):
    id: int
    session_id: str
    frame_number: int

    x: int
    y: int
    width: int
    height: int

    confidence: float
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get("/roi", response_model=List[ROIDetectionSchema])
async def get_roi_data():
    """
    Return latest 50 ROI detections.
    """

    async with SessionLocal() as session:
        result = await session.execute(
            select(ROIDetection)
            .order_by(ROIDetection.id.desc())
            .limit(10) 
        )

        rows = result.scalars().all()

        return rows