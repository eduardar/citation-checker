import os, json, hashlib, requests, trafilatura
from dotenv import load_dotenv
from nimble_python import Nimble

load_dotenv()
nimble = Nimble(api_key=os.environ.get("NIMBLE_API_KEY"))
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(url):
    return os.path.join(CACHE_DIR, hashlib.md5(url.encode()).hexdigest() + ".json")

def fetch_text(url: str, max_chars: int = 40000) -> str:
    path = _cache_path(url)
    if os.path.exists(path):  # already fetched: reuse it
        return json.load(open(path, encoding="utf-8"))["text"]

    text = ""
    try:
        r = nimble.extract.run(url=url, render=True)
        text = trafilatura.extract(r.data.html) or ""
    except Exception as e:
        print(f"Nimble failed on {url}: {e}")

    if not text:  # backup: plain request
        try:
            html = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}).text
            text = trafilatura.extract(html) or ""
        except Exception as e:
            print(f"Fetch failed on {url}: {e}")

    text = text[:max_chars]
    if text:
        json.dump({"url": url, "text": text}, open(path, "w", encoding="utf-8"))
    return text