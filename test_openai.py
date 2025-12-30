#!/usr/bin/env python3
"""
Test script to verify OpenAI API connectivity
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_openai():
    print("🔧 OpenAI API Test")
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        return

    try:
        client = OpenAI()
        print("✅ OpenAI client initialized")

        # Test simple completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10
        )

        print(f"✅ API call successful: {response.choices[0].message.content}")

    except Exception as e:
        print(f"❌ OpenAI API error: {e}")

if __name__ == "__main__":
    test_openai()