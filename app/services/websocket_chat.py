from fastapi import WebSocket, WebSocketDisconnect
from openai import OpenAI
import re

import os
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path)  # Adjust path relative to this file

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




# Generic system prompt base
BASE_SYSTEM_PROMPT = """
You are a helpful AI assistant that can answer any question on any topic.
Be informative, accurate, and engaging.

Response guidelines:
- For "what is" or definition questions: Provide concise, clear definitions with simple examples if helpful.
- For "how it works" or "how does it work" questions: Give clear, concise step-by-step explanations.
- For comparisons: Use bullet points or simple tables.
- For general questions: Provide natural, conversational responses.
- Keep answers clean, demo-ready, and focused.
- Use Markdown formatting for better readability (**bold**, *italic*, - bullet lists, 1. numbered lists, ### headers).
- Include relevant examples to illustrate points when appropriate.
- When terms have multiple meanings, prioritize AI/ML/Tech interpretations if applicable, but explain all relevant meanings when appropriate.
"""

def get_system_prompt(mode: str) -> str:
    """Generate system prompt based on mode."""
    if mode == "concise":
        return BASE_SYSTEM_PROMPT + "\nProvide brief, direct answers with key facts only."
    elif mode == "structured":
        return BASE_SYSTEM_PROMPT + "\nProvide clear, concise step-by-step explanations."
    else:
        return BASE_SYSTEM_PROMPT + "\nProvide balanced, informative responses without overwhelming details."

def detect_mode(user_message: str) -> str:
    """Automatically detect mode based on user query."""
    msg_lower = user_message.lower().strip()
    greetings = ["hi", "hello", "hey", "hiya", "hi there", "hey there", "good morning", "good afternoon", "good evening"]
    if msg_lower in greetings:
        return "concise"
    elif "what is" in msg_lower or "define" in msg_lower or "meaning of" in msg_lower:
        return "concise"
    elif "how" in msg_lower or "explain" in msg_lower or "step" in msg_lower:
        return "structured"
    else:
        return "default"

def refine_prompt(user_message: str) -> str:
    """Internally refine unclear or short prompts for better GPT responses."""
    greetings = ["hi", "hello", "hey", "hiya", "hi there", "hey there", "good morning", "good afternoon", "good evening"]
    if user_message.lower().strip() in greetings:
        return user_message
    words = user_message.split()
    if len(words) < 3:
        # Short prompt, add context
        return f"Please provide a detailed answer to: {user_message}"
    elif not any(word in user_message.lower() for word in ["what", "how", "why", "when", "where", "who", "explain", "compare", "difference"]):
        # Not a clear question, make it one
        return f"Can you explain: {user_message}"
    return user_message

def extract_topic(user_message: str) -> str:
    """Extract main topic from user message (simple heuristic)."""
    # Remove common question words
    cleaned = re.sub(r'\b(what|how|why|when|where|who|is|are|does|do|can|you|explain|tell|me|about)\b', '', user_message, flags=re.IGNORECASE)
    # Take first few words as topic
    words = cleaned.strip().split()[:3]
    return ' '.join(words) if words else user_message.strip()

async def handle_chat(websocket: WebSocket, username: str):
    # Per-connection context
    conversation = []  # List of {"role": "user"|"assistant", "content": str}
    last_topic = None  # Track last user topic for vague follow-ups


    try:
        while True:
            user_message = await websocket.receive_text()
            print(f" Received message from {username}: {user_message}")

            # Handle vague follow-ups
            msg_lower = user_message.lower().strip()
            vague_followups = ["how it works", "how does it work", "explain more", "working flow"]
            if msg_lower in vague_followups and last_topic:
                user_message = f"Explain how {last_topic} works"
                print(" Expanded vague follow-up to:", user_message)

            # Update last topic if not a vague follow-up
            if msg_lower not in vague_followups:
                last_topic = extract_topic(user_message)
                print(f" Updated last topic to: {last_topic}")

            # Refine prompt internally
            refined_message = refine_prompt(user_message)
            print(f" Refined message: {refined_message}")

            # Determine mode
            mode = detect_mode(refined_message)
            print(f" Detected mode: {mode}")

            # Add user message to conversation
            conversation.append({"role": "user", "content": refined_message})
            # Keep only last 6 messages for context
            if len(conversation) > 6:
                conversation = conversation[-6:]

            # Build messages for GPT
            system_prompt = get_system_prompt(mode)
            messages = [{"role": "system", "content": system_prompt}] + conversation
            print(f" Sending {len(messages)} messages to OpenAI")

            # GPT-4o streaming response
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    stream=True,
                )
                print(" OpenAI stream created successfully")
            except Exception as e:
                print(f" OpenAI API error: {e}")
                await websocket.send_text("__START__")
                await websocket.send_text("Sorry, I'm having trouble connecting to my brain right now. Please try again.")
                await websocket.send_text("__END__")
                continue

            # Send start marker
            await websocket.send_text("__START__")
            print(" Sent __START__ marker")

            full_response = ""
            chunk_count = 0
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content

                    full_response += delta
                    await websocket.send_text(delta)
                    chunk_count += 1

            print(f" Sent {chunk_count} chunks, total response length: {len(full_response)}")

            # Send end marker
            await websocket.send_text("__END__")
            print(" Sent __END__ marker")

            # Add assistant response to conversation
            conversation.append({"role": "assistant", "content": full_response})

    except WebSocketDisconnect:
        print(f" WebSocket disconnected for user: {username}")
    except Exception as e:
        print(f" Unexpected error in handle_chat for {username}: {e}")
        import traceback
        traceback.print_exc()
