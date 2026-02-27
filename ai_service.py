import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

        # Try parsing JSON
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

    except Exception as e:
        # ---- FALLBACK (Hackathon Safety Net) ----
        print("Groq error:", e)

        return {
            "emotion": "stressed",
            "response": "I understand this feels overwhelming. Take a slow breath — you're not alone, and things will get better step by step."
        }