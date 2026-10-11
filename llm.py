import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(timeout=90_000))
FAST_MODEL = "gemini-3.5-flash-lite"
SMART_MODEL = "gemini-3.8-flash"

def ask_llm(prompt: str, model: str = FAST_MODEL) -> str:
    return client.models.generate_content(model=model, contents=prompt).text

def ask_json(prompt: str, model: str = FAST_MODEL):
    r = client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(r.text)