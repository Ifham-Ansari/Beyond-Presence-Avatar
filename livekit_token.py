# main.py
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("livekit-backend")

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
    logger.error("Missing LiveKit credentials in environment variables")

app = FastAPI(title="LiveKit Token Server", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_token")
def get_token(room_name: str = "test-room", identity: str = "test_user") -> dict:
    """
    Generates a LiveKit access token with a room name and identity.
    """
    try:
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            raise HTTPException(status_code=500, detail="LiveKit API credentials not set.")

        logger.info(f"Generating token for room={room_name}, identity={identity}")
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)

        # Define grants
        grant = api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        )

        # Apply grants and identity
        token.with_grants(grant)
        token.identity = identity
        
        jwt_token = token.to_jwt()

        logger.info(f"Token generated successfully for {identity}")

        return {
            "url": LIVEKIT_URL,
            "token": jwt_token,
            "room_name": room_name,
            "identity": identity
        }

    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "livekit_url": LIVEKIT_URL,
        "has_credentials": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET)
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting LiveKit Token Server on port 8011")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)