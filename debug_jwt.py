#!/usr/bin/env python3
"""
Debug script to test JWT token creation and verification
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import create_access_token, verify_token
from app.core.config import SECRET_KEY, ALGORITHM

def test_jwt():
    print("🔧 JWT Debug Test")
    print(f"SECRET_KEY: {SECRET_KEY}")
    print(f"ALGORITHM: {ALGORITHM}")

    # Create token
    test_data = {"sub": "testuser"}
    token = create_access_token(test_data)
    print(f"✅ Created token: {token[:50]}...")

    # Verify token
    payload = verify_token(token)
    if payload:
        print(f"✅ Token verified successfully: {payload}")
    else:
        print("❌ Token verification failed")

if __name__ == "__main__":
    test_jwt()