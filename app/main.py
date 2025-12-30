from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import auth, chat
import os
from dotenv import load_dotenv
import os

from dotenv import load_dotenv
import os

# Load the .env file from app folder explicitly
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print(" Database tables created successfully")
except Exception as e:
    print(f" Failed to create database tables: {e}")
    print("Please ensure PostgreSQL is running and credentials are correct.")

app = FastAPI(title="GPT-4o Streaming Chatbot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, tags=["chat"])

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    """Serve index.html at root URL"""
    return FileResponse(os.path.join("frontend", "index.html"))
