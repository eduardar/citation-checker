import json
from fetch import fetch_text

ex = json.load(open("example.json", encoding="utf-8"))
for k, url in ex["sources"].items():
    text = fetch_text(url)
    print(f"[{k}] {url}: {len(text)} chars")
    for word in ["330", "Koechlin", "Bastille", "visitors"]:
        if word in text:
            print(f"   found '{word}'")