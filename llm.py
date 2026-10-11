import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.8-flash" 

def ask_llm(prompt: str) -> str:
    return client.models.generate_content(model=MODEL, contents=prompt).text

def ask_json(prompt: str):
    r = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(r.text)