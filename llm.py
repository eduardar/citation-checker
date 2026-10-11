import json, time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(timeout=180_000))
FAST_MODEL = "gemini-3.5-flash-lite"
SMART_MODEL = "gemini-3.8-flash"

def _with_retry(fn, retries=6):
    for attempt in range(retries):
        try:
            return fn()
        except errors.APIError as e:
            if e.code in (429, 503, 504) and attempt < retries - 1:
                wait = 45 if e.code == 429 else 15 * (attempt + 1)
                print(f"  Gemini {e.code}, waiting {wait}s and retrying...")
                time.sleep(wait)
            else:
                raise

def ask_llm(prompt: str, model: str = FAST_MODEL) -> str:
    return _with_retry(lambda: client.models.generate_content(model=model, contents=prompt).text)

def ask_json(prompt: str, model: str = FAST_MODEL):
    def call():
        r = client.models.generate_content(
            model=model, contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(r.text)
    return _with_retry(call)