import json
from judge import check_coherence

data = json.load(open("demo_run.json", encoding="utf-8"))
data["results"] = [check_coherence(r) for r in data["results"]]
json.dump(data, open("demo_run.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for r in data["results"]:
    if r.get("coherent") is False:
        print(f"INCOHERENT: {r['claim'][:70]} | {r['verdict']} -> {r['implied_verdict']}")