from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from schema.summary import Summary
from services.game_service import game_service
from services.summary_service import summary_service
from utils.validate_appid import is_existing_game

router = APIRouter()


@router.get("/summary", response_model=Summary)
async def get_summary(db: AsyncSession = Depends(get_db), gameid: int = 0) -> Summary:
    """get game's reviews summary."""
    is_known_game = (
        True
        if await game_service.read_game_by_id(session=db, gameid=gameid) is not None
        else False
    )
    if not is_known_game:
        is_known_game = is_existing_game(gameid=gameid)

    if not is_known_game:
        raise HTTPException(status_code=404, detail="Game not found on Steam")

    try:
        summary = summary_service.get_summary(gameid=gameid)
        return summary
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
