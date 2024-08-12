from fastapi import APIRouter

from schema.utils import Years

router = APIRouter()


@router.get("/years", response_model=Years)
async def get_years() -> Years:
    return Years(max_year=2024, min_year=2017)
