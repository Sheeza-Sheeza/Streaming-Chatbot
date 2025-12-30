from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from app.core.security import verify_token
from app.services.websocket_chat import handle_chat

router = APIRouter()

async def get_token_from_query(websocket: WebSocket) -> str:
    """Extract and validate JWT token from WebSocket query parameters."""
    token = websocket.query_params.get("token")
    if not token:
        print(" No token in query params")
        await websocket.close(code=1008, reason="Authentication required")
        raise HTTPException(status_code=401, detail="Token required")

    print(f" Verifying token: {token[:20]}...")
    payload = verify_token(token)
    if not payload:
        print(" Invalid token")
        await websocket.close(code=1008, reason="Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    if not username:
        print(" No username in token")
        await websocket.close(code=1008, reason="Invalid token payload")
        raise HTTPException(status_code=401, detail="Invalid token")

    print(f" Token verified for user: {username}")
    return username

@router.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    try:
        # Extract and validate token BEFORE accepting connection
        username = await get_token_from_query(websocket)

        # Accept the WebSocket connection
        await websocket.accept()
        print(f" WebSocket connection accepted for {username}")

        # Handle chat
        await handle_chat(websocket, username)

    except HTTPException:
        # Token validation failed, connection already closed
        pass
    except WebSocketDisconnect:
        print(f" WebSocket disconnected for user: {username}")
    except Exception as e:
        print(f" WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
