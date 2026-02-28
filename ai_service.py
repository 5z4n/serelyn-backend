import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Groq client (fail fast if key missing on import)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in environment. Add it in .env locally or in Render dashboard.")
client = Groq(api_key=GROQ_API_KEY)

PROMPT_TEMPLATE = """You are an empathetic mental health companion.

Analyze the emotional state from this message: "{text}"

Classify the emotion as exactly one of: happy, sad, anxious, stressed, angry, neutral.

Then write a short, warm, supportive response (2-3 sentences max).

Respond ONLY in valid JSON:
{{
  "emotion": "happy/sad/anxious/stressed/angry/neutral",
  "response": "your message"
}}
"""


def _extract_json(raw: str) -> str:
    """Strip markdown code fences if present so json.loads works."""
    raw = raw.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if match:
        return match.group(1).strip()
    return raw


def analyze_text(text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(text=text)

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a mental health assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=200
        )

        raw = completion.choices[0].message.content.strip()
        raw = _extract_json(raw)
        parsed = json.loads(raw)

        valid_emotions = {"happy", "sad", "anxious", "stressed", "angry", "neutral"}
        emotion = parsed.get("emotion", "neutral").lower()

        if emotion not in valid_emotions:
            emotion = "neutral"

        response_text = parsed.get(
            "response",
            "I'm here for you. You're not alone. Take a deep breath."
        )

        return {"emotion": emotion, "response": response_text}

    except json.JSONDecodeError as e:
        print("Groq JSON parse error:", e)
        raise ValueError(f"AI returned invalid format: {e}") from e
    except Exception as e:
        print("Groq error:", e)
        raise RuntimeError(f"AI service failed: {e}") from e
