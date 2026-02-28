# Serelyn Backend

AI-powered mental health companion API built with FastAPI + PostgreSQL + Groq (Llama).

---

## Local Setup

```bash
# 1. Clone and enter the project
cd serelyn-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env: DATABASE_URL, GROQ_API_KEY, JWT_SECRET (see below)

# 5. Create database tables
# Run schema.sql in your Supabase SQL editor or psql client

# 6. Run the server
uvicorn main:app --reload
```

Server will be live at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs

---

## Where to get secrets

- **GROQ_API_KEY** – Create an API key at [Groq Console](https://console.groq.com). The backend calls Groq for real LLM responses; if this is missing on Render, `/analyze` will return 502.
- **JWT_SECRET** – You don’t “get” this from anywhere; you generate it yourself and keep it private. Use a long random string. Examples:
  - **PowerShell:** `[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])`
  - **Python:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - Or any password generator (32+ random characters). On Render, set **JWT_SECRET** in Environment to this value.

---

## Database Setup (Supabase)

1. Create a project at https://supabase.com
2. Go to **SQL Editor**
3. Paste and run the contents of `schema.sql`
4. Go to **Settings → Database** and copy the **Connection String (URI)**
5. Paste it as `DATABASE_URL` in your `.env`

---

## API Endpoints

### GET /health
```bash
curl http://localhost:8000/health
```
Response:
```json
{"status": "ok", "service": "Serelyn API"}
```

---

### POST /register
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```
Response:
```json
{"message": "User registered successfully", "user_id": 1}
```

---

### POST /login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```
Response:
```json
{"message": "Login successful", "user_id": 1, "access_token": "eyJ..."}
```
Use `access_token` in the `Authorization: Bearer <token>` header for protected routes.

---

### POST /analyze (requires auth)
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"text": "I feel so stressed about my exams"}'
```
Response:
```json
{
  "emotion": "stressed",
  "response": "It sounds like you're carrying a lot right now. Take a breath — you've handled hard things before, and you can get through this too."
}
```

---

## Deploying to Render (Free Tier)

1. Push your code to a GitHub repository.

2. Go to https://render.com and create a **New Web Service**.

3. Connect your GitHub repo.

4. Configure the service:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** Leave default (uses Procfile: `uvicorn main:app --host 0.0.0.0 --port $PORT`)

5. Add Environment Variables in the Render dashboard:
   - `DATABASE_URL` → your Supabase connection string
   - `GROQ_API_KEY` → your Groq API key (https://console.groq.com)
   - `JWT_SECRET` → a long random secret for signing tokens
   - `CORS_ORIGINS` → your frontend URL(s), comma-separated (e.g. `https://yourapp.com`)

6. Click **Deploy**. Render will build and host your API.

> **Tip:** Supabase requires SSL. If you get a connection error, append `?sslmode=require` to your `DATABASE_URL`.

---

## Project Structure

```
serelyn-backend/
├── main.py          # FastAPI app, route handlers, JWT auth
├── database.py      # Connection pool (psycopg2)
├── models.py        # Pydantic request models
├── auth.py          # bcrypt + JWT (hash, verify, create/verify token)
├── ai_service.py    # Groq API call + JSON parsing
├── schema.sql       # Database table definitions
├── requirements.txt
├── Procfile         # Render start command
└── .env.example
```
