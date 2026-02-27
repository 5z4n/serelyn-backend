import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT_TEMPLATE = """You are an empathetic mental health companion.

Analyze the emotional state from this message: "{text}"

Classify the emotion as exactly one of: happy, sad, anxious, stressed, angry, neutral

Then write a short, warm, supportive response (2-3 sentences max).

Respond ONLY with valid JSON in this exact format:
{{
  "emotion": "<one of the 6 emotions>",
  "response": "<your supportive message>"
}}

No markdown, no code blocks, no extra text. JSON only."""


def analyze_text(text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(text=text)
    result = model.generate_content(prompt)
    raw = result.text.strip()

    # Strip markdown code fences if Gemini wraps with ```json ... ```
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    parsed = json.loads(raw)

    valid_emotions = {"happy", "sad", "anxious", "stressed", "angry", "neutral"}
    emotion = parsed.get("emotion", "neutral").lower()
    if emotion not in valid_emotions:
        emotion = "neutral"

    response_text = parsed.get("response", "I'm here for you. You're not alone.")

    return {"emotion": emotion, "response": response_text}
