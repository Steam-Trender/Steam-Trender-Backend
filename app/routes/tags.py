from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from schema.tag import Tag
from services.game_service import game_service

router = APIRouter()


@router.get("/tags", response_model=List[Tag])
async def get_tags(db: AsyncSession = Depends(get_db)) -> List[Tag]:
    """Get all tags."""
    try:
        tags = await game_service.read_all_tags(db)
        return tags
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
