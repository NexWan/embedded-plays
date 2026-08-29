import base64
import random

import httpx
from fastapi import APIRouter, Response, status
from fastapi.responses import RedirectResponse

from app.core.config import settings

router = APIRouter()

@router.get("/login")
async def login():
    state = random.randbytes(16).hex()
    scope="user-read-playback-state user-read-currently-playing"

    return RedirectResponse(
        url=(
            f"https://accounts.spotify.com/authorize?response_type=code&client_id={settings.CLIENT_ID}"
            f"&scope={scope}&redirect_uri={settings.REDIRECT_URI}&state={state}"
        )
    )

@router.get("/callback")
async def callback(code: str, state: str, res: Response):
    if not state:
        res.status_code = status.HTTP_418_IM_A_TEAPOT # muhehe
        return {"error": "State parameter is missing. Please try again."}

    auth_options = {
        "url": "https://accounts.spotify.com/api/token",
        "data": {
            "code": code,
            "redirect_uri": settings.REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        "headers": {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + base64.b64encode(
                f"{settings.CLIENT_ID}:{settings.CLIENT_SECRET}".encode()
            ).decode()
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(**auth_options)
        if response.status_code != 200:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Failed to retrieve access token from Spotify."}

        token_data = response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        # return at the moment, change later to set cookies or session
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "scope": token_data.get("scope"),
        }
    


