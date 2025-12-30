import os
from dotenv import load_dotenv

# Get path to app folder (parent of core)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load .env from app folder
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv("SECRET_KEY", "akjdkjaknxmxsqs-sKNNSKJhs-sakjdhkajshd")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Test connection
try:
    import psycopg2
    conn = psycopg2.connect(SQLALCHEMY_DATABASE_URL)
    conn.close()
    print("✅ PostgreSQL connection successful")
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")
    print("Falling back to SQLite")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./chatbot.db"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
