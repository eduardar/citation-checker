import json, time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors
from anthropic import Anthropic

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(timeout=180_000))
FAST_MODEL = "gemini-3.5-flash-lite"
SMART_MODEL = "gemini-3.8-flash"
CHECKER_MODEL = "claude-haiku-5-5"   # different model family, for the coherence check

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

def ask_json_other(prompt: str):
    """Ask a model from a different family (Claude), so the check is independent of Gemini."""
    claude = Anthropic()  # reads ANTHROPIC_API_KEY from .env
    r = claude.messages.create(
        model=CHECKER_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt + "\n\nReply ONLY with valid JSON, no other text."}],
    )
    text = next(b.text for b in r.content if b.type == "text")
    text = text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(text)