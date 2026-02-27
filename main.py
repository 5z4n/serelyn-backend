from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection
from models import RegisterRequest, LoginRequest, AnalyzeRequest
from auth import hash_password, verify_password
from ai_service import analyze_text

app = FastAPI(title="Serelyn API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        conn.close()


@app.post("/login")
def login(body: LoginRequest):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (body.email,))
            user = cur.fetchone()
            if not user or not verify_password(body.password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            return {"message": "Login successful", "user_id": user["id"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/analyze")
def analyze(body: AnalyzeRequest):
    # Validate user exists
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", (body.user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    # Call Gemini
    try:
        result = analyze_text(body.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    # Save interaction
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO interactions (user_id, text, emotion, response) VALUES (%s, %s, %s, %s)",
                (body.user_id, body.text, result["emotion"], result["response"]),
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

    return result
