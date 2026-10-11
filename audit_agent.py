import json, re
from pipeline import check
from fetch import fetch_text

def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()

ex = json.load(open("agent_example.json", encoding="utf-8"))

# 1. Keep only the answer body (drop the appended source index)
answer = ex["answer"].split("Source index:")[0].split("\n---")[0]

# 2. Do Nimble's own excerpts actually appear on the live pages?
print("=== Nimble excerpt check ===")
found = total = 0
for c in ex["nimble_claims"]:
    page = norm(" ".join(fetch_text(u) for u in c["urls"]))
    for e in c["excerpts"]:
        total += 1
        ok = norm(e) in page
        found += ok
        if not ok:
            print(f"  [{c['callout']}] NOT FOUND: {e[:100]}")
print(f"{found}/{total} Nimble excerpts found verbatim on the fetched pages\n")

# 3. Our independent judge vs. Nimble's per-claim confidence
print("=== Our verdict vs. Nimble confidence ===")
conf = {c["callout"]: c["confidence"] for c in ex["nimble_claims"]}
results = check(answer, ex["sources"])
for r in results:
    nim = ", ".join(f"[{n}] {conf.get(n, '?')}" for n in r["citations"])
    print(f"{r['verdict'].upper():13} | Nimble: {nim:25} | {r['claim'][:70]}")

json.dump(results, open("agent_results.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)