import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from database import get_connection, return_connection
from models import RegisterRequest, LoginRequest, AnalyzeRequest
from auth import hash_password, verify_password, create_access_token, verify_token
from ai_service import analyze_text

load_dotenv()

app = FastAPI(title="Serelyn API", version="1.0.0")

# CORS: restrict origins in production via CORS_ORIGINS env (comma-separated)
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").strip()
origins = [o.strip() for o in _cors_origins.split(",")] if _cors_origins else ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


def get_current_user_id(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> int:
    if not credentials or credentials.scheme != "Bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id


@app.get("/health")
def health():
    return {"status": "ok", "service": "Serelyn API"}


@app.post("/register", status_code=201)
def register(body: RegisterRequest):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (body.email,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="Email already registered")

            pw_hash = hash_password(body.password)
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (body.email, pw_hash),
            )
            user_id = cur.fetchone()["id"]
            conn.commit()
            return {"message": "User registered successfully", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        return_connection(conn)


@app.post("/login")
def login(body: LoginRequest):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (body.email,))
            user = cur.fetchone()
            if not user or not verify_password(body.password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            token = create_access_token(user["id"])
            return {"message": "Login successful", "user_id": user["id"], "access_token": token}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        return_connection(conn)


@app.post("/analyze")
def analyze(body: AnalyzeRequest, user_id: int = Depends(get_current_user_id)):
    # Call Groq for emotion + response
    try:
        result = analyze_text(body.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO interactions (user_id, text, emotion, response) VALUES (%s, %s, %s, %s)",
                (user_id, body.text, result["emotion"], result["response"]),
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        return_connection(conn)

    return result
