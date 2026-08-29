from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.spotify import SpotifyToken as SpotifyTokenModel

router = APIRouter()


@router.get("/view")
async def me(
    uid: str,
    res: Response,
    db: AsyncSession = Depends(get_db),
):
    if not await _is_valid_uid(uid, db):
        res.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "Invalid user ID. Please log in again."}

    return {"message": "You are logged in."}


async def _is_valid_uid(uid: str, db: AsyncSession) -> bool:
    result = await db.execute(
        select(SpotifyTokenModel).where(
            SpotifyTokenModel.user_id == uid
        )
    )
    spotify = result.scalar_one_or_none()
    return spotify is not None