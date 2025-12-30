import asyncio
import websockets
import json
import requests

async def test_websocket_auth():
    # First, create a test user
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }

    try:
        # Signup
        signup_response = requests.post(
            "http://127.0.0.1:8000/auth/signup",
            json=signup_data
        )
        print(f"Signup response: {signup_response.status_code}")
        if signup_response.status_code != 200:
            print(f"Signup failed: {signup_response.text}")
            # Try signin instead
            signin_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            signin_response = requests.post(
                "http://127.0.0.1:8000/auth/signin",
                data=signin_data
            )
            print(f"Signin response: {signin_response.status_code}")

            if signin_response.status_code == 200:
                token_data = signin_response.json()
                token = token_data.get("access_token")
                print(f"Got token: {token[:20]}...")

                # Test WebSocket connection
                uri = f"ws://127.0.0.1:8000/ws/chat?token={token}"
                print(f"Connecting to: {uri}")

                async with websockets.connect(uri) as websocket:
                    print("WebSocket connected successfully!")

                    # Send a test message
                    await websocket.send("Hello, can you help me test this chatbot?")
                    print("Sent test message")

                    # Receive responses
                    while True:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            print(f"Received: {response}")
                            if response == "__END__":
                                break
                        except asyncio.TimeoutError:
                            print("Timeout waiting for response")
                            break

            else:
                print(f"Signin failed: {signin_response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_auth())