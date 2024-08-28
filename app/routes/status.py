from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from schema.utils import ServerStatus
from services.db_service import db_service

router = APIRouter()


@router.get("/health", response_model=ServerStatus)
async def get_health(db: AsyncSession = Depends(get_db)) -> ServerStatus:
    """Check API status"""
    last_update = await db_service.get_last_update(db)
    return ServerStatus(status="online", update=last_update)
