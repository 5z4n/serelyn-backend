# Serelyn Backend

AI-powered mental health companion API built with FastAPI + PostgreSQL + Gemini.

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
# Edit .env and fill in DATABASE_URL and GEMINI_API_KEY

# 5. Create database tables
# Run schema.sql in your Supabase SQL editor or psql client

# 6. Run the server
uvicorn main:app --reload
```

Server will be live at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs

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
{"message": "Login successful", "user_id": 1}
```

---

### POST /analyze
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "text": "I feel so stressed about my exams"}'
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
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`

5. Add Environment Variables in the Render dashboard:
   - `DATABASE_URL` → your Supabase connection string
   - `GEMINI_API_KEY` → your Google Gemini API key

6. Click **Deploy**. Render will build and host your API.

> **Tip:** Supabase requires SSL. If you get a connection error, append `?sslmode=require` to your `DATABASE_URL`.

---

## Project Structure

```
serelyn-backend/
├── main.py          # FastAPI app, all route handlers
├── database.py      # psycopg2 connection helper
├── models.py        # Pydantic request models
├── auth.py          # bcrypt password hashing & verification
├── ai_service.py    # Gemini API call + JSON parsing
├── schema.sql       # Database table definitions
├── requirements.txt
└── .env.example
```
