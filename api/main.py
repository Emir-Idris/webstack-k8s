import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI, HTTPException

DB_HOST = os.getenv("DB_HOST", "mariadb")
DB_USER = os.getenv("DB_USER", "webuser")
DB_PASS = os.getenv("DB_PASS", "webpass")
DB_NAME = os.getenv("DB_NAME", "webapp")
DEFAULT_NAME = os.getenv("DEFAULT_NAME", "JM")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI()

# Frontend draait op :8080 => CORS toelaten. [web:10]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
              id INT AUTO_INCREMENT PRIMARY KEY,
              name VARCHAR(255) NOT NULL
            )
        """))
        cnt = conn.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        if cnt == 0:
            conn.execute(
                text("INSERT INTO users (name) VALUES (:name)"),
                {"name": DEFAULT_NAME},
            )

@app.on_event("startup")
def on_startup():
    # MariaDB kan nog even nodig hebben om “ready” te worden. [web:142]
    for _ in range(30):
        try:
            init_db()
            return
        except OperationalError:
            time.sleep(1)
    init_db()

@app.get("/user")
def get_user():
    with engine.connect() as conn:
        row = conn.execute(text("SELECT name FROM users ORDER BY id LIMIT 1")).fetchone()
        return {"name": row[0] if row else "Unknown"}

@app.get("/container")
def get_container():
    return {"container_id": os.getenv("HOSTNAME", "unknown")}


@app.get("/health")
def health_check():
    """Liveness: Check if process is alive."""
    return {"status": "alive"}

@app.get("/ready")
def readiness_check():
    """Readiness: Check if DB connection works."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")