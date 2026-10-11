import json
from fetch import fetch_text

ex = json.load(open("agent_example.json", encoding="utf-8"))
print("=== Fetched text per source ===")
for k, url in ex["sources"].items():
    print(f"[{k}] {len(fetch_text(url)):6} chars  {url}")

print("\n=== Non-supported claims: evidence and reason ===")
for r in json.load(open("agent_results.json", encoding="utf-8")):
    if r["verdict"] != "supported":
        print(f"\n{r['verdict'].upper()} {r['citations']}: {r['claim']}")
        print(f"   evidence: {r.get('evidence', '')[:200]}")
        print(f"   reason:   {r.get('reason', '')}")

print("\n=== Raw Nimble claim example ===")
print(json.dumps(ex["nimble_claims"][:2], indent=2, ensure_ascii=False))