from fastapi import APIRouter, HTTPException

from schema.summary import Summary
from services.summary_service import summary_service
from utils.validate_appid import validate_game

router = APIRouter()


@router.get("/summary", response_model=Summary)
async def get_summary(gameid: int) -> Summary:
    """get game's reviews summary."""
    is_gameid_valid = validate_game(gameid)

    if not is_gameid_valid:
        raise HTTPException(status_code=404, detail="Game not found on Steam")

    try:
        summary = summary_service.get_summary(gameid=gameid)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
